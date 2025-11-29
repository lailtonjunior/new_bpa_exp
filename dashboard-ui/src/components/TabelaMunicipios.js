import React from 'react';

// Estilos para a tabela (reutilizados do componente de produtividade)
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

const TabelaMunicipios = ({ dados }) => {
    if (!dados || dados.length === 0) {
        return <p>Não há dados de municípios para o período selecionado.</p>;
    }

    return (
        <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table style={tableStyle}>
                <thead>
                    <tr>
                        <th style={thStyle}>#</th>
                        <th style={thStyle}>Município</th>
                        <th style={thStyle}>UF</th>
                        <th style={thStyle}>Nº de Pacientes</th>
                    </tr>
                </thead>
                <tbody>
                    {dados.map((municipio, index) => (
                        <tr key={municipio.municipio_ibge || index}>
                            <td style={tdStyle}>{index + 1}</td>
                            <td style={tdStyle}>{municipio.municipio_nome}</td>
                            <td style={tdStyle}>{municipio.uf}</td>
                            <td style={tdStyle}>{municipio.total_pacientes}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default TabelaMunicipios;