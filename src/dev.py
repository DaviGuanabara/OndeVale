import subprocess
import signal

backend = subprocess.Popen(["uv", "run", "uvicorn", "backend.app:app", "--reload"])

frontend = subprocess.Popen(["npm", "run", "dev"], cwd="frontend")

try:
    backend.wait()
except KeyboardInterrupt:
    pass
finally:
    backend.terminate()
    frontend.terminate()
