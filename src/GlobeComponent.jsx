import React, { useEffect, useRef, useState } from 'react';
import Globe from 'react-globe.gl';

const GlobeComponent = () => {
    const globeEl = useRef();
    const [places, setPlaces] = useState([]);

    useEffect(() => {
        if (globeEl.current) {
            // Initial camera position (focused on IMEC region)
            globeEl.current.pointOfView({ lat: 25.0, lng: 55.0, altitude: 2.5 });
        }

        // Define IMEC Nodes
        const imecNodes = [
            { name: "Mumbai (India)", lat: 18.94, lng: 72.82, type: "port" },
            { name: "Jebel Ali (UAE)", lat: 25.00, lng: 55.06, type: "port" },
            { name: "Riyadh (Saudi)", lat: 24.71, lng: 46.67, type: "rail" },
            { name: "Haifa (Israel)", lat: 32.80, lng: 34.98, type: "port" },
            { name: "Piraeus (Greece)", lat: 37.94, lng: 23.63, type: "port" },

            // Critical Points (Traditional Route)
            { name: "Bab el-Mandeb (Chokepoint)", lat: 12.60, lng: 43.30, type: "chokepoint" },
            { name: "Suez Canal (Chokepoint)", lat: 30.58, lng: 32.27, type: "chokepoint" }
        ];
        setPlaces(imecNodes);
    }, []);

    return (
        <Globe
            ref={globeEl}
            globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
            backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
            labelsData={places}
            labelLat={d => d.lat}
            labelLng={d => d.lng}
            labelText={d => d.name}
            labelSize={1.5}
            labelDotRadius={0.5}
            labelColor={() => "rgba(255, 165, 0, 0.75)"}
            labelResolution={2}
            arcsData={[
                // Route A: IMEC (Hybrid) - ORANGE/BLUE
                { startLat: 18.94, startLng: 72.82, endLat: 25.00, endLng: 55.06, color: ['blue', 'blue'], label: "IMEC Sea" },
                { startLat: 25.00, startLng: 55.06, endLat: 24.71, endLng: 46.67, color: ['orange', 'orange'], label: "IMEC Rail" },
                { startLat: 24.71, startLng: 46.67, endLat: 32.80, endLng: 34.98, color: ['orange', 'orange'], label: "IMEC Rail" },
                { startLat: 32.80, startLng: 34.98, endLat: 37.94, endLng: 23.63, color: ['blue', 'blue'], label: "IMEC Sea" },

                // Route B: Traditional (Suez) - CYAN
                { startLat: 18.94, startLng: 72.82, endLat: 12.60, endLng: 45.00, color: ['cyan', 'cyan'], label: "Red Sea" }, // Mumbai -> Bab el-Mandeb
                { startLat: 12.60, startLng: 45.00, endLat: 29.90, endLng: 32.50, color: ['cyan', 'cyan'], label: "Red Sea" }, // Bab el-Mandeb -> Suez
                { startLat: 29.90, startLng: 32.50, endLat: 37.94, endLng: 23.63, color: ['cyan', 'cyan'], label: "Mediterranean" } // Suez -> Greece
            ]}
            arcLabel={d => d.label}
            arcColor={d => d.color}
            arcDashLength={0.4}
            arcDashGap={0.2}
            arcDashAnimateTime={1500}
            arcStroke={0.5}
        />
    );
};

export default GlobeComponent;
