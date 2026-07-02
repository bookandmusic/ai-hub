# openai-image-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python >=3.11](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://www.python.org/)

基于 [FastMCP](https://github.com/jlowin/fastmcp) 的 MCP 服务器，将多个图像生成后端（`sensenova`、`modelscope` 等）分别暴露为独立的 MCP 工具。每个后端的 API endpoint、密钥、模型列表、异步模式、工具描述均通过环境变量配置，**代码不内置任何服务或默认配置**——所有 backend 都需通过 env vars 显式启用。适用于 opencode、Claude Code、Cursor 等 MCP 客户端。

---

## 快速启动

```bash
uvx --from "git+https://github.com/bookandmusic/ai-hub#subdirectory=mcp/openai-image-mcp" openai-image-mcp
```

无环境变量时启动会立即报错并提示需要配置的字段。配置环境变量后即可使用。

---

## 工具列表

| 工具名 | 说明 |
|---|---|
| `list_models` | 列出所有配置的后端、工具名和可用模型 |
| `<service>_generate_image` | 各 backend 对应的图像生成工具（动态注册） |

工具为动态注册：环境变量中每个 backend 对应一个 MCP 工具，工具名、模型列表均可自定义。工具描述：`TOOL_DESCRIPTION` env 优先，否则用通用模板 `Generate images via <service> backend`。

### 关于 `size` 参数

`generate_image` 工具的 `size` 参数为可选字符串（格式 `WxH`，如 `1024x1024`）：

- **不传**：让后端 API 用其默认尺寸
- **传非合法值**：代码不本地校验，请求发到后端 API 由它拒错（enum 校验已按 YAGNI 删除）
- **合法值列表**：代码不内置，需查阅对应 backend 的 API 文档

### 已知 backend 尺寸参考

以下尺寸列表来自 `sensenova` 和 `modelscope` 的 API 文档（**仅作参考**；以最新官方文档为准）：

**sensenova**（`sensenova-u1-fast`，2K 分辨率，11 种）：

| 尺寸 (WxH) | 宽高比 |
|---|---|
| 1664x2496 | 2:3 |
| 2496x1664 | 3:2 |
| 1760x2368 | 3:4 |
| 2368x1760 | 4:3 |
| 1824x2272 | 4:5 |
| 2272x1824 | 5:4 |
| 2048x2048 | 1:1 |
| 2752x1536 | 16:9 |
| 1536x2752 | 9:16 |
| 3072x1376 | 21:9 |
| 1344x3136 | 9:21 |

**modelscope**（Qwen-Image 系列，7 种）：

| 尺寸 (WxH) | 宽高比 |
|---|---|
| 1328x1328 | 1:1 |
| 1664x928 | 16:9 |
| 928x1664 | 9:16 |
| 1472x1140 | 4:3 |
| 1140x1472 | 3:4 |
| 1584x1056 | 3:2 |
| 1056x1584 | 2:3 |

其他 backend 的支持尺寸需查阅其 API 文档。

---

## 配置（环境变量）

### 命名约定

所有配置走三段式环境变量：

```
OPENAI_IMAGE_MCP_<SERVICE>_<FIELD>
└─ mcp 名 ──┘ └服务名┘ └字段┘
```

- **服务名**：小写字母 + 数字（不允许 `_` 或 `-`），upper 后作为 env 前缀
- **字段名**：固定集合，见下表

### 字段集合

| 字段 | 必填 | 含义 | 默认值 |
|---|---|---|---|
| `API` | ✅ | API endpoint URL（base_url） | — |
| `KEY` | ✅ | 认证密钥 | — |
| `MODEL` | ✅ | model_id 列表，逗号分隔 | — |
| `ASYNC` | ❌ | 异步模式（`true`/`false`） | `false` |
| `TIMEOUT` | ❌ | 单次 HTTP 请求超时（秒） | `120` |
| `TIMEOUT_POLL` | ❌ | 异步轮询间隔（秒） | `5` |
| `TIMEOUT_MAX_WAIT` | ❌ | 异步最大等待（秒） | `600` |
| `TOOL_NAME` | ❌ | MCP 工具名 | `<service>_generate_image` |
| `TOOL_DESCRIPTION` | ❌ | 工具描述 | 未设置时用通用模板 `Generate images via <service> backend` |

### 多 backend 自动识别

服务器启动时扫描所有 `OPENAI_IMAGE_MCP_<SERVICE>_<FIELD>` 环境变量，按服务名自动分组，无需列表锚点。每个服务必填 `API` / `KEY` / `MODEL` 三个字段，缺一即报错退出。

### 配置示例

```env
# Sensenova（同步模式）
OPENAI_IMAGE_MCP_SENSENOVA_API=https://token.sensenova.cn/v1
OPENAI_IMAGE_MCP_SENSENOVA_KEY=sk-...
OPENAI_IMAGE_MCP_SENSENOVA_MODEL=sensenova-u1-fast
OPENAI_IMAGE_MCP_SENSENOVA_TIMEOUT=600

# ModelScope（异步模式，Qwen-Image 系列）
OPENAI_IMAGE_MCP_MODELSCOPE_API=https://api-inference.modelscope.cn/v1
OPENAI_IMAGE_MCP_MODELSCOPE_KEY=ms-...
OPENAI_IMAGE_MCP_MODELSCOPE_MODEL=Qwen/Qwen-Image-2512,Qwen/Qwen-Image-Edit-2511
OPENAI_IMAGE_MCP_MODELSCOPE_ASYNC=true
```

### 添加新 backend

只需三步，零代码改动：

1. 选定服务名（小写字母 + 数字，如 `myapi`）
2. 设置三个必填字段：`OPENAI_IMAGE_MCP_MYAPI_API` / `_KEY` / `_MODEL`
3. （可选）设置 `ASYNC` / `TIMEOUT_*` / `TOOL_NAME` / `TOOL_DESCRIPTION`

启动后自动注册为 `myapi_generate_image` 工具，描述默认 `Generate images via myapi backend`（可通过 `TOOL_DESCRIPTION` 覆盖）。

> **约束**：`async: true` 当前仅兼容 ModelScope 异步协议（`X-ModelScope-Async-Mode` / `X-ModelScope-Task-Type` header）。其他 backend 请使用同步模式。

---

## 客户端配置

### opencode

```json
{
  "mcp": {
    "openai-image-mcp": {
      "type": "local",
      "command": [
        "uvx", "--from", "git+https://github.com/bookandmusic/ai-hub#subdirectory=mcp/openai-image-mcp",
        "openai-image-mcp"
      ],
      "env": {
        "OPENAI_IMAGE_MCP_SENSENOVA_API": "https://token.sensenova.cn/v1",
        "OPENAI_IMAGE_MCP_SENSENOVA_KEY": "sk-...",
        "OPENAI_IMAGE_MCP_SENSENOVA_MODEL": "sensenova-u1-fast",
        "OPENAI_IMAGE_MCP_SENSENOVA_TIMEOUT": "600",
        "OPENAI_IMAGE_MCP_MODELSCOPE_API": "https://api-inference.modelscope.cn/v1",
        "OPENAI_IMAGE_MCP_MODELSCOPE_KEY": "ms-...",
        "OPENAI_IMAGE_MCP_MODELSCOPE_MODEL": "Qwen/Qwen-Image-2512,Qwen/Qwen-Image-Edit-2511",
        "OPENAI_IMAGE_MCP_MODELSCOPE_ASYNC": "true"
      },
      "enabled": true,
      "timeout": 600000
    }
  }
}
```

### Claude Code

添加到 `~/.claude/settings.json`：

```json
{
  "mcpServers": {
    "openai-image-mcp": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/bookandmusic/ai-hub#subdirectory=mcp/openai-image-mcp",
        "openai-image-mcp"
      ],
      "env": {
        "OPENAI_IMAGE_MCP_SENSENOVA_API": "https://token.sensenova.cn/v1",
        "OPENAI_IMAGE_MCP_SENSENOVA_KEY": "sk-...",
        "OPENAI_IMAGE_MCP_SENSENOVA_MODEL": "sensenova-u1-fast",
        "OPENAI_IMAGE_MCP_MODELSCOPE_API": "https://api-inference.modelscope.cn/v1",
        "OPENAI_IMAGE_MCP_MODELSCOPE_KEY": "ms-...",
        "OPENAI_IMAGE_MCP_MODELSCOPE_MODEL": "Qwen/Qwen-Image-2512,Qwen/Qwen-Image-Edit-2511",
        "OPENAI_IMAGE_MCP_MODELSCOPE_ASYNC": "true"
      }
    }
  }
}
```

也可放在项目级 `.claude/settings.local.json` 中。

---

## License

MIT — 详见 [LICENSE](./LICENSE)。
