import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import Mockup from './components/Mockup';
import Demo from './components/Demo';
import Pricing from './components/Pricing';
import Footer from './components/Footer';

function App() {
  const [sharedUrl, setSharedUrl] = React.useState('');

  const handleHeroAnalyse = (url) => {
    setSharedUrl(url);
    const demoSection = document.getElementById('demo');
    if (demoSection) {
      demoSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero onAnalyse={handleHeroAnalyse} />
      <Mockup />
      <Features />
      <Demo initialUrl={sharedUrl} onUrlChange={setSharedUrl} />
      <Pricing />
      <Footer />
    </div>
  );
}

export default App;
