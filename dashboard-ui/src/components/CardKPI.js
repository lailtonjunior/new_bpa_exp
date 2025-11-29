import React from 'react';

// Estilos básicos para o card (podemos mover para um arquivo CSS depois)
const cardStyle = {
  backgroundColor: '#f8f9fa',
  borderRadius: '8px',
  padding: '20px',
  margin: '10px',
  textAlign: 'center',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  minWidth: '200px',
};

const titleStyle = {
  fontSize: '16px',
  color: '#6c757d',
  marginBottom: '10px',
};

const valueStyle = {
  fontSize: '32px',
  fontWeight: 'bold',
  color: '#343a40',
};

/**
 * Um componente simples para exibir um título e um valor de KPI.
 * @param {{title: string, value: number | string}} props
 */
const CardKPI = ({ title, value }) => (
  <div style={cardStyle}>
    <h3 style={titleStyle}>{title}</h3>
    <p style={valueStyle}>{value}</p>
  </div>
);

export default CardKPI;
