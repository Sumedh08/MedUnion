import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import MetricCard from '../../components/common/MetricCard';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import { Map, Activity, AlertTriangle, TrendingUp, Users, ShieldCheck } from 'lucide-react';

export default function CommunityDashboard() {
    const [districts, setDistricts] = useState([]);
    const [outbreaks, setOutbreaks] = useState([]);
    const [kpiSummary, setKpiSummary] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            api.community.districts(),
            api.community.outbreaks(),
            api.community.kpiSummary(),
        ])
            .then(([dData, oData, kData]) => {
                setDistricts(dData || []);
                setOutbreaks(oData || []);
                setKpiSummary(kData || {});
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-6 text-white animate-pulse">Loading community data...</div>;

    const totalCases = kpiSummary.total_confirmed_cases || 0;
    const activeOutbreaks = kpiSummary.total_active_outbreaks || 0;

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Community Health Intelligence</h1>
                    <p className="text-gray-400 text-sm mt-1">District-level disease surveillance and KPIs</p>
                </div>
                <DataSourceBadge workspace="community" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard title="Districts Monitored" value={districts.length} icon={Map} color="blue" />
                <MetricCard title="Total Confirmed Cases" value={totalCases.toLocaleString()} icon={Activity} color="red" />
                <MetricCard title="Active Outbreaks" value={activeOutbreaks} icon={AlertTriangle} color={activeOutbreaks > 2 ? 'red' : 'amber'} />
                <MetricCard title="Avg Vaccination" value={`${kpiSummary.avg_vaccination_coverage || 0}%`} trend={kpiSummary.avg_vaccination_coverage >= 90 ? 'up' : 'down'} trendValue={kpiSummary.avg_vaccination_coverage >= 90 ? 'on target' : 'below target'} icon={ShieldCheck} color={kpiSummary.avg_vaccination_coverage >= 90 ? 'green' : 'amber'} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">District Disease Summary</h2>
                    <div className="space-y-3">
                        {districts.map(d => (
                            <div key={d.id} className="flex items-center justify-between p-3 bg-background-primary rounded-lg border border-gray-800">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${d.active_outbreaks > 0 ? 'bg-red-500' : 'bg-green-500'}`} />
                                    <span className="text-white font-medium">{d.name}</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-gray-400 text-sm">{d.total_confirmed_cases || 0} cases</span>
                                    {d.active_outbreaks > 0 && (
                                        <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 font-medium">OUTBREAK</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Active Outbreak Alerts</h2>
                    {outbreaks.filter(o => o.status === 'active' || o.status === 'monitoring').length === 0 ? (
                        <p className="text-gray-500 text-center py-8">No active outbreaks detected</p>
                    ) : (
                        <div className="space-y-4">
                            {outbreaks.filter(o => o.status === 'active' || o.status === 'monitoring').map((o, i) => (
                                <div key={i} className="p-4 bg-red-500/5 border border-red-500/20 rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <AlertTriangle className="w-4 h-4 text-red-500" />
                                        <span className="text-white font-semibold">{o.disease}</span>
                                        <span className="text-gray-400 text-sm">- {o.district_id}</span>
                                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${o.risk_level === 'critical' ? 'bg-red-500/20 text-red-400' : o.risk_level === 'high' ? 'bg-amber-500/20 text-amber-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                            {o.risk_level?.toUpperCase()}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-400">
                                        {o.cases} confirmed cases — Status: {o.status}
                                    </p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
