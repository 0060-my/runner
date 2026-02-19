import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

RUNNER_DIR = os.environ.get("RUNNER_WORKDIR", "/tmp/runner")
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
            subprocess.check_call([
                f"{RUNNER_DIR}/config.sh",
                "--url", repo,
                "--token", token,
                "--unattended",
                "--replace"
            ])

            with open(LOCK_FILE, "w") as f:
                f.write("installed")

            subprocess.Popen([f"{RUNNER_DIR}/run.sh"])

            self._resp(200, "Runner started")

        except Exception as e:
            self._resp(500, str(e))

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server running on {PORT}")
    server.serve_forever()
