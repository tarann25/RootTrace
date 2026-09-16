#!/usr/bin/env bash
# ==============================================================================
# RootTrace Startup Script
# Starts both FastAPI Backend (port 8000) and Vite React Frontend (port 5173)
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "=================================================="
echo "          Starting RootTrace Suite                "
echo "=================================================="

# 1. Check Ollama Status
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[✓] Local Ollama service is RUNNING (qwen2.5:7b)"
else
    echo "[!] Warning: Local Ollama service not detected on port 11434."
    echo "    Make sure to run 'ollama serve' if narrative synthesis fails."
fi

# 2. Check Virtual Environment
if [ ! -d "venv" ]; then
    echo "[✗] Python virtual environment 'venv' not found! Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 3. Start FastAPI Backend in background
echo "[*] Starting FastAPI Backend on http://127.0.0.1:8000 ..."
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# 4. Start Vite Frontend in background
echo "[*] Starting Vite React Frontend on http://127.0.0.1:5173 ..."
(cd frontend && npm run dev -- --host 127.0.0.1 --port 5173) &
FRONTEND_PID=$!

# Clean shutdown on Ctrl+C
cleanup() {
    echo -e "\n[*] Shutting down RootTrace services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "[✓] Stopped all services. Goodbye!"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "=================================================="
echo "    RootTrace is LIVE and ready to use!           "
echo "=================================================="
echo "  ▸ Web Dashboard:  http://localhost:5173"
echo "  ▸ FastAPI Backend: http://localhost:8000"
echo "  ▸ API Docs (Docs): http://localhost:8000/docs"
echo "=================================================="
echo "  (Press Ctrl+C to stop both servers)"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
