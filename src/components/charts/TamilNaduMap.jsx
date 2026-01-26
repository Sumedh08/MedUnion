import { useEffect, useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function TamilNaduMap({ facilities }) {
    const mapRef = useRef(null);
    const mapInstance = useRef(null);

    useEffect(() => {
        if (!mapRef.current) return;

        // Initialize map only once
        if (!mapInstance.current) {
            mapInstance.current = L.map(mapRef.current).setView([13.05, 80.20], 10);

            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(mapInstance.current);
        }

        // Clear existing markers
        mapInstance.current.eachLayer((layer) => {
            if (layer instanceof L.Marker) {
                mapInstance.current.removeLayer(layer);
            }
        });

        // Add markers
        if (facilities && facilities.length > 0) {
            facilities.forEach(fac => {
                if (fac.latitude && fac.longitude) {
                    const color = fac.risk_score?.level === 'RED' ? 'red' :
                        fac.risk_score?.level === 'AMBER' ? 'orange' : 'green';

                    const marker = L.marker([fac.latitude, fac.longitude])
                        .addTo(mapInstance.current)
                        .bindPopup(`
                            <div class="p-1">
                                <h3 class="font-bold text-sm mb-1">${fac.name}</h3>
                                <p class="text-xs text-gray-600 mb-1">${fac.type}</p>
                                <div class="text-xs font-bold px-2 py-1 rounded inline-block text-white bg-${color}-500">
                                   Risk: ${fac.risk_score?.score ? Math.round(fac.risk_score.score) : 0}%
                                </div>
                            </div>
                        `);
                }
            });
        }

        // Cleanup on unmount (optional, but good practice)
        return () => {
            // mapInstance.current.remove(); 
            // Often better to keep instance in React unless strict cleanup needed
        };
    }, [facilities]);

    return <div ref={mapRef} style={{ height: '100%', width: '100%', minHeight: '400px', zIndex: 0 }} />;
}
