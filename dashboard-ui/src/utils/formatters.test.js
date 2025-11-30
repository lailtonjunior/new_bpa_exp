import { formatCurrency, formatNumber, formatPercent } from './formatters';

describe('formatters', () => {
  test('formata moeda em pt-BR e trata valores vazios', () => {
    expect(formatCurrency(1234.56)).toMatch(/R\$\s?1\.234,56/);
    expect(formatCurrency(null)).toBe('R$ 0,00');
  });

  test('formata números com separador de milhar', () => {
    expect(formatNumber(9876543)).toBe('9.876.543');
    expect(formatNumber('42')).toBe('42');
    expect(formatNumber(undefined)).toBe('0');
  });

  test('formata percentuais e trata entradas inválidas', () => {
    expect(formatPercent(0.1234)).toBe('12,34%');
    expect(formatPercent('0.5', 1)).toBe('50,0%');
    expect(formatPercent(undefined)).toBe('0%');
  });
});
