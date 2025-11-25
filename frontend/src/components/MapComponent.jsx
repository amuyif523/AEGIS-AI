import React, { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useWebSocket } from '../contexts/WebSocketContext';

// Fix for default marker icons in React-Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const CommentSection = ({ incidentId, token }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");

  const fetchComments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/incidents/${incidentId}/comments/`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setComments(data);
      }
    } catch (error) {
      console.error("Failed to fetch comments:", error);
    }
  };

  const submitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/incidents/${incidentId}/comments/`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content: newComment })
      });
      if (response.ok) {
        setNewComment("");
        fetchComments();
      }
    } catch (error) {
      console.error("Failed to post comment:", error);
    }
  };

  useEffect(() => {
    if (token) {
        fetchComments();
    }
  }, [incidentId, token]);

  return (
    <div className="mt-3 border-t pt-2">
      <h4 className="text-xs font-bold mb-2">Agency Chat</h4>
      <div className="max-h-24 overflow-y-auto mb-2 space-y-1">
        {comments.map((c) => (
          <div key={c.id} className="bg-slate-100 p-1 rounded text-[10px]">
            <span className="font-bold text-slate-700">{c.username || 'Dispatcher'}:</span> {c.content}
          </div>
        ))}
        {comments.length === 0 && <div className="text-[10px] text-slate-400 italic">No comments yet.</div>}
      </div>
      <form onSubmit={submitComment} className="flex gap-1">
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add update..."
          className="flex-1 border rounded px-1 text-[10px]"
        />
        <button type="submit" className="bg-slate-800 text-white text-[10px] px-2 rounded">Send</button>
      </form>
    </div>
  );
};

