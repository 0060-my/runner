import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 8080))
LOCK_FILE = "/runner/.installed.lock"

class Handler(BaseHTTPRequestHandler):

    def _response(self, code, body):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        if self.path == "/health":
            self._response(200, "OK")
        else:
            self._response(404, "Not Found")

    def do_POST(self):
        if self.path == "/setup":
            if os.path.exists(LOCK_FILE):
                self._response(200, "Runner already installed")
                return

            try:
                repo_url = os.environ.get("REPO_URL")
                token = os.environ.get("RUNNER_TOKEN")

                if not repo_url or not token:
                    self._response(400, "Missing REPO_URL or RUNNER_TOKEN")
                    return

                # 注册 runner
                subprocess.check_call([
                    "./config.sh",
                    "--url", repo_url,
                    "--token", token,
                    "--unattended",
                    "--replace"
                ])

                # 创建 lock 文件
                with open(LOCK_FILE, "w") as f:
                    f.write("installed")

                # 启动 runner（后台）
                subprocess.Popen(["./run.sh"])

                self._response(200, "Runner installed and started")

            except Exception as e:
                self._response(500, f"Error: {str(e)}")
        else:
            self._response(404, "Not Found")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server running on port {PORT}")
    server.serve_forever()
