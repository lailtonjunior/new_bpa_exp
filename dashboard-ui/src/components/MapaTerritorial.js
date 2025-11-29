import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Corrige o problema do icone padrao do marcador no Leaflet com React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const MapaTerritorial = ({ dados }) => {
    // Posicao central inicial do mapa (Tocantins)
    const position = [-9.5, -48.5]; 

    // TODO: Precisariamos de um servico ou arquivo JSON para buscar as coordenadas (lat/long) de cada municipio.
    // Por enquanto, usamos coordenadas fixas para alguns municipios conhecidos como demonstracao.
    const coordenadasMock = {
        "Colinas do Tocantins": [-8.06, -48.47],
        "Araguaina": [-7.19, -48.20],
        "Palmas": [-10.18, -48.33],
        "Gurupi": [-11.72, -49.06],
        "Porto Nacional": [-10.70, -48.41],
    };

    const municipiosComCoords = dados
        .filter((municipio) => coordenadasMock[municipio.municipio_nome])
        .slice(0, 10);

    return (
        <MapContainer center={position} zoom={6} style={{ height: '500px', width: '100%' }}>
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            {municipiosComCoords.map((municipio) => {
                const coords = coordenadasMock[municipio.municipio_nome];
                return (
                    <Marker position={coords} key={`${municipio.municipio_ibge}-${municipio.municipio_nome}`}>
                        <Popup>
                            <strong>{municipio.municipio_nome} - {municipio.uf}</strong>
                            <br />
                            Pacientes: {municipio.total_pacientes}
                        </Popup>
                    </Marker>
                );
            })}
        </MapContainer>
    );
};

export default MapaTerritorial;
