import React, { useState } from 'react';
import { X, AlertTriangle, Camera, MapPin, Send } from 'lucide-react';

const ReportModal = ({ isOpen, onClose, onSubmit, token }) => {
  if (!isOpen) return null;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    type: 'accident',
    description: '',
    location: '',
    severity: 'medium'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Prepare payload for Backend API
      // Note: In a real app, we would get actual GPS coordinates here.
      // For MVP Sprint 2, we are sending mock coordinates for Addis Ababa.
      const payload = {
        title: formData.location, // Using location text as title for now
        description: formData.description,
        incident_type: formData.type,
        severity: formData.severity,
        latitude: 9.0300 + (Math.random() * 0.01), // Mock variation
        longitude: 38.7400 + (Math.random() * 0.01) // Mock variation
      };

      const headers = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('http://localhost:8000/incidents/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to submit report');
      }

      const data = await response.json();
      console.log("Report saved to DB:", data);
      
      onSubmit(formData); // Keep existing parent callback for UI updates if any
      onClose();
    } catch (err) {
      console.error("Submission error:", err);
      setError("Failed to connect to Command Center. Try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-[#0D1117] border border-slate-700 w-full max-w-md rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="bg-[#161B22] p-4 border-b border-slate-700 flex justify-between items-center">
          <div className="flex items-center gap-2 text-red-400 font-bold">
            <AlertTriangle className="w-5 h-5" />
            <span>Report Incident</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          {error && (
            <div className="bg-red-900/20 border border-red-500/50 text-red-400 text-xs p-3 rounded">
              {error}
            </div>
          )}

          {/* Incident Type */}
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1 uppercase">Incident Type</label>
            <select 
              className="w-full bg-[#0A0F1A] border border-slate-700 rounded p-2 text-white focus:border-blue-500 focus:outline-none transition-colors"
              value={formData.type}
              onChange={(e) => setFormData({...formData, type: e.target.value})}
            >
              <option value="accident">Traffic Accident</option>
              <option value="fire">Fire Outbreak</option>
              <option value="flood">Flash Flood</option>
              <option value="crime">Crime / Violence</option>
              <option value="infrastructure">Infrastructure Failure</option>
            </select>
          </div>

          {/* Location */}
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1 uppercase">Location</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
              <input 
                type="text" 
                placeholder="e.g. Bole Road, near Friendship Park"
                className="w-full bg-[#0A0F1A] border border-slate-700 rounded p-2 pl-9 text-white focus:border-blue-500 focus:outline-none transition-colors"
                value={formData.location}
                onChange={(e) => setFormData({...formData, location: e.target.value})}
                required
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1 uppercase">Description</label>
            <textarea 
              rows="3"
              placeholder="Describe the situation..."
              className="w-full bg-[#0A0F1A] border border-slate-700 rounded p-2 text-white focus:border-blue-500 focus:outline-none transition-colors resize-none"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            ></textarea>
          </div>

          {/* Photo Upload (Mock) */}
          <div className="border-2 border-dashed border-slate-700 rounded-lg p-4 flex flex-col items-center justify-center text-slate-500 hover:border-blue-500/50 hover:bg-blue-500/5 transition-all cursor-pointer">
            <Camera className="w-6 h-6 mb-2" />
            <span className="text-xs">Tap to upload photo evidence</span>
          </div>

          {/* Submit Button */}
          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full bg-red-600 hover:bg-red-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-bold py-3 rounded flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(220,38,38,0.4)]"
          >
            {isLoading ? (
              <span className="animate-pulse">TRANSMITTING...</span>
            ) : (
              <>
                <Send className="w-4 h-4" />
                SUBMIT REPORT
              </>
            )}
          </button>

        </form>
      </div>
    </div>
  );
};

export default ReportModal;
