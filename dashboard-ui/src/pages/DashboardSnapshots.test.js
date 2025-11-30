import { render, screen } from '@testing-library/react';
import DashboardAssistencial from './DashboardAssistencial';
import DashboardProdutividade from './DashboardProdutividade';
import DashboardTerritorial from './DashboardTerritorial';
import fetchData from '../services/api';

jest.mock('../services/api');
jest.mock('../components/GraficoBarrasHorizontais', () => ({ chartTitle }) => (
  <div data-testid="grafico-barras">{chartTitle}</div>
));
jest.mock('../components/GraficoPiramideEtaria', () => ({ chartTitle }) => (
  <div data-testid="grafico-piramide">{chartTitle}</div>
));
jest.mock('../components/GraficoDonut', () => ({ chartTitle }) => (
  <div data-testid="grafico-donut">{chartTitle}</div>
));
jest.mock('../components/TabelaProdutividade', () => ({ dados }) => (
  <div data-testid="tabela-produtividade">total: {dados.length}</div>
));
jest.mock('../components/MapaTerritorial', () => ({ dados }) => (
  <div data-testid="mapa-territorial">municipios: {dados.length}</div>
));
jest.mock('../components/TabelaMunicipios', () => ({ dados }) => (
  <div data-testid="tabela-municipios">municipios: {dados.length}</div>
));

describe('snapshots dos dashboards', () => {
  test('Assistencial com dados', async () => {
    fetchData
      .mockResolvedValueOnce({
        data: [
          { cid_codigo: 'A00', cid_descricao: 'Doenca A', frequencia: 10 },
          { cid_codigo: 'B00', cid_descricao: 'Doenca B', frequencia: 5 },
        ],
        error: null,
      })
      .mockResolvedValueOnce({
        data: [
          { faixa_etaria: '0-5', masculino: 2, feminino: 3 },
          { faixa_etaria: '6-10', masculino: 1, feminino: 4 },
        ],
        error: null,
      })
      .mockResolvedValueOnce({
        data: [
          { tipo: 'Auditiva', total_pacientes: 7 },
          { tipo: 'Motora', total_pacientes: 3 },
        ],
        error: null,
      });

    const { asFragment } = render(<DashboardAssistencial />);

    await screen.findByTestId('grafico-barras');

    expect(asFragment()).toMatchSnapshot();
  });

  test('Produtividade com dados', async () => {
    fetchData.mockResolvedValueOnce({
      data: [
        { profissional: 'Ana', total_atendimentos: 12, media_diaria: 3 },
        { profissional: 'Bruno', total_atendimentos: 8, media_diaria: 2 },
      ],
      error: null,
    });

    const { asFragment } = render(<DashboardProdutividade />);

    await screen.findByTestId('tabela-produtividade');

    expect(asFragment()).toMatchSnapshot();
  });

  test('Territorial com dados', async () => {
    fetchData.mockResolvedValueOnce({
      data: [
        { municipio: 'Cidade A', total_atendimentos: 20, pacientes_unicos: 10 },
        { municipio: 'Cidade B', total_atendimentos: 15, pacientes_unicos: 9 },
      ],
      error: null,
    });

    const { asFragment } = render(<DashboardTerritorial />);

    await screen.findByTestId('mapa-territorial');

    expect(asFragment()).toMatchSnapshot();
  });
});
