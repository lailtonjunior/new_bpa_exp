import React, { useState, useEffect, useCallback } from 'react';
import CardKPI from '../components/CardKPI';
import GraficoAtendimentos from '../components/GraficoAtendimentos';
import FiltroPeriodo from '../components/FiltroPeriodo';
import fetchData from '../services/api';
import { formatCurrency, formatNumber } from '../utils/formatters';
import LoadingBlock from '../components/LoadingBlock';
import EmptyState from '../components/EmptyState';

const dashboardStyle = {
  padding: '20px',
};

const containerStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  justifyContent: 'center',
};

const DashboardExecutivo = () => {
  const [kpis, setKpis] = useState(null);
  const [graficoData, setGraficoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async (inicio, fim) => {
    setLoading(true);
    setError(null);
    
    const [dataKpisResp, dataGraficoResp] = await Promise.all([
        fetchData('/api/indicadores/executivo/kpis_principais', inicio, fim),
        fetchData('/api/indicadores/executivo/atendimentos_por_periodo', inicio, fim)
    ]);

    if (dataKpisResp.error || dataGraficoResp.error) {
        setError(dataKpisResp.error || dataGraficoResp.error);
        setLoading(false);
        return;
    }

    setKpis(dataKpisResp.data);

    if (dataGraficoResp.data.length > 0) {
        setGraficoData({
            labels: dataGraficoResp.data.map(item => item.periodo),
            datasets: [
                {
                    label: 'Total de Atendimentos',
                    data: dataGraficoResp.data.map(item => item.total_atendimentos),
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                },
                {
                    label: 'Pacientes unicos',
                    data: dataGraficoResp.data.map(item => item.pacientes_unicos),
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                }
            ]
        });
    } else {
        setGraficoData(null);
    }

    setLoading(false);
  }, []);
  
  const handleFilterChange = (inicio, fim) => {
    loadData(inicio, fim);
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div style={dashboardStyle}>
      <h1>Dashboard Executivo</h1>
      
      <FiltroPeriodo onFilterChange={handleFilterChange} />

      {loading ? (
          <LoadingBlock height="260px" />
      ) : error ? (
          <p style={{ color: 'red' }}>Falha ao carregar dados: {error}</p>
      ) : (
          <>
            <div style={containerStyle}>
              <CardKPI 
                title="Total de Atendimentos no Periodo" 
                value={formatNumber(kpis?.total_atendimentos_mes ?? 0)}
              />
              <CardKPI 
                title="Pacientes unicos no Periodo" 
                value={formatNumber(kpis?.pacientes_unicos_mes ?? 0)}
              />
              <CardKPI 
                title="Faturamento Estimado (BPA/APAC)" 
                value={formatCurrency(kpis?.faturamento_estimado_mes ?? 0)}
              />
            </div>
            {graficoData ? (
              <GraficoAtendimentos 
                  chartData={graficoData}
                  chartTitle="Evolucao Mensal"
              />
            ) : (
              <EmptyState message="Sem dados de atendimentos para o periodo selecionado." />
            )}
          </>
      )}
    </div>
  );
};

export default DashboardExecutivo;
