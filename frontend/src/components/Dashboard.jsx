import React, { useState, useEffect, useCallback } from 'react';
import { Shield, Activity, Users, Radio, LogOut, Bell, BarChart, HelpCircle, X } from 'lucide-react';
import MapComponent from './MapComponent';
import { useWebSocket } from '../contexts/WebSocketContext';

const BootSequence = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const steps = [
    "INITIALIZING AEGIS KERNEL...",
    "CONNECTING TO NATIONAL GRID...",
    "LOADING GEOSPATIAL ASSETS...",
    "ESTABLISHING SECURE UPLINK...",
    "SYSTEM READY."
  ];

  useEffect(() => {
    if (step < steps.length) {
      const timer = setTimeout(() => setStep(s => s + 1), 600);
      return () => clearTimeout(timer);
    } else {
      const timer = setTimeout(onComplete, 500);
      return () => clearTimeout(timer);
    }
  }, [step]);

  return (
    <div className="fixed inset-0 bg-black z-[5000] flex items-center justify-center font-mono text-green-500">
      <div className="w-96">
        <div className="mb-4 text-xs text-slate-500 border-b border-slate-800 pb-2">AEGIS-AI v1.0.0 BOOTLOADER</div>
        {steps.map((s, i) => (
          <div key={i} className={`mb-1 ${i > step ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}>
            <span className="mr-2">{i === step ? '>' : (i < step ? '✓' : ' ')}</span>
            {s}
          </div>
        ))}
        <div className="mt-4 h-1 bg-slate-800 rounded overflow-hidden">
          <div 
            className="h-full bg-green-500 transition-all duration-300 ease-linear"
            style={{ width: `${Math.min((step / (steps.length - 1)) * 100, 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

const HelpModal = ({ onClose }) => (
  <div className="fixed inset-0 z-[3000] bg-black/80 flex items-center justify-center p-4">
    <div className="bg-[#161B22] border border-slate-700 rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto text-slate-300">
      <div className="p-4 border-b border-slate-700 flex justify-between items-center sticky top-0 bg-[#161B22]">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-blue-500" />
          System Manual
        </h2>
        <button onClick={onClose} className="text-slate-500 hover:text-white"><X className="w-5 h-5" /></button>
      </div>
      <div className="p-6 space-y-6">
        <section>
          <h3 className="text-white font-bold mb-2">1. Live Operations Map</h3>
          <p className="text-sm">The main view shows real-time incidents. <span className="text-red-400">Red markers</span> indicate critical threats. Click any marker to view details, dispatch units, or resolve the incident.</p>
        </section>
        <section>
          <h3 className="text-white font-bold mb-2">2. Dispatching Units</h3>
          <p className="text-sm">Admins can dispatch units to an incident by clicking "DISPATCH" on an incident popup. Only <span className="text-green-400">IDLE</span> units are available for assignment.</p>
        </section>
        <section>
          <h3 className="text-white font-bold mb-2">3. Broadcast Alerts</h3>
          <p className="text-sm">Use the "Broadcast Alert" tab to send a city-wide notification. This will appear on all connected citizen devices immediately.</p>
        </section>
        <section>
          <h3 className="text-white font-bold mb-2">4. Offline Mode</h3>
          <p className="text-sm">If the connection is lost, a red "OFFLINE MODE" badge will appear. You can still view cached data, but updates will be paused until connection is restored.</p>
        </section>
      </div>
    </div>
  </div>
);

const UnitList = ({ token }) => {
  const [units, setUnits] = useState([]);
  const { lastMessage } = useWebSocket();

  const fetchUnits = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/units/', {
          headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUnits(data);
      }
    } catch (error) {
      console.error("Failed to fetch units:", error);
    }
  }, [token]);

  useEffect(() => {
    fetchUnits();
  }, [fetchUnits]);

  useEffect(() => {
    if (lastMessage === "refresh_units") {
        console.log("Real-time update: Refreshing Units");
        fetchUnits();
    }
  }, [lastMessage, fetchUnits]);

  if (units.length === 0) {
    return <div className="text-xs text-slate-500 text-center p-4">No active units found.</div>;
  }

  return (
    <div className="space-y-3">
      {units.map(unit => (
        <div key={unit.id} className="bg-[#0A0F1A] p-3 rounded border border-slate-800">
            <div className="flex justify-between items-center mb-2">
                <span className={`text-sm font-bold ${unit.unit_type === 'medical' ? 'text-red-400' : unit.unit_type === 'fire' ? 'text-orange-400' : 'text-blue-400'}`}>
                    {unit.callsign}
                </span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    unit.status === 'idle' ? 'bg-green-900/50 text-green-400' : 
                    unit.status === 'busy' ? 'bg-red-900/50 text-red-400' : 
                    'bg-slate-800 text-slate-400'
                }`}>
                    {unit.status.toUpperCase()}
                </span>
            </div>
            <div className="text-xs text-slate-400">Type: {unit.unit_type.toUpperCase()}</div>
            <div className="text-xs text-slate-500 mt-1">Last active: {new Date(unit.last_updated).toLocaleTimeString()}</div>
        </div>
      ))}
    </div>
  );
};

const Dashboard = ({ onLogout, token, username, initialRole = null }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [userRole, setUserRole] = useState(initialRole);
  const [showBootSequence, setShowBootSequence] = useState(true);
  const [showHelp, setShowHelp] = useState(false);
  const [stats, setStats] = useState(() => {
      const saved = localStorage.getItem('dashboard_stats');
      return saved ? JSON.parse(saved) : { total: 0, critical: 0, active: 0 };
  });
  const [analyticsData, setAnalyticsData] = useState(() => {
      const saved = localStorage.getItem('dashboard_analytics');
      return saved ? JSON.parse(saved) : null;
  });
  const [alerts, setAlerts] = useState(() => {
      const saved = localStorage.getItem('dashboard_alerts');
      return saved ? JSON.parse(saved) : [];
  });
  const [showAlertsDropdown, setShowAlertsDropdown] = useState(false);
  
  const { lastMessage, isConnected } = useWebSocket();

  // Fetch stats and alerts
  const fetchData = useCallback(async () => {
      try {
        // Fetch User Role if token exists
        if (token && !userRole) {
            const userRes = await fetch('http://localhost:8000/users/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (userRes.ok) {
                const userData = await userRes.json();
                setUserRole(userData.role);
            }
        }

        // Fetch Incidents
        const incResponse = await fetch('http://localhost:8000/incidents/');
        if (incResponse.status === 401 && token) {
            onLogout();
            return;
        }
        if (incResponse.ok) {
          const data = await incResponse.json();
          const newStats = {
            total: data.length,
            critical: data.filter(i => i.severity === 'critical').length,
            active: data.filter(i => i.status !== 'resolved').length
          };
          setStats(newStats);
          localStorage.setItem('dashboard_stats', JSON.stringify(newStats));
        }

        // Fetch Alerts
        const alertResponse = await fetch('http://localhost:8000/alerts/');
        if (alertResponse.ok) {
          const alertData = await alertResponse.json();
          setAlerts(alertData);
          localStorage.setItem('dashboard_alerts', JSON.stringify(alertData));
        }

        // Fetch Analytics
        const analyticsResponse = await fetch('http://localhost:8000/analytics/stats');
        if (analyticsResponse.ok) {
            const data = await analyticsResponse.json();
            setAnalyticsData(data);
            localStorage.setItem('dashboard_analytics', JSON.stringify(data));
        }

      } catch (e) {
        console.error(e);
      }
    }, [token, userRole, onLogout]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
      if (lastMessage === "refresh_incidents" || lastMessage === "refresh_alerts") {
          console.log("Real-time update: Refreshing Dashboard Data");
          fetchData();
      }
  }, [lastMessage, fetchData]);

  if (showBootSequence) {
    return <BootSequence onComplete={() => setShowBootSequence(false)} />;
  }

  return (
    <div className="flex h-screen bg-[#0D1117] text-white overflow-hidden">
      {showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
      
      {/* Sidebar */}
      <div className="w-64 border-r border-slate-800 flex flex-col bg-[#0A0F1A]">
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="font-bold text-lg tracking-wider">AEGIS-AI</h1>
            <div className="text-[10px] text-slate-500 font-mono">COMMAND CENTER</div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <button 
            onClick={() => setActiveTab('overview')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded transition-colors ${activeTab === 'overview' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-slate-400 hover:bg-slate-800'}`}
          >
            <Activity className="w-5 h-5" />
            <span className="font-medium">Live Operations</span>
          </button>
          
          {token && (
            <>
              <button 
                onClick={() => setActiveTab('units')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded transition-colors ${activeTab === 'units' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-slate-400 hover:bg-slate-800'}`}
              >
                <Users className="w-5 h-5" />
                <span className="font-medium">Units & Resources</span>
              </button>

              <button 
                onClick={() => setActiveTab('analytics')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded transition-colors ${activeTab === 'analytics' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-slate-400 hover:bg-slate-800'}`}
              >
                <BarChart className="w-5 h-5" />
                <span className="font-medium">Analytics</span>
              </button>

              <button 
                onClick={() => setActiveTab('broadcast')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded transition-colors ${activeTab === 'broadcast' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-slate-400 hover:bg-slate-800'}`}
              >
                <Radio className="w-5 h-5" />
                <span className="font-medium">Broadcast Alert</span>
              </button>
            </>
          )}

          <button 
            onClick={() => setShowHelp(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded transition-colors text-slate-400 hover:bg-slate-800 mt-auto"
          >
            <HelpCircle className="w-5 h-5" />
            <span className="font-medium">System Manual</span>
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-800/50 rounded p-3 mb-4">
            <div className="text-xs text-slate-500 mb-1">SYSTEM STATUS</div>
            <div className="flex items-center gap-2 text-emerald-400 text-sm font-mono">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
              OPERATIONAL
            </div>
          </div>
          {token ? (
            <button onClick={onLogout} className="flex items-center gap-2 text-slate-500 hover:text-white text-sm transition-colors">
              <LogOut className="w-4 h-4" />
              Disconnect
            </button>
          ) : (
            <button onClick={onLogout} className="flex items-center gap-2 text-blue-400 hover:text-white text-sm transition-colors font-bold">
              <LogOut className="w-4 h-4 rotate-180" />
              Login to Console
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative">
        
        {/* Top Bar */}
        <div className="h-16 border-b border-slate-800 bg-[#0A0F1A] flex items-center justify-between px-6">
          <div className="flex gap-6">
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-500 font-mono">ACTIVE INCIDENTS</span>
              <span className="text-xl font-bold text-white">{stats.active}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-500 font-mono">CRITICAL THREATS</span>
              <span className="text-xl font-bold text-red-500">{stats.critical}</span>
            </div>
          </div>

          <div className="flex items-center gap-4 relative">
            <button 
              className="p-2 text-slate-400 hover:text-white relative"
              onClick={() => setShowAlertsDropdown(!showAlertsDropdown)}
            >
              <Bell className="w-5 h-5" />
              {alerts.length > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] flex items-center justify-center text-white font-bold">
                  {alerts.length}
                </span>
              )}
            </button>

            {/* Alerts Dropdown */}
            {showAlertsDropdown && (
              <div className="absolute top-14 right-40 w-80 bg-[#161B22] border border-slate-700 rounded shadow-2xl z-[2000] max-h-96 overflow-y-auto">
                <div className="p-3 border-b border-slate-700 font-bold text-sm">System Alerts</div>
                {alerts.length === 0 ? (
                  <div className="p-4 text-center text-slate-500 text-xs">No active alerts</div>
                ) : (
                  alerts.map(alert => (
                    <div key={alert.id} className="p-3 border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                      <div className="flex justify-between items-start mb-1">
                        <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${alert.severity === 'critical' ? 'bg-red-900/50 text-red-400' : 'bg-amber-900/50 text-amber-400'}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="text-[10px] text-slate-500">{new Date(alert.created_at).toLocaleTimeString()}</span>
                      </div>
                      <div className="text-sm font-bold text-slate-200">{alert.title}</div>
                      <div className="text-xs text-slate-400 mt-1">{alert.message}</div>
                    </div>
                  ))
                )}
              </div>
            )}

            <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center font-bold text-xs">
                {username ? username.substring(0, 2).toUpperCase() : 'CM'}
              </div>
              <div className="text-sm">
                <div className="font-bold">{username || 'Commander'}</div>
                <div className="text-xs text-slate-500">Addis Ababa HQ</div>
              </div>
            </div>
          </div>
        </div>

        {/* Map View */}
        <div className="flex-1 relative">
          <MapComponent adminMode={userRole && userRole !== 'citizen'} token={token} />
          
          {/* Overlay for "Broadcast" tab (Mock) */}
          {activeTab === 'broadcast' && (
            <div className="absolute top-4 left-4 z-[1000] bg-[#161B22] border border-slate-700 p-4 rounded shadow-xl w-80">
              <h3 className="font-bold text-white mb-2">Emergency Broadcast</h3>
              <p className="text-xs text-slate-400 mb-4">Send alert to all citizens in active zones.</p>
              <form onSubmit={async (e) => {
                e.preventDefault();
                const msg = e.target.message.value;
                if(!msg) return;
                try {
                    const res = await fetch('http://localhost:8000/alerts/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                        body: JSON.stringify({ title: "COMMAND BROADCAST", message: msg, severity: "critical", incident_id: 1 }) // Mock incident ID for now
                    });
                    if(res.ok) { alert("Broadcast Sent!"); e.target.reset(); }
                    else { alert("Failed to send broadcast"); }
                } catch(err) { console.error(err); }
              }}>
                <textarea name="message" className="w-full bg-[#0A0F1A] border border-slate-700 rounded p-2 text-sm text-white mb-3" rows="3" placeholder="Message..."></textarea>
                <button type="submit" className="w-full bg-red-600 hover:bg-red-500 text-white font-bold py-2 rounded text-sm">SEND ALERT</button>
              </form>
            </div>
          )}

          {/* Overlay for "Units" tab (Mock) */}
          {activeTab === 'units' && (
            <div className="absolute top-4 left-4 z-[1000] bg-[#161B22] border border-slate-700 p-4 rounded shadow-xl w-80 max-h-[80vh] overflow-y-auto">
              <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-400" />
                Active Units
              </h3>
              
              <UnitList token={token} />
            </div>
          )}

          {/* Analytics View Overlay */}
          {activeTab === 'analytics' && analyticsData && (
            <div className="absolute inset-0 z-[1000] bg-[#0D1117] p-8 overflow-y-auto">
                <h2 className="text-2xl font-bold mb-6">Operational Analytics</h2>
                
                <div className="grid grid-cols-3 gap-6 mb-8">
                    <div className="bg-[#161B22] p-6 rounded border border-slate-800">
                        <div className="text-slate-400 text-sm mb-2">Total Incidents</div>
                        <div className="text-4xl font-bold text-white">{analyticsData.total_incidents}</div>
                    </div>
                    <div className="bg-[#161B22] p-6 rounded border border-slate-800">
                        <div className="text-slate-400 text-sm mb-2">Critical Incidents</div>
                        <div className="text-4xl font-bold text-red-500">{analyticsData.by_severity.critical || 0}</div>
                    </div>
                    <div className="bg-[#161B22] p-6 rounded border border-slate-800">
                        <div className="text-slate-400 text-sm mb-2">Resolved Incidents</div>
                        <div className="text-4xl font-bold text-emerald-500">{analyticsData.by_status.resolved || 0}</div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div className="bg-[#161B22] p-6 rounded border border-slate-800">
                        <h3 className="font-bold mb-4">Incidents by Severity</h3>
                        <div className="space-y-3">
                            {Object.entries(analyticsData.by_severity).map(([severity, count]) => (
                                <div key={severity}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="capitalize text-slate-300">{severity}</span>
                                        <span className="font-mono text-slate-400">{count}</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div 
                                            className={`h-full ${severity === 'critical' ? 'bg-red-500' : severity === 'high' ? 'bg-orange-500' : 'bg-blue-500'}`} 
                                            style={{ width: `${(count / analyticsData.total_incidents) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="bg-[#161B22] p-6 rounded border border-slate-800">
                        <h3 className="font-bold mb-4">Incidents by Status</h3>
                        <div className="space-y-3">
                            {Object.entries(analyticsData.by_status).map(([status, count]) => (
                                <div key={status}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="capitalize text-slate-300">{status}</span>
                                        <span className="font-mono text-slate-400">{count}</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div 
                                            className={`h-full ${status === 'resolved' ? 'bg-emerald-500' : status === 'dispatched' ? 'bg-blue-500' : 'bg-slate-500'}`} 
                                            style={{ width: `${(count / analyticsData.total_incidents) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
