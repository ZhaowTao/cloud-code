#!/bin/bash
# Claude Code + Ollama 完整启动脚本
# 一键启动所有服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Claude Code + Ollama 完整启动器${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================
# 步骤 1: 启动 Ollama 服务
# ============================================
echo -e "${YELLOW}[1/4] 检查 Ollama 服务...${NC}"

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama 已在运行${NC}"
else
    echo -e "${YELLOW}⚠ Ollama 未运行，正在启动...${NC}"
    
    # 检查 ollama 是否安装
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}✗ 错误：Ollama 未安装${NC}"
        echo "请先安装 Ollama:"
        echo "  brew install ollama"
        echo "  或访问: https://ollama.com"
        exit 1
    fi
    
    # 后台启动 Ollama
    ollama serve &
    OLLAMA_PID=$!
    
    # 等待 Ollama 启动
    echo "  等待 Ollama 启动..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Ollama 启动成功 (PID: $OLLAMA_PID)${NC}"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ Ollama 启动超时${NC}"
            exit 1
        fi
    done
fi

# ============================================
# 步骤 2: 检查模型
# ============================================
echo -e "${YELLOW}[2/4] 检查模型...${NC}"

# 从 .env 读取配置的模型
MODEL=$(grep "ANTHROPIC_MODEL=" .env | cut -d'=' -f2 | tr -d '"' || echo "qwen3:14b")
echo "  配置模型: $MODEL"

# 检查模型是否已下载
if ollama list | grep -q "$MODEL"; then
    echo -e "${GREEN}✓ 模型 $MODEL 已就绪${NC}"
else
    echo -e "${YELLOW}⚠ 模型 $MODEL 未下载${NC}"
    echo "  正在下载模型（这可能需要几分钟）..."
    ollama pull "$MODEL"
    echo -e "${GREEN}✓ 模型下载完成${NC}"
fi

# ============================================
# 步骤 3: 启动代理服务器
# ============================================
echo -e "${YELLOW}[3/4] 启动代理服务器...${NC}"

# 检查端口是否被占用
PROXY_PID=$(lsof -ti:11435 2>/dev/null || echo "")
if [ -n "$PROXY_PID" ]; then
    echo "  关闭旧代理进程 (PID: $PROXY_PID)"
    kill $PROXY_PID 2>/dev/null || true
    sleep 1
fi

# 启动代理
python3 "$SCRIPT_DIR/ollama_proxy.py" > /dev/null 2>&1 &
PROXY_PID=$!

# 等待代理启动
sleep 2
if curl -s http://localhost:11435/v1/models > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 代理服务器已启动 (PID: $PROXY_PID)${NC}"
else
    echo -e "${RED}✗ 代理服务器启动失败${NC}"
    exit 1
fi

# ============================================
# 步骤 4: 启动 Claude Code
# ============================================
echo ""
echo -e "${YELLOW}[4/4] 启动 Claude Code...${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 所有服务已就绪！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  模型: $MODEL"
echo "  Ollama: http://localhost:11434"
echo "  代理: http://localhost:11435"
echo ""
echo "  提示:"
echo "    - 输入 '/help' 查看所有命令"
echo "    - 按 Ctrl+C 退出 Claude Code"
echo "    - 退出后会自动清理代理进程"
echo ""
echo -e "${BLUE}----------------------------------------${NC}"
echo ""

# 设置清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在关闭服务...${NC}"
    
    # 关闭代理
    if kill $PROXY_PID 2>/dev/null; then
        echo "  ✓ 代理已关闭"
    fi
    
    # 注意：我们不关闭 Ollama，因为它可能是系统服务
    echo "  ✓ 清理完成"
    echo ""
    echo "提示: Ollama 仍在后台运行"
    echo "      如需关闭，请运行: ./stop-all.sh"
}
trap cleanup EXIT

# 启动 Claude Code
./bin/claude-haha
