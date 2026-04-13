import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Play } from 'lucide-react';

const Hero = () => {
  return (
    <section className="hero-section container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '0.5rem', 
          padding: '0.25rem 0.75rem', 
          borderRadius: '999px',
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          marginBottom: '2rem'
        }}
      >
        <span className="animate-pulse" style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-blue)' }}></span>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#60a5fa', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Now available as Chrome extension
        </span>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="headline font-bold"
      >
        Light up any link. <br /> 
        <span className="gradient-text">Ask anything.</span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="subheadline"
      >
        Paste any URL and have a real conversation about it. 
        Understand complex pages, compare websites, and get instant answers — in seconds.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass url-input-container"
      >
        <input 
          type="text" 
          placeholder="https://research.mit.edu/quantum-computing-breakthrough"
          className="url-input"
        />
        <button className="btn-secondary" style={{ padding: '0.5rem 1.5rem', borderRadius: '0.75rem', background: 'rgba(255, 255, 255, 0.05)' }}>
          Analyse
        </button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex-center"
        style={{ gap: '1rem' }}
      >
        <button className="btn-primary">
          Start for free <ArrowRight size={18} />
        </button>
        <button className="btn-secondary">
          <Play size={18} fill="currentColor" /> Watch demo
        </button>
      </motion.div>
    </section>
  );
};

export default Hero;
