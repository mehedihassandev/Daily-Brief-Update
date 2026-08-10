"""
Main Entry point for Daily Brief Project (Python Backend + React Support)

Usage:
  python main.py             # Starts Python Backend API on port 8090
  python main.py --port 8090 # Starts Python Backend API on custom port
"""

import sys
import os

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app import run_backend_server

if __name__ == "__main__":
    port = 8090
    if len(sys.argv) > 1 and sys.argv[1] == "--port" and len(sys.argv) > 2:
        port = int(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
        
    run_backend_server(port=port)
