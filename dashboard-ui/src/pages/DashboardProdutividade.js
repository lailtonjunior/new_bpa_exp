import React, { useState, useEffect, useCallback } from 'react';
import TabelaProdutividade from '../components/TabelaProdutividade';
import FiltroPeriodo from '../components/FiltroPeriodo';
import fetchData from '../services/api';

const DashboardProdutividade = () => {
    const [dadosProdutividade, setDadosProdutividade] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadData = useCallback(async (inicio, fim) => {
        setLoading(true);
        setError(null);
        const response = await fetchData('/api/indicadores/produtividade/ranking_profissionais', inicio, fim);
        if (response.error) {
            setError(response.error);
            setLoading(false);
            return;
        }
        setDadosProdutividade(response.data);
        setLoading(false);
    }, []);

    const handleFilterChange = (inicio, fim) => {
        loadData(inicio, fim);
    };

    useEffect(() => {
        loadData();
    }, [loadData]);

    return (
        <div style={{ padding: '20px' }}>
            <h1>Dashboard de Produtividade</h1>
            <FiltroPeriodo onFilterChange={handleFilterChange} />
            <div style={{ marginTop: '20px' }}>
                {loading 
                    ? <p>Carregando ranking de produtividade para o periodo...</p>
                    : error 
                        ? <p style={{ color: 'red' }}>Erro: {error}</p>
                        : <TabelaProdutividade dados={dadosProdutividade} />
                }
            </div>
        </div>
    );
};

export default DashboardProdutividade;
