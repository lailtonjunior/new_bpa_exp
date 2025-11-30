import React, { createContext, useContext, useEffect, useMemo } from 'react';

const theme = {
  palette: {
    primary: '#2563eb',
    secondary: '#22c55e',
    background: '#f5f7fb',
    surface: '#ffffff',
    surfaceMuted: '#f1f5f9',
    text: '#0f172a',
    muted: '#64748b',
    border: '#e2e8f0',
    danger: '#ef4444',
    warning: '#f59e0b',
  },
  typography: {
    fontFamily: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
    baseSize: '16px',
    headingsWeight: 700,
    bodyWeight: 500,
  },
  spacing: {
    unit: 8,
    scale: {
      1: 4,
      2: 8,
      3: 12,
      4: 16,
      5: 24,
      6: 32,
    },
  },
  radius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
  },
  shadow: {
    soft: '0 10px 30px rgba(15, 23, 42, 0.08)',
  },
};

const ThemeContext = createContext(theme);

export const ThemeProvider = ({ children }) => {
  useEffect(() => {
    const root = document.documentElement;
    const setVar = (key, value) => root.style.setProperty(key, value);

    Object.entries(theme.palette).forEach(([key, value]) => setVar(`--color-${key}`, value));
    Object.entries(theme.spacing.scale).forEach(([key, value]) => setVar(`--space-${key}`, `${value}px`));
    setVar('--spacing-unit', `${theme.spacing.unit}px`);
    setVar('--font-family-base', theme.typography.fontFamily);
    setVar('--font-size-base', theme.typography.baseSize);
    setVar('--font-weight-headings', theme.typography.headingsWeight);
    setVar('--font-weight-body', theme.typography.bodyWeight);
    setVar('--radius-sm', theme.radius.sm);
    setVar('--radius-md', theme.radius.md);
    setVar('--radius-lg', theme.radius.lg);
    setVar('--shadow-soft', theme.shadow.soft);
    setVar('--grid-max-width', '1200px');
  }, []);

  const value = useMemo(() => theme, []);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => useContext(ThemeContext);
export { theme };
