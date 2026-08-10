"""
Daily Brief Launcher - Starts Python Backend API and React Frontend concurrently (via Yarn)
"""

import subprocess
import sys
import os
import time
import signal

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

print("========================================================")
print("  🚀 Launching Daily Brief (Python Backend + React UI)  ")
print("========================================================")

processes = []

def cleanup(sig, frame):
    print("\n🛑 Stopping all servers...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# 1. Launch Python Backend (Port 8090)
print("🐍 Starting Python Backend on http://localhost:8090...")
backend_proc = subprocess.Popen([sys.executable, "main.py", "--port", "8090"], cwd=PROJECT_DIR)
processes.append(backend_proc)

time.sleep(1)

# 2. Launch React Frontend via Yarn (Port 3000)
frontend_dir = os.path.join(PROJECT_DIR, "frontend")
print("⚛️  Starting React Frontend (Yarn) on http://localhost:3000...")
frontend_proc = subprocess.Popen(["yarn", "dev"], cwd=frontend_dir)
processes.append(frontend_proc)

print("\n✅ Both servers are running! Press Ctrl+C to stop.")
print("   - React UI (Yarn): http://localhost:3000")
print("   - Python API: http://localhost:8090\n")

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    cleanup(None, None)
