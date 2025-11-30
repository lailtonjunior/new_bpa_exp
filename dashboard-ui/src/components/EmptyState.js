import React from 'react';

const EmptyState = ({ message }) => (
  <div className="empty-state" role="status">
    {message}
  </div>
);

export default EmptyState;
