import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldAlert, 
  Terminal, 
  Network, 
  Clock, 
  FileText, 
  Download, 
  UploadCloud, 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp, 
  Filter, 
  AlertTriangle, 
  Sparkles, 
  RefreshCw, 
  Layers, 
  X, 
  Copy, 
  ExternalLink,
  Users,
  Globe,
  Radio,
  ArrowRight,
  PlusCircle,
  FileCode
} from 'lucide-react';
import './App.css';
import { DEMO_INCIDENT } from './demoData';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export default function App() {
  // viewMode: 'upload' | 'correlating' | 'dashboard'
  const [viewMode, setViewMode] = useState('upload');
  const [incidents, setIncidents] = useState([]);
  const [activeIncidentId, setActiveIncidentId] = useState(null);
  const [incidentData, setIncidentData] = useState(null);
  const [activeTab, setActiveTab] = useState('widgets'); // 'widgets' | 'report'
  const [selectedEntityFilter, setSelectedEntityFilter] = useState('ALL');
  const [expandedEvidence, setExpandedEvidence] = useState({});
  const [healthStatus, setHealthStatus] = useState({ online: false, ollama: false });
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [correlatingPhase, setCorrelatingPhase] = useState('Ingesting heterogeneous log files...');
  const [correlateProgress, setCorrelateProgress] = useState(15);
  
  const fileInputRef = useRef(null);

  useEffect(() => {
    checkHealth();
    fetchIncidents();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        setHealthStatus({ online: true, ollama: data.ollama_available });
      } else {
        setHealthStatus({ online: false, ollama: false });
      }
    } catch {
      setHealthStatus({ online: false, ollama: false });
    }
  };

  const downloadReportFile = () => {
    if (!incidentData?.report_markdown) return;
    const blob = new Blob([incidentData.report_markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const idSlug = (activeIncidentId || 'rca').slice(0, 8);
    link.download = `roottrace_incident_${idSlug}_report.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const fetchIncidents = async () => {
    try {
      const res = await fetch(`${API_BASE}/incidents`);
      if (res.ok) {
        const list = await res.json();
        setIncidents(list);
      }
    } catch (err) {
      console.error('Error fetching incidents:', err);
    }
  };

  const fetchIncidentDetails = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/incidents/${id}`);
      if (res.ok) {
        const data = await res.json();
        setIncidentData(data);
        setActiveIncidentId(id);
      }
    } catch (err) {
      console.error('Error fetching incident details:', err);
    }
  };

  const createNewIncident = async (title = 'Multi-Source Incident Analysis') => {
    try {
      const res = await fetch(`${API_BASE}/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });
      if (res.ok) {
        const created = await res.json();
        setIncidents(prev => [created, ...prev]);
        setActiveIncidentId(created.id);
        return created.id;
      }
    } catch (err) {
      console.error('Error creating incident:', err);
    }
    return null;
  };

  // Drag and Drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const dropped = Array.from(e.dataTransfer.files);
      setSelectedFiles(prev => [...prev, ...dropped]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const chosen = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...chosen]);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Start Correlation Flow (Upload + Reconstruct)
  const handleStartCorrelation = async () => {
    if (selectedFiles.length === 0) return;

    setViewMode('correlating');
    setCorrelatingPhase('Initializing investigation session & SQLite storage...');
    setCorrelateProgress(20);

    const incidentId = await createNewIncident('Custom Ingested Incident Investigation');
    if (!incidentId) {
      alert('Backend service not reachable. Ensure the local backend is running, or use the 1-Click Demo on Netlify.');
      setViewMode('upload');
      return;
    }

    try {
      // 1. Upload files
      setCorrelatingPhase('Ingesting uploaded log files into SQLite...');
      setCorrelateProgress(35);
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      await fetch(`${API_BASE}/incidents/${incidentId}/upload`, {
        method: 'POST',
        body: formData
      });

      // 2. Normalizing & Correlating
      setCorrelatingPhase('Normalizing heterogeneous logs into Canonical Event Records...');
      setCorrelateProgress(55);
      await new Promise(r => setTimeout(r, 600));

      setCorrelatingPhase('Executing Identity, Network & Phishing Pivot Correlation...');
      setCorrelateProgress(75);

      // 3. Call reconstruct (which calls Ollama)
      setCorrelatingPhase('Synthesizing executive root cause narrative via Local LLM (qwen2.5:7b)...');
      const res = await fetch(`${API_BASE}/incidents/${incidentId}/reconstruct`, {
        method: 'POST'
      });

      setCorrelateProgress(95);
      setCorrelatingPhase('Generating final forensic incident report...');

      if (res.ok) {
        await new Promise(r => setTimeout(r, 500));
        await fetchIncidentDetails(incidentId);
        await fetchIncidents();
        setSelectedFiles([]);
        setViewMode('dashboard');
      } else {
        const errData = await res.json();
        alert('Reconstruction failed: ' + (errData.detail || 'Unknown error'));
        setViewMode('upload');
      }
    } catch (err) {
      console.error('Correlation error:', err);
      alert('Correlation failed: ' + err.message);
      setViewMode('upload');
    }
  };

  // 1-Click Load Synthetic Sample Flow (with Netlify fail-safe client simulation)
  const handleLoadSampleSuite = async () => {
    setViewMode('correlating');
    setCorrelatingPhase('Ingesting synthetic multi-source phishing log suite...');
    setCorrelateProgress(25);

    try {
      const incidentId = await createNewIncident('Phishing-to-Cloud Reconnaissance Investigation');
      if (incidentId) {
        await fetch(`${API_BASE}/incidents/${incidentId}/load-sample`, { method: 'POST' });
        setCorrelateProgress(50);
        setCorrelatingPhase('Mapping Wazuh, CloudTrail, Proxy, DNS & Email into Canonical Records...');
        await new Promise(r => setTimeout(r, 600));

        setCorrelateProgress(75);
        setCorrelatingPhase('Executing dynamic entity correlation & synthesizing narrative via LLM...');

        const res = await fetch(`${API_BASE}/incidents/${incidentId}/reconstruct`, { method: 'POST' });
        setCorrelateProgress(95);
        setCorrelatingPhase('Finalizing forensic incident response report...');

        if (res.ok) {
          await new Promise(r => setTimeout(r, 500));
          await fetchIncidentDetails(incidentId);
          await fetchIncidents();
          setViewMode('dashboard');
          return;
        }
      }
    } catch (err) {
      console.warn('Backend unavailable, running in client-side demonstration mode:', err);
    }

    // Client-side fallback (works seamlessly on Netlify even without backend!)
    setCorrelateProgress(45);
    setCorrelatingPhase('Mapping Wazuh, CloudTrail, Proxy, DNS & Email into Canonical Records...');
    await new Promise(r => setTimeout(r, 700));

    setCorrelateProgress(70);
    setCorrelatingPhase('Executing dynamic entity correlation & synthesizing narrative...');
    await new Promise(r => setTimeout(r, 800));

    setCorrelateProgress(95);
    setCorrelatingPhase('Finalizing forensic incident response report...');
    await new Promise(r => setTimeout(r, 600));

    setIncidentData(DEMO_INCIDENT);
    setActiveIncidentId(DEMO_INCIDENT.id);
    setViewMode('dashboard');
  };

  const openPastIncident = async (id) => {
    await fetchIncidentDetails(id);
    setViewMode('dashboard');
  };

  const toggleEvidence = (eventId) => {
    setExpandedEvidence(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  const copyReportMarkdown = () => {
    if (incidentData?.report_markdown) {
      navigator.clipboard.writeText(incidentData.report_markdown);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  // Filter events by selected entity
  const filteredEvents = (incidentData?.events || []).filter(e => {
    if (selectedEntityFilter === 'ALL') return true;
    if (selectedEntityFilter.startsWith('user:')) {
      const u = selectedEntityFilter.replace('user:', '').toLowerCase();
      return e.user?.toLowerCase() === u || e.metadata?.target_user?.toLowerCase() === u;
    }
    if (selectedEntityFilter.startsWith('ip:')) {
      const ip = selectedEntityFilter.replace('ip:', '');
      return e.source_ip === ip || JSON.stringify(e.metadata).includes(ip);
    }
    if (selectedEntityFilter.startsWith('domain:')) {
      const dom = selectedEntityFilter.replace('domain:', '');
      return JSON.stringify(e.metadata).includes(dom) || e.raw_ref?.includes(dom);
    }
    return true;
  });

  return (
    <div className="app-container">
      {/* 1. Global Header / Navbar */}
      <nav className="navbar">
        <div className="brand" onClick={() => setViewMode('upload')} style={{ cursor: 'pointer' }}>
          <div className="brand-icon">
            <ShieldAlert size={24} />
          </div>
          <div>
            <div className="brand-title">ROOTTRACE</div>
            <div className="brand-subtitle">Incident Timeline Reconstructor</div>
          </div>
        </div>

        <div className="nav-actions">
          <div className="status-badge" title={healthStatus.online ? "Local Ollama Inference Engine Connected" : "Static Demo Mode active on Netlify"}>
            <span className={`pulse-dot ${healthStatus.ollama ? 'online' : healthStatus.online ? 'working' : 'online'}`}></span>
            <span>
              {healthStatus.ollama 
                ? 'Ollama: qwen2.5 (Online)' 
                : healthStatus.online 
                  ? 'Backend: Online (Ollama Offline)' 
                  : 'Cloud Demo Mode (Netlify)'}
            </span>
          </div>

          {viewMode === 'dashboard' && (
            <button 
              className="btn btn-primary"
              onClick={() => {
                setSelectedFiles([]);
                setViewMode('upload');
              }}
            >
              <PlusCircle size={16} />
              <span>Upload New Logs</span>
            </button>
          )}
        </div>
      </nav>

      {/* 2. STATE A: UPLOAD & INGESTION VIEW (Default Landing) */}
      {viewMode === 'upload' && (
        <div className="upload-hero-container">
          <div className="upload-hero-badge">
            <Radio size={14} />
            <span>Root Cause Forensic Analysis</span>
          </div>

          <h1 className="upload-hero-title">Reconstruct Incident Timeline</h1>
          <p className="upload-hero-desc">
            Upload heterogeneous security logs across your systems. RootTrace automatically standardizes them into a canonical schema, correlates attacker entities, and uses local AI to synthesize the complete chronological attack narrative.
          </p>

          <div className="upload-card-main">
            {/* Main Drag-and-Drop Zone */}
            <div 
              className={`main-dropzone ${isDragOver ? 'dragover' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                multiple 
                style={{ display: 'none' }} 
                onChange={handleFileChange}
                accept=".json,.log,.txt"
              />
              <UploadCloud className="dropzone-big-icon" />
              <div className="dropzone-title">
                Drag & Drop Alert Logs Here, or Click to Browse
              </div>
              <div className="dropzone-hint">
                Select one or more log files from any of your security systems
              </div>

              <div className="supported-tags">
                <span className="source-pill">Wazuh alerts.json</span>
                <span className="source-pill">AWS CloudTrail (.json)</span>
                <span className="source-pill">Web Proxy (.log)</span>
                <span className="source-pill">DNS Queries (.log)</span>
                <span className="source-pill">Email Gateway (.json)</span>
              </div>
            </div>

            {/* Selected Files Preview */}
            {selectedFiles.length > 0 && (
              <div className="selected-files-box">
                <div className="selected-files-header">
                  <span>Selected Logs for Reconstruction ({selectedFiles.length})</span>
                  <button 
                    style={{ background: 'transparent', border: 'none', color: 'var(--rose)', cursor: 'pointer', fontSize: '0.75rem' }}
                    onClick={() => setSelectedFiles([])}
                  >
                    Clear All
                  </button>
                </div>

                <div className="file-chips-grid">
                  {selectedFiles.map((f, i) => (
                    <div key={i} className="file-chip">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <FileCode size={15} color="var(--cyan)" />
                        <span>{f.name}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ color: 'var(--text-muted)' }}>{(f.size / 1024).toFixed(1)} KB</span>
                        <button className="file-remove-btn" onClick={() => removeFile(i)}>
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons Row */}
            <div className="upload-actions-row">
              <button 
                className="btn btn-secondary"
                onClick={handleLoadSampleSuite}
                title="Loads 5 synthetic phishing & cloud recon log files for immediate testing"
              >
                <Sparkles size={16} color="var(--amber)" />
                <span>1-Click Phishing Attack Demo</span>
              </button>

              <button 
                className="btn btn-primary"
                disabled={selectedFiles.length === 0}
                onClick={handleStartCorrelation}
                style={{ padding: '11px 24px', fontSize: '0.95rem' }}
              >
                <Terminal size={18} />
                <span>Correlate & Generate RC Report</span>
              </button>
            </div>
          </div>

          {/* Past Investigations List */}
          {incidents.length > 0 && (
            <div className="past-investigations-box">
              <div className="past-investigations-title">
                <Layers size={16} />
                <span>Past Investigation Reports ({incidents.length})</span>
              </div>
              <div className="past-investigations-list">
                {incidents.slice(0, 5).map(inc => (
                  <div key={inc.id} className="past-item" onClick={() => openPastIncident(inc.id)}>
                    <div>
                      <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.88rem' }}>{inc.title}</div>
                      <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        ID: {inc.id.slice(0, 16)}... • Status: {inc.status}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--cyan)' }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>View Report</span>
                      <ArrowRight size={15} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. STATE B: CORRELATING LOGS ANIMATION SCREEN */}
      {viewMode === 'correlating' && (
        <div className="correlating-screen">
          <div className="radar-wrapper">
            <div className="radar-ring inner"></div>
            <div className="radar-ring outer"></div>
            <div className="radar-sweep"></div>
            <ShieldAlert size={36} className="radar-center-icon" />
          </div>

          <h2 className="correlating-title">Correlating your logs...</h2>
          <div className="correlating-phase">{correlatingPhase}</div>

          <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: `${correlateProgress}%` }}></div>
          </div>

          <div className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Processing multi-source logs • Identifying attack vectors • Local LLM reasoning
          </div>
        </div>
      )}

      {/* 4. STATE C: RESULTS DASHBOARD WITH WIDGETS & TIMELINE */}
      {viewMode === 'dashboard' && (
        <>
          {/* Incident Control Bar */}
          <div className="incident-header">
            <div className="incident-meta">
              <div className="incident-title-row">
                <h1 className="incident-title">{incidentData?.title || 'Incident Investigation'}</h1>
                <span className={`badge-tag ${incidentData?.status || 'completed'}`}>
                  {incidentData?.status || 'completed'}
                </span>
              </div>
              <div className="incident-subtitle mono">
                ID: {incidentData?.id || '---'} • {incidentData?.events?.length || 0} Correlated Events
              </div>
            </div>

            <div className="view-tabs">
              <button 
                className={`tab-btn ${activeTab === 'widgets' ? 'active' : ''}`}
                onClick={() => setActiveTab('widgets')}
              >
                <Layers size={16} />
                <span>Timeline & Correlation Widgets</span>
              </button>
              <button 
                className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
                onClick={() => setActiveTab('report')}
              >
                <FileText size={16} />
                <span>Forensic Incident Report</span>
              </button>
            </div>
          </div>

          {activeTab === 'widgets' ? (
            <>
              {/* Executive Summary Widget */}
              <div className="summary-box">
                <div className="summary-header">
                  <div className="summary-title-wrapper">
                    <span className="summary-title">
                      <Terminal size={18} color="var(--cyan)" />
                      Root Cause Executive Summary
                    </span>
                    <span className="ai-pill">
                      <Sparkles size={12} /> Local LLM Synthesized
                    </span>
                  </div>

                  {incidentData?.report_markdown && (
                    <button 
                      onClick={downloadReportFile}
                      className="btn btn-outline"
                      style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                    >
                      <Download size={13} />
                      <span>Download Report</span>
                    </button>
                  )}
                </div>

                <div className="summary-content">
                  {incidentData?.summary || 'Reconstruction complete. Summary ready.'}
                </div>
              </div>

              {/* Threat Metrics Bar */}
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-info">
                    <span className="metric-label">Correlated Events</span>
                    <span className="metric-value">{incidentData?.metrics?.total_events || incidentData?.events?.length || 0}</span>
                  </div>
                  <div className="metric-icon-box cyan">
                    <Layers size={22} />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-info">
                    <span className="metric-label">Compromised Identities</span>
                    <span className="metric-value">{incidentData?.metrics?.compromised_users || incidentData?.entities?.users?.length || 0}</span>
                  </div>
                  <div className="metric-icon-box purple">
                    <Users size={22} />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-info">
                    <span className="metric-label">Pivot / Attacker IPs</span>
                    <span className="metric-value">{incidentData?.metrics?.malicious_ips || incidentData?.entities?.ips?.length || 0}</span>
                  </div>
                  <div className="metric-icon-box rose">
                    <Radio size={22} />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-info">
                    <span className="metric-label">Malicious Domains</span>
                    <span className="metric-value">{incidentData?.metrics?.phishing_domains || incidentData?.entities?.domains?.length || 0}</span>
                  </div>
                  <div className="metric-icon-box amber">
                    <Globe size={22} />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-info">
                    <span className="metric-label">Attack Duration</span>
                    <span className="metric-value">{incidentData?.metrics?.duration_minutes || 0}m</span>
                  </div>
                  <div className="metric-icon-box cyan">
                    <Clock size={22} />
                  </div>
                </div>
              </div>

              {/* Entity Filter Bar */}
              <div className="entity-filters">
                <span className="filter-label">
                  <Filter size={14} />
                  Entity Filter:
                </span>
                <button 
                  className={`entity-pill ${selectedEntityFilter === 'ALL' ? 'active' : ''}`}
                  onClick={() => setSelectedEntityFilter('ALL')}
                >
                  ALL ({incidentData?.events?.length || 0})
                </button>

                {(incidentData?.entities?.users || []).map(u => (
                  <button
                    key={`user-${u}`}
                    className={`entity-pill user ${selectedEntityFilter === `user:${u}` ? 'active' : ''}`}
                    onClick={() => setSelectedEntityFilter(`user:${u}`)}
                  >
                    user:{u}
                  </button>
                ))}

                {(incidentData?.entities?.ips || []).map(ip => (
                  <button
                    key={`ip-${ip}`}
                    className={`entity-pill ip ${selectedEntityFilter === `ip:${ip}` ? 'active' : ''}`}
                    onClick={() => setSelectedEntityFilter(`ip:${ip}`)}
                  >
                    ip:{ip}
                  </button>
                ))}

                {(incidentData?.entities?.domains || []).map(d => (
                  <button
                    key={`domain-${d}`}
                    className={`entity-pill domain ${selectedEntityFilter === `domain:${d}` ? 'active' : ''}`}
                    onClick={() => setSelectedEntityFilter(`domain:${d}`)}
                  >
                    domain:{d}
                  </button>
                ))}
              </div>

              {/* Vertical Chronological Timeline */}
              <div className="timeline-container">
                <div className="timeline-line"></div>

                {filteredEvents.length === 0 ? (
                  <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No events match the selected entity filter.
                  </div>
                ) : (
                  filteredEvents.map((evt) => {
                    const isExpanded = !!expandedEvidence[evt.id];
                    return (
                      <div key={evt.id} className="timeline-event-card">
                        <div className={`timeline-node ${evt.log_source}`}></div>

                        <div className="event-top-bar">
                          <span className={`event-source-tag source-${evt.log_source}`}>
                            {evt.log_source}
                          </span>
                          <span className="event-timestamp">
                            {evt.timestamp_utc ? evt.timestamp_utc.replace('T', ' ') : 'N/A'}
                          </span>
                        </div>

                        <div className="event-title">{evt.event_type}</div>

                        <div className="event-actors">
                          {evt.user && (
                            <div className="actor-item">
                              <span>User:</span>
                              <strong>{evt.user}</strong>
                            </div>
                          )}
                          {evt.source_ip && (
                            <div className="actor-item">
                              <span>Source IP:</span>
                              <strong>{evt.source_ip}</strong>
                            </div>
                          )}
                          {evt.host && (
                            <div className="actor-item">
                              <span>Host:</span>
                              <strong>{evt.host}</strong>
                            </div>
                          )}
                        </div>

                        {evt.metadata && Object.keys(evt.metadata).length > 0 && (
                          <div className="event-meta-chips">
                            {Object.entries(evt.metadata).map(([k, v]) => {
                              if (v === null || v === undefined || v === '') return null;
                              const valStr = typeof v === 'object' ? JSON.stringify(v) : String(v);
                              return (
                                <span key={k} className="meta-chip">
                                  <strong>{k}:</strong> {valStr.length > 55 ? `${valStr.slice(0, 55)}...` : valStr}
                                </span>
                              );
                            })}
                          </div>
                        )}

                        <button 
                          className="raw-evidence-toggle"
                          onClick={() => toggleEvidence(evt.id)}
                        >
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          <span>{isExpanded ? 'Hide Raw Evidence' : 'Inspect Raw Log Evidence'}</span>
                        </button>

                        {isExpanded && (
                          <div className="raw-evidence-block">
                            {evt.raw_ref || JSON.stringify(evt, null, 2)}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </>
          ) : (
            /* Report View Tab */
            <div className="report-pane">
              <div className="report-action-bar">
                <div>
                  <h2 style={{ margin: 0, fontSize: '1.25rem', color: '#fff' }}>Forensic Incident Response Report</h2>
                  <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Synthesized via Jinja2 & Local LLM (qwen2.5:7b)
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-secondary" onClick={copyReportMarkdown}>
                    <Copy size={16} />
                    <span>{copySuccess ? 'Copied!' : 'Copy Markdown'}</span>
                  </button>

                  <button 
                    className="btn btn-primary"
                    onClick={downloadReportFile}
                  >
                    <Download size={16} />
                    <span>Download Report (.md)</span>
                  </button>
                </div>
              </div>

              <div className="report-body">
                {incidentData?.report_markdown ? (
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                    {incidentData.report_markdown}
                  </pre>
                ) : (
                  <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No report available.
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
