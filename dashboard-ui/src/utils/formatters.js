export const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'R$ 0,00';
  const number = Number(value);
  return number.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

export const formatNumber = (value) => {
  if (value === null || value === undefined) return '0';
  return Number(value).toLocaleString('pt-BR');
};

export const formatPercent = (value, fractionDigits = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '0%';
  const number = Number(value);
  return number.toLocaleString('pt-BR', {
    style: 'percent',
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
};
