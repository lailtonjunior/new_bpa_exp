import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const GraficoPiramideEtaria = ({ chartData, chartTitle }) => {
    if (!chartData) {
        return <div>Carregando dados do gráfico...</div>;
    }

    const options = {
        indexAxis: 'y',
        responsive: true,
        scales: {
            x: {
                stacked: true,
                ticks: {
                    // Formata os labels do eixo X para mostrar números positivos
                    callback: function(value) {
                        return Math.abs(value);
                    }
                }
            },
            y: {
                stacked: true,
            }
        },
        plugins: {
            legend: { position: 'top' },
            title: {
                display: true,
                text: chartTitle,
                font: { size: 18 }
            },
            tooltip: {
                // Formata os tooltips para mostrar números positivos
                callbacks: {
                    label: function(context) {
                        return `${context.dataset.label}: ${Math.abs(context.raw)}`;
                    }
                }
            }
        },
    };

    return <Bar options={options} data={chartData} />;
};

export default GraficoPiramideEtaria;