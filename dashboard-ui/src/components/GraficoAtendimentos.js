import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Registra os componentes do Chart.js que vamos usar
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Função para buscar os dados do nosso novo endpoint
const fetchAtendimentosPeriodo = async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/indicadores/executivo/atendimentos_por_periodo');
        if (!response.ok) throw new Error('Falha ao buscar dados');
        return await response.json();
    } catch (error) {
        console.error("Erro no fetch do gráfico:", error);
        return [];
    }
};

const GraficoAtendimentos = () => {
    const [chartData, setChartData] = useState(null);

    useEffect(() => {
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
                            label: 'Pacientes Únicos',
                            data: pacientes,
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        }
                    ]
                });
            }
        });
    }, []);

    if (!chartData) {
        return <div>Carregando dados do gráfico...</div>;
    }

    return (
        <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', marginTop: '20px' }}>
            <Line 
                options={{
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Evolução Mensal (Últimos 12 Meses)' }
                    }
                }} 
                data={chartData} 
            />
        </div>
    );
};

export default GraficoAtendimentos;