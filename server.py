import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

RUNNER_DIR = "/actions-runner"
LOCK_FILE = f"{RUNNER_DIR}/.installed.lock"
PORT = int(os.environ.get("PORT", 8080))


class Handler(BaseHTTPRequestHandler):

    def _resp(self, code, msg):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(str(msg).encode())

    def do_GET(self):
        if self.path == "/health":
            self._resp(200, "OK")
        else:
            self._resp(404, "Not Found")

    def do_POST(self):
        try:
            if self.path != "/setup":
                self._resp(404, "Not Found")
                return
    
            print("==== /setup called ====")
    
            if os.path.exists(LOCK_FILE):
                self._resp(200, "Already installed")
                return
    
            repo = os.environ.get("REPO_URL")
            token = os.environ.get("RUNNER_TOKEN")
    
            print("Repo:", repo)
            print("Token exists:", bool(token))
    
            if not repo or not token:
                self._resp(400, "Missing REPO_URL or RUNNER_TOKEN")
                return
    
            cmd = [
                "./config.sh",
                "--url", repo,
                "--token", token,
                "--unattended",
                "--replace"
            ]
    
            print("Running config.sh...")
    
            result = subprocess.run(
                cmd,
                cwd=RUNNER_DIR,
                capture_output=True,
                text=True
            )
    
            print("Return code:", result.returncode)
            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
    
            if result.returncode != 0:
                msg = f"CONFIG FAILED\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                print(msg)
                self._resp(500, msg)
                return
    
            print("Config success")
    
            subprocess.Popen(["./run.sh"], cwd=RUNNER_DIR)
    
            self._resp(200, "Runner installed and started")
    
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("EXCEPTION:\n", tb)
            self._resp(500, tb)


if __name__ == "__main__":
    print("Working directory:", os.getcwd())
    print("Runner dir files:", os.listdir(RUNNER_DIR))

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server running on {PORT}")
    server.serve_forever()
