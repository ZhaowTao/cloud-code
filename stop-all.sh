#!/bin/bash
# Claude Code + Ollama 一键关闭脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Claude Code + Ollama 关闭工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================
# 关闭 Claude Code
# ============================================
echo -e "${YELLOW}[1/3] 检查 Claude Code...${NC}"

CLAUDE_PID=$(ps aux | grep "claude-haha" | grep -v grep | awk '{print $2}' || echo "")
if [ -n "$CLAUDE_PID" ]; then
    echo "  发现 Claude Code 进程 (PID: $CLAUDE_PID)"
    kill $CLAUDE_PID 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ Claude Code 已关闭${NC}"
else
    echo "  Claude Code 未运行"
fi

# ============================================
# 关闭代理服务器
# ============================================
echo -e "${YELLOW}[2/3] 检查代理服务器...${NC}"

PROXY_PID=$(lsof -ti:11435 2>/dev/null || echo "")
if [ -n "$PROXY_PID" ]; then
    echo "  发现代理进程 (PID: $PROXY_PID)"
    kill $PROXY_PID 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ 代理服务器已关闭${NC}"
else
    echo "  代理服务器未运行"
fi

# ============================================
# 关闭 Ollama（可选）
# ============================================
echo -e "${YELLOW}[3/3] 检查 Ollama...${NC}"

OLLAMA_PID=$(lsof -ti:11434 2>/dev/null || echo "")
if [ -n "$OLLAMA_PID" ]; then
    echo "  发现 Ollama 进程 (PID: $OLLAMA_PID)"
    echo ""
    read -p "是否关闭 Ollama 服务? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $OLLAMA_PID 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✓ Ollama 已关闭${NC}"
    else
        echo "  Ollama 保持运行"
    fi
else
    echo "  Ollama 未运行"
fi

# ============================================
# 清理完成
# ============================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ 清理完成${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 显示状态
echo "当前状态:"

# 检查端口占用
echo -n "  Claude Code: "
if ps aux | grep "claude-haha" | grep -v grep > /dev/null; then
    echo -e "${RED}运行中${NC}"
else
    echo -e "${GREEN}已停止${NC}"
fi

echo -n "  代理服务器: "
if lsof -ti:11435 > /dev/null 2>&1; then
    echo -e "${RED}运行中${NC}"
else
    echo -e "${GREEN}已停止${NC}"
fi

echo -n "  Ollama: "
if lsof -ti:11434 > /dev/null 2>&1; then
    echo -e "${YELLOW}运行中${NC} (如需关闭请再次运行本脚本)"
else
    echo -e "${GREEN}已停止${NC}"
fi

echo ""
echo "提示: 如需重新启动，请运行 ./start-all.sh"
echo ""
