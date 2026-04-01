# Claude Code + Ollama 本地运行版

基于 [instructkr/claude-code](https://github.com/instructkr/claude-code) 修改，支持连接本地 Ollama 模型，无需 API Key，完全免费。

## 特性

- ✅ 完全本地化运行，无需联网（除首次下载模型）
- ✅ 支持任意 Ollama 模型（qwen3、llama3、deepseek-coder 等）
- ✅ GPU 加速推理（Apple Silicon / NVIDIA）
- ✅ 一键启动脚本
- ✅ 代理服务器自动转换 Anthropic API ↔ Ollama API

## 系统要求

- macOS / Linux / Windows
- Python 3.9+
- Bun 运行时
- Ollama
- 8GB+ 内存（推荐 16GB+）

## 快速开始

### 1. 安装 Ollama

```bash
# macOS
brew install ollama

# 或其他方式
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. 下载模型

```bash
# 推荐模型（中文友好）
ollama pull qwen3:14b

# 或更小的模型（更快）
ollama pull qwen3:7b
```

### 3. 启动 Ollama 服务

```bash
ollama serve
```

### 4. 启动 Claude Code

```bash
./start-claude.sh
```

## 配置

编辑 `.env` 文件修改模型：

```bash
# 使用不同的模型
ANTHROPIC_MODEL=qwen3:7b
```

## 项目结构

```
.
├── bin/claude-haha          # Claude Code 入口脚本
├── src/                      # 源码（已修改支持 Ollama）
│   └── utils/model/validateModel.ts  # 模型验证逻辑
├── .env                      # 环境变量配置
├── ollama_proxy.py           # API 代理服务器
├── start-claude.sh           # 一键启动脚本
└── README.md                 # 本文件
```

## 核心修改

### 1. 模型验证绕过

修改 `src/utils/model/validateModel.ts`，添加本地模型检测：

```typescript
// 检查是否使用 Ollama 本地模型
const apiBaseUrl = process.env.ANTHROPIC_BASE_URL || ''
if (apiBaseUrl.includes('localhost') || apiBaseUrl.includes('127.0.0.1')) {
  validModelCache.set(normalizedModel, true)
  return { valid: true }
}
```

### 2. API 代理服务器

`ollama_proxy.py` 实现 Anthropic API 到 Ollama API 的转换：

- `/v1/models` → Ollama 模型列表
- `/v1/messages` → Ollama chat 接口
- 自动转换消息格式
- 限制 max_tokens 优化速度

### 3. 环境变量配置

`.env` 文件配置本地 Ollama：

```bash
ANTHROPIC_BASE_URL=http://localhost:11435  # 代理地址
ANTHROPIC_AUTH_TOKEN=ollama
ANTHROPIC_MODEL=qwen3:14b
```

## 性能优化

### 模型选择

| 模型 | 大小 | 速度 | 质量 |
|------|------|------|------|
| qwen3:7b | 4.5GB | 快 | 良好 |
| qwen3:14b | 9GB | 中等 | 优秀 |
| qwen3:30b | 18GB | 慢 | 极佳 |

### 显存优化

如果显存不足，可以使用量化版本：

```bash
ollama pull qwen3:14b-q4_K_M
```

## 故障排除

### 模型验证失败

确保代理服务器已启动：

```bash
curl http://localhost:11435/v1/models
```

### 响应慢

1. 检查 GPU 是否启用：`ollama ps`
2. 使用更小的模型
3. 限制 max_tokens（已自动限制为 2048）

### 代理日志

查看代理服务器日志：

```bash
tail -f proxy.log
```

## 许可证

基于原始 Claude Code 泄露源码修改，仅供学习和研究使用。

## 致谢

- [instructkr/claude-code](https://github.com/instructkr/claude-code) - 原始源码
- [Ollama](https://ollama.com) - 本地模型运行框架
- [Qwen](https://github.com/QwenLM/Qwen) - 通义千问模型
