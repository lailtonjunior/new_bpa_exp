import React, { useState } from 'react';

const filtroContainerStyle = {
    display: 'flex',
    gap: '15px',
    alignItems: 'center',
    padding: '10px',
    backgroundColor: '#f1f3f5',
    borderRadius: '8px',
    marginBottom: '20px',
};

const inputGroupStyle = {
    display: 'flex',
    flexDirection: 'column',
};

const labelStyle = {
    fontSize: '12px',
    fontWeight: 'bold',
    marginBottom: '4px',
    color: '#495057',
};

const inputStyle = {
    padding: '8px',
    border: '1px solid #ced4da',
    borderRadius: '4px',
};

const buttonStyle = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#007bff',
    color: 'white',
    cursor: 'pointer',
    fontWeight: 'bold',
};

const errorStyle = { color: 'red', fontSize: '12px', marginLeft: '8px' };

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
        <div>
            <div style={filtroContainerStyle}>
                <div style={inputGroupStyle}>
                    <label style={labelStyle} htmlFor="data-inicio">Data de Inicio</label>
                    <input 
                        id="data-inicio"
                        type="date" 
                        value={dataInicio} 
                        onChange={e => setDataInicio(e.target.value)}
                        style={inputStyle}
                    />
                </div>
                <div style={inputGroupStyle}>
                    <label style={labelStyle} htmlFor="data-fim">Data de Fim</label>
                    <input 
                        id="data-fim"
                        type="date" 
                        value={dataFim} 
                        onChange={e => setDataFim(e.target.value)}
                        style={inputStyle}
                    />
                </div>
                <button onClick={handleFilterClick} style={buttonStyle}>Aplicar Filtro</button>
            </div>
            {error && <span style={errorStyle}>{error}</span>}
        </div>
    );
};

export default FiltroPeriodo;
