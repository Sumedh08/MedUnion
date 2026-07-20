import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import MetricCard from '../../components/common/MetricCard';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import { Activity, TrendingUp, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

export default function DiseaseSurveillance() {
    const [districts, setDistricts] = useState([]);
    const [reports, setReports] = useState([]);
    const [selectedDisease, setSelectedDisease] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            api.community.districts(),
            api.community.diseaseReports(),
        ])
            .then(([dData, rData]) => {
                setDistricts(dData || []);
                setReports(rData || []);
                const diseases = [...new Set((rData || []).map(r => r.disease))];
                if (diseases.length) setSelectedDisease(diseases[0]);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-6 text-white animate-pulse">Loading disease data...</div>;

    const diseases = [...new Set(reports.map(r => r.disease))];
    const filtered = selectedDisease ? reports.filter(r => r.disease === selectedDisease) : [];
    const totalCases = filtered.reduce((s, r) => s + (r.confirmed_cases || 0), 0);
    const districtsMap = Object.fromEntries(districts.map(d => [d.id, d.name]));

    const byDistrict = {};
    for (const r of filtered) {
        const did = r.district_id;
        if (!byDistrict[did]) byDistrict[did] = { cases: 0, deaths: 0, suspected: 0 };
        byDistrict[did].cases += r.confirmed_cases || 0;
        byDistrict[did].deaths += r.deaths || 0;
        byDistrict[did].suspected += r.suspected_cases || 0;
    }

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Disease Surveillance</h1>
                    <p className="text-gray-400 text-sm mt-1">Track disease incidence across districts</p>
                </div>
                <DataSourceBadge workspace="community" />
            </div>

            <div className="flex gap-2 flex-wrap">
                {diseases.map(d => (
                    <button
                        key={d}
                        onClick={() => setSelectedDisease(d)}
                        className={clsx(
                            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                            selectedDisease === d
                                ? 'bg-red-600 text-white'
                                : 'bg-background-tertiary text-gray-400 hover:text-white'
                        )}
                    >
                        {d}
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard title={`${selectedDisease || ''} Total Cases`} value={totalCases} icon={Activity} color="red" />
                <MetricCard title="Affected Districts" value={Object.keys(byDistrict).length} icon={TrendingUp} color="amber" />
                <MetricCard title="Total Deaths" value={filtered.reduce((s, r) => s + (r.deaths || 0), 0)} icon={AlertTriangle} color="red" />
            </div>

            <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">District Breakdown</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(byDistrict).sort((a, b) => b[1].cases - a[1].cases).map(([did, data], i) => (
                        <div key={did} className="flex items-center justify-between p-4 bg-background-primary rounded-lg border border-gray-800">
                            <div className="flex items-center gap-3">
                                <span className={clsx(
                                    'w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold',
                                    data.cases > 100 ? 'bg-red-500/20 text-red-400' :
                                        data.cases > 50 ? 'bg-amber-500/20 text-amber-400' :
                                            'bg-green-500/20 text-green-400'
                                )}>
                                    {i + 1}
                                </span>
                                <div>
                                    <p className="text-white font-medium">{districtsMap[did] || did}</p>
                                    <p className="text-xs text-gray-500">{data.cases} cases, {data.deaths} deaths</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
