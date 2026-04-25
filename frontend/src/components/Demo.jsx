import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// FastAPI can return detail as an array (422 validation errors) or a string
const parseApiError = (data) => {
  if (!data) return 'An unknown error occurred';
  if (Array.isArray(data.detail)) return data.detail.map(e => e.msg).join(', ');
  if (typeof data.detail === 'string') return data.detail;
  if (typeof data.message === 'string') return data.message;
  return JSON.stringify(data);
};

const Demo = ({ initialUrl, onUrlChange }) => {
  const [question, setQuestion] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAnswering, setIsAnswering] = useState(false);
  const [answer, setAnswer] = useState('');
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');
  const [useSearch, setUseSearch] = useState(false);
  const [isAutomating, setIsAutomating] = useState(false);
  const [automationSuccess, setAutomationSuccess] = useState(false);

  // Clear error when URL changes (e.g. returning from History)
  useEffect(() => { setError(''); }, [initialUrl]);

  const handleAutomate = async () => {
    const webhookUrl = localStorage.getItem('n8n_webhook_url');
    if (!webhookUrl) {
      setError("Please set your n8n Webhook URL in Settings (gear icon) first!");
      return;
    }

    setIsAutomating(true);
    setAutomationSuccess(false);
    try {
      let api_base = import.meta.env.VITE_API_URL || 'https://linklyt-backend.onrender.com';
      api_base = api_base.replace(/\/$/, "");

      const response = await fetch(`${api_base}/automate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          url, 
          summary, 
          answer,
          webhook_url: webhookUrl 
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(parseApiError(data));
      
      setAutomationSuccess(true);
      setTimeout(() => setAutomationSuccess(false), 3000);
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setIsAutomating(false);
    }
  };

  // Use props if provided, otherwise fallback to local state logic
  const url = initialUrl || '';
  const setUrl = onUrlChange;
  const handleAnalyze = async () => {
    if (!url) return;
    setIsAnalyzing(true);
    setError('');
    try {
      let api_base = import.meta.env.VITE_API_URL || 'https://linklyt-backend.onrender.com';
      api_base = api_base.replace(/\/$/, "");
      
      const response = await fetch(`${api_base}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(parseApiError(data));
      
      setSummary(data.summary);
      setAnswer(data.message);
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAsk = async () => {
    if (!url || !question) return;
    setIsAnswering(true);
    setAnswer('');
    setError('');
    try {
      let api_base = import.meta.env.VITE_API_URL || 'https://linklyt-backend.onrender.com';
      api_base = api_base.replace(/\/$/, "");

      const response = await fetch(`${api_base}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, question, use_search: useSearch }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(parseApiError(data));
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullAnswer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              fullAnswer += data.token;
              setAnswer(fullAnswer);
            } catch (e) {
              console.error("Error parsing stream chunk", e);
            }
          }
        }
      }
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setIsAnswering(false);
    }
  };

  return (
    <section id="demo" className="container" style={{ padding: '5rem 0', background: 'rgba(255, 255, 255, 0.01)' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.2rem', color: 'var(--text-secondary)' }}>Try it live</span>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginTop: '0.5rem' }}>See Linklyt in action</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Type a URL and question below</p>
      </div>

      <div className="glass" style={{ padding: '2rem', borderRadius: '2.5rem', maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="text" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence"
              className="url-input glass"
              style={{ borderRadius: '0.75rem', padding: '0.75rem 1.25rem', fontSize: '0.875rem' }}
            />
            <button 
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="btn-secondary"
              style={{ padding: '0.75rem 1.5rem', fontSize: '0.875rem', whiteSpace: 'nowrap' }}
            >
              {isAnalyzing ? 'Indexing...' : 'Analyse'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <input 
              type="text" 
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What are the main risks of AI?"
              className="url-input glass"
              style={{ borderRadius: '0.75rem', padding: '0.75rem 1.25rem', fontSize: '0.875rem', flex: 1 }}
            />
            <button 
              onClick={() => setUseSearch(!useSearch)}
              style={{ 
                padding: '0.75rem', 
                borderRadius: '0.75rem', 
                background: useSearch ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                border: useSearch ? '1px solid #06b6d4' : '1px solid rgba(255, 255, 255, 0.1)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              title="Deep Search Mode"
            >
              🌐
            </button>
            <button 
              onClick={handleAsk}
              disabled={isAnswering || isAnalyzing}
              className="btn-primary"
              style={{ padding: '0.75rem 1.5rem', fontSize: '0.875rem', whiteSpace: 'nowrap' }}
            >
              {isAnswering ? 'Analysing...' : 'Ask'}
            </button>
          </div>

          {summary && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              style={{ 
                padding: '1rem', 
                background: 'rgba(6, 182, 212, 0.05)', 
                borderRadius: '1rem', 
                borderLeft: '4px solid #06b6d4',
                fontSize: '0.875rem' 
              }}
            >
              <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#06b6d4' }}>Auto Summary:</strong>
              <div style={{ whiteSpace: 'pre-line' }}>{summary}</div>
            </motion.div>
          )}

          <AnimatePresence>
            {(error || answer) && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                style={{ 
                  marginTop: '1.5rem', 
                  padding: '1.5rem', 
                  background: error ? 'rgba(239, 68, 68, 0.05)' : 'rgba(255, 255, 255, 0.05)', 
                  borderRadius: '1.25rem', 
                  minHeight: '80px',
                  border: error ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid rgba(255, 255, 255, 0.05)'
                }}
              >
                <p style={{ 
                  fontSize: '0.875rem', 
                  color: error ? '#f87171' : 'var(--text-secondary)', 
                  lineHeight: 1.6, 
                  fontStyle: error ? 'normal' : 'italic' 
                }}>
                  {error || answer}
                </p>

                {answer && !isAnswering && !error && (
                  <div style={{ marginTop: '1.25rem', display: 'flex', justifyContent: 'flex-end' }}>
                    <button 
                      onClick={handleAutomate}
                      disabled={isAutomating}
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '0.5rem', 
                        background: automationSuccess ? 'rgba(34, 197, 94, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                        border: automationSuccess ? '1px solid #22c55e' : '1px solid rgba(255, 255, 255, 0.1)',
                        color: automationSuccess ? '#22c55e' : 'var(--text-secondary)',
                        padding: '0.4rem 0.8rem',
                        borderRadius: '0.6rem',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      {isAutomating ? 'Sending...' : automationSuccess ? '✓ Sent to n8n' : '⚡ Automate'}
                    </button>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

export default Demo;
