import React, { useState, useEffect, useCallback } from 'react';
import TabelaProdutividade from '../components/TabelaProdutividade';
import FiltroPeriodo from '../components/FiltroPeriodo';
import fetchData from '../services/api';
import LoadingBlock from '../components/LoadingBlock';
import CardError from '../components/CardError';

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
        <div className="page">
            <h1 className="page__title">Dashboard de Produtividade</h1>
            <div className="stack">
                <FiltroPeriodo onFilterChange={handleFilterChange} />
                <div className="section">
                    {loading 
                        ? <LoadingBlock size="md" />
                        : error 
                            ? <CardError message={`Erro: ${error}`} />
                            : <TabelaProdutividade dados={dadosProdutividade} />
                    }
                </div>
            </div>
        </div>
    );
};

export default DashboardProdutividade;
