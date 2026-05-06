import { useState } from 'react'
import './index.css'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-logo">CG</div>
          <div>
            <div className="navbar-title">ConstructGuard AI</div>
            <div className="navbar-subtitle">Autonomous Safety Monitor</div>
          </div>
        </div>
        <div className="navbar-status">
          <span className="status-dot"></span>
          System Active — Mock Mode
        </div>
      </nav>
      <Dashboard />
    </div>
  )
}

export default App
