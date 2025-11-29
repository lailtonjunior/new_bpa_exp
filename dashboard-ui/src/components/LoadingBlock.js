import React from 'react';

const blockStyle = {
  background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
  backgroundSize: '200% 100%',
  animation: 'shine 1.5s infinite',
  borderRadius: '8px',
  minHeight: '120px',
  width: '100%',
};

const LoadingBlock = ({ height = '120px' }) => (
  <div style={{ ...blockStyle, minHeight: height }} aria-busy="true" />
);

export default LoadingBlock;
