import React from 'react';

const CardError = ({ title = 'Erro ao carregar', message }) => (
  <div className="card card--error" role="alert">
    <h3 className="card__title">{title}</h3>
    <p className="card__message">{message}</p>
  </div>
);

export default CardError;
