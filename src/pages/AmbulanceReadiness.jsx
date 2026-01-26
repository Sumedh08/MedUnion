import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Ambulance, Zap } from 'lucide-react';
import clsx from 'clsx';
import RiskGauge from '../components/charts/RiskGauge';

export default function AmbulanceReadiness() {
    const [fleet, setFleet] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const data = await api.ambulance.getFleetStatus();
                setFleet(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) return <div className="p-6 text-white">Loading fleet status...</div>;

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Ambulance Fleet Readiness</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {fleet.map((zone) => {
                    const utilization = (zone.busy / zone.total_ambulances) * 100;
                    return (
                        <div key={zone.zone} className="bg-background-secondary rounded-xl border border-gray-800 p-6 relative overflow-hidden">
                            {zone.surge_risk === "HIGH" && (
                                <div className="absolute top-0 right-0 bg-red-500 text-white text-xs px-3 py-1 rounded-bl-lg font-bold">
                                    SURGE RISK
                                </div>
                            )}

                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-500">
                                    <Ambulance className="w-6 h-6" />
                                </div>
                                <h3 className="text-xl font-bold text-white">{zone.zone}</h3>
                            </div>

                            <div className="flex justify-between items-center mb-6">
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-white">{zone.available}</p>
                                    <p className="text-xs text-gray-500 uppercase">Available</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-gray-400">{zone.busy}</p>
                                    <p className="text-xs text-gray-500 uppercase">Busy</p>
                                </div>
                                <div className="text-center">
                                    <p className={clsx("text-3xl font-bold", zone.avg_response_time > 15 ? "text-red-400" : "text-green-400")}>
                                        {zone.avg_response_time}m
                                    </p>
                                    <p className="text-xs text-gray-500 uppercase">Avg Resp</p>
                                </div>
                            </div>

                            <div className="mt-4">
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-gray-400">Utilization</span>
                                    <span className="text-white">{Math.round(utilization)}%</span>
                                </div>
                                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                    <div
                                        className={clsx("h-full", utilization > 80 ? "bg-red-500" : "bg-blue-500")}
                                        style={{ width: `${utilization}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
