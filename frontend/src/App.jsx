import React, { useState, useEffect } from 'react';
import MapComponent from './components/MapComponent';
import ReportModal from './components/ReportModal';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { 
  Shield, Map, AlertTriangle, Brain, Activity, 
  Layers, Lock, Globe, ChevronRight, Search, 
  Menu, X, Zap, Phone, BarChart3, Users,
  Smartphone, WifiOff, FileText, ArrowUpRight
} from 'lucide-react';

const AegisLanding = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [view, setView] = useState('landing'); // 'landing' | 'dashboard' | 'login'
  const [token, setToken] = useState(localStorage.getItem('aegis_token'));
  const [username, setUsername] = useState(localStorage.getItem('aegis_user'));
  const [role, setRole] = useState(localStorage.getItem('aegis_role'));

  const handleReportSubmit = (data) => {
    console.log("Report Submitted:", data);
    alert(`Report Submitted!\nType: ${data.type}\nLocation: ${data.location}`);
  };

  const handleLogin = (newToken, newUsername, newRole) => {
    setToken(newToken);
    setUsername(newUsername);
    setRole(newRole);
    localStorage.setItem('aegis_token', newToken);
    localStorage.setItem('aegis_user', newUsername);
    if (newRole) {
      localStorage.setItem('aegis_role', newRole);
    } else {
      localStorage.removeItem('aegis_role');
    }
    setView('dashboard');
  };

  const handleLogout = () => {
    setToken(null);
    setUsername(null);
    setRole(null);
    localStorage.removeItem('aegis_token');
    localStorage.removeItem('aegis_user');
    localStorage.removeItem('aegis_role');
    setView('landing');
  };

  // Handle scroll effects for navbar
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // --- LOGIN VIEW ---
  if (view === 'login') {
    return <Login onLogin={handleLogin} onCancel={() => setView('landing')} />;
  }

  // --- DASHBOARD VIEW ---
  if (view === 'dashboard') {
    // Allow public access (token can be null)
    return (
      <WebSocketProvider clientId={Math.floor(Math.random() * 1000000)}>
        <Dashboard onLogout={handleLogout} token={token} username={username} initialRole={role} />
      </WebSocketProvider>
    );
  }

  // --- LANDING PAGE VIEW ---
  return (
    <WebSocketProvider clientId={Math.floor(Math.random() * 1000000)}>
    <div className="min-h-screen">
      {/* --- Navigation --- */}
      <ReportModal 
        isOpen={isReportModalOpen} 
        onClose={() => setIsReportModalOpen(false)} 
        onSubmit={handleReportSubmit}
        token={token}
      />
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 border-b ${isScrolled ? 'bg-[#0A0F1A]/90 backdrop-blur-md border-blue-900/30 py-3' : 'bg-transparent border-transparent py-5'}`}>
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center gap-2 group cursor-pointer" onClick={() => setView('landing')}>
            <div className="relative">
              <Shield className="w-8 h-8 text-blue-500 fill-blue-500/10 group-hover:text-cyan-400 transition-colors" />
              <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold tracking-tight text-white">AEGIS<span className="text-blue-500">-AI</span></span>
              <span className="text-blue-500 text-[10px] uppercase tracking-[0.2em] text-cyan-400 font-mono">Geospatial Command</span>
            </div>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#mission" className="hover:text-white transition-colors">Mission</a>
            <a href="#technology" className="hover:text-white transition-colors">Technology</a>
            <a href="#intelligence" className="hover:text-white transition-colors">Intelligence</a>
            <button 
              onClick={() => setIsReportModalOpen(true)}
              className="flex items-center gap-2 px-5 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/50 rounded-sm font-mono text-xs tracking-widest uppercase transition-all"
            >
              <AlertTriangle className="w-3 h-3" />
              <span>Test Reporting Uplink</span>
            </button>
            <button 
              onClick={() => setView(token ? 'dashboard' : 'login')}
              className="flex items-center gap-2 px-6 py-2 bg-white text-black hover:bg-slate-200 rounded-sm font-bold transition-all shadow-[0_0_20px_rgba(255,255,255,0.3)]"
            >
              <span>{token ? 'OPEN DASHBOARD' : 'AGENCY LOGIN'}</span>
            </button>
          </div>

          {/* Mobile Menu Toggle */}
          <button className="md:hidden text-slate-300" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Nav Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 w-full bg-[#0D1117] border-b border-blue-900/30 p-6 flex flex-col gap-4 shadow-2xl">
            <a href="#mission" className="text-slate-300 py-2 border-b border-slate-800">Mission</a>
            <a href="#technology" className="text-slate-300 py-2 border-b border-slate-800">Technology</a>
            <button onClick={() => setView(token ? 'dashboard' : 'login')} className="w-full py-3 bg-white text-black font-bold rounded-sm mt-2">{token ? 'OPEN DASHBOARD' : 'AGENCY LOGIN'}</button>
          </div>
        )}
      </nav>

      {/* --- Hero Section (Hormozi: Grand Slam Offer) --- */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-cyber-grid opacity-30 pointer-events-none"></div>
        
        {/* Ambient Glows */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-[80px] pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-900/10 text-emerald-400 text-xs font-mono mb-8 animate-pulse-slow">
            <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
            STATUS: ACCEPTING PILOT PARTNERS FOR Q4 2025
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight mb-6 leading-[1.1]">
            Stop Managing Chaos. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300 text-glow">Start Commanding Your City.</span>
          </h1>
          
          <p className="max-w-3xl mx-auto text-lg md:text-xl text-slate-400 mb-10 leading-relaxed">
            The only AI-driven intelligence platform engineered specifically for Ethiopia's infrastructure. 
            <span className="text-white font-semibold"> Cut incident response times by 60%</span> without upgrading your existing hardware or internet connectivity.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm tracking-wide rounded-sm shadow-[0_0_20px_rgba(59,130,246,0.4)] transition-all flex items-center justify-center gap-2 group">
              SECURE PILOT ACCESS
              <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="w-full sm:w-auto px-8 py-4 bg-transparent hover:bg-white/5 border border-slate-600 text-slate-300 font-bold text-sm tracking-wide rounded-sm transition-all flex items-center justify-center gap-2">
              <Activity className="w-4 h-4" />
              SEE THE LIVE DEMO
            </button>
          </div>
          <p className="mt-4 text-xs text-slate-500 font-mono">Limited availability for Addis Ababa & Adama zones.</p>
        </div>

        {/* Hero Visual: The "Magic" Mechanism */}
        <div className="mt-20 relative max-w-5xl mx-auto h-[300px] md:h-[400px] border-x border-t border-blue-900/30 bg-[#0D1117]/50 backdrop-blur-sm rounded-t-xl overflow-hidden">
          <div className="absolute inset-0 grid grid-cols-6 grid-rows-4 gap-[1px] opacity-20">
            {[...Array(24)].map((_, i) => (
              <div key={i} className="bg-blue-500/10"></div>
            ))}
          </div>
          <div className="scanline-overlay"></div>
          
          {/* The "Map" Area */}
            <div className="h-[400px] bg-[#0F1520] relative">
              <MapComponent />
            </div>
        </div>
      </section>

      {/* --- The "Blind Spot" Problem (Brunson: Agitate) --- */}
      <section id="mission" className="py-24 bg-[#0A0F1A] border-y border-slate-800">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">The "2-Hour Gap" is Costing Lives.</h2>
          <p className="text-slate-400 text-lg mb-12">
            In most Ethiopian cities, there is a 2-hour delay between a major incident occurring and the command center getting a verified picture. 
            <span className="text-red-400"> That gap is where chaos happens.</span>
          </p>
          
          <div className="grid md:grid-cols-3 gap-8">
             <div className="p-6 bg-[#161B22] rounded border border-slate-800">
                <div className="text-red-500 font-bold text-xl mb-2">Unverified Noise</div>
                <p className="text-sm text-slate-500">Social media is faster than 911, but 80% of it is fake news or exaggeration.</p>
             </div>
             <div className="p-6 bg-[#161B22] rounded border border-slate-800">
                <div className="text-red-500 font-bold text-xl mb-2">Data Silos</div>
                <p className="text-sm text-slate-500">Police, Fire, and Traffic departments operate on different channels, leading to confusion.</p>
             </div>
             <div className="p-6 bg-[#161B22] rounded border border-slate-800">
                <div className="text-red-500 font-bold text-xl mb-2">Connectivity Blackouts</div>
                <p className="text-sm text-slate-500">When the network drops, traditional cloud systems go blind. You lose control.</p>
             </div>
          </div>
        </div>
      </section>

      {/* --- The Solution (Sutherland: Reframing) --- */}
      <section id="technology" className="py-24 bg-[#0D1117] relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-sm font-mono text-blue-400 tracking-wider uppercase mb-2">The AEGIS Advantage</h2>
            <h3 className="text-3xl md:text-4xl font-bold text-white">Military-Grade Situational Awareness</h3>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { 
                icon: WifiOff, 
                title: "Unbreakable Connectivity", 
                desc: "Our 'Offline-First' architecture caches data locally. Your command center keeps running even if the city-wide internet goes dark.",
                color: "text-blue-400" 
              },
              { 
                icon: Brain, 
                title: "Automated Triage AI", 
                desc: "Don't waste resources on false alarms. Our NLP algorithms analyze Amharic & English reports to filter spam with 98% accuracy.",
                color: "text-purple-400" 
              },
              { 
                icon: Users, 
                title: "Citizen Intelligence Grid", 
                desc: "Turn every smartphone in the city into a sensor. Verified crowdsourced data gives you eyes on the ground before units arrive.",
                color: "text-cyan-400" 
              },
              { 
                icon: Shield, 
                title: "The 'Truth' Dashboard", 
                desc: "A single pane of glass for Police, Fire, and EMS. Everyone sees the same map, the same threats, and the same status.",
                color: "text-emerald-400" 
              },
              { 
                icon: Phone, 
                title: "Legacy Integration", 
                desc: "Works with your existing radio systems and dispatch protocols. No need to retrain your entire force.",
                color: "text-red-400" 
              },
              { 
                icon: BarChart3, 
                title: "Predictive Policing", 
                desc: "Stop chasing incidents. Use historical data to deploy resources to hotspots *before* accidents happen.",
                color: "text-amber-400" 
              },
            ].map((feature, idx) => (
              <div key={idx} className="group p-6 bg-[#161B22] border border-slate-800 hover:border-blue-500/50 rounded-lg transition-all hover:bg-[#1C2128]">
                <div className={`p-3 rounded-md bg-slate-900 inline-block mb-4 border border-slate-700 group-hover:border-${feature.color.split('-')[1]}-500/30`}>
                  <feature.icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <h4 className="text-xl font-bold text-slate-100 mb-2">{feature.title}</h4>
                <p className="text-slate-400 text-sm leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* --- Map Showcase --- */}
      <section id="map-showcase" className="py-24 bg-[#0A0F1A] relative overflow-hidden">
        {/* Background Element */}
        <div className="absolute inset-0 bg-cyber-grid opacity-10"></div>

        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
              <span className="text-red-400 font-mono text-sm tracking-widest uppercase">Live System Feed</span>
            </div>
            <h2 className="text-4xl font-bold text-white mb-6">See Incidents As They Happen.</h2>
            <p className="text-slate-400 mb-8 text-lg">
              The AEGIS map provides a granular view of urban safety. Filter by category, view photos, and track incident status in real-time.
            </p>

            <ul className="space-y-4 mb-10">
              {[
                { label: "Category Filtering (Fire, Crime, Flood)", icon: Layers },
                { label: "Heatmap Visualization", icon: Activity },
                { label: "Photo Evidence & Timestamps", icon: FileText },
                { label: "Sub-city & Woreda Level Data", icon: Search },
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-3 text-slate-300">
                  <div className="p-1 rounded bg-slate-800 text-blue-400">
                    <item.icon className="w-4 h-4" />
                  </div>
                  {item.label}
                </li>
              ))}
            </ul>

            <button className="px-6 py-3 border border-blue-500 text-blue-400 hover:bg-blue-500/10 font-mono text-sm rounded-sm transition-colors uppercase tracking-wider">
              Explore Live Map
            </button>
          </div>

          {/* Map UI Mockup */}
          <div className="relative rounded-xl border border-slate-700 bg-[#0D1117] shadow-2xl overflow-hidden group">
            <div className="absolute top-0 w-full h-12 bg-[#161B22] border-b border-slate-700 flex items-center px-4 justify-between">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-slate-600"></div>
                <div className="w-3 h-3 rounded-full bg-slate-600"></div>
              </div>
              <div className="text-xs font-mono text-slate-500">map_view.js</div>
            </div>
            
            {/* The "Map" Area */}
            <div className="h-[400px] bg-[#0F1520] relative">
              <MapComponent />
            </div>
          </div>
        </div>
      </section>

      {/* --- AI Intelligence Section --- */}
      <section id="intelligence" className="py-24 bg-[#0D1117] border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center gap-12">
            <div className="md:w-1/2 order-2 md:order-1 relative">
              {/* Abstract AI Viz */}
              <div className="aspect-square bg-[#0A0F1A] rounded-2xl border border-slate-800 p-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10"></div>
                
                {/* Nodes */}
                <div className="absolute inset-0 flex items-center justify-center">
                   <div className="relative w-48 h-48">
                      <div className="absolute inset-0 border border-blue-500/30 rounded-full animate-[spin_10s_linear_infinite]"></div>
                      <div className="absolute inset-4 border border-cyan-500/30 rounded-full animate-[spin_15s_linear_infinite_reverse]"></div>
                      
                      <div className="absolute inset-0 flex items-center justify-center">
                         <Brain className="w-16 h-16 text-blue-400 drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
                      </div>
                      
                      {/* Floating Data Tags */}
                      <div className="absolute -top-4 -right-4 bg-slate-800 border border-blue-500/50 px-2 py-1 text-[10px] text-blue-300 rounded font-mono animate-bounce">NLP: Amharic</div>
                      <div className="absolute -bottom-4 -left-4 bg-slate-800 border border-purple-500/50 px-2 py-1 text-[10px] text-purple-300 rounded font-mono animate-bounce delay-700">Veracity: 98%</div>
                   </div>
                </div>
              </div>
            </div>

            <div className="md:w-1/2 order-1 md:order-2">
              <div className="inline-block px-3 py-1 bg-purple-900/20 border border-purple-500/30 rounded-full text-purple-400 text-xs font-mono mb-4">
                ARTIFICIAL INTELLIGENCE CORE
              </div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Automated Threat Classification
              </h2>
              <p className="text-slate-400 text-lg mb-8">
                AEGIS doesn't just display dots on a map. Our proprietary AI analyzes incoming reports in Amharic and English, filtering out spam and calculating severity scores instantly.
              </p>
              
              <div className="space-y-6">
                <div className="flex gap-4">
                   <div className="mt-1 bg-slate-800 p-2 rounded text-blue-400 h-fit"><Users className="w-5 h-5"/></div>
                   <div>
                     <h4 className="text-white font-bold text-sm">Spam & Fake Report Filtering</h4>
                     <p className="text-slate-500 text-sm mt-1">Cross-referencing multiple reports from the same location to verify authenticity.</p>
                   </div>
                </div>
                <div className="flex gap-4">
                   <div className="mt-1 bg-slate-800 p-2 rounded text-blue-400 h-fit"><Zap className="w-5 h-5"/></div>
                   <div>
                     <h4 className="text-white font-bold text-sm">Instant Severity Scoring</h4>
                     <p className="text-slate-500 text-sm mt-1">AI assigns a priority level (1-5) based on keywords like "Fire", "Injury", or "Blocked".</p>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- Reporting Workflow --- */}
      <section className="py-20 bg-[#0A0F1A]">
         <div className="max-w-7xl mx-auto px-6 text-center">
            <h2 className="text-3xl font-bold text-white mb-16">The 3-Step "Rapid Response" Protocol</h2>
            
            <div className="grid md:grid-cols-3 gap-8 relative">
               {/* Connecting Line (Desktop) */}
               <div className="hidden md:block absolute top-12 left-[20%] right-[20%] h-[2px] bg-gradient-to-r from-transparent via-slate-700 to-transparent z-0"></div>

               {[
                 { step: "01", title: "One-Touch Signal", desc: "No forms. No waiting. Citizens send a secure, geo-tagged signal in under 5 seconds.", icon: Smartphone },
                 { step: "02", title: "Instant Truth Verification", desc: "Our AI cross-references 50+ data points to validate the threat instantly. Zero false alarms.", icon: Brain },
                 { step: "03", title: "City-Wide Synchronization", desc: "Responders and citizens are alerted simultaneously. The gap between 'incident' and 'action' disappears.", icon: Globe },
               ].map((item, idx) => (
                 <div key={idx} className="relative z-10 flex flex-col items-center">
                    <div className="w-24 h-24 bg-[#161B22] border border-slate-700 rounded-full flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(0,0,0,0.5)] group hover:border-blue-500 transition-colors">
                       <item.icon className="w-10 h-10 text-slate-400 group-hover:text-blue-400 transition-colors" />
                    </div>
                    <div className="text-4xl font-black text-slate-800 absolute top-0 -right-4 -z-10 select-none opacity-50">{item.step}</div>
                    <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                    <p className="text-slate-400 text-sm max-w-xs">{item.desc}</p>
                 </div>
               ))}
            </div>
         </div>
      </section>

      {/* --- Admin Dashboard Preview --- */}
      <section id="dashboard" className="py-24 bg-[#0D1117] border-y border-slate-800">
        <div className="max-w-6xl mx-auto px-6">
           <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-white">Command Center: Total Situational Awareness</h2>
              <p className="text-slate-400 mt-4">Stop guessing. Start knowing. See your entire city's pulse in real-time.</p>
           </div>

           <div className="bg-[#0A0F1A] border border-slate-700 rounded-xl overflow-hidden shadow-2xl">
              <div className="p-4 border-b border-slate-700 bg-[#161B22] flex justify-between items-center">
                 <div className="flex gap-4 text-sm font-medium text-slate-300">
                    <span className="text-white border-b-2 border-blue-500 pb-4 -mb-4">Overview</span>
                    <span className="opacity-50">Incidents</span>
                    <span className="opacity-50">Resources</span>
                 </div>
                 <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                    <span className="text-xs font-mono text-red-400">LIVE ACTION REQUIRED (3)</span>
                 </div>
              </div>
              
              <div className="p-6 grid md:grid-cols-3 gap-6">
                 {/* Stat Card 1 */}
                 <div className="bg-[#161B22] p-4 rounded border border-slate-800">
                    <div className="text-slate-500 text-xs font-mono mb-2">RESPONSE VELOCITY</div>
                    <div className="text-3xl font-bold text-white">14m</div>
                    <div className="text-emerald-400 text-xs mt-2 flex items-center gap-1"><ArrowUpRight className="w-3 h-3"/> 40% Faster than Avg</div>
                 </div>
                 {/* Stat Card 2 */}
                 <div className="bg-[#161B22] p-4 rounded border border-slate-800">
                    <div className="text-slate-500 text-xs font-mono mb-2">THREATS NEUTRALIZED</div>
                    <div className="text-3xl font-bold text-white">1,204</div>
                    <div className="text-emerald-400 text-xs mt-2 flex items-center gap-1"><ArrowUpRight className="w-3 h-3"/> +12% vs yesterday</div>
                 </div>
                 {/* Stat Card 3 */}
                 <div className="bg-[#161B22] p-4 rounded border border-slate-800">
                    <div className="text-slate-500 text-xs font-mono mb-2">ACTIVE HOTSPOTS</div>
                    <div className="text-3xl font-bold text-amber-500">5</div>
                    <div className="text-slate-500 text-xs mt-2">Requires verification</div>
                 </div>

                 {/* Mock Chart Area */}
                 <div className="md:col-span-2 bg-[#161B22] p-4 rounded border border-slate-800 h-48 flex items-end justify-between gap-2 px-8 pb-4 relative">
                    <div className="absolute top-4 left-4 text-xs font-mono text-slate-500">INCIDENT TRENDS</div>
                    {[40, 65, 30, 80, 55, 90, 45, 60, 75, 50].map((h, i) => (
                       <div key={i} style={{height: `${h}%`}} className="w-full bg-blue-900/40 border-t border-blue-500 hover:bg-blue-500/20 transition-colors rounded-t-sm relative group">
                          <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">{h}</div>
                       </div>
                    ))}
                 </div>

                 {/* Recent List */}
                 <div className="bg-[#161B22] p-4 rounded border border-slate-800 h-48 overflow-hidden">
                    <div className="text-slate-500 text-xs font-mono mb-4">RECENT ALERTS</div>
                    <div className="space-y-3">
                       {[
                          { loc: "Bole Rd", type: "Accident", time: "2m ago", color: "text-red-400" },
                          { loc: "4 Kilo", type: "Protest", time: "12m ago", color: "text-amber-400" },
                          { loc: "Meskel Sq", type: "Traffic", time: "25m ago", color: "text-blue-400" },
                       ].map((alert, i) => (
                          <div key={i} className="flex justify-between items-center text-sm border-b border-slate-800 pb-2">
                             <div>
                                <span className={`block font-bold ${alert.color}`}>{alert.type}</span>
                                <span className="text-slate-400 text-xs">{alert.loc}</span>
                             </div>
                             <span className="text-slate-600 text-xs font-mono">{alert.time}</span>
                          </div>
                       ))}
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* --- Built For Ethiopia Context --- */}
      <section className="py-20 bg-[#0A0F1A]">
         <div className="max-w-7xl mx-auto px-6">
            <div className="grid md:grid-cols-2 gap-12 items-center">
               <div className="space-y-6">
                  <h2 className="text-3xl font-bold text-white">The "Offline-Proof" Guarantee</h2>
                  <p className="text-slate-400">
                     While other systems crash when the network drops, AEGIS gets stronger. Built for the reality of Addis Ababa, not Silicon Valley.
                  </p>
                  
                  <ul className="space-y-4">
                     <li className="flex items-start gap-4">
                        <WifiOff className="w-6 h-6 text-slate-500 mt-1" />
                        <div>
                           <h4 className="text-white font-semibold">Zero-Data Mode</h4>
                           <p className="text-sm text-slate-500">Maps cache locally and reports queue automatically. We never lose a signal.</p>
                        </div>
                     </li>
                     <li className="flex items-start gap-4">
                        <Smartphone className="w-6 h-6 text-slate-500 mt-1" />
                        <div>
                           <h4 className="text-white font-semibold">2G/3G Optimized</h4>
                           <p className="text-sm text-slate-500">Engineered to load instantly on older Android devices and congested networks.</p>
                        </div>
                     </li>
                     <li className="flex items-start gap-4">
                        <Globe className="w-6 h-6 text-slate-500 mt-1" />
                        <div>
                           <h4 className="text-white font-semibold">Hyper-Local Intelligence</h4>
                           <p className="text-sm text-slate-500">Context-aware categories for rainy season flooding, road blockages, and local infrastructure.</p>
                        </div>
                     </li>
                  </ul>
               </div>
               
               {/* Visual Placeholder for "Local" */}
               <div className="bg-[#161B22] p-8 rounded-xl border border-slate-800 flex items-center justify-center min-h-[300px] text-center">
                  <div>
                    <div className="text-5xl font-black text-slate-800 mb-2">AEGIS</div>
                    <div className="text-lg text-slate-500 font-mono">ADDIS ABABA • DIRE DAWA • ADAMA</div>
                    <div className="mt-8 flex justify-center gap-4">
                        <div className="px-4 py-1 bg-slate-800 rounded text-xs text-slate-400">Amharic</div>
                        <div className="px-4 py-1 bg-slate-800 rounded text-xs text-slate-400">English</div>
                        <div className="px-4 py-1 bg-slate-800 rounded text-xs text-slate-400">Oromiffa</div>
                    </div>
                  </div>
               </div>
            </div>
         </div>
      </section>

      {/* --- Resources Section --- */}
      <section id="resources" className="py-20 bg-[#0D1117] border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-2">
            <Lock className="w-6 h-6 text-blue-500" />
            Strategic Emergency Uplink
          </h2>
          <div className="grid md:grid-cols-4 gap-4">
            {['Federal Police', 'Ambulance Service', 'Fire Brigade', 'Traffic Police'].map((r, i) => (
              <a key={i} href="#" className="flex items-center justify-between p-4 bg-[#161B22] border border-slate-800 hover:border-blue-500/50 rounded transition-colors group">
                <span className="text-slate-300 font-medium group-hover:text-white">{r}</span>
                <Phone className="w-4 h-4 text-slate-600 group-hover:text-blue-400" />
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* --- CTA Section --- */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0F1A] to-blue-900/20"></div>
        <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">The City is Speaking. Are You Listening?</h2>
          <p className="text-xl text-slate-400 mb-10">Join the elite network of citizens and responders who are shaping the future of urban safety. Don't get left in the dark.</p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button 
              onClick={() => setView('dashboard')}
              className="px-10 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-[0_0_30px_rgba(59,130,246,0.4)] transition-all"
            >
              LAUNCH COMMAND INTERFACE
            </button>
            <button className="px-10 py-4 bg-[#161B22] hover:bg-[#1C2128] text-white border border-slate-700 font-medium rounded transition-all">
              SECURE DEMO ACCESS
            </button>
          </div>
        </div>
      </section>

      {/* --- Footer --- */}
      <footer className="bg-[#050910] border-t border-slate-800 py-12 text-sm text-slate-500">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 text-slate-200 font-bold mb-4">
               <Shield className="w-5 h-5 text-blue-500" />
               AEGIS-AI
            </div>
            <p>The Operating System for Safer Cities.</p>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">Platform</h4>
            <ul className="space-y-2">
               <li><a href="#" className="hover:text-blue-400">Live Map</a></li>
               <li><a href="#" className="hover:text-blue-400">Dashboard</a></li>
               <li><a href="#" className="hover:text-blue-400">API Access</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">Governance</h4>
            <ul className="space-y-2">
               <li><a href="#" className="hover:text-blue-400">Privacy Policy</a></li>
               <li><a href="#" className="hover:text-blue-400">Data Standards</a></li>
               <li><a href="#" className="hover:text-blue-400">Verify Organization</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">Contact</h4>
            <p>Addis Ababa, Ethiopia</p>
            <p>support@aegis-ai.et</p>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-6 mt-12 pt-8 border-t border-slate-900 text-center text-xs font-mono">
           © 2025 AEGIS-AI SYSTEMS. SECURED CONNECTION.
        </div>
      </footer>
    </div>
    </WebSocketProvider>
  );
};

export default AegisLanding;
