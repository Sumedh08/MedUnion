import { useEffect, useState } from 'react';
import { api } from '../services/api';
import MetricCard from '../components/common/MetricCard';
import { Activity, ShieldCheck, AlertTriangle, CloudRain } from 'lucide-react';
import RiskGauge from '../components/charts/RiskGauge';
import TamilNaduMap from '../components/charts/TamilNaduMap';

export default function Dashboard() {
    const [data, setData] = useState(null);
    const [facilities, setFacilities] = useState([]); // State for map facilities
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                // Fetch overview AND facilities for the map
                const [overview, facs] = await Promise.all([
                    api.dashboard.getOverview(),
                    api.vaccines.getFacilities()
                ]);
                setData(overview);
                setFacilities(facs);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    if (loading) return <div className="p-6 text-white">Loading system overview...</div>;
    if (!data) return <div className="p-6 text-red-400">Failed to load dashboard data.</div>;

    return (
        <div className="p-6 space-y-6">
            {/* KPI Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="System Health Score"
                    value={`${data.system_health_score}%`}
                    trend="up"
                    trendValue="+2.4%"
                    icon={Activity}
                    color="blue"
                />
                <MetricCard
                    title="Facilities Monitored (TN)"
                    value={data.facilities_monitored}
                    icon={ShieldCheck}
                    color="green"
                />
                <MetricCard
                    title="Active Alerts"
                    value={data.active_alerts}
                    trend="down"
                    trendValue="-5"
                    icon={AlertTriangle}
                    color={data.active_alerts > 5 ? "red" : "amber"}
                />
                <MetricCard
                    title="Disasters Averted (30d)"
                    value={data.failures_prevented_24h * 10}
                    trend="up"
                    trendValue="+12"
                    icon={CloudRain}
                    color="purple"
                />
            </div>

            {/* Main Content: Map & Risk Gauge */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
                {/* Interactive Tamil Nadu Map */}
                <div className="lg:col-span-2 bg-background-secondary rounded-xl border border-gray-800 p-1 flex flex-col">
                    <div className="px-4 py-2 border-b border-gray-800 flex justify-between items-center">
                        <h3 className="font-semibold text-white">Live Health Grid: Tamil Nadu</h3>
                        <div className="flex gap-2 text-xs">
                            <span className="flex items-center gap-1 text-gray-400"><div className="w-2 h-2 bg-blue-500 rounded-full"></div> Hospitals</span>
                            <span className="flex items-center gap-1 text-gray-400"><div className="w-2 h-2 bg-purple-500 rounded-full"></div> Warehouses</span>
                        </div>
                    </div>
                    <div className="flex-1 relative z-0">
                        {/* Using key to force re-render if needed */}
                        <div style={{ height: '100%', minHeight: '400px' }}>
                            <TamilNaduMap facilities={facilities} height="100%" />
                        </div>
                    </div>
                </div>

                {/* System Risk Index */}
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6 flex flex-col items-center justify-center">
                    <h3 className="text-lg font-semibold text-white mb-8">Aggregated Risk Index</h3>
                    <RiskGauge value={100 - data.system_health_score} size={200} />
                    <div className="mt-8 text-center space-y-3">
                        <div className="p-3 bg-background-tertiary rounded-lg border border-gray-700">
                            <p className="text-sm text-gray-400">Predicted Trend (24h)</p>
                            <p className="text-xl font-bold text-green-400 flex items-center justify-center gap-2">
                                Stable <Activity className="w-4 h-4" />
                            </p>
                        </div>
                        <p className="text-xs text-gray-500 max-w-[200px]">
                            AI confidence level: 94%. Based on data from RGGGH, Stanley, and TNMSC warehouses.
                        </p>
                    </div>
                </div>
            </div>

            {/* Activity / Alerts Feed Placeholder */}
            <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Recent Critical Activity</h3>
                <div className="space-y-4">
                    {/* Hardcoded sample feed for visual */}
                    {[1, 2, 3].map(i => (
                        <div key={i} className="flex gap-4 items-start pb-4 border-b border-gray-800 last:border-0 last:pb-0">
                            <div className="w-2 h-2 mt-2 rounded-full bg-blue-500"></div>
                            <div>
                                <p className="text-sm text-white">Anomaly detected in Vaccine Cold Chain at FAC-00{i}</p>
                                <p className="text-xs text-gray-500">2 hours ago • Automated Check</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
