import React, { useState, useEffect, useCallback } from 'react';
import MapaTerritorial from '../components/MapaTerritorial';
import TabelaMunicipios from '../components/TabelaMunicipios';
import FiltroPeriodo from '../components/FiltroPeriodo';
import fetchData from '../services/api';
import LoadingBlock from '../components/LoadingBlock';
import CardError from '../components/CardError';

const DashboardTerritorial = () => {
    const [dados, setDados] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadData = useCallback(async (inicio, fim) => {
        setLoading(true);
        setError(null);
        const response = await fetchData('/api/indicadores/territorial/atendimentos_por_municipio', inicio, fim);
        if (response.error) {
            setError(response.error);
            setLoading(false);
            return;
        }
        setDados(response.data);
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
            <h1 className="page__title">Dashboard Territorial</h1>
            <div className="stack">
                <FiltroPeriodo onFilterChange={handleFilterChange} />
                
                {loading ? (
                    <LoadingBlock size="xl" />
                ) : error ? (
                    <CardError message={`Erro ao carregar dados: ${error}`} />
                ) : (
                    <div className="grid-duo">
                        <div className="section">
                            <MapaTerritorial dados={dados} />
                        </div>
                        <div className="section">
                            <TabelaMunicipios dados={dados} />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DashboardTerritorial;
