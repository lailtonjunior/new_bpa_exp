import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import DashboardExecutivo from './pages/DashboardExecutivo';
import DashboardAssistencial from './pages/DashboardAssistencial';
import DashboardProdutividade from './pages/DashboardProdutividade';
import DashboardTerritorial from './pages/DashboardTerritorial';

function App() {
  return (
    <Router>
      <div className="app-shell">
        <nav className="top-nav">
          <Link to="/" className="top-nav__link">Executivo</Link>
          <Link to="/assistencial" className="top-nav__link">Assistencial</Link>
          <Link to="/produtividade" className="top-nav__link">Produtividade</Link>
          <Link to="/territorial" className="top-nav__link">Territorial</Link>
        </nav>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<DashboardExecutivo />} />
            <Route path="/assistencial" element={<DashboardAssistencial />} />
            <Route path="/produtividade" element={<DashboardProdutividade />} />
            <Route path="/territorial" element={<DashboardTerritorial />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
