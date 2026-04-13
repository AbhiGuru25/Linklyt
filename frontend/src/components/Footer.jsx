import React from 'react';

const Footer = () => {
  return (
    <footer style={{ padding: '3rem 0', borderTop: '1px solid rgba(255, 255, 255, 0.05)', marginTop: '5rem' }}>
      <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <img src="/logo.png" alt="Linklyt Logo" style={{ width: '1.5rem', height: '1.5rem', borderRadius: '0.3rem' }} />
          <span style={{ fontSize: '1.125rem', fontWeight: 700, color: '#ffffff' }}>Link<span style={{ color: '#3b82f6' }}>lyt</span></span>
        </div>

        <div style={{ display: 'flex', gap: '2rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
          <a href="#" style={{ color: 'inherit', textDecoration: 'none' }}>Twitter</a>
          <a href="#" style={{ color: 'inherit', textDecoration: 'none' }}>GitHub</a>
          <a href="#" style={{ color: 'inherit', textDecoration: 'none' }}>Terms</a>
          <a href="#" style={{ color: 'inherit', textDecoration: 'none' }}>Privacy</a>
        </div>

        <p style={{ fontSize: '0.75rem', color: '#475569' }}>
          © 2026 Linklyt AI. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
