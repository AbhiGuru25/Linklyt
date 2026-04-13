import React from 'react';
import { motion } from 'framer-motion';

const Mockup = () => {
  return (
    <section className="container" style={{ padding: '5rem 0' }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        className="glass"
        style={{ 
          padding: '1.5rem', 
          borderRadius: '2.5rem', 
          position: 'relative' 
        }}
      >
        {/* Mockup Header */}
        <div className="glass" style={{ 
          display: 'flex', 
          alignItems: 'center', 
          padding: '1rem', 
          borderRadius: '1.25rem', 
          marginBottom: '1.5rem' 
        }}>
          <div style={{ 
            flex: 1, 
            fontSize: '0.75rem', 
            color: 'var(--text-secondary)', 
            fontFamily: 'monospace', 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap',
            marginRight: '1rem' 
          }}>
            https://research.mit.edu/quantum-computing-breakthrough
          </div>
          <div className="glass" style={{ 
            padding: '0.25rem 0.75rem', 
            borderRadius: '0.5rem', 
            fontSize: '0.75rem', 
            fontWeight: 600, 
            color: '#cbd5e1' 
          }}>
            Analyse
          </div>
        </div>

        {/* Chat area */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxHeight: '400px', overflow: 'hidden' }}>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ 
              width: '2rem', 
              height: '2rem', 
              borderRadius: '50%', 
              background: 'rgba(59, 130, 246, 0.2)', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              flexShrink: 0 
            }}>
              <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--accent-blue)' }}>L</span>
            </div>
            <div style={{ 
              background: 'rgba(255, 255, 255, 0.05)', 
              padding: '1rem', 
              borderRadius: '1.25rem', 
              borderTopLeftRadius: 0, 
              fontSize: '0.875rem', 
              color: '#d1d5db', 
              maxWidth: '80%' 
            }}>
              Page loaded. 8-minute read about MIT's quantum breakthrough. Ask me anything about it.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', flexDirection: 'row-reverse' }}>
            <div style={{ 
              width: '2rem', 
              height: '2rem', 
              borderRadius: '50%', 
              background: 'var(--accent-blue)', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              flexShrink: 0 
            }}>
              <span style={{ fontSize: '10px', fontWeight: 700, color: 'white' }}>A</span>
            </div>
            <div style={{ 
              background: 'var(--accent-blue)', 
              padding: '1rem', 
              borderRadius: '1.25rem', 
              borderTopRightRadius: 0, 
              fontSize: '0.875rem', 
              color: 'white', 
              maxWidth: '80%' 
            }}>
              What's the main discovery and how does it affect encryption?
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ 
              width: '2rem', 
              height: '2rem', 
              borderRadius: '50%', 
              background: 'rgba(59, 130, 246, 0.2)', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              flexShrink: 0 
            }}>
              <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--accent-blue)' }}>L</span>
            </div>
            <div className="glass" style={{ 
              padding: '1rem', 
              borderRadius: '1.25rem', 
              borderTopLeftRadius: 0, 
              fontSize: '0.875rem', 
              color: '#d1d5db', 
              maxWidth: '80%',
              borderColor: 'rgba(59, 130, 246, 0.2)' 
            }}>
              MIT researchers achieved stable 1000-qubit entanglement at room temperature — previously only possible near absolute zero. This directly threatens RSA encryption: algorithms that took classical computers billions of years could be broken in hours. The paper recommends transitioning to lattice-based cryptography by 2027.
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default Mockup;
