import React, { useState, useEffect, useCallback } from 'react';
import GraficoBarrasHorizontais from '../components/GraficoBarrasHorizontais';
import GraficoPiramideEtaria from '../components/GraficoPiramideEtaria';
import GraficoDonut from '../components/GraficoDonut';
import FiltroPeriodo from '../components/FiltroPeriodo';
import fetchData from '../services/api';

const DashboardAssistencial = () => {
    const [diagnosticosData, setDiagnosticosData] = useState(null);
    const [perfilEtarioData, setPerfilEtarioData] = useState(null);
    const [prevalenciaData, setPrevalenciaData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadAllData = useCallback(async (inicio, fim) => {
        setLoading(true);
        setError(null);
        
        const [diagnosticos, perfil, prevalencia] = await Promise.all([
            fetchData('/api/indicadores/assistencial/top_diagnosticos', inicio, fim),
            fetchData('/api/indicadores/assistencial/perfil_etario', inicio, fim),
            fetchData('/api/indicadores/assistencial/prevalencia_deficiencias', inicio, fim)
        ]);

        if (diagnosticos.error || perfil.error || prevalencia.error) {
            setError(diagnosticos.error || perfil.error || prevalencia.error);
            setLoading(false);
            return;
        }

        if (diagnosticos.data.length > 0) {
            const reversedData = [...diagnosticos.data].reverse();
            setDiagnosticosData({
                labels: reversedData.map(item => `${item.cid_codigo} - ${item.cid_descricao}`),
                datasets: [{ label: 'Frequencia', data: reversedData.map(item => item.frequencia), backgroundColor: 'rgba(75, 192, 192, 0.5)' }]
            });
        } else { setDiagnosticosData(null); }

        if (perfil.data.length > 0) {
            setPerfilEtarioData({
                labels: perfil.data.map(item => item.faixa_etaria),
                datasets: [
                    { label: 'Masculino', data: perfil.data.map(item => -item.masculino), backgroundColor: 'rgba(54, 162, 235, 0.7)' },
                    { label: 'Feminino', data: perfil.data.map(item => item.feminino), backgroundColor: 'rgba(255, 99, 132, 0.7)' },
                ]
            });
        } else { setPerfilEtarioData(null); }

        if (prevalencia.data.length > 0) {
            setPrevalenciaData({
                labels: prevalencia.data.map(item => item.tipo),
                datasets: [{
                    label: 'Numero de Pacientes',
                    data: prevalencia.data.map(item => item.total_pacientes),
                    backgroundColor: ['rgba(255, 159, 64, 0.7)', 'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(255, 205, 86, 0.7)']
                }]
            });
        } else { setPrevalenciaData(null); }
        
        setLoading(false);
    }, []);
    
    const handleFilterChange = (inicio, fim) => {
        loadAllData(inicio, fim);
    };

    useEffect(() => {
        loadAllData();
    }, [loadAllData]);

    const gridStyle = {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '40px',
        marginTop: '20px',
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Dashboard Assistencial</h1>
            <FiltroPeriodo onFilterChange={handleFilterChange} />
            
            {loading ? <p>Carregando dados para o periodo...</p> : error ? (
                <p style={{ color: 'red' }}>Erro ao carregar dados: {error}</p>
            ) : (
                <>
                    <div style={{ marginTop: '20px' }}>
                        <GraficoBarrasHorizontais 
                            chartData={diagnosticosData} 
                            chartTitle="Top 15 Diagnosticos (CID-10)" 
                        />
                    </div>
                    <div style={gridStyle}>
                        <GraficoPiramideEtaria 
                            chartData={perfilEtarioData} 
                            chartTitle="Piramide Etaria de Pacientes"
                        />
                        <GraficoDonut
                            chartData={prevalenciaData}
                            chartTitle="Prevalencia de Deficiencias"
                        />
                    </div>
                </>
            )}
        </div>
    );
};

export default DashboardAssistencial;
