# RootTrace 🛡️ // Incident Timeline Reconstructor

RootTrace is an **AI-powered cybersecurity Incident Timeline Reconstructor & Root Cause Analysis platform**. It ingests heterogeneous security logs from multiple disparate systems (Wazuh SIEM, AWS CloudTrail, Web Proxy, BIND DNS, Email Gateways), normalizes them into a canonical event schema, executes dynamic entity and network pivot correlations, and uses a local LLM (`qwen2.5:7b` via Ollama) to synthesize an executive root cause narrative and generate a forensic incident response report.

---

## ⚡ Quick Start (Run with 1 Command)

Make sure local **Ollama** is running:
```bash
ollama serve
```

Then start both the FastAPI backend and Vite frontend with:
```bash
./start.sh
```

- **Web Dashboard**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

*(Press `Ctrl+C` in the terminal anytime to cleanly stop both servers).*

---

## 🛠️ Manual Startup (Alternative)

If you prefer to run the backend and frontend in separate terminals:

### Terminal 1: Backend (FastAPI + SQLite)
```bash
# 1. Activate Python virtual environment
source venv/bin/activate

# 2. Start the API server
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Frontend (React + Vite)
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Start the Vite dev server
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 🚀 How to Use the App

1. Open **[http://localhost:5173](http://localhost:5173)** in your browser.
2. **Upload Logs**:
   - Drag & drop your alert log files (`alerts.json`, `cloudtrail.json`, `proxy_access.log`, `queries.log`, `email_gateway.json`).
   - Or click **"1-Click Phishing Attack Demo"** to test with the bundled synthetic dataset.
3. **Correlating Logs**:
   - Click **"Correlate & Generate RC Report"**.
   - Watch the animated radar screen while the correlation engine and local LLM analyze the attack timeline.
4. **Interactive Investigation**:
   - **Executive Summary Card**: Read the local LLM synthesized root cause narrative.
   - **Threat Metrics**: View total events, compromised users, malicious IPs, phishing domains, and attack duration.
   - **Entity Filters**: Click entity pills (`user:tsingh`, `ip:198.51.100.42`, `domain:...`) to dynamically filter the timeline.
   - **Vertical Timeline**: Inspect chronological events and expand **"Inspect Raw Log Evidence"** for deep forensics.
   - **Report Tab**: View and download the full `.md` report with 1 click.
5. **Start New Analysis**: Click **"+ Upload New Logs"** in the top navbar anytime.

---

## 📂 Project Structure

```
RootTrace/
├── start.sh                 # 1-command startup script
├── requirements.txt         # Python dependencies
├── src/
│   ├── api.py               # FastAPI REST endpoints
│   ├── database.py          # SQLite database schema (SQLAlchemy)
│   ├── pipeline.py          # Ingestion, correlation & report orchestrator
│   ├── correlation.py       # Dynamic entity & pivot correlation engine
│   ├── decoders.py          # Fast deterministic log decoders (Wazuh, CloudTrail, Proxy, DNS, Email)
│   ├── llm_extractor.py     # Local Ollama structured extraction
│   ├── report.py            # LLM narrative synthesis & Jinja2 report generator
│   └── schema.py            # CanonicalEventRecord Pydantic schema
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Interactive React SOC Dashboard
│   │   ├── App.css          # Cyber SOC theme & radar animation styles
│   │   └── index.css        # Base design tokens
│   └── package.json
├── data/
│   ├── roottrace.db         # SQLite persistent database
│   └── sample_phishing_01/  # Ground-truth synthetic attack logs
├── reports/                 # Generated Markdown forensic reports
└── templates/
    └── report_template.md   # Jinja2 incident report template
```
