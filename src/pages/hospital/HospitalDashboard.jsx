import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import MetricCard from '../../components/common/MetricCard';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import {
    Building2, Activity, Users, Clock,
    AlertTriangle, TrendingUp, BedDouble,
} from 'lucide-react';

export default function HospitalDashboard() {
    const [hospitals, setHospitals] = useState([]);
    const [kpiSummary, setKpiSummary] = useState({});
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            api.hospital.list(),
            api.hospital.kpiSummary(),
            api.hospital.alerts(),
        ])
            .then(([hData, kData, aData]) => {
                setHospitals(hData || []);
                setKpiSummary(kData || {});
                setAlerts(aData || []);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <LoadingSkeleton />;

    const totalBeds = hospitals.reduce((s, h) => s + (h.total_beds || 0), 0);
    const occupiedBeds = hospitals.reduce((s, h) => s + (h.occupied_beds || 0), 0);
    const avgOccupancy = totalBeds ? Math.round((occupiedBeds / totalBeds) * 100) : 0;
    const criticalCount = kpiSummary.critical_hospitals || alerts.filter(a => a.severity === 'critical').length;

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Hospital Operations Intelligence</h1>
                    <p className="text-gray-400 text-sm mt-1">Real-time monitoring across {hospitals.length} facilities</p>
                </div>
                <DataSourceBadge workspace="hospital" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard title="Total Beds" value={totalBeds.toLocaleString()} icon={BedDouble} color="blue" />
                <MetricCard title="Avg Occupancy" value={`${avgOccupancy}%`} trend={avgOccupancy > 80 ? 'up' : 'down'} trendValue={`${Math.abs(avgOccupancy - 75)}%`} icon={Activity} color={avgOccupancy > 80 ? 'red' : 'green'} />
                <MetricCard title="Total Staff" value={kpiSummary.total_staff || 0} icon={Users} color="blue" />
                <MetricCard title="Active Alerts" value={alerts.length} icon={AlertTriangle} color={criticalCount > 0 ? 'red' : 'amber'} />
            </div>

            {alerts.length > 0 && (
                <div className="bg-background-secondary rounded-xl border border-red-900/50 p-6">
                    <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                        Active Alerts
                    </h2>
                    <div className="space-y-2">
                        {alerts.slice(0, 5).map((a, i) => (
                            <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-background-primary/50 border border-gray-800">
                                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${a.severity === 'critical' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}`}>
                                    {a.severity.toUpperCase()}
                                </span>
                                <div className="flex-1 min-w-0">
                                    <p className="text-white text-sm">{a.hospital_name}</p>
                                    <p className="text-gray-400 text-xs">{a.message}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Facility Status Overview</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-800">
                                <th className="text-left py-3 px-2 text-gray-400 font-medium">Facility</th>
                                <th className="text-center py-3 px-2 text-gray-400 font-medium">Type</th>
                                <th className="text-center py-3 px-2 text-gray-400 font-medium">Occupancy</th>
                                <th className="text-center py-3 px-2 text-gray-400 font-medium">Beds</th>
                                <th className="text-center py-3 px-2 text-gray-400 font-medium">Staff</th>
                                <th className="text-center py-3 px-2 text-gray-400 font-medium">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {hospitals.map((h) => (
                                <tr key={h.id} className="border-b border-gray-800/50 hover:bg-background-tertiary/50 transition-colors">
                                    <td className="py-3 px-2 text-white font-medium">{h.name}</td>
                                    <td className="py-3 px-2 text-center text-gray-400">{h.type || 'N/A'}</td>
                                    <td className="py-3 px-2 text-center">
                                        <OccupancyBar value={h.bed_occupancy_pct || 0} />
                                    </td>
                                    <td className="py-3 px-2 text-center text-gray-300">{h.occupied_beds || 0}/{h.total_beds || 0}</td>
                                    <td className="py-3 px-2 text-center text-gray-300">{h.active_staff_count || 0}</td>
                                    <td className="py-3 px-2 text-center">
                                        <StatusBadge occupancy={h.bed_occupancy_pct || 0} />
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function OccupancyBar({ value }) {
    const color = value > 85 ? 'bg-red-500' : value > 70 ? 'bg-amber-500' : 'bg-green-500';
    return (
        <div className="flex items-center gap-2">
            <div className="w-20 bg-gray-700 h-1.5 rounded-full overflow-hidden">
                <div className={`h-full ${color}`} style={{ width: `${Math.min(value, 100)}%` }} />
            </div>
            <span className="text-gray-300 text-xs w-8">{value}%</span>
        </div>
    );
}

function StatusBadge({ occupancy }) {
    if (occupancy > 85) return <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 font-medium">Critical</span>;
    if (occupancy > 70) return <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-medium">Warning</span>;
    return <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 font-medium">Normal</span>;
}

function LoadingSkeleton() {
    return (
        <div className="p-6 space-y-6 animate-pulse">
            <div className="h-8 w-64 bg-gray-800 rounded" />
            <div className="grid grid-cols-4 gap-4">
                {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-gray-800 rounded-xl" />)}
            </div>
            <div className="h-96 bg-gray-800 rounded-xl" />
        </div>
    );
}
