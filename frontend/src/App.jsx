import React, { useState, useEffect } from 'react';

export default function App() {
  const [briefData, setBriefData] = useState(null);
  const [status, setStatus] = useState({ slack: false, jira: false, github: false, gemini: false, jira_domain: '', jira_email: '' });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [selectedEventIndex, setSelectedEventIndex] = useState(0);

  const [formData, setFormData] = useState({
    slack_token: '',
    jira_domain: '',
    jira_email: '',
    jira_token: '',
    github_token: '',
    gemini_key: ''
  });

  const checkStatus = async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      setStatus(data);
      if (data.jira_domain) {
        setFormData(prev => ({ ...prev, jira_domain: data.jira_domain, jira_email: data.jira_email || '' }));
      }
    } catch (err) {
      console.error('Error checking status:', err);
    }
  };

  const fetchBrief = async () => {
    setSyncing(true);
    try {
      const res = await fetch('/api/brief', { method: 'POST' });
      const data = await res.json();
      setBriefData(data);
    } catch (err) {
      alert('Error fetching brief: ' + err.message);
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    checkStatus();
    fetchBrief();
  }, []);

  const saveSettings = async (e) => {
    e.preventDefault();
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      setIsModalOpen(false);
      checkStatus();
      fetchBrief();
    } catch (err) {
      alert('Error saving settings: ' + err.message);
    }
  };

  const openTaskApp = (ticketId) => {
    if (!ticketId) return;
    ticketId = ticketId.trim();
    if (/^[A-Z]+-\d+$/i.test(ticketId)) {
      if (!status.jira_domain) {
        alert('Please set JIRA_DOMAIN in your .env or Settings modal.');
        setIsModalOpen(true);
        return;
      }
      window.open(`https://${status.jira_domain}/browse/${ticketId}`, '_blank');
    } else if (ticketId.toLowerCase().includes('pr') || ticketId.includes('-')) {
      window.open(`https://github.com/search?q=${encodeURIComponent(ticketId)}`, '_blank');
    } else {
      window.open(`https://google.com/search?q=${encodeURIComponent(ticketId)}`, '_blank');
    }
  };

  return (
    <div>
      {/* Navigation */}
      <nav class="top-nav">
        <a href="#" class="brand">
          <div class="brand-dot">D</div>
          Daily Brief
        </a>

        <div class="status-bar">
          <div class="status-indicator">
            <span class={status.slack ? "dot-green" : "dot-gray"}></span> Slack
          </div>
          <div class="status-indicator">
            <span class={status.jira ? "dot-green" : "dot-gray"}></span> Jira
          </div>
          <div class="status-indicator">
            <span class={status.github ? "dot-green" : "dot-gray"}></span> GitHub
          </div>
          <div class="status-indicator">
            <span class={status.gemini ? "dot-green" : "dot-gray"}></span> Gemini
          </div>

          <button class="btn-action" onClick={() => setIsModalOpen(true)}>⚙️ Settings</button>
          <button class="btn-action btn-sync" onClick={fetchBrief} disabled={syncing}>
            {syncing ? '⌛ Syncing...' : '✨ Sync Now'}
          </button>
        </div>
      </nav>

      {/* Main Container */}
      <div class="container">
        <div class="brief-wrapper">
          <div class="side-meta-left">10 AUG 2026</div>
          <div class="side-meta-right">10:54 AM</div>

          {/* Hero Artwork */}
          <div class="hero-artwork-card">
            <img src="https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1200&q=80" alt="Artwork" class="hero-img" />
            <div class="hero-overlay">
              <div class="brief-title-sub">The</div>
              <div class="brief-title-main">{briefData?.title || 'Monday Brief'}</div>
              <div class="hero-caption">{briefData?.subtitle || 'Loading your daily brief...'}</div>
            </div>
          </div>

          {/* Section: Push Work Forward */}
          {briefData?.push_work_title && (
            <div class="brief-section">
              <div class="push-card">
                <div class="push-content">
                  <div class="push-title">{briefData.push_work_title}</div>
                  <div class="push-desc">{briefData.push_work_desc}</div>
                </div>
                <div class="starburst-badge" onClick={() => alert('Status note copied to clipboard!')}>
                  Let's<br />do it →
                </div>
              </div>
            </div>
          )}

          {/* Section: Slack Channel Brief */}
          {briefData?.slack_brief && (
            <div class="brief-section">
              <div class="slack-box">
                <div class="slack-box-header">💬 Slack Channel Brief</div>
                <div>
                  {briefData.slack_brief.key_discussions?.map((disc, idx) => (
                    <div key={idx} class="slack-discussion-item">
                      <a href="slack://open" target="_blank" class="slack-channel-name">{disc.channel} ↗</a>
                      <div class="slack-discussion-text">{disc.summary}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Section: Top To-Dos */}
          {briefData?.top_todos && (
            <div class="brief-section">
              <div class="section-heading">Top to-dos</div>
              <div class="todo-list">
                {briefData.top_todos.map((todo, idx) => (
                  <div key={idx} class="todo-item">
                    <input type="checkbox" class="todo-checkbox" />
                    <div class="todo-text-wrap">
                      <div class="todo-title">
                        {todo.title}
                        <a href="#" onClick={(e) => { e.preventDefault(); openTaskApp(todo.ticket_id); }} class="ticket-badge">
                          📌 {todo.ticket_id} ↗
                        </a>
                      </div>
                      <div class="todo-detail">{todo.detail}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section: New Updates */}
          {briefData?.new_updates && (
            <div class="brief-section">
              <div class="section-heading">New updates</div>
              <div class="updates-list">
                {briefData.new_updates.map((update, idx) => (
                  <div key={idx} class="update-item">
                    <div class="update-icon-dot"></div>
                    <div class="update-content">
                      <div class="update-headline">{update.headline} <span class="update-tag">{update.project_tag}</span></div>
                      <div class="update-body">{update.body} 📌</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section: Schedule */}
          {briefData?.schedule && (
            <div class="brief-section">
              <div class="section-heading">Your day</div>
              <div class="schedule-grid">
                <div class="time-events-list">
                  {briefData.schedule.map((event, idx) => (
                    <div key={idx} class={`event-slot ${selectedEventIndex === idx ? 'active' : ''}`} onClick={() => setSelectedEventIndex(idx)}>
                      <span class="event-time">{event.time_slot.split('–')[0]}</span>
                      <span class="event-title">{event.title}</span>
                    </div>
                  ))}
                </div>

                <div class="meeting-prep-card">
                  <div>
                    <div class="prep-header">
                      {briefData.schedule[selectedEventIndex]?.title} — {briefData.schedule[selectedEventIndex]?.time_slot}
                    </div>
                    <div class="prep-body">{briefData.schedule[selectedEventIndex]?.prep_notes}</div>
                  </div>
                  <div class="prep-badge-position">
                    <div class="starburst-badge">Prep<br />me →</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Footer */}
          <footer class="brief-footer">
            <div>Made for you by <strong>Daily Brief</strong> using <strong>React</strong>, <strong>Python</strong>, <strong>Slack</strong>, <strong>Jira</strong>, <strong>GitHub</strong>, and <strong>Gemini AI</strong>.</div>
          </footer>
        </div>
      </div>

      {/* Settings Modal */}
      {isModalOpen && (
        <div class="modal-overlay">
          <div class="modal-card">
            <div class="modal-header">
              <h3>Workspace Integration Credentials (.env)</h3>
              <button onClick={() => setIsModalOpen(false)} style={{ background: 'none', border: 'none', color: '#646a78', cursor: 'pointer' }}>✕</button>
            </div>

            <form onSubmit={saveSettings}>
              <div class="form-group">
                <label class="form-label">Slack User / Bot Token</label>
                <input type="password" class="form-control" placeholder="SLACK_BOT_TOKEN (xoxb-...)" value={formData.slack_token} onChange={e => setFormData({ ...formData, slack_token: e.target.value })} />
              </div>

              <div class="form-group">
                <label class="form-label">Jira Domain</label>
                <input type="text" class="form-control" placeholder="JIRA_DOMAIN (yourorg.atlassian.net)" value={formData.jira_domain} onChange={e => setFormData({ ...formData, jira_domain: e.target.value })} />
              </div>

              <div class="form-group">
                <label class="form-label">Jira Email</label>
                <input type="email" class="form-control" placeholder="JIRA_EMAIL (you@company.com)" value={formData.jira_email} onChange={e => setFormData({ ...formData, jira_email: e.target.value })} />
              </div>

              <div class="form-group">
                <label class="form-label">Jira API Token</label>
                <input type="password" class="form-control" placeholder="JIRA_API_TOKEN" value={formData.jira_token} onChange={e => setFormData({ ...formData, jira_token: e.target.value })} />
              </div>

              <div class="form-group">
                <label class="form-label">GitHub Personal Access Token (PAT)</label>
                <input type="password" class="form-control" placeholder="GITHUB_PAT (ghp_...)" value={formData.github_token} onChange={e => setFormData({ ...formData, github_token: e.target.value })} />
              </div>

              <div class="form-group">
                <label class="form-label">Gemini API Key</label>
                <input type="password" class="form-control" placeholder="GEMINI_API_KEY (AIzaSy...)" value={formData.gemini_key} onChange={e => setFormData({ ...formData, gemini_key: e.target.value })} />
              </div>

              <button type="submit" class="btn-action btn-sync" style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}>
                Save Credentials to .env & Sync
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
