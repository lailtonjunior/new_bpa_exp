import React, { useState } from 'react';

const FiltroPeriodo = ({ onFilterChange }) => {
  const getInitialDates = () => {
    const hoje = new Date();
    const primeiroDiaMesAtual = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
    const ultimoDiaMesAnterior = new Date(primeiroDiaMesAtual - 1);
    const primeiroDiaMesAnterior = new Date(ultimoDiaMesAnterior.getFullYear(), ultimoDiaMesAnterior.getMonth(), 1);
    return {
      inicio: primeiroDiaMesAnterior.toISOString().split('T')[0],
      fim: ultimoDiaMesAnterior.toISOString().split('T')[0],
    };
  };

  const [dataInicio, setDataInicio] = useState(getInitialDates().inicio);
  const [dataFim, setDataFim] = useState(getInitialDates().fim);
  const [error, setError] = useState(null);

  const handleFilterClick = () => {
    if (!dataInicio || !dataFim) {
      setError('Preencha as duas datas.');
      return;
    }
    if (new Date(dataInicio) > new Date(dataFim)) {
      setError('Data inicial nao pode ser maior que a final.');
      return;
    }
    setError(null);
    onFilterChange(dataInicio, dataFim);
  };

  return (
    <div className="stack">
      <div className="filter-panel">
        <div className="filter-panel__group">
          <label className="filter-panel__label" htmlFor="data-inicio">Data de Inicio</label>
          <input
            id="data-inicio"
            type="date"
            value={dataInicio}
            onChange={e => setDataInicio(e.target.value)}
            className="filter-panel__input"
          />
        </div>
        <div className="filter-panel__group">
          <label className="filter-panel__label" htmlFor="data-fim">Data de Fim</label>
          <input
            id="data-fim"
            type="date"
            value={dataFim}
            onChange={e => setDataFim(e.target.value)}
            className="filter-panel__input"
          />
        </div>
        <div className="filter-panel__actions">
          <button onClick={handleFilterClick} className="btn btn--primary">Aplicar Filtro</button>
        </div>
      </div>
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};

export default FiltroPeriodo;
