# RootTrace 🛡️ // Incident Timeline Reconstructor

RootTrace is an **AI-powered cybersecurity Incident Timeline Reconstructor & Root Cause Analysis platform**. It ingests heterogeneous security logs from multiple disparate enterprise systems (Wazuh SIEM, AWS CloudTrail, Web Proxy, BIND DNS, Email Gateways), normalizes them into a canonical event schema, executes dynamic entity and network pivot correlations, and uses an air-gapped local LLM (`qwen2.5:7b` via Ollama) to synthesize an executive root cause narrative and generate a 16-section forensic incident response report.

---

## 🌐 Dual Deployment Architecture: Local & Netlify + ngrok

RootTrace is architected with a flexible **hybrid operational model** to accommodate both strict air-gapped enterprise environments and remote cloud evaluations:

```
[ Live Netlify Edge CDN ]  --- HTTPS ---> [ ngrok Encrypted Bridge ] ---> [ Local FastAPI Backend ] ---> [ Local Ollama (qwen2.5) ]
 (Public Cyber SOC UI)                      (Bypasses Mixed Content)         (Port 8000 + SQLite)            (Air-Gapped AI Engine)
```

1. **Local Air-Gapped Mode**: The entire stack (FastAPI backend + Ollama LLM + Vite frontend) runs entirely offline on an analyst's workstation with zero external network dependencies.
2. **Cloud Netlify + ngrok Hybrid Mode**: 
   - The React frontend is deployed globally on **Netlify Edge CDN** with automated SPA redirect routing (`netlify.toml`).
   - The public Netlify web interface connects securely to the local backend workstation via an **ngrok encrypted HTTPS tunnel** (`./ngrok http 8000`), allowing remote evaluators to interact with the live local AI engine without exposing open ports or violating browser mixed-content security policies.
   - **In-Browser Dynamic Connector**: Analysts can paste or update their active ngrok tunnel URL directly from the top-navbar connection modal on Netlify without needing to trigger redeploys.
   - **Standalone Demo Fail-Safe**: If the local backend is offline, the Netlify app seamlessly falls back to client-side demonstration mode (`demoData.js`) so the interactive dashboard, entity filters, and report viewer remain accessible anywhere.

---

## ⚡ Quick Start: Running with Netlify & ngrok

If you are accessing RootTrace via the live Netlify deployment:

### Step 1: Start your Local Services
Ensure your local backend and Ollama instance are running on port `8000`:
```bash
# Terminal 1: Make sure Ollama is serving
ollama serve

# Terminal 2: Start local backend
source venv/bin/activate
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Open the ngrok Secure Ingress Tunnel
From the project root directory, launch the tunnel:
```bash
./ngrok http 8000
```
ngrok will display a forwarding line in your terminal:
```text
Forwarding   https://xxxx-xx-xx-xx.ngrok-free.app -> http://localhost:8000
```
Copy the `https://xxxx-xx-xx-xx.ngrok-free.app` URL.

### Step 3: Link on Netlify
1. Open your Netlify site URL in your browser.
2. Click the status badge in the top-right navbar: **`Cloud Demo Mode (Netlify) ⚙️`**.
3. Paste your ngrok HTTPS forwarding URL into the modal input and click **Connect**.
4. The badge will immediately switch to:
   > 🟢 **`Ollama: qwen2.5 (Online)`**

---

## 💻 Local 1-Command Startup (Offline Mode)

If you prefer to run both the frontend and backend strictly locally on your machine:

1. Ensure Ollama is active:
   ```bash
   ollama serve
   ```
2. Start both servers with the bundled startup script:
   ```bash
   ./start.sh
   ```

- **Web Dashboard**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

*(Press `Ctrl+C` in the terminal anytime to cleanly terminate both processes).*

---

## 🛠️ Manual Startup (Two Terminals)

