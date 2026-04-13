import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, LayoutPanelLeft, Clock, Bell } from 'lucide-react';

const featureList = [
  {
    icon: <MessageSquare style={{ color: 'var(--accent-blue)' }} size={24} />,
    title: "Single URL Q&A",
    desc: "Paste any URL — article, docs, product page, research paper — and ask questions in plain language."
  },
  {
    icon: <LayoutPanelLeft style={{ color: '#a855f7' }} size={24} />,
    title: "Multi-URL compare",
    desc: "Paste 2-5 URLs and compare them side by side. Perfect for product research and competitor analysis."
  },
  {
    icon: <Clock style={{ color: '#22c55e' }} size={24} />,
    title: "URL memory",
    desc: "Every page you analyse is remembered forever. Ask about pages you visited weeks ago — no re-pasting."
  },
  {
    icon: <Bell style={{ color: '#f97316' }} size={24} />,
    title: "Page alerts",
    desc: "Monitor any URL for changes. Get notified when prices drop, policies update, or articles change."
  }
];

const Features = () => {
  return (
    <section id="features" className="container" style={{ padding: '5rem 0' }}>
      <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <span style={{ color: 'var(--accent-blue)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.2em', fontSize: '0.75rem' }}>Features</span>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginTop: '1rem', marginBottom: '1rem' }}>Everything you need to understand the web</h2>
        <p style={{ color: 'var(--text-secondary)' }}>Four powerful capabilities, one clean interface</p>
      </div>

      <div className="features-grid">
        {featureList.map((f, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="glass feature-card"
          >
            <div style={{ 
              width: '3rem', 
              height: '3rem', 
              borderRadius: '1rem', 
              background: 'rgba(255, 255, 255, 0.05)', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              marginBottom: '1.5rem' 
            }}>
              {f.icon}
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.75rem' }}>{f.title}</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.6 }}>{f.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default Features;
