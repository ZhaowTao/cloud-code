#!/usr/bin/env python3
"""
轻量级代理：将 Anthropic API 格式转换为 Ollama API 格式
"""
import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
from urllib.parse import urlparse
from datetime import datetime

OLLAMA_URL = "http://localhost:11434"
LOG_FILE = "/Users/dawn/bot/proxy.log"

# 重定向日志到文件
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        # 清空旧日志
        with open(log_file, 'w') as f:
            f.write(f"Proxy started at {datetime.now()}\n")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_line)

logger = Logger(LOG_FILE)

class AnthropicToOllamaHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 只记录到文件，不输出到终端
        logger.log(f"{args[0]}")
    
    def do_GET(self):
        """处理 GET 请求（如模型列表）"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/v1/models":
            try:
                req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
                with urllib.request.urlopen(req) as response:
                    ollama_data = json.loads(response.read().decode())
                    
                models = {
                    "data": [
                        {
                            "id": model["name"],
                            "object": "model",
                            "created": 0,
                            "owned_by": "ollama"
                        }
                        for model in ollama_data.get("models", [])
                    ]
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(models).encode())
            except Exception as e:
                logger.log(f"Error in GET /v1/models: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404)
    
    def do_POST(self):
        """处理 POST 请求（如聊天完成）"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/v1/messages":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                anthropic_req = json.loads(body.decode())
                
                # 记录到文件
                logger.log(f"Received request for model: {anthropic_req.get('model')}")
                
                # 转换为 Ollama 格式
                model = anthropic_req.get("model", "qwen3:14b")
                messages = anthropic_req.get("messages", [])
                max_tokens = min(anthropic_req.get("max_tokens", 1024), 2048)
                
                # 转换消息格式
                ollama_messages = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    if isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict) and "text" in part:
                                text_parts.append(part["text"])
                        content = "\n".join(text_parts)
                    
                    ollama_messages.append({
                        "role": role,
                        "content": content
                    })
                
                ollama_req = {
                    "model": model,
                    "messages": ollama_messages,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens
                    }
                }
                
                # 发送请求到 Ollama
                req = urllib.request.Request(
                    f"{OLLAMA_URL}/api/chat",
                    data=json.dumps(ollama_req).encode(),
                    headers={"Content-Type": "application/json"}
                )
                
                try:
                    with urllib.request.urlopen(req) as response:
                        ollama_data = json.loads(response.read().decode())
                except urllib.error.HTTPError as e:
                    error_body = e.read().decode()
                    logger.log(f"Ollama error: {e.code} - {error_body}")
                    raise
                
                # 转换为 Anthropic 格式
                content = ollama_data.get("message", {}).get("content", "")
                anthropic_resp = {
                    "id": "msg_" + str(hash(content))[:16],
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "text", "text": content}],
                    "model": model,
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": 0,
                        "output_tokens": len(content.split())
                    }
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(anthropic_resp).encode())
                
            except urllib.error.HTTPError as e:
                self.send_error(e.code, e.reason)
            except Exception as e:
                import traceback
                logger.log(f"Error: {e}\n{traceback.format_exc()}")
                self.send_error(500, str(e))
        else:
            self.send_error(404)

def main():
    port = 11435
    server = HTTPServer(("localhost", port), AnthropicToOllamaHandler)
    
    # 只打印一次启动信息到 stderr（这样不会干扰 stdout）
    print(f"🚀 代理服务器启动成功！日志: {LOG_FILE}", file=sys.stderr)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ 服务器已停止", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
