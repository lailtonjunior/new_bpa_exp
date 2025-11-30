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

    const municipiosComCoords = dados
        .filter((municipio) => municipio.latitude && municipio.longitude)
        .slice(0, 50);

    return (
        <MapContainer center={position} zoom={6} className="map-container">
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            {municipiosComCoords.map((municipio) => {
                const coords = [municipio.latitude, municipio.longitude];
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
