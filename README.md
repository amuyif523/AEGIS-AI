# AEGIS-AI: Geospatial Incident Intelligence Platform

## Overview
AEGIS-AI is a next-generation, AI-driven geospatial incident intelligence and rapid response platform designed for the Horn of Africa (specifically Ethiopia). It provides real-time visibility into incidents such as accidents, crimes, floods, and hazards using AI-enhanced geospatial intelligence and crowdsourced verification.

## Features
- **Geospatial Intelligence:** Real-time mapping with layer-based filtering.
- **AI Severity Classification:** Automated severity tagging (Low, Medium, Critical).
- **Crowdsourced Reporting:** Citizen-led incident reporting with verification.
- **Offline-First Architecture:** Optimized for low-bandwidth environments.

## Tech Stack
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide React
- **Backend (Planned):** Python (FastAPI), PostgreSQL (PostGIS)
- **Real-time:** Socket.io

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation
1. Clone the repository (if applicable).
2. Install dependencies:
   ```bash
   npm install
   ```

### Development
To start the development server:
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) to view it in the browser.

### Build
To build for production:
```bash
npm run build
```

## Project Structure
- `src/`: Source code
  - `App.jsx`: Main application component
  - `main.jsx`: Entry point
  - `index.css`: Global styles (Tailwind directives)
- `public/`: Static assets
- `index.html`: HTML entry point
- `vite.config.js`: Vite configuration
- `tailwind.config.js`: Tailwind configuration

## Roadmap
- [x] Project Scaffolding (Vite + React)
- [x] Interactive Map Integration (Leaflet/Mapbox)
- [ ] Backend API Setup (FastAPI)
- [ ] Database Schema Design (PostgreSQL)
- [ ] Real-time WebSocket Integration
