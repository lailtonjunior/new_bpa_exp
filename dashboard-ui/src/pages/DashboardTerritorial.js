import React, { useState, useEffect, useCallback } from 'react';
import MapaTerritorial from '../components/MapaTerritorial';
import TabelaMunicipios from '../components/TabelaMunicipios';
import FiltroPeriodo from '../components/FiltroPeriodo';
import fetchData from '../services/api';

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

    const layoutStyle = {
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: '20px',
        marginTop: '20px',
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Dashboard Territorial</h1>
            <FiltroPeriodo onFilterChange={handleFilterChange} />
            
            {loading ? (
                <p>Carregando dados geograficos para o periodo...</p>
            ) : error ? (
                <p style={{ color: 'red' }}>Erro ao carregar dados: {error}</p>
            ) : (
                <div style={layoutStyle}>
                    <div>
                        <MapaTerritorial dados={dados} />
                    </div>
                    <div>
                        <TabelaMunicipios dados={dados} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default DashboardTerritorial;
