import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Book, ExternalLink, Clock, RefreshCw, Trash2, ChevronRight } from 'lucide-react';

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
      setError('Could not load your history. Is the server running?');
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
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
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
    <section id="history" className="py-24 relative overflow-hidden bg-[#0A0A0B]">
      {/* Background Orbs */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] translate-y-1/2 -translate-x-1/2" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4"
            >
              <Book className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-medium text-blue-400 uppercase tracking-wider">Your Library</span>
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-4xl md:text-5xl font-bold text-white mb-4"
            >
              Research History
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-gray-400 max-w-2xl"
            >
              Access your previous intelligence reports. Every link you index is stored in your personal vault for instant recall.
            </motion.p>
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={fetchHistory}
            className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white hover:bg-white/10 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Library
          </motion.button>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 mb-8">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence mode="popLayout">
            {isLoading && history.length === 0 ? (
              // Skeleton Loading
              [...Array(3)].map((_, i) => (
                <div key={i} className="h-48 rounded-2xl bg-white/5 border border-white/10 animate-pulse" />
              ))
            ) : history.length === 0 ? (
              <div className="col-span-full py-20 text-center rounded-3xl bg-white/5 border border-dashed border-white/10">
                <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Book className="w-8 h-8 text-gray-600" />
                </div>
                <p className="text-gray-500">No research history yet. Start by indexing your first link!</p>
              </div>
            ) : (
              history.map((item, index) => (
                <motion.div
                  key={item.url}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ y: -5 }}
                  className="group relative p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-500/30 hover:bg-white/[0.07] transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-white/5 p-2 flex items-center justify-center group-hover:bg-blue-500/10 transition-colors">
                      <img 
                        src={getFavicon(item.url)} 
                        alt="favicon" 
                        className="w-full h-full object-contain opacity-80 group-hover:opacity-100"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                      <div className="hidden w-full h-full items-center justify-center">
                        <Book className="w-6 h-6 text-gray-500" />
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-[10px] font-medium text-gray-500 uppercase tracking-tighter">
                      <Clock className="w-3 h-3" />
                      {formatDate(item.created_at)}
                    </div>
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2 line-clamp-1 group-hover:text-blue-400 transition-colors">
                    {item.title || 'Untitled Research'}
                  </h3>
                  <p className="text-xs text-gray-500 mb-6 line-clamp-1 font-mono">
                    {item.url}
                  </p>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => onSelectUrl(item.url)}
                      className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-colors"
                    >
                      Return to Research
                      <ChevronRight className="w-4 h-4" />
                    </button>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
                    >
                      <ExternalLink className="w-4 h-4" />
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
