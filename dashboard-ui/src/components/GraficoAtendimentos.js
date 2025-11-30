import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const fetchAtendimentosPeriodo = async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/indicadores/executivo/atendimentos_por_periodo');
        if (!response.ok) throw new Error('Falha ao buscar dados');
        return await response.json();
    } catch (error) {
        console.error("Erro no fetch do grǭfico:", error);
        return [];
    }
};

const GraficoAtendimentos = ({ chartData: externalData = null, chartTitle = 'Evolu��ǜo Mensal (�sltimos 12 Meses)' }) => {
    const [chartData, setChartData] = useState(externalData);

    useEffect(() => {
        if (externalData) {
            setChartData(externalData);
            return;
        }
        fetchAtendimentosPeriodo().then(data => {
            if (data.length > 0) {
                const labels = data.map(item => item.periodo);
                const atendimentos = data.map(item => item.total_atendimentos);
                const pacientes = data.map(item => item.pacientes_unicos);

                setChartData({
                    labels: labels,
                    datasets: [
                        {
                            label: 'Total de Atendimentos',
                            data: atendimentos,
                            borderColor: 'rgb(54, 162, 235)',
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        },
                        {
                            label: 'Pacientes �snicos',
                            data: pacientes,
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        }
                    ]
                });
            }
        });
    }, [externalData]);

    if (!chartData) {
        return <div className="muted-text">Carregando dados do grǭfico...</div>;
    }

    return (
        <div className="chart-wrapper">
            <Line 
                options={{
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: chartTitle }
                    }
                }} 
                data={chartData} 
            />
        </div>
    );
};

export default GraficoAtendimentos;
