import React from 'react';
import '../styles/LoadingOverlay.css';

const LoadingOverlay = () => (
  <div className="loading-overlay">
    <div className="loading-content">
      <div className="gradient-spinner"></div>
      <div className="loading-text">Loading...</div>
    </div>
  </div>
);

export default LoadingOverlay;