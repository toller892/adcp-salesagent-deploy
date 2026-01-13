"""Fix format_ids validation to allow parameterized formats

The original validation function only allowed agent_url and id fields.
This update allows additional optional fields: width, height, duration_ms
to support parameterized format IDs per AdCP spec.

Revision ID: fix_format_ids_validation
Revises: g1h2i3j4k5l6
Create Date: 2026-01-14 18:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fix_format_ids_validation"
down_revision: Union[str, Sequence[str], None] = "g1h2i3j4k5l6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update validate_format_ids to allow parameterized format fields."""
    
    # Drop existing function and recreate with relaxed validation
    validation_function = """
    CREATE OR REPLACE FUNCTION validate_format_ids(format_ids_json jsonb)
    RETURNS boolean AS $$
    DECLARE
        format_id jsonb;
        keys text[];
    BEGIN
        -- Must be array
        IF jsonb_typeof(format_ids_json) != 'array' THEN
            RAISE EXCEPTION 'format_ids must be a JSON array, got: %', jsonb_typeof(format_ids_json);
        END IF;

        -- Validate each FormatId object
        FOR format_id IN SELECT * FROM jsonb_array_elements(format_ids_json)
        LOOP
            -- Must be object
            IF jsonb_typeof(format_id) != 'object' THEN
                RAISE EXCEPTION 'Each format_id must be an object, got: %', jsonb_typeof(format_id);
            END IF;

            -- Must have at least agent_url and id (allow additional fields like width, height, duration_ms)
            SELECT array_agg(key) INTO keys FROM jsonb_object_keys(format_id) key;
            IF NOT (keys @> ARRAY['agent_url', 'id']) THEN
                RAISE EXCEPTION 'FormatId must have "agent_url" and "id" properties, got: %', keys;
            END IF;

            -- agent_url must be string
            IF jsonb_typeof(format_id->'agent_url') != 'string' THEN
                RAISE EXCEPTION 'FormatId.agent_url must be a string, got: %', jsonb_typeof(format_id->'agent_url');
            END IF;

            -- id must be string
            IF jsonb_typeof(format_id->'id') != 'string' THEN
                RAISE EXCEPTION 'FormatId.id must be a string, got: %', jsonb_typeof(format_id->'id');
            END IF;

            -- Validate agent_url is not empty
            IF length(format_id->>'agent_url') = 0 THEN
                RAISE EXCEPTION 'FormatId.agent_url cannot be empty string';
            END IF;

            -- Validate id is not empty
            IF length(format_id->>'id') = 0 THEN
                RAISE EXCEPTION 'FormatId.id cannot be empty string';
            END IF;
            
            -- Optional: validate width/height/duration_ms types if present
            IF format_id ? 'width' AND jsonb_typeof(format_id->'width') != 'number' THEN
                RAISE EXCEPTION 'FormatId.width must be a number, got: %', jsonb_typeof(format_id->'width');
            END IF;
            
            IF format_id ? 'height' AND jsonb_typeof(format_id->'height') != 'number' THEN
                RAISE EXCEPTION 'FormatId.height must be a number, got: %', jsonb_typeof(format_id->'height');
            END IF;
            
            IF format_id ? 'duration_ms' AND jsonb_typeof(format_id->'duration_ms') != 'number' THEN
                RAISE EXCEPTION 'FormatId.duration_ms must be a number, got: %', jsonb_typeof(format_id->'duration_ms');
            END IF;
        END LOOP;

        RETURN true;
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
    """
    
    op.execute(validation_function)


def downgrade() -> None:
    """Restore strict validation (only agent_url and id allowed)."""
    
    validation_function = """
    CREATE OR REPLACE FUNCTION validate_format_ids(format_ids_json jsonb)
    RETURNS boolean AS $$
    DECLARE
        format_id jsonb;
        keys text[];
    BEGIN
        -- Must be array
        IF jsonb_typeof(format_ids_json) != 'array' THEN
            RAISE EXCEPTION 'format_ids must be a JSON array, got: %', jsonb_typeof(format_ids_json);
        END IF;

        -- Validate each FormatId object
        FOR format_id IN SELECT * FROM jsonb_array_elements(format_ids_json)
        LOOP
            -- Must be object
            IF jsonb_typeof(format_id) != 'object' THEN
                RAISE EXCEPTION 'Each format_id must be an object, got: %', jsonb_typeof(format_id);
            END IF;

            -- Must have exactly 2 keys: agent_url and id
            SELECT array_agg(key) INTO keys FROM jsonb_object_keys(format_id) key;
            IF array_length(keys, 1) != 2 OR NOT (keys @> ARRAY['agent_url', 'id']) THEN
                RAISE EXCEPTION 'FormatId must have exactly "agent_url" and "id" properties, got: %', keys;
            END IF;

            -- agent_url must be string
            IF jsonb_typeof(format_id->'agent_url') != 'string' THEN
                RAISE EXCEPTION 'FormatId.agent_url must be a string, got: %', jsonb_typeof(format_id->'agent_url');
            END IF;

            -- id must be string
            IF jsonb_typeof(format_id->'id') != 'string' THEN
                RAISE EXCEPTION 'FormatId.id must be a string, got: %', jsonb_typeof(format_id->'id');
            END IF;

            -- Validate agent_url is not empty
            IF length(format_id->>'agent_url') = 0 THEN
                RAISE EXCEPTION 'FormatId.agent_url cannot be empty string';
            END IF;

            -- Validate id is not empty
            IF length(format_id->>'id') = 0 THEN
                RAISE EXCEPTION 'FormatId.id cannot be empty string';
            END IF;
        END LOOP;

        RETURN true;
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
    """
    
    op.execute(validation_function)
