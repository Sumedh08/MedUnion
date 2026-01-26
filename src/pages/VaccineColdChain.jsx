import { useEffect, useState } from 'react';
import { api } from '../services/api';
import RiskCard from '../components/common/RiskCard';
import TimeSeriesChart from '../components/charts/TimeSeriesChart';
import { Thermometer, Zap, AlertTriangle, ArrowRight } from 'lucide-react';
import clsx from 'clsx';

export default function VaccineColdChain() {
    const [facilities, setFacilities] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const data = await api.vaccines.getFacilities();
                setFacilities(data);
                if (data.length > 0) setSelectedId(data[0].id);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    const selectedFacility = facilities.find(f => f.id === selectedId);

    // Generate some dummy history for the chart based on current temp
    const chartData = selectedFacility ? Array.from({ length: 24 }, (_, i) => ({
        time: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        temp: selectedFacility.name.includes('005')
            ? 4 + Math.sin(i / 3) + (i > 18 ? (i - 18) * 0.5 : 0) // Drift up
            : 4 + Math.sin(i / 3) * 0.5 + (Math.random() - 0.5)
    })) : [];

    if (loading) return <div className="p-6 text-white">Loading vaccine data...</div>;

    return (
        <div className="h-full flex flex-col md:flex-row overflow-hidden">
            {/* Sidebar List */}
            <div className="w-full md:w-1/3 border-r border-gray-800 bg-background-secondary flex flex-col">
                <div className="p-4 border-b border-gray-800">
                    <h3 className="font-semibold text-white">Monitored Facilities ({facilities.length})</h3>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {facilities.map(fac => (
                        <div key={fac.id} onClick={() => setSelectedId(fac.id)}>
                            <div className={clsx("rounded-xl transition-all", selectedId === fac.id && "ring-2 ring-blue-500")}>
                                <RiskCard facility={fac} />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 bg-background-primary overflow-y-auto p-6">
                {selectedFacility ? (
                    <div className="space-y-6 max-w-4xl mx-auto">
                        {/* Header */}
                        <div className="flex justify-between items-start">
                            <div>
                                <h2 className="text-2xl font-bold text-white">{selectedFacility.name}</h2>
                                <div className="flex gap-4 mt-2 text-sm text-gray-400">
                                    <span className="flex items-center gap-1"><Thermometer className="w-4 h-4" /> Cold Chain Unit A</span>
                                    <span className="flex items-center gap-1"><Zap className="w-4 h-4" /> Power: Stable</span>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-3xl font-mono font-bold text-white">
                                    {chartData[chartData.length - 1]?.temp.toFixed(1)}°C
                                </div>
                                <div className="text-xs text-gray-500 uppercase tracking-wider">Current Temp</div>
                            </div>
                        </div>

                        {/* Chart */}
                        <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                            <h4 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">24-Hour Temperature Log</h4>
                            <TimeSeriesChart
                                data={chartData}
                                xKey="time"
                                yKey="temp"
                                thresholdMin={2}
                                thresholdMax={8}
                                height={300}
                            />
                        </div>

                        {/* Risk Prediction Panel */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                                <h4 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">Risk Prediction</h4>
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-gray-300">Failure Probability (24h)</span>
                                    <span className={clsx("font-bold",
                                        selectedFacility.risk_score.score > 50 ? "text-red-500" : "text-green-500"
                                    )}>
                                        {Math.round(selectedFacility.risk_score.score)}%
                                    </span>
                                </div>
                                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                    <div
                                        className={clsx("h-full",
                                            selectedFacility.risk_score.score > 50 ? "bg-red-500" : "bg-green-500"
                                        )}
                                        style={{ width: `${selectedFacility.risk_score.score}%` }}
                                    ></div>
                                </div>
                                <p className="mt-4 text-sm text-gray-400">
                                    Intelligence Engine detects {selectedFacility.risk_score.level === 'GREEN' ? 'no significant anomalies' : 'an upward drift pattern consistent with compressor fatigue'}.
                                </p>
                            </div>

                            {/* Recommendations */}
                            <div className="bg-blue-900/10 rounded-xl border border-blue-500/20 p-6">
                                <h4 className="text-sm font-semibold text-blue-400 mb-4 uppercase tracking-wider">Recommended Actions</h4>
                                {selectedFacility.recommendations.length > 0 ? (
                                    <div className="space-y-3">
                                        {selectedFacility.recommendations.map(rec => (
                                            <div key={rec.id} className="bg-background-PRIMARY p-3 rounded-lg border border-blue-500/30 flex gap-3">
                                                <div className="mt-1"><ArrowRight className="w-4 h-4 text-blue-400" /></div>
                                                <div>
                                                    <p className="text-white font-medium text-sm">{rec.title}</p>
                                                    <p className="text-gray-400 text-xs mt-1">{rec.description}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center h-32 text-gray-500 text-sm">
                                        <ShieldCheck className="w-8 h-8 mb-2 opacity-50" />
                                        No actions required at this time.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center justify-center h-full text-gray-500">Select a facility to view details</div>
                )}
            </div>
        </div>
    );
}

function ShieldCheck(props) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
            <path d="m9 12 2 2 4-4" />
        </svg>
    )
}
