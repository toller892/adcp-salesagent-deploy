# SalesAgent Zeabur 部署指南

## 项目信息

- **项目类型**: Python + Docker
- **Dockerfile**: 根目录 `Dockerfile`
- **暴露端口**: 8000
- **需要数据库**: PostgreSQL

## 部署步骤

### 1. 添加 PostgreSQL 数据库

在 Zeabur 项目中：
- 点击 "Add Service" → "Marketplace" → "PostgreSQL"
- 等待数据库创建完成

### 2. 部署应用

- 点击 "Add Service" → "Git" → 选择此仓库
- Zeabur 会自动检测 Dockerfile 并构建

### 3. 配置环境变量

在应用的 "Variables" 中添加：

```
DATABASE_URL=${POSTGRES_CONNECTION_STRING}
ENCRYPTION_KEY=E6YaI-HtJrA1z0eVZQfJqKANEzgCgdYkC3ipPhpNNAQ=
ADCP_AUTH_TEST_MODE=true
PRODUCTION=true
```

**注意**: `${POSTGRES_CONNECTION_STRING}` 是 Zeabur 的变量引用，会自动替换为实际的数据库连接字符串。

### 4. 配置网络

- 点击 "Networking" → "Public"
- 生成公网域名
- 端口设置为 `8000`

### 5. 验证部署

访问以下端点验证：

| 端点 | URL |
|------|-----|
| Health | `https://<your-domain>/health` |
| Dashboard | `https://<your-domain>/admin` |
| MCP Server | `https://<your-domain>/mcp/` |

### 6. 登录测试

测试账号：
- Email: `test_super_admin@example.com`
- Password: `test123`

## Docker 构建说明

本项目使用多阶段构建：

1. **Builder 阶段**: 安装 Python 依赖
2. **Runtime 阶段**: 运行应用

入口点: `/app/.venv/bin/python scripts/deploy/run_all_services.py`

该脚本会启动：
- Nginx 反向代理 (端口 8000)
- MCP Server (端口 8080)
- Admin UI (端口 8001)
- A2A Server

## 环境变量说明

| 变量 | 必需 | 说明 |
|------|------|------|
| DATABASE_URL | ✅ | PostgreSQL 连接字符串 |
| ENCRYPTION_KEY | ✅ | Fernet 加密密钥 (32字节 base64) |
| ADCP_AUTH_TEST_MODE | ❌ | 设为 `true` 启用测试账号登录 |
| PRODUCTION | ❌ | 设为 `true` 启用生产模式 |

## 故障排除

### 构建失败
- 检查 Dockerfile 是否在根目录
- 确保 `pyproject.toml` 和 `uv.lock` 存在

### 启动失败
- 检查 DATABASE_URL 是否正确设置
- 检查 ENCRYPTION_KEY 格式是否正确

### 502 Bad Gateway
- 确保端口设置为 8000
- 检查 Runtime Logs 查看错误信息

## 资源需求

- 内存: 建议 512MB+
- CPU: 共享即可
- 存储: 1GB+
