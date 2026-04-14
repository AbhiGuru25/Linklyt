import { motion } from 'framer-motion';
import { Settings } from 'lucide-react';

const Navbar = ({ onOpenSettings }) => {
  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="glass glass-nav"
    >
      <div className="logo-container">
        <img src="/logo.png" alt="Linklyt Logo" style={{ width: '2rem', height: '2rem', borderRadius: '0.4rem' }} />
        <span className="text-xl font-bold tracking-tight" style={{ color: '#ffffff' }}>Link<span style={{ color: '#3b82f6' }}>lyt</span></span>
      </div>

      <div className="hidden-mobile" style={{ display: 'flex', gap: '2rem' }}>
        <a href="#features" className="text-sm font-medium" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Features</a>
        <a href="#how-it-works" className="text-sm font-medium" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>How it works</a>
        <a href="#pricing" className="text-sm font-medium" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Pricing</a>
      </div>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button 
          onClick={onOpenSettings}
          style={{ 
            background: 'none', 
            border: 'none', 
            color: 'var(--text-secondary)', 
            cursor: 'pointer',
            padding: '0.5rem',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <Settings size={20} />
        </button>
        <button className="btn-primary text-sm">
          Get started free
        </button>
      </div>
    </motion.nav>
  );
};

export default Navbar;
