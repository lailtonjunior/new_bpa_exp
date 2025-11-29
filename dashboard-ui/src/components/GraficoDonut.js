import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, Title);

const GraficoDonut = ({ chartData, chartTitle }) => {
    if (!chartData) {
        return <div>Carregando dados do gráfico...</div>;
    }

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: chartTitle,
                font: { size: 18 }
            },
        },
    };

    return <Doughnut options={options} data={chartData} />;
};

export default GraficoDonut;