import React from 'react';

const TableWrapper = ({ children, scroll = false }) => {
  const wrapperClass = scroll ? 'table-wrapper table-wrapper--scroll' : 'table-wrapper';
  return <div className={wrapperClass}>{children}</div>;
};

export default TableWrapper;
