import React from 'react';

// Estilos para a tabela
const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '20px',
    fontSize: '14px',
};

const thStyle = {
    backgroundColor: '#e9ecef',
    color: '#495057',
    padding: '12px',
    border: '1px solid #dee2e6',
    textAlign: 'left',
};

const tdStyle = {
    padding: '12px',
    border: '1px solid #dee2e6',
};

const TabelaProdutividade = ({ dados }) => {
    if (!dados || dados.length === 0) {
        return <p>Não há dados de produtividade para o período selecionado.</p>;
    }

    return (
        <table style={tableStyle}>
            <thead>
                <tr>
                    <th style={thStyle}>#</th>
                    <th style={thStyle}>Profissional</th>
                    <th style={thStyle}>CBO</th>
                    <th style={thStyle}>Total de Atendimentos</th>
                    <th style={thStyle}>Pacientes Únicos</th>
                    <th style={thStyle}>Média Diária</th>
                </tr>
            </thead>
            <tbody>
                {dados.map((prof, index) => (
                    <tr key={prof.cns_profissional || index}>
                        <td style={tdStyle}>{index + 1}</td>
                        <td style={tdStyle}>{prof.profissional_nome}</td>
                        <td style={tdStyle}>{prof.cbo_descricao || 'N/A'}</td>
                        <td style={tdStyle}>{prof.total_atendimentos}</td>
                        <td style={tdStyle}>{prof.pacientes_unicos}</td>
                        <td style={tdStyle}>{prof.media_diaria_atendimentos}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default TabelaProdutividade;