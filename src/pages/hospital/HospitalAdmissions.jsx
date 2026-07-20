import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import MetricCard from '../../components/common/MetricCard';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import TimeSeriesChart from '../../components/charts/TimeSeriesChart';
import { Users, TrendingUp, TrendingDown, Activity } from 'lucide-react';

export default function HospitalAdmissions() {
    const [hospitals, setHospitals] = useState([]);
    const [selected, setSelected] = useState(null);
    const [admissions, setAdmissions] = useState([]);
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
        api.hospital.admissions(selected).then(data => setAdmissions(data || [])).catch(console.error);
    }, [selected]);

    if (loading) return <div className="p-6 text-white animate-pulse">Loading...</div>;

    const totalAdmissions = admissions.reduce((s, d) => s + (d.admissions || 0), 0);

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Patient Flow</h1>
                    <p className="text-gray-400 text-sm mt-1">Admissions and discharge trends</p>
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

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard title="Total Admissions (30d)" value={totalAdmissions} icon={TrendingUp} color="blue" />
                <MetricCard title="Avg Daily" value={admissions.length ? (totalAdmissions / admissions.length).toFixed(1) : 0} icon={Activity} color="green" />
                <MetricCard title="Hospitals Monitored" value={hospitals.length} icon={Users} color="blue" />
            </div>

            <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Admissions Trend (30 days)</h2>
                <TimeSeriesChart
                    data={admissions.map(d => ({ ...d, time: d.date }))}
                    xKey="time"
                    yKey="admissions"
                    color="#3b82f6"
                    height={350}
                />
            </div>
        </div>
    );
}
