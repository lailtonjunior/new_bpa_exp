import { render, screen } from '@testing-library/react';
import DashboardExecutivo from './DashboardExecutivo';
import fetchData from '../services/api';

jest.mock('../services/api');
jest.mock('../components/GraficoAtendimentos', () => ({ chartData, chartTitle }) => (
  <div data-testid="grafico-atendimentos">
    <span>{chartTitle}</span>
    <pre>{JSON.stringify(chartData)}</pre>
  </div>
));

describe('DashboardExecutivo', () => {
  test('exibe estado de carregamento inicial', () => {
    fetchData.mockImplementation(() => new Promise(() => {}));
    const { container } = render(<DashboardExecutivo />);
    expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument();
  });

  test('exibe estado vazio quando não há dados para o gráfico', async () => {
    fetchData
      .mockResolvedValueOnce({ data: {}, error: null })
      .mockResolvedValueOnce({ data: [], error: null });

    render(<DashboardExecutivo />);

    expect(await screen.findByText(/Sem dados de atendimentos para o periodo/i)).toBeInTheDocument();
  });

  test('exibe estado de erro quando fetch falha', async () => {
    fetchData
      .mockResolvedValueOnce({ data: {}, error: 'Erro na API' })
      .mockResolvedValueOnce({ data: [], error: null });

    render(<DashboardExecutivo />);

    expect(await screen.findByText(/Falha ao carregar dados: Erro na API/i)).toBeInTheDocument();
  });

  test('gera snapshot com dados carregados', async () => {
    fetchData
      .mockResolvedValueOnce({
        data: {
          total_atendimentos_mes: 1200,
          pacientes_unicos_mes: 800,
          faturamento_estimado_mes: 98765.43,
        },
        error: null,
      })
      .mockResolvedValueOnce({
        data: [
          { periodo: '2024-01', total_atendimentos: 100, pacientes_unicos: 50 },
          { periodo: '2024-02', total_atendimentos: 200, pacientes_unicos: 120 },
        ],
        error: null,
      });

    const { asFragment } = render(<DashboardExecutivo />);

    await screen.findByTestId('grafico-atendimentos');

    expect(asFragment()).toMatchSnapshot();
  });
});
