#!/usr/bin/env python3
"""
Claude Code 项目管理器
用于在 Mac 上方便地启动/停止 Claude Code + Ollama 服务
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header():
    """打印标题"""
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}  Claude Code 项目管理器{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print()

def print_menu():
    """打印菜单"""
    print("请选择操作:")
    print()
    print(f"  {Colors.GREEN}[1]{Colors.NC} 启动所有服务 (Ollama + 代理 + Claude Code)")
    print(f"  {Colors.RED}[2]{Colors.NC} 停止所有服务")
    print(f"  {Colors.YELLOW}[3]{Colors.NC} 查看服务状态")
    print(f"  {Colors.BLUE}[4]{Colors.NC} 仅启动代理 (不启动 Claude Code)")
    print()
    print(f"  {Colors.YELLOW}[0]{Colors.NC} 退出")
    print()

def run_command(cmd, capture_output=True):
    """运行 shell 命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"
    except Exception as e:
        return False, "", str(e)

def check_ollama():
    """检查 Ollama 是否运行"""
    success, _, _ = run_command("curl -s http://localhost:11434/api/tags > /dev/null 2>&1")
    return success

def check_proxy():
    """检查代理是否运行"""
    success, _, _ = run_command("curl -s http://localhost:11435/v1/models > /dev/null 2>&1")
    return success

def check_claude():
    """检查 Claude Code 是否运行"""
    success, stdout, _ = run_command("ps aux | grep 'claude-haha' | grep -v grep")
    return success and stdout.strip() != ""

def get_pid_by_port(port):
    """通过端口获取进程 ID"""
    success, stdout, _ = run_command(f"lsof -ti:{port} 2>/dev/null")
    if success and stdout.strip():
        return stdout.strip().split('\n')[0]
    return None

def get_claude_pid():
    """获取 Claude Code 进程 ID"""
    success, stdout, _ = run_command("ps aux | grep 'claude-haha' | grep -v grep | awk '{print $2}'")
    if success and stdout.strip():
        return stdout.strip().split('\n')[0]
    return None

def start_ollama():
    """启动 Ollama"""
    print(f"{Colors.YELLOW}[1/4] 检查 Ollama 服务...{Colors.NC}")
    
    if check_ollama():
        print(f"  {Colors.GREEN}✓ Ollama 已在运行{Colors.NC}")
        return True
    
    print(f"  {Colors.YELLOW}⚠ Ollama 未运行，正在启动...{Colors.NC}")
    
    # 检查 ollama 是否安装
    success, _, _ = run_command("command -v ollama")
    if not success:
        print(f"  {Colors.RED}✗ 错误：Ollama 未安装{Colors.NC}")
        print("请先安装 Ollama:")
        print("  brew install ollama")
        print("  或访问: https://ollama.com")
        return False
    
    # 后台启动 Ollama
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    # 等待 Ollama 启动
    print("  等待 Ollama 启动...")
    for i in range(30):
        if check_ollama():
            print(f"  {Colors.GREEN}✓ Ollama 启动成功{Colors.NC}")
            return True
        time.sleep(1)
    
    print(f"  {Colors.RED}✗ Ollama 启动超时{Colors.NC}")
    return False

def check_model():
    """检查并下载模型"""
    print(f"{Colors.YELLOW}[2/4] 检查模型...{Colors.NC}")
    
    # 从 .env 读取配置的模型
    model = "qwen3:14b"  # 默认模型
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("ANTHROPIC_MODEL="):
                    model = line.split("=")[1].strip().strip('"')
                    break
    
    print(f"  配置模型: {model}")
    
    # 检查模型是否已下载
    success, stdout, _ = run_command(f"ollama list | grep '{model}'")
    if success and stdout.strip():
        print(f"  {Colors.GREEN}✓ 模型 {model} 已就绪{Colors.NC}")
        return True
    
    print(f"  {Colors.YELLOW}⚠ 模型 {model} 未下载{Colors.NC}")
    print("  正在下载模型（这可能需要几分钟）...")
    
    # 下载模型
    success, _, stderr = run_command(f"ollama pull {model}", capture_output=False)
    if success:
        print(f"  {Colors.GREEN}✓ 模型下载完成{Colors.NC}")
        return True
    else:
        print(f"  {Colors.RED}✗ 模型下载失败: {stderr}{Colors.NC}")
        return False

