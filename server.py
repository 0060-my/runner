import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

RUNNER_DIR = "/actions-runner"
LOCK_FILE = f"{RUNNER_DIR}/.installed.lock"
PORT = int(os.environ.get("PORT", 8080))

class Handler(BaseHTTPRequestHandler):

    def _resp(self, code, msg):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(msg.encode())

    def do_GET(self):
        if self.path == "/health":
            self._resp(200, "OK")
        else:
            self._resp(404, "Not Found")

    def do_POST(self):
        if self.path != "/setup":
            self._resp(404, "Not Found")
            return

        if os.path.exists(LOCK_FILE):
            self._resp(200, "Already installed")
            return

        repo = os.environ.get("REPO_URL")
        token = os.environ.get("RUNNER_TOKEN")

        if not repo or not token:
            self._resp(400, "Missing REPO_URL or RUNNER_TOKEN")
            return
     try:
        cmd = [
            "./config.sh",
            "--url", repo,
            "--token", token,
            "--unattended",
            "--replace"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=RUNNER_DIR,      # 非常关键
            capture_output=True, # 捕获输出
            text=True            # 转成字符串
        )
        
        print("========== CONFIG.SH RESULT ==========")
        print("Return code:", result.returncode)
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
        print("======================================")
        
        if result.returncode != 0:
            raise Exception("Runner config failed")
        
        print("Config success, starting runner...")
        
        subprocess.Popen(
            ["./run.sh"],
            cwd=RUNNER_DIR
        )
        self._resp(200, exit_code)
    except Exception as e:
            self._resp(500, str(e))

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server running on {PORT}")
    server.serve_forever()