### Terminal 1: Backend (FastAPI + SQLite)
```bash
source venv/bin/activate
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Frontend (React + Vite)
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 🚀 How to Use the App

1. Open the dashboard (on Netlify or `http://localhost:5173`).
2. **Ingest Telemetry**:
   - Click **"Load Synthetic Multi-Source Attack Suite (1-Click)"** to simulate an end-to-end credential phishing attack leading to AWS IAM reconnaissance.
   - Or drag & drop your own raw log files (`.json`, `.log`, `.csv`, `.eml`) into the upload dropzone and click **"Upload Logs & Reconstruct Incident"**.
3. **Forensic Correlation & Synthesis**:
   - Watch the animated radar screen as RootTrace executes log normalization, entity graph pivot correlation, and local LLM narrative deduction.
4. **Interactive Investigation**:
   - **Executive Summary**: Review the synthesized root cause narrative and confidence metrics.
   - **Threat Metrics Bar**: Inspect total correlated events, compromised accounts, attacker IPs, spoofed domains, and total incident duration.
   - **Entity Filter Pills**: Click pills (`user:tsingh`, `ip:198.51.100.42`, `domain:...`) to dynamically filter the chronological event graph.
   - **Vertical Timeline Cards**: Inspect chronological event hops, MITRE ATT&CK techniques, and expand **"Inspect Raw Log Evidence"** for deep payload inspection.
   - **16-Section RCA Report Tab**: Preview and download the full compliance-ready Markdown report with 1 click.

---

## 📂 Project Structure

```
RootTrace/
├── PROJECT_REPORT.md        # Comprehensive internship evaluation project report
├── README.md                # Project documentation and quickstart guide
├── start.sh                 # 1-command local startup script
├── netlify.toml             # Netlify deployment & SPA redirect configuration
├── ngrok                    # Standalone secure tunneling executable
├── requirements.txt         # Python dependencies
├── src/
│   ├── api.py               # FastAPI REST endpoints & CORS configuration
│   ├── database.py          # SQLite database schema (SQLAlchemy ORM)
│   ├── pipeline.py          # Multi-stage forensic pipeline orchestrator
│   ├── correlation.py       # Deterministic entity & pivot correlation engine
│   ├── decoders.py          # Log decoders (Wazuh, CloudTrail, Proxy, DNS, Email)
│   ├── llm_extractor.py     # Local Ollama structured extraction client
│   ├── report.py            # Local LLM narrative deduction & Jinja2 compiler
│   └── schema.py            # CanonicalEventRecord Pydantic validation schema
├── frontend/
│   ├── public/
│   │   └── _redirects       # Netlify SPA routing rules
│   ├── src/
│   │   ├── App.jsx          # Interactive React SOC Dashboard & ngrok connector
│   │   ├── App.css          # Cyber SOC dark theme & radar animation styles
│   │   ├── demoData.js      # Offline client fail-safe dataset for Netlify
│   │   └── index.css        # Base typography and design tokens
│   └── package.json
├── data/
│   ├── roottrace.db         # SQLite persistent database
│   └── sample_phishing_01/  # Ground-truth synthetic attack logs
├── reports/                 # Auto-generated Markdown forensic reports
└── templates/
    └── report_template.md   # Standardized 16-section incident report template
```

---

## 🛡️ Forensic Pipeline & Core Capabilities

- **Deterministic Decoders**: Fast regex and structured JSON extractors normalizing Wazuh alerts, AWS CloudTrail, Squid web proxy, BIND DNS queries, and email gateway logs into microsecond-accurate UTC records.
- **Entity Graph Pivot Correlation**: Rule-based mathematical joins across identity parameters (`user`), network nodes (`source_ip`, `destination_ip`), domain infrastructure (`domain`), and sliding time windows.
- **Air-Gapped Generative AI**: Local `qwen2.5:7b` inference via Ollama enforcing strict anti-hallucination prompt boundaries (zero external cloud data leakage).
- **Audit-Grade 16-Section RCA Reports**: Conforms to NIST SP 800-61 Rev. 2 and ISO/IEC 27035 incident response standards.
- **Robust Cloud-to-Local Bridge**: Seamless Netlify hosting with ngrok tunneling and `'ngrok-skip-browser-warning'` header integration.