def start_proxy():
    """启动代理服务器"""
    print(f"{Colors.YELLOW}[3/4] 启动代理服务器...{Colors.NC}")
    
    # 检查是否已运行
    if check_proxy():
        print(f"  {Colors.GREEN}✓ 代理服务器已在运行{Colors.NC}")
        return True
    
    # 检查端口是否被占用
    old_pid = get_pid_by_port(11435)
    if old_pid:
        print(f"  关闭旧代理进程 (PID: {old_pid})")
        run_command(f"kill {old_pid} 2>/dev/null")
        time.sleep(1)
    
    # 启动代理
    script_dir = Path(__file__).parent
    proxy_script = script_dir / "ollama_proxy.py"
    
    subprocess.Popen(
        [sys.executable, str(proxy_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    # 等待代理启动
    time.sleep(2)
    if check_proxy():
        print(f"  {Colors.GREEN}✓ 代理服务器已启动{Colors.NC}")
        return True
    else:
        print(f"  {Colors.RED}✗ 代理服务器启动失败{Colors.NC}")
        return False

def start_claude():
    """启动 Claude Code"""
    print()
    print(f"{Colors.YELLOW}[4/4] 启动 Claude Code...{Colors.NC}")
    print()
    print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
    print(f"{Colors.GREEN}  🎉 所有服务已就绪！{Colors.NC}")
    print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
    print()
    print("  提示:")
    print("    - 输入 '/help' 查看所有命令")
    print("    - 按 Ctrl+C 退出 Claude Code")
    print("    - 退出后会自动清理代理进程")
    print()
    print(f"{Colors.BLUE}{'-'*50}{Colors.NC}")
    print()
    
    # 启动 Claude Code
    script_dir = Path(__file__).parent
    claude_bin = script_dir / "bin" / "claude-haha"
    
    try:
        # 使用 exec 替换当前进程
        os.execv(str(claude_bin), [str(claude_bin)])
    except Exception as e:
        print(f"{Colors.RED}启动 Claude Code 失败: {e}{Colors.NC}")
        return False

def start_all():
    """启动所有服务"""
    print_header()
    
    # 步骤 1: 启动 Ollama
    if not start_ollama():
        return False
    
    # 步骤 2: 检查模型
    if not check_model():
        print(f"{Colors.YELLOW}警告: 模型检查失败，继续启动...{Colors.NC}")
    
    # 步骤 3: 启动代理
    if not start_proxy():
        return False
    
    # 步骤 4: 启动 Claude Code (这会替换当前进程)
    return start_claude()

def start_proxy_only():
    """仅启动代理"""
    print_header()
    
    # 启动 Ollama
    if not start_ollama():
        return False
    
    # 检查模型
    check_model()
    
    # 启动代理
    if start_proxy():
        print()
        print(f"{Colors.GREEN}✓ 代理服务器已启动{Colors.NC}")
        print(f"  地址: http://localhost:11435")
        print()
        print(f"{Colors.YELLOW}提示: 代理正在后台运行{Colors.NC}")
        print("      你可以现在使用 Trae IDE 或其他客户端连接")
        print("      按 Enter 键停止代理并退出...")
        input()
        stop_all()
    return True

def stop_all():
    """停止所有服务"""
    print_header()
    
    print(f"{Colors.YELLOW}[1/3] 检查 Claude Code...{Colors.NC}")
    claude_pid = get_claude_pid()
    if claude_pid:
        print(f"  发现 Claude Code 进程 (PID: {claude_pid})")
        run_command(f"kill {claude_pid} 2>/dev/null")
        time.sleep(1)
        print(f"  {Colors.GREEN}✓ Claude Code 已关闭{Colors.NC}")
    else:
        print("  Claude Code 未运行")
    
    print()
    print(f"{Colors.YELLOW}[2/3] 检查代理服务器...{Colors.NC}")
    proxy_pid = get_pid_by_port(11435)
    if proxy_pid:
        print(f"  发现代理进程 (PID: {proxy_pid})")
        run_command(f"kill {proxy_pid} 2>/dev/null")
        time.sleep(1)
        print(f"  {Colors.GREEN}✓ 代理服务器已关闭{Colors.NC}")
    else:
        print("  代理服务器未运行")
    
    print()
    print(f"{Colors.YELLOW}[3/3] 检查 Ollama...{Colors.NC}")
    ollama_pid = get_pid_by_port(11434)
    if ollama_pid:
        print(f"  发现 Ollama 进程 (PID: {ollama_pid})")
        response = input("  是否关闭 Ollama 服务? (y/N): ").strip().lower()
        if response == 'y':
            run_command(f"kill {ollama_pid} 2>/dev/null")
            time.sleep(1)
            print(f"  {Colors.GREEN}✓ Ollama 已关闭{Colors.NC}")
        else:
            print("  Ollama 保持运行")
    else:
        print("  Ollama 未运行")
    
    print()
    print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
    print(f"{Colors.GREEN}  ✓ 清理完成{Colors.NC}")
    print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
    print()
    show_status()

def show_status():
    """显示服务状态"""
    print("当前状态:")
    print()
    
    # Claude Code
    print(f"  Claude Code: ", end="")
    if check_claude():
        print(f"{Colors.RED}运行中{Colors.NC}")
    else:
        print(f"{Colors.GREEN}已停止{Colors.NC}")
    
    # 代理
    print(f"  代理服务器: ", end="")
    if check_proxy():
        print(f"{Colors.RED}运行中{Colors.NC}")
    else:
        print(f"{Colors.GREEN}已停止{Colors.NC}")
    
    # Ollama
    print(f"  Ollama: ", end="")
    if check_ollama():
        print(f"{Colors.YELLOW}运行中{Colors.NC}")
    else:
        print(f"{Colors.GREEN}已停止{Colors.NC}")
    
    print()

def main():
    """主函数"""
    # 确保在项目目录中运行
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    while True:
        print_header()
        print_menu()
        
        choice = input("请输入选项 (0-4): ").strip()
        print()
        
        if choice == '1':
            start_all()
            break  # start_all 会替换进程，不会执行到这里
        elif choice == '2':
            stop_all()
            break
        elif choice == '3':
            show_status()
            input("\n按 Enter 键继续...")
        elif choice == '4':
            start_proxy_only()
            break
        elif choice == '0':
            print(f"{Colors.GREEN}再见！{Colors.NC}")
            break
        else:
            print(f"{Colors.RED}无效选项，请重新选择{Colors.NC}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(f"\n{Colors.YELLOW}已取消{Colors.NC}")
        sys.exit(0)
