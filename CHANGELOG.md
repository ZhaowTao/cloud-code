# Changelog

## [1.0.0] - 2026-04-01

### 新增

- **Ollama 本地模型支持**
  - 添加 `ollama_proxy.py` API 代理服务器
  - 支持 Anthropic API 到 Ollama API 的自动转换
  - 支持任意 Ollama 模型（qwen3、llama3、deepseek-coder 等）

- **一键启动脚本**
  - 添加 `start-claude.sh` 启动脚本
  - 自动检查 Ollama 服务状态
  - 自动启动/停止代理服务器
  - 退出时自动清理

### 修改

- **模型验证逻辑** (`src/utils/model/validateModel.ts`)
  - 添加本地模型检测，跳过 Anthropic API 验证
  - 检测 `ANTHROPIC_BASE_URL` 是否包含 localhost/127.0.0.1
  - 本地模型自动视为有效

- **启动脚本** (`bin/claude-haha`)
  - 使用完整路径调用 Bun (`~/.bun/bin/bun`)
  - 避免 PATH 问题

- **代理服务器** (`ollama_proxy.py`)
  - 限制 `max_tokens` 最大为 2048，优化响应速度
  - 日志写入文件，避免干扰 TUI 界面
  - 支持消息格式自动转换（数组 → 字符串）

### 配置

- **环境变量** (`.env`)
  - 默认使用本地 Ollama 代理 (`http://localhost:11435`)
  - 默认模型：`qwen3:14b`
  - 禁用遥测和非必要网络请求

## [原始版本] - 2026-03-31

### 来源

- 基于 [instructkr/claude-code](https://github.com/instructkr/claude-code) 仓库
- 原始泄露源码修复版本

### 功能

- 完整的 Ink TUI 交互界面
- 支持 MCP 服务器、插件、Skills
- 支持自定义 API 端点和模型
- 降级 Recovery CLI 模式
