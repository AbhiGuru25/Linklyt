import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Book, ExternalLink, Clock, RefreshCw, ChevronRight } from 'lucide-react';

const History = ({ onSelectUrl }) => {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'https://linklyt-backend.onrender.com';

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/history`);
      if (!response.ok) throw new Error('Failed to fetch research history');
      const data = await response.json();
      setHistory(data);
      setError(null);
    } catch (err) {
      console.error('History Error:', err);
      setError('Could not load library.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    }).format(date);
  };

  const getFavicon = (url) => {
    try {
      const domain = new URL(url).hostname;
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;
    } catch (e) {
      return '';
    }
  };

  return (
    <section className="history-section">
      <div className="container">
        <div className="history-header">
          <div className="history-title-group">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              className="logo-container"
              style={{ marginBottom: '1rem' }}
            >
              <div className="logo-icon" style={{ width: '1.5rem', height: '1.5rem' }}>
                <Book className="w-3 h-3 text-white" />
              </div>
              <span className="gradient-text font-bold text-xs uppercase tracking-tight">Your Library</span>
            </motion.div>
            
            <h2 className="headline" style={{ fontSize: '3rem', textAlign: 'left', margin: 0 }}>Research History</h2>
            <p className="subheadline" style={{ textAlign: 'left', margin: '1rem 0 0', maxWidth: '100%' }}>
              Access your previous intelligence reports instantly.
            </p>
          </div>

          <button onClick={fetchHistory} className="btn-secondary" style={{ width: 'fit-content' }}>
            <RefreshCw className={isLoading ? 'animate-pulse' : ''} style={{ width: '1rem' }} />
            Refresh Library
          </button>
        </div>

        {error && (
          <div className="glass" style={{ padding: '1.5rem', borderRadius: '1rem', color: '#f87171', marginBottom: '2rem' }}>
            {error}
          </div>
        )}

        <div className="history-grid">
          <AnimatePresence mode="popLayout">
            {isLoading && history.length === 0 ? (
              [...Array(3)].map((_, i) => (
                <div key={i} className="history-card glass animate-pulse" style={{ height: '200px' }} />
              ))
            ) : history.length === 0 ? (
              <div className="history-empty glass">
                <Book style={{ width: '2rem', height: '2rem', margin: '0 auto 1rem', opacity: 0.3 }} />
                <p>No research history yet. Start by indexing your first link!</p>
              </div>
            ) : (
              history.map((item, index) => (
                <motion.div
                  key={item.url}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="history-card glass"
                >
                  <div className="history-card-header">
                    <div className="history-card-icon">
                      <img src={getFavicon(item.url)} alt="fav" onError={(e) => (e.target.style.opacity = 0)} />
                    </div>
                    <div className="history-card-date">
                      <Clock style={{ width: '0.8rem' }} />
                      {formatDate(item.created_at)}
                    </div>
                  </div>

                  <h3 className="history-card-title">{item.title || 'Untitled Research'}</h3>
                  <p className="history-card-url">{item.url}</p>

                  <div className="history-card-actions">
                    <button onClick={() => onSelectUrl(item.url)} className="btn-history-load">
                      Return <ChevronRight style={{ width: '1rem' }} />
                    </button>
                    <a href={item.url} target="_blank" rel="noreferrer" className="btn-history-view">
                      <ExternalLink style={{ width: '1rem' }} />
                    </a>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

export default History;
