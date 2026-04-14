import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Demo = ({ initialUrl, onUrlChange }) => {
  const [question, setQuestion] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAnswering, setIsAnswering] = useState(false);
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');

  // Use props if provided, otherwise fallback to local state logic
  const url = initialUrl || '';
  const setUrl = onUrlChange;

  const handleAnalyze = async () => {
    if (!url) return;
    setIsAnalyzing(true);
    setError('');
    try {
      let api_base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      // Safety: Remove trailing slash if present
      api_base = api_base.replace(/\/$/, "");
      
      const response = await fetch(`${api_base}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to analyze URL');
      setAnswer(data.message);
    } catch (err) {
      setError(err.message);
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
      let api_base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      // Safety: Remove trailing slash if present
      api_base = api_base.replace(/\/$/, "");

      const response = await fetch(`${api_base}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, question }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to get answer');
      setAnswer(data.answer);
    } catch (err) {
      setError(err.message);
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

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="text" 
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What are the main risks of AI?"
              className="url-input glass"
              style={{ borderRadius: '0.75rem', padding: '0.75rem 1.25rem', fontSize: '0.875rem' }}
            />
            <button 
              onClick={handleAsk}
              disabled={isAnswering || isAnalyzing}
              className="btn-primary"
              style={{ padding: '0.75rem 1.5rem', fontSize: '0.875rem', whiteSpace: 'nowrap' }}
            >
              {isAnswering ? 'Analysing...' : 'Ask'}
            </button>
          </div>

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
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

export default Demo;
