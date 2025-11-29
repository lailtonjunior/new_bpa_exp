import React from 'react';

const container = {
  padding: '16px',
  border: '1px dashed #ced4da',
  borderRadius: '8px',
  backgroundColor: '#fff',
  textAlign: 'center',
  color: '#6c757d',
};

const EmptyState = ({ message }) => (
  <div style={container} role="status">
    {message}
  </div>
);

export default EmptyState;
