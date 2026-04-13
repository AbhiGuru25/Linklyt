import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

const tiers = [
  {
    name: "Free",
    price: "0",
    period: "forever",
    features: [
      "5 URL queries per day",
      "7-day memory",
      "Single URL only",
      "Chrome extension"
    ],
    cta: "Get started",
    highlighted: false
  },
  {
    name: "Pro",
    price: "499",
    period: "per month",
    features: [
      "Unlimited URL queries",
      "Permanent memory",
      "Multi-URL comparison",
      "Page change alerts",
      "Export conversations"
    ],
    cta: "Start Pro — free 7 days",
    highlighted: true
  },
  {
    name: "Team",
    price: "1,999",
    period: "per month • 5 users",
    features: [
      "Everything in Pro",
      "Shared URL workspaces",
      "Team annotations",
      "Priority support"
    ],
    cta: "Contact us",
    highlighted: false
  }
];

const Pricing = () => {
  return (
    <section id="pricing" className="container" style={{ padding: '5rem 0' }}>
      <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <span style={{ color: 'var(--accent-blue)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.2em', fontSize: '0.75rem' }}>Pricing</span>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginTop: '1rem', marginBottom: '1rem' }}>Simple, honest pricing</h2>
        <p style={{ color: 'var(--text-secondary)' }}>Start free, upgrade when you need more</p>
      </div>

      <div className="pricing-grid">
        {tiers.map((t, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className={`glass pricing-card ${t.highlighted ? 'highlighted' : ''}`}
            style={{ position: 'relative' }}
          >
            {t.highlighted && <div className="badge">Most popular</div>}
            
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '1rem' }}>{t.name}</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.25rem' }}>
                <span style={{ fontSize: '2.25rem', fontWeight: 700 }}>₹{t.price}</span>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{t.period}</span>
              </div>
            </div>

            <ul style={{ listStyle: 'none', marginBottom: '2.5rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {t.features.map((f, j) => (
                <li key={j} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.875rem', color: '#cbd5e1' }}>
                  <Check size={16} style={{ color: 'var(--accent-blue)' }} />
                  {f}
                </li>
              ))}
            </ul>

            <button className={`${t.highlighted ? 'btn-primary' : 'btn-secondary'}`} style={{ width: '100%', justifyContent: 'center', padding: '1rem 0', fontSize: '12px' }}>
              {t.cta}
            </button>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default Pricing;
