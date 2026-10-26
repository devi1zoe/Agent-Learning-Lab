"""Loopback-only learning site with allowlisted offline Notebook execution."""
import argparse
import json
import os
import secrets
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.request import urlopen

from .web_catalog import ROOT, WEB, build


class LearningServer(ThreadingHTTPServer):
    daemon_threads = True
    # On Windows SO_REUSEADDR may bind a second server to the same live port.
    allow_reuse_address = False
    def __init__(self, address, catalog):
        super().__init__(address, Handler)
        self.catalog = catalog
        self.token = secrets.token_urlsafe(24)
        self.jobs = {}
        self.lock = threading.Lock()
        self.running = False
        self.allowed = {l["id"] for l in catalog["lessons"] if l["runnable"]}
        self.practice = {s["lesson"]: s["id"] for s in catalog["stages"] if s["id"] > 0}

    def start_job(self, lesson, mode="offline"):
        with self.lock:
            if self.running:
                return None
            self.running = True
            job_id = secrets.token_hex(8)
            self.jobs[job_id] = {"id": job_id, "status": "running", "log": "", "lesson": lesson, "mode": mode}
        def worker():
            job = self.jobs[job_id]
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            command = [sys.executable, "-m", "learning.verify_notebooks", "--offline", "--notebook", lesson]
            if mode == "practice":
                destination = ROOT / ".learning_output/web-practice" / job_id
                command = [sys.executable, "-m", "learning.course_practice", "--stage", str(self.practice[lesson]), "--output", str(destination)]
            logs = ROOT / ".learning_output/web-jobs"
            logs.mkdir(parents=True, exist_ok=True)
            logfile = logs / (job_id + ".log")
            try:
                with logfile.open("w", encoding="utf-8") as stream:
                    process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
                    started = time.monotonic()
                    while process.poll() is None:
                        job["log"] = logfile.read_text(encoding="utf-8", errors="replace")[-80000:]
                        if time.monotonic() - started > 240:
                            process.kill()
                            process.wait()
                            job["status"] = "failed"
                            job["log"] += "\n运行达到 240 秒上限，已终止验证进程。"
                            return
                        time.sleep(.3)
                job["log"] = logfile.read_text(encoding="utf-8", errors="replace")[-80000:]
                job["status"] = "passed" if process.returncode == 0 else "failed"
                # Include the actual outputs, not only the verifier's progress messages.
                executed = ROOT / ".learning_output/executed" / Path(lesson).name
                if mode == "offline" and executed.exists():
                    notebook = json.loads(executed.read_text(encoding="utf-8"))
                    outputs = []
                    for i, cell in enumerate(notebook["cells"]):
                        for output in cell.get("outputs", []):
                            value = output.get("text") or output.get("data", {}).get("text/plain") or output.get("traceback")
                            if value:
                                text = "".join(value) if isinstance(value, list) else str(value)
                                outputs.append(f"\n── CELL {i+1} ──\n" + text[:12000])
                    job["log"] += "\n\n实际单元格输出：\n" + "\n".join(outputs)[-80000:]
            except Exception as error:
                job["status"], job["log"] = "failed", f"{type(error).__name__}: {error}"
            finally:
                with self.lock:
                    self.running = False
        threading.Thread(target=worker, daemon=True).start()
        return job_id


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB / "dist"), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, format, *args):
        # Do not log session tokens, code or model payloads.
        pass

    def trusted_host(self):
        try:
            parsed = urlsplit("http://" + self.headers.get("Host", ""))
            return parsed.hostname in {"127.0.0.1", "localhost"} and parsed.port == self.server.server_port
        except ValueError:
            return False

    def json_response(self, status, value):
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if not self.trusted_host():
            return self.json_response(403, {"error": "invalid host"})
        path = urlsplit(self.path).path
        if path == "/api/status":
            return self.json_response(200, {"app": "miniagent-learning", "mode": "local", "token": self.server.token, "python": sys.version.split()[0]})
        if path.startswith("/api/jobs/"):
            job = self.server.jobs.get(path.rsplit("/", 1)[-1])
            return self.json_response(200 if job else 404, job or {"error": "unknown job"})
        if path.startswith("/api/"):
            return self.json_response(404, {"error": "unknown endpoint"})
        target = (WEB / "dist" / unquote(path).lstrip("/")).resolve()
        if not target.is_relative_to((WEB / "dist").resolve()) or target.is_dir() and path != "/":
            return self.json_response(404, {"error": "not found"})
        return super().do_GET()

    def do_POST(self):
        origin = self.headers.get("Origin")
        allowed_origins = {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}
        if (not self.trusted_host() or self.headers.get("X-MiniAgent-Token") != self.server.token or
                origin is not None and origin not in allowed_origins):
            return self.json_response(403, {"error": "only this local learning page may start experiments"})
        if urlsplit(self.path).path != "/api/run":
            return self.json_response(404, {"error": "unknown endpoint"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("invalid request size")
            body = json.loads(self.rfile.read(length))
            lesson = body.get("lesson")
            mode = body.get("mode", "offline")
            if not isinstance(lesson, str) or lesson not in self.server.allowed:
                raise ValueError("only known course notebooks can be run")
            if mode not in {"offline", "practice"} or mode == "practice" and lesson not in self.server.practice:
                raise ValueError("invalid experiment mode")
        except (ValueError, TypeError, AttributeError):
            return self.json_response(400, {"error": "请选择课程内的 Notebook，不接受任意代码或文件路径"})
        job_id = self.server.start_job(lesson, mode)
        if job_id is None:
            return self.json_response(409, {"error": "已有实验运行中，请等待它结束"})
        return self.json_response(202, {"id": job_id})


def main():
    parser = argparse.ArgumentParser(description="Build and serve the miniAgent learning site locally")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open the learning site in the default browser")
    args = parser.parse_args()
    catalog = build()
    try:
        server = LearningServer(("127.0.0.1", args.port), catalog)
    except OSError:
        url = f"http://127.0.0.1:{args.port}"
        try:
            status = json.load(urlopen(url + "/api/status", timeout=2))
        except Exception:
            raise
        if status.get("app") != "miniagent-learning":
            raise RuntimeError("Port is used by another application; choose --port 8766")
        print("miniAgent is already running:", url, flush=True)
        if args.open:
            webbrowser.open(url)
        return
    url = f"http://127.0.0.1:{server.server_port}"
    print("miniAgent learning site:", url, flush=True)
    print("Reading and offline course experiments are ready. Press Ctrl+C to stop.", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
