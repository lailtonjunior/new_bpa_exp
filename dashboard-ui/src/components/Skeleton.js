import React from 'react';

const Skeleton = ({ size = 'md', className = '' }) => {
  const sizeClass = `skeleton--${size}`;
  return <div className={`skeleton ${sizeClass} ${className}`.trim()} aria-busy="true" />;
};

export default Skeleton;
