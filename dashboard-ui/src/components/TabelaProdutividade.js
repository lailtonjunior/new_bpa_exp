import React from 'react';
import TableWrapper from './TableWrapper';

const TabelaProdutividade = ({ dados }) => {
  if (!dados || dados.length === 0) {
    return <p className="muted-text">Nǜo hǭ dados de produtividade para o per��odo selecionado.</p>;
  }

  return (
    <TableWrapper>
      <table className="data-table">
        <thead>
          <tr>
            <th className="data-table__cell data-table__cell--head data-table__cell--number">#</th>
            <th className="data-table__cell data-table__cell--head">Profissional</th>
            <th className="data-table__cell data-table__cell--head">CBO</th>
            <th className="data-table__cell data-table__cell--head">Total de Atendimentos</th>
            <th className="data-table__cell data-table__cell--head">Pacientes �snicos</th>
            <th className="data-table__cell data-table__cell--head">MǸdia Diǭria</th>
          </tr>
        </thead>
        <tbody>
          {dados.map((prof, index) => (
            <tr key={prof.cns_profissional || index}>
              <td className="data-table__cell data-table__cell--number">{index + 1}</td>
              <td className="data-table__cell">{prof.profissional_nome}</td>
              <td className="data-table__cell">{prof.cbo_descricao || 'N/A'}</td>
              <td className="data-table__cell">{prof.total_atendimentos}</td>
              <td className="data-table__cell">{prof.pacientes_unicos}</td>
              <td className="data-table__cell">{prof.media_diaria_atendimentos}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </TableWrapper>
  );
};

export default TabelaProdutividade;
