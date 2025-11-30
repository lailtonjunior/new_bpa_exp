import React from 'react';
import TableWrapper from './TableWrapper';

const TabelaMunicipios = ({ dados }) => {
  if (!dados || dados.length === 0) {
    return <p className="muted-text">Nǜo hǭ dados de munic��pios para o per��odo selecionado.</p>;
  }

  return (
    <TableWrapper scroll>
      <table className="data-table">
        <thead>
          <tr>
            <th className="data-table__cell data-table__cell--head data-table__cell--number">#</th>
            <th className="data-table__cell data-table__cell--head">Munic��pio</th>
            <th className="data-table__cell data-table__cell--head">UF</th>
            <th className="data-table__cell data-table__cell--head">N�� de Pacientes</th>
          </tr>
        </thead>
        <tbody>
          {dados.map((municipio, index) => (
            <tr key={municipio.municipio_ibge || index}>
              <td className="data-table__cell data-table__cell--number">{index + 1}</td>
              <td className="data-table__cell">{municipio.municipio_nome}</td>
              <td className="data-table__cell">{municipio.uf}</td>
              <td className="data-table__cell">{municipio.total_pacientes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </TableWrapper>
  );
};

export default TabelaMunicipios;
