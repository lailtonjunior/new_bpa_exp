const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
const REQUEST_TIMEOUT_MS = 10000;

/**
 * Funcao generica para buscar dados da API, com timeout e tratamento de erro padrao.
 * @param {string} endpoint endpoint da API (ex: '/api/indicadores/executivo/kpis_principais')
 * @param {string} [inicio] data de inicio AAAA-MM-DD
 * @param {string} [fim] data de fim AAAA-MM-DD
 * @returns {Promise<{data: any, error: string | null}>}
 */
const fetchData = async (endpoint, inicio, fim) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const apiKey = process.env.REACT_APP_API_KEY;

  try {
    const params = new URLSearchParams();
    if (inicio) params.append('data_inicio', inicio);
    if (fim) params.append('data_fim', fim);

    const url = `${API_URL}${endpoint}?${params.toString()}`;
    const response = await fetch(url, { 
      signal: controller.signal,
      headers: apiKey ? { 'X-API-Key': apiKey } : {}
    });

    if (!response.ok) {
      const detail = await response.text();
      return { data: endpoint.includes('kpis') ? {} : [], error: `Erro ${response.status}: ${detail}` };
    }
    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    const message = error.name === 'AbortError' ? 'Requisicao excedeu o tempo limite' : `Erro ao buscar ${endpoint}`;
    return { data: endpoint.includes('kpis') ? {} : [], error: message };
  } finally {
    clearTimeout(timeout);
  }
};

export default fetchData;
