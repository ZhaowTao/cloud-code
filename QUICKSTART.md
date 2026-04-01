# Claude Code + Ollama 快速使用指南

## 📋 目录

1. [快速启动](#快速启动)
2. [完整启动流程](#完整启动流程)
3. [常用命令](#常用命令)
4. [使用技巧](#使用技巧)
5. [故障排除](#故障排除)

---

## 🚀 快速启动

### 方式一：一键启动（推荐）

```bash
cd /Users/dawn/bot
./start-all.sh
```

这个脚本会自动：
1. 启动 Ollama 服务
2. 启动 API 代理
3. 启动 Claude Code

### 方式二：分步启动

**终端 1 - 启动 Ollama：**
```bash
ollama serve
```

**终端 2 - 启动 Claude Code：**
```bash
cd /Users/dawn/bot
./start-claude.sh
```

---

## 📖 完整启动流程

### 1. 检查 Ollama 模型

```bash
# 查看已下载的模型
ollama list

# 查看运行中的模型
ollama ps
```

### 2. 下载新模型（可选）

```bash
# 中文编程推荐
ollama pull qwen3:14b

# 更快的版本
ollama pull qwen3:7b

# 英文编程
ollama pull codellama:13b
```

### 3. 配置模型

编辑 `.env` 文件：
```bash
# 切换模型
ANTHROPIC_MODEL=qwen3:7b
```

### 4. 启动服务

```bash
# 启动所有服务
./start-all.sh
```

---

## ⌨️ 常用命令

### Ollama 命令

| 命令 | 说明 |
|------|------|
| `ollama serve` | 启动 Ollama 服务 |
| `ollama list` | 列出已下载模型 |
| `ollama ps` | 查看运行中的模型 |
| `ollama pull <模型>` | 下载模型 |
| `ollama rm <模型>` | 删除模型 |
| `ollama run <模型>` | 直接运行模型对话 |

### Claude Code 命令

在 Claude Code 中输入：

| 命令 | 说明 |
|------|------|
| `/help` | 查看所有命令 |
| `/model` | 切换模型 |
| `/theme` | 切换主题 |
| `/cost` | 查看使用情况 |
| `Ctrl+C` | 中断当前操作 |
| `exit` 或 `quit` | 退出 |

---

## 💡 使用技巧

### 1. 高效提问

✅ **好的提问方式：**
```
帮我写一个 Python 函数，实现斐波那契数列，要求：
1. 使用递归方式
2. 添加类型注解
3. 包含异常处理
```

❌ **避免：**
```
写个斐波那契数列代码
```

### 2. 文件操作

```bash
# 让 Claude 读取文件
请帮我分析这个文件的内容：/path/to/file.py

# 让 Claude 修改文件
请把上面的函数改成迭代实现
```

### 3. 代码解释

```
请解释这段代码的作用：
[paste code here]
```

### 4. 多轮对话

Claude Code 会记住对话上下文，可以连续提问：
```
你：帮我写一个登录页面
Claude: [生成代码]
你：添加密码强度检查
Claude: [修改代码]
你：再用 CSS 美化一下
```

### 5. 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+T` | 切换主题 |
| `Ctrl+C` | 中断/取消 |
| `Tab` | 自动补全 |
| `↑/↓` | 历史记录 |

---

## 🔧 故障排除

### 问题 1：Ollama 连接失败

**现象：**
```
Error: could not connect to ollama
```

**解决：**
```bash
# 检查 Ollama 是否运行
ollama ps

# 如果没运行，重新启动
ollama serve
```

### 问题 2：模型验证失败

**现象：**
```
There's an issue with the selected model
```

**解决：**
```bash
# 检查代理是否运行
curl http://localhost:11435/v1/models

# 如果没运行，重启代理
./start-claude.sh
```

### 问题 3：响应太慢

**解决：**
1. 使用更小的模型（7B 代替 14B）
2. 检查 GPU 是否启用：`ollama ps`
3. 限制生成长度（已自动限制为 2048 tokens）

### 问题 4：内存不足

**解决：**
```bash
# 关闭其他程序
# 使用更小的模型
ollama pull qwen3:7b

# 编辑 .env 切换模型
ANTHROPIC_MODEL=qwen3:7b
```

---

## 📊 性能对比

| 模型 | 显存占用 | 速度 | 适合场景 |
|------|---------|------|---------|
| qwen3:7b | 4.5GB | 快 | 日常编程 |
| qwen3:14b | 9GB | 中等 | 复杂任务 |
| qwen3:30b | 18GB | 慢 | 高精度需求 |

---

## 📝 查看日志

```bash
# 查看代理日志
tail -f /Users/dawn/bot/proxy.log

# 查看 Ollama 日志
# (在 ollama serve 的终端中查看)
```

---

## 🎉 开始使用

现在你已经准备好了，开始你的 AI 编程之旅吧！

```bash
./start-all.sh
```

然后输入你的第一个问题：
```
你好，请帮我写一个 Python 爬虫程序
```
