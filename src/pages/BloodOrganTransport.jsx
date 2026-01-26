import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Droplet, MapPin, Clock } from 'lucide-react';
import clsx from 'clsx';

export default function BloodOrganTransport() {
    const [transports, setTransports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const data = await api.blood.getTransports();
                setTransports(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) return <div className="p-6 text-white">Loading transport data...</div>;

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Active Blood & Organ Transports</h2>

            <div className="space-y-4">
                {transports.map((t) => (
                    <div key={t.transport_id} className="bg-background-secondary rounded-xl border border-gray-800 p-6 flex flex-col md:flex-row items-center gap-6">
                        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-500/10 text-red-500 shrink-0">
                            <Droplet className="w-6 h-6" />
                        </div>

                        <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div>
                                <h3 className="font-semibold text-white">{t.type} Transport #{t.transport_id}</h3>
                                <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                                    <MapPin className="w-4 h-4" />
                                    <span>{t.source}</span>
                                    <span>→</span>
                                    <span>{t.destination}</span>
                                </div>
                            </div>

                            <div>
                                <p className="text-xs text-gray-500 mb-1">ETA</p>
                                <div className="flex items-center gap-2 text-white font-mono">
                                    <Clock className="w-4 h-4 text-blue-400" />
                                    {new Date(t.eta).toLocaleTimeString()}
                                </div>
                            </div>

                            <div>
                                <p className="text-xs text-gray-500 mb-1">Current Status</p>
                                <div className="flex gap-3">
                                    <span className={clsx("px-2 py-1 rounded text-xs font-bold",
                                        t.traffic_status === 'HEAVY' ? "bg-red-500/20 text-red-400" : "bg-green-500/20 text-green-400"
                                    )}>
                                        {t.traffic_status} TRAFFIC
                                    </span>
                                    <span className={clsx("px-2 py-1 rounded text-xs font-bold",
                                        t.temperature > 6 ? "bg-red-500/20 text-red-400" : "bg-green-500/20 text-green-400"
                                    )}>
                                        {t.temperature.toFixed(1)}°C
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