const MapComponent = ({ adminMode = false, token = null }) => {
  const position = [9.005401, 38.763611]; // Addis Ababa
  const [incidents, setIncidents] = useState(() => {
      const saved = localStorage.getItem('incidents');
      return saved ? JSON.parse(saved) : [];
  });
  const [units, setUnits] = useState([]);
  const [dispatchModalOpen, setDispatchModalOpen] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [isOffline, setIsOffline] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false); // Mock Heatmap Toggle
  const { lastMessage } = useWebSocket();

  // Fetch incidents from Backend API
  const fetchIncidents = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/incidents/');
      if (response.ok) {
        const data = await response.json();
        setIncidents(data);
        localStorage.setItem('incidents', JSON.stringify(data));
        setIsOffline(false);
      }
    } catch (error) {
      console.error("Failed to fetch incidents:", error);
      setIsOffline(true);
    }
  }, []);

  // Fetch units for dispatch
  const fetchUnits = async () => {
    if (!token) return;
    try {
        const response = await fetch('http://localhost:8000/units/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();
            setUnits(data.filter(u => u.status === 'idle')); // Only show idle units
        }
    } catch (error) {
        console.error("Failed to fetch units:", error);
    }
  };

  const updateStatus = async (id, newStatus, unitId = null) => {
    try {
      let url = `http://localhost:8000/incidents/${id}?status=${newStatus}`;
      if (unitId) {
          url += `&unit_id=${unitId}`;
      }

      const response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        fetchIncidents(); // Refresh data
        setDispatchModalOpen(false);
      } else if (response.status === 403) {
        alert("Unauthorized: Only Command/Admin can dispatch or resolve incidents.");
      } else {
        console.error("Failed to update status:", response.statusText);
      }
    } catch (error) {
      console.error("Failed to update status:", error);
    }
  };

  const handleDispatchClick = (incidentId) => {
      setSelectedIncidentId(incidentId);
      fetchUnits();
      setDispatchModalOpen(true);
  };
  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  useEffect(() => {
    if (lastMessage === "refresh_incidents") {
        fetchIncidents();
    }
  }, [lastMessage, fetchIncidents]);

  return (
    <div className="h-full w-full relative z-0">
      {/* Offline Indicator */}
      {isOffline && (
        <div className="absolute top-4 right-4 z-[1000] bg-red-600 text-white px-3 py-1 rounded shadow-lg text-xs font-bold flex items-center gap-2 animate-pulse">
          <span className="w-2 h-2 bg-white rounded-full"></span>
          OFFLINE MODE
        </div>
      )}

      {/* Heatmap Toggle (Mock) */}
      <div className="absolute bottom-8 left-4 z-[1000] bg-[#161B22] border border-slate-700 rounded p-2">
          <label className="flex items-center gap-2 text-xs text-white cursor-pointer">
              <input type="checkbox" checked={showHeatmap} onChange={() => setShowHeatmap(!showHeatmap)} />
              <span>Enable Heatmap Overlay</span>
          </label>
      </div>

      {/* Dispatch Modal */}
      {dispatchModalOpen && (
          <div className="absolute inset-0 z-[2000] bg-black/80 flex items-center justify-center p-4">
              <div className="bg-white rounded-lg p-6 w-full max-w-md">
                  <h3 className="text-lg font-bold mb-4 text-slate-900">Select Unit to Dispatch</h3>
                  <div className="space-y-2 max-h-60 overflow-y-auto mb-4">
                      {units.length === 0 ? (
                          <div className="text-slate-500 text-sm">No idle units available nearby.</div>
                      ) : (
                          units.map(unit => (
                              <button 
                                key={unit.id}
                                onClick={() => updateStatus(selectedIncidentId, 'dispatched', unit.id)}
                                className="w-full flex justify-between items-center p-3 border rounded hover:bg-blue-50 transition-colors text-left"
                              >
                                  <div>
                                      <div className="font-bold text-slate-800">{unit.callsign}</div>
                                      <div className="text-xs text-slate-500">{unit.unit_type.toUpperCase()}</div>
                                  </div>
                                  <div className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded font-bold">IDLE</div>
                              </button>
                          ))
                      )}
                  </div>
                  <button 
                    onClick={() => setDispatchModalOpen(false)}
                    className="w-full bg-slate-200 text-slate-700 font-bold py-2 rounded hover:bg-slate-300"
                  >
                      Cancel
                  </button>
              </div>
          </div>
      )}

      <MapContainer 
        center={position} 
        zoom={13} 
        scrollWheelZoom={true} 
        style={{ height: '100%', width: '100%', background: '#0F1520' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {incidents.map((incident) => (
          <React.Fragment key={incident.id}>
            <Marker position={[incident.latitude, incident.longitude]}>
              <Popup>
                <div className="text-slate-900 min-w-[150px]">
                  <strong className="uppercase text-red-600 block mb-1">{incident.severity}: {incident.incident_type}</strong>
                  <div className="text-sm font-bold mb-1">{incident.title}</div>
                  <div className="text-xs text-slate-600">{incident.description}</div>
                  <div className="text-[10px] text-slate-400 mt-2 border-t pt-1 mb-2">
                    Status: <span className="font-bold">{incident.status}</span>
                    {incident.assigned_unit_id && <div className="text-blue-600 mt-1">Unit Assigned (ID: {incident.assigned_unit_id})</div>}
                  </div>
                  
                  {adminMode && (
                    <>
                      <div className="flex gap-1 mt-2">
                        <button 
                          onClick={() => handleDispatchClick(incident.id)}
                          className="flex-1 bg-blue-600 text-white text-[10px] py-1 px-2 rounded hover:bg-blue-500"
                        >
                          DISPATCH
                        </button>
                        <button 
                          onClick={() => updateStatus(incident.id, 'resolved')}
                          className="flex-1 bg-green-600 text-white text-[10px] py-1 px-2 rounded hover:bg-green-500"
                        >
                          RESOLVE
                        </button>
                      </div>
                      <CommentSection incidentId={incident.id} token={token} />
                    </>
                  )}
                </div>
              </Popup>
            </Marker>
            {/* Mock Heatmap Circle */}
            {showHeatmap && (
                <L.Circle 
                    center={[incident.latitude, incident.longitude]} 
                    radius={500}
                    pathOptions={{ 
                        color: incident.severity === 'critical' ? 'red' : 'orange', 
                        fillColor: incident.severity === 'critical' ? 'red' : 'orange', 
                        fillOpacity: 0.2,
                        stroke: false
                    }} 
                />
            )}
          </React.Fragment>
        ))}

      </MapContainer>
    </div>
  );
};

export default MapComponent;
