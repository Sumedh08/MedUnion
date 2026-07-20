import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import MetricCard from '../../components/common/MetricCard';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import { BedDouble, Activity, TrendingUp, AlertTriangle } from 'lucide-react';

export default function HospitalOccupancy() {
    const [hospitals, setHospitals] = useState([]);
    const [selected, setSelected] = useState(null);
    const [occupancy, setOccupancy] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.hospital.list()
            .then(data => {
                setHospitals(data || []);
                if (data?.length) setSelected(data[0].id);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        if (!selected) return;
        api.hospital.occupancy(selected).then(data => setOccupancy(data || [])).catch(console.error);
    }, [selected]);

    if (loading) return <div className="p-6 text-white animate-pulse">Loading...</div>;
    const sel = hospitals.find(h => h.id === selected);

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Bed Occupancy</h1>
                    <p className="text-gray-400 text-sm mt-1">Real-time ward-level occupancy tracking</p>
                </div>
                <DataSourceBadge workspace="hospital" />
            </div>

            <div className="flex gap-2 flex-wrap">
                {hospitals.map(h => (
                    <button
                        key={h.id}
                        onClick={() => setSelected(h.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                            selected === h.id
                                ? 'bg-blue-600 text-white'
                                : 'bg-background-tertiary text-gray-400 hover:text-white'
                        }`}
                    >
                        {h.name}
                    </button>
                ))}
            </div>

            {sel && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <MetricCard title="Total Beds" value={sel.total_beds || 0} icon={BedDouble} color="blue" />
                    <MetricCard title="Occupied" value={sel.occupied_beds || 0} icon={Activity} color="amber" />
                    <MetricCard title="Occupancy Rate" value={`${sel.bed_occupancy_pct || 0}%`} icon={TrendingUp} color={(sel.bed_occupancy_pct || 0) > 80 ? 'red' : 'amber'} />
                    <MetricCard title="Available" value={sel.available_beds || 0} icon={AlertTriangle} color="green" />
                </div>
            )}

            <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Ward-Level Occupancy</h2>
                {occupancy.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No occupancy data available</p>
                ) : (
                    <div className="space-y-4">
                        {occupancy.map((w, i) => {
                            const pct = w.occupancy_pct || 0;
                            const color = pct > 85 ? 'bg-red-500' : pct > 70 ? 'bg-amber-500' : 'bg-green-500';
                            return (
                                <div key={i} className="flex items-center gap-4">
                                    <span className="text-white font-medium w-40 text-sm truncate">{w.department} - {w.ward_name}</span>
                                    <div className="flex-1 bg-gray-700 h-4 rounded-full overflow-hidden">
                                        <div className={`h-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
                                    </div>
                                    <span className="text-gray-300 text-sm w-24 text-right">{w.occupied}/{w.total} ({pct}%)</span>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
