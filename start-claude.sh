#!/bin/bash
# Claude Code + Ollama 一键启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Claude Code + Ollama 启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Ollama 是否运行
echo -e "${YELLOW}[1/3] 检查 Ollama 服务...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama 已在运行${NC}"
else
    echo -e "${YELLOW}⚠ Ollama 未运行${NC}"
    echo ""
    echo "请在另一个终端先运行: ollama serve"
    echo "然后按回车继续..."
    read
fi

# 启动代理服务器
echo -e "${YELLOW}[2/3] 启动代理服务器...${NC}"
PROXY_PID=$(lsof -ti:11435 2>/dev/null || echo "")
if [ -n "$PROXY_PID" ]; then
    kill $PROXY_PID 2>/dev/null || true
    sleep 1
fi

# 启动代理，日志重定向到文件
python3 /Users/dawn/bot/ollama_proxy.py > /dev/null 2>&1 &
PROXY_PID=$!
echo -e "${GREEN}✓ 代理服务器已启动 (PID: $PROXY_PID)${NC}"
echo "  日志文件: /Users/dawn/bot/proxy.log"

# 等待代理服务器就绪
sleep 2

# 检查代理是否成功启动
if ! curl -s http://localhost:11435/v1/models > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ 代理服务器启动中，请稍等...${NC}"
    sleep 3
fi

# 启动 Claude Code
echo ""
echo -e "${YELLOW}[3/3] 启动 Claude Code...${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  所有服务已就绪！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 设置清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在关闭代理服务器...${NC}"
    kill $PROXY_PID 2>/dev/null || true
    echo -e "${GREEN}✓ 已清理${NC}"
}
trap cleanup EXIT

# 启动 Claude Code
cd /Users/dawn/bot
./bin/claude-haha
