import React from 'react';

const CardKPI = ({ title, value }) => (
  <div className="card card--kpi">
    <h3 className="card__title">{title}</h3>
    <p className="card__value">{value}</p>
  </div>
);

export default CardKPI;
