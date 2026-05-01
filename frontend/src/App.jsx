import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import Mockup from './components/Mockup';
import Demo from './components/Demo';
import SettingsModal from './components/SettingsModal';
import Pricing from './components/Pricing';
import Footer from './components/Footer';
import History from './components/History';
import ReportView from './components/ReportView';

function App() {
  const [sharedUrl, setSharedUrl] = React.useState('');
  const [isSettingsOpen, setIsSettingsOpen] = React.useState(false);
  const [reportData, setReportData] = React.useState(null);

  const handleHeroAnalyse = (url) => {
    setSharedUrl(url);
    const demoSection = document.getElementById('demo');
    if (demoSection) {
      demoSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  if (reportData) {
    return <ReportView data={reportData} onBack={() => setReportData(null)} />;
  }

  return (
    <div className="min-h-screen">
      <Navbar onOpenSettings={() => setIsSettingsOpen(true)} />
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <Hero onAnalyse={handleHeroAnalyse} />
      <Mockup />
      <Features />
      <History onSelectUrl={handleHeroAnalyse} />
      <Demo initialUrl={sharedUrl} onUrlChange={setSharedUrl} onExportReport={setReportData} />
      <Pricing />
      <Footer />
    </div>
  );
}

export default App;
