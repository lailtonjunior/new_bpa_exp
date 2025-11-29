import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const GraficoBarrasHorizontais = ({ chartData, chartTitle }) => {
    if (!chartData) {
        return <div>Carregando dados do gráfico...</div>;
    }

    const options = {
        indexAxis: 'y', // Isso torna o gráfico de barras horizontal
        elements: {
            bar: {
                borderWidth: 2,
            },
        },
        responsive: true,
        plugins: {
            legend: {
                display: false, // Vamos esconder a legenda para um visual mais limpo
            },
            title: {
                display: true,
                text: chartTitle,
                font: { size: 18 }
            },
        },
    };

    return <Bar options={options} data={chartData} />;
};

export default GraficoBarrasHorizontais;