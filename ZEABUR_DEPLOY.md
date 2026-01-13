# SalesAgent Zeabur 部署指南

## 架构说明

本项目在生产环境使用**单容器多服务**架构：

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Nginx (端口 8000)                   │   │
│  │         反向代理，对外唯一入口                    │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│         ┌───────────────┼───────────────┐              │
│         ▼               ▼               ▼              │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐        │
│  │MCP Server │   │ Admin UI  │   │A2A Server │        │
│  │ (8080)    │   │ (8001)    │   │ (8091)    │        │
│  └───────────┘   └───────────┘   └───────────┘        │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    PostgreSQL       │
              │  (Zeabur Managed)   │
              └─────────────────────┘
```

入口脚本: `scripts/deploy/run_all_services.py`

## 部署步骤

### 步骤 1: 创建 Zeabur 项目

1. 登录 https://zeabur.com/
2. 点击 "Create Project"
3. 选择区域（推荐 Hong Kong 或 Singapore）

### 步骤 2: 添加 PostgreSQL 数据库

1. 在项目中点击 "Add Service"
2. 选择 "Marketplace" → "PostgreSQL"
3. 等待数据库创建完成（约 1-2 分钟）

### 步骤 3: 部署应用

1. 点击 "Add Service" → "Git"
2. 连接 GitHub 并选择 `toller892/adcp-salesagent-deploy` 仓库
3. Zeabur 会自动检测 `zeabur.json` 和 `Dockerfile`
4. 等待构建完成（首次约 5-10 分钟）

### 步骤 4: 配置环境变量

在应用的 "Variables" 标签中添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DATABASE_URL` | `${POSTGRES_CONNECTION_STRING}` | Zeabur 自动注入数据库连接 |
| `ENCRYPTION_KEY` | `E6YaI-HtJrA1z0eVZQfJqKANEzgCgdYkC3ipPhpNNAQ=` | Fernet 加密密钥 |
| `ADCP_AUTH_TEST_MODE` | `true` | 启用测试账号登录 |
| `PRODUCTION` | `true` | 生产模式 |

**重要**: `${POSTGRES_CONNECTION_STRING}` 是 Zeabur 的变量引用语法，会自动替换为实际的数据库连接字符串。

### 步骤 5: 配置网络

1. 点击应用服务
2. 进入 "Networking" 标签
3. 点击 "Public" 生成公网域名
4. **确保端口设置为 `8000`**

### 步骤 6: 验证部署

等待服务状态变为 "Running" 后，访问：

| 端点 | URL | 说明 |
|------|-----|------|
| Health | `https://<your-domain>/health` | 应返回 "healthy" |
| Dashboard | `https://<your-domain>/admin` | 管理界面 |
| MCP Server | `https://<your-domain>/mcp/` | AI 代理接口 |

### 步骤 7: 登录测试

测试账号（需要 `ADCP_AUTH_TEST_MODE=true`）：
- **Email**: `test_super_admin@example.com`
- **Password**: `test123`

## 环境变量详解

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `DATABASE_URL` | ✅ | - | PostgreSQL 连接字符串，格式: `postgresql://user:pass@host:5432/db` |
| `ENCRYPTION_KEY` | ✅ | - | Fernet 加密密钥，用于加密敏感数据。必须是 32 字节的 URL-safe base64 编码字符串 |
| `ADCP_AUTH_TEST_MODE` | ❌ | `false` | 设为 `true` 启用测试账号登录（生产环境建议关闭） |
| `PRODUCTION` | ❌ | `false` | 设为 `true` 启用生产模式日志 |
| `ADCP_MULTI_TENANT` | ❌ | `false` | 多租户模式（需要额外配置） |

## 故障排除

### 问题: 构建失败

**检查项**:
1. 确保 `Dockerfile` 在仓库根目录
2. 确保 `pyproject.toml` 和 `uv.lock` 存在
3. 查看 Build Logs 获取详细错误

### 问题: 启动失败 / 服务状态 UNKNOWN

**常见原因**:
1. `DATABASE_URL` 未设置或格式错误
2. `ENCRYPTION_KEY` 格式不正确（必须是有效的 Fernet 密钥）
3. 数据库连接失败

**解决方法**:
- 检查 Runtime Logs 查看具体错误
- 确保 PostgreSQL 服务已启动
- 验证环境变量是否正确设置

### 问题: 502 Bad Gateway

**原因**: Nginx 启动了但后端服务未响应

**解决方法**:
1. 检查 Runtime Logs 查看服务启动日志
2. 确保端口设置为 `8000`
3. 等待服务完全启动（首次启动需要运行数据库迁移）

### 问题: 登录页面无法登录

**检查项**:
1. 确保 `ADCP_AUTH_TEST_MODE=true` 已设置
2. 使用正确的测试账号: `test_super_admin@example.com` / `test123`
3. 检查浏览器控制台是否有错误

### 问题: 内存不足

**解决方法**:
- Zeabur 免费版可能内存有限
- 升级到付费计划获取更多资源
- 或使用其他平台（如自有服务器）

## 资源需求

| 资源 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 内存 | 512MB | 1GB+ |
| CPU | 0.5 核 | 1 核 |
| 存储 | 1GB | 2GB+ |

## 与本地开发的区别

| 方面 | 本地 (docker-compose) | Zeabur (生产) |
|------|----------------------|---------------|
| 容器数量 | 4 个独立容器 | 1 个容器 |
| 数据库 | 本地 PostgreSQL 容器 | Zeabur 托管 PostgreSQL |
| 服务启动 | 各容器独立启动 | `run_all_services.py` 统一管理 |
| Nginx | 独立容器 | 容器内进程 |
| 热重载 | 支持 | 不支持 |

## 生成新的 ENCRYPTION_KEY

如果需要生成新的加密密钥：

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

或使用 Node.js：

```javascript
const crypto = require('crypto');
console.log(crypto.randomBytes(32).toString('base64url') + '=');
```
