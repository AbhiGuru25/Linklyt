import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import Mockup from './components/Mockup';
import Demo from './components/Demo';
import Pricing from './components/Pricing';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      <Mockup />
      <Features />
      <Demo />
      <Pricing />
      <Footer />
    </div>
  );
}

export default App;
