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

        cmd = (
            "cd /actions-runner && "
            f"./config.sh --url {repo} --token {token} --unattended --replace && "
            "touch .installed.lock && "
            "./run.sh &"
        )
        
        exit_code = os.system(cmd)
        
        if exit_code != 0:
            self._resp(400, error)
            return
        self._resp(200, "runed")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server running on {PORT}")
    server.serve_forever()
