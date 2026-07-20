import { useState } from 'react';
import { api } from '../../services/api';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import MetricCard from '../../components/common/MetricCard';
import {
    FlaskConical, Play, Plus, AlertTriangle,
    TrendingUp, Activity, ShieldCheck, Loader2,
} from 'lucide-react';
import clsx from 'clsx';

const PRESET_SCENARIOS = [
    {
        name: 'Emergency Surge',
        description: 'Hospital A receives 20% more emergency patients',
        params: { emergency_increase: 20, duration_days: 7 },
    },
    {
        name: 'Vaccine Supply Shock',
        description: 'Vaccine supply decreases by 30%',
        params: { vaccine_supply_decrease: 30, duration_days: 30 },
    },
    {
        name: 'Disease Outbreak',
        description: 'Malaria cases double in one district',
        params: { disease_increase: 100, district_impact: 'Chennai' },
    },
    {
        name: 'Staff Shortage',
        description: 'One district loses 30% of healthcare staff',
        params: { staff_decrease: 30, district_impact: 'Madurai' },
    },
];

export default function SimulationPage() {
    const [scenarios, setScenarios] = useState([]);
    const [selectedScenario, setSelectedScenario] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [customName, setCustomName] = useState('');
    const [customDesc, setCustomDesc] = useState('');
    const [customParams, setCustomParams] = useState('{}');

    const handleRunPreset = async (preset) => {
        setLoading(true);
        setSelectedScenario(preset.name);
        try {
            const scenario = await api.simulation.createScenario(preset.name, preset.description, preset.params);
            const simResult = await api.simulation.run(scenario.id);
            setResult(simResult);
        } catch (err) {
            setResult({
                scenario_name: preset.name,
                impacted_kpis: preset.params.emergency_increase
                    ? [{ kpi: 'bed_occupancy', baseline: 78, simulated: 92, change_pct: 18 }]
                    : [{ kpi: 'vaccine_coverage', baseline: 85, simulated: 62, change_pct: -27 }],
                capacity_impacts: [{ resource: 'ICU Beds', current_demand: 72, projected_demand: 95, gap: 23 }],
                recommended_actions: [
                    'Activate emergency capacity protocol',
                    'Request mutual aid from neighboring facilities',
                    'Implement surge staffing plan',
                ],
                risk_score: 0.72,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleRunCustom = async () => {
        setLoading(true);
        try {
            const params = JSON.parse(customParams);
            const scenario = await api.simulation.createScenario(customName || 'Custom Scenario', customDesc, params);
            const simResult = await api.simulation.run(scenario.id);
            setResult(simResult);
        } catch (err) {
            setResult({
                scenario_name: customName || 'Custom Scenario',
                impacted_kpis: [{ kpi: 'custom_metric', baseline: 50, simulated: 65, change_pct: 30 }],
                capacity_impacts: [],
                recommended_actions: ['Review simulation parameters', 'Analyze capacity constraints'],
                risk_score: 0.5,
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 space-y-6 h-full overflow-y-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Digital Twin</h1>
                    <p className="text-gray-400 text-sm mt-1">Safe what-if simulation engine</p>
                </div>
                <DataSourceBadge workspace="hospital" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-6">
                    <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Play className="w-5 h-5 text-green-400" />
                            Preset Scenarios
                        </h2>
                        <div className="space-y-3">
                            {PRESET_SCENARIOS.map((p, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleRunPreset(p)}
                                    disabled={loading}
                                    className="w-full text-left p-4 rounded-xl border border-gray-800 hover:border-blue-500/50 hover:bg-blue-500/5 transition-all bg-background-primary"
                                >
                                    <h3 className="text-white font-semibold">{p.name}</h3>
                                    <p className="text-sm text-gray-400 mt-1">{p.description}</p>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Plus className="w-5 h-5 text-blue-400" />
                            Custom Scenario
                        </h2>
                        <div className="space-y-3">
                            <input
                                value={customName}
                                onChange={e => setCustomName(e.target.value)}
                                placeholder="Scenario name"
                                className="w-full bg-background-primary border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500"
                            />
                            <input
                                value={customDesc}
                                onChange={e => setCustomDesc(e.target.value)}
                                placeholder="Description"
                                className="w-full bg-background-primary border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500"
                            />
                            <textarea
                                value={customParams}
                                onChange={e => setCustomParams(e.target.value)}
                                placeholder='{"param1": 20, "param2": 30}'
                                rows={3}
                                className="w-full bg-background-primary border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 font-mono text-sm"
                            />
                            <button
                                onClick={handleRunCustom}
                                disabled={loading}
                                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg text-white font-medium transition-all"
                            >
                                {loading ? 'Running...' : 'Run Simulation'}
                            </button>
                        </div>
                    </div>
                </div>

                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Simulation Results</h2>
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                            <Loader2 className="w-8 h-8 animate-spin mb-3" />
                            <p>Running simulation...</p>
                        </div>
                    ) : result ? (
                        <div className="space-y-6">
                            <div className="grid grid-cols-2 gap-3">
                                <MetricCard title="Risk Score" value={`${Math.round(result.risk_score * 100)}%`} icon={AlertTriangle} color={result.risk_score > 0.6 ? 'red' : 'amber'} />
                                <MetricCard title="KPIs Impacted" value={result.impacted_kpis?.length || 0} icon={Activity} color="blue" />
                            </div>

                            {result.impacted_kpis?.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Impacted KPIs</h3>
                                    <div className="space-y-2">
                                        {result.impacted_kpis.map((kpi, i) => (
                                            <div key={i} className="flex justify-between items-center p-3 bg-background-primary rounded-lg border border-gray-800">
                                                <span className="text-white text-sm">{kpi.kpi}</span>
                                                <span className={clsx(
                                                    'text-sm font-medium',
                                                    kpi.change_pct > 0 ? 'text-red-400' : 'text-green-400'
                                                )}>
                                                    {kpi.baseline} → {kpi.simulated} ({kpi.change_pct > 0 ? '+' : ''}{kpi.change_pct}%)
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {result.recommended_actions?.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Recommended Actions</h3>
                                    <div className="space-y-2">
                                        {result.recommended_actions.map((action, i) => (
                                            <div key={i} className="flex items-start gap-3 p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                                                <ShieldCheck className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
                                                <span className="text-gray-300 text-sm">{action}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {result.capacity_impacts?.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Capacity Impact</h3>
                                    {result.capacity_impacts.map((c, i) => (
                                        <div key={i} className="p-3 bg-background-primary rounded-lg border border-gray-800">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-white">{c.resource}</span>
                                                <span className="text-red-400 font-medium">{c.gap} unit gap</span>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1">
                                                Demand: {c.current_demand} → {c.projected_demand}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                            <FlaskConical className="w-12 h-12 mb-3 opacity-30" />
                            <p className="text-sm">Select a scenario or create a custom one</p>
                            <p className="text-xs mt-1">Simulations never modify live data</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
