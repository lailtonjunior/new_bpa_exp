import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import DashboardExecutivo from './pages/DashboardExecutivo';
import DashboardAssistencial from './pages/DashboardAssistencial';
import DashboardProdutividade from './pages/DashboardProdutividade';
import DashboardTerritorial from './pages/DashboardTerritorial';

// Estilos para a navegacao principal
const navStyle = {
    backgroundColor: '#343a40',
    padding: '10px 20px',
    display: 'flex',
    gap: '20px',
};

const linkStyle = {
    color: 'white',
    textDecoration: 'none',
    fontSize: '18px',
    fontWeight: 'bold',
};

function App() {
  return (
    <Router>
      <div>
        <nav style={navStyle}>
          <Link to="/" style={linkStyle}>Executivo</Link>
          <Link to="/assistencial" style={linkStyle}>Assistencial</Link>
          <Link to="/produtividade" style={linkStyle}>Produtividade</Link>
          <Link to="/territorial" style={linkStyle}>Territorial</Link>
        </nav>

        <main>
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
