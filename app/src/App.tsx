import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Layouts
// TODO: import DashboardLayout from './layouts/DashboardLayout';

// Auth Pages
import Login from './pages/auth/Login';

// Dashboard Pages
import DashboardOverview from './pages/dashboard/DashboardOverview';
import ContentFactory from './pages/dashboard/ContentFactory';
import MarketplaceHome from './pages/marketplace/MarketplaceHome';
import PluginStore from './pages/plugins/PluginStore';
import FounderAssistant from './pages/assistant/FounderAssistant';
import MobileBottomNav from './components/MobileBottomNav';

function App() {
  const isAuthenticated = true; // TODO: Connect to real auth state

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Protected Dashboard Routes */}
        <Route path="/" element={isAuthenticated ? <div>Layout Setup</div> : <Navigate to="/login" />}>
          <Route index element={<DashboardOverview />} />
          <Route path="content" element={<ContentFactory />} />
          <Route path="brands" element={<div>Brands</div>} />
          <Route path="analytics" element={<div>Analytics</div>} />
          <Route path="trends" element={<div>Trends Intelligence</div>} />
          <Route path="automation" element={<div>Automation</div>} />
          <Route path="marketplace" element={<MarketplaceHome />} />
          <Route path="plugins" element={<PluginStore />} />
          <Route path="assistant" element={<FounderAssistant />} />
          <Route path="profile" element={<div>Profile</div>} />
        </Route>
      </Routes>
      <MobileBottomNav />
    </Router>
  );
}

export default App;
