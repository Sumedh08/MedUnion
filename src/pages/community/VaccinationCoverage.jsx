import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import MetricCard from '../../components/common/MetricCard';
import { Activity, ShieldCheck, AlertTriangle, TrendingUp } from 'lucide-react';
import clsx from 'clsx';

export default function VaccinationCoverage() {
    const [districts, setDistricts] = useState([]);
    const [vaxSummary, setVaxSummary] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            api.community.districts(),
            api.community.vaccinations(),
        ])
            .then(([dData, vData]) => {
                setDistricts(dData || []);
                setVaxSummary(vData || {});
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-6 text-white animate-pulse">Loading vaccination data...</div>;

    const vaccines = vaxSummary.by_vaccine ? Object.entries(vaxSummary.by_vaccine) : [];
    const avgCoverage = vaccines.length ? Math.round(vaccines.reduce((s, [, v]) => s + v.avg_coverage, 0) / vaccines.length) : 0;
    const belowTarget = vaccines.filter(([, v]) => v.avg_coverage < 90).length;

    const districtCoverage = districts.map(d => ({
        name: d.name,
        coverage: d.avg_vaccination_coverage || 0,
        cases: d.total_confirmed_cases || 0,
    }));

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Vaccination Coverage</h1>
                    <p className="text-gray-400 text-sm mt-1">District-level immunization tracking</p>
                </div>
                <DataSourceBadge workspace="community" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard title="Avg Coverage" value={`${avgCoverage}%`} icon={Activity} color={avgCoverage >= 90 ? 'green' : 'amber'} />
                <MetricCard title="Vaccine Types" value={vaccines.length} icon={ShieldCheck} color="blue" />
                <MetricCard title="Below Target (90%)" value={belowTarget} icon={AlertTriangle} color={belowTarget > 2 ? 'red' : 'amber'} />
                <MetricCard title="Districts" value={districts.length} icon={TrendingUp} color="blue" />
            </div>

            {vaccines.length > 0 && (
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Vaccine Coverage Details</h2>
                    <div className="space-y-3">
                        {vaccines.sort((a, b) => a[1].avg_coverage - b[1].avg_coverage).map(([name, data], i) => {
                            const color = data.avg_coverage >= 90 ? 'bg-green-500' : data.avg_coverage >= 70 ? 'bg-amber-500' : 'bg-red-500';
                            return (
                                <div key={i} className="flex items-center gap-4 p-3 bg-background-primary rounded-lg border border-gray-800">
                                    <span className="text-white font-medium w-32 text-sm">{name}</span>
                                    <div className="flex-1 bg-gray-700 h-3 rounded-full overflow-hidden">
                                        <div className={`h-full ${color} transition-all`} style={{ width: `${data.avg_coverage}%` }} />
                                    </div>
                                    <span className={clsx('text-sm font-medium w-16 text-right', data.avg_coverage >= 90 ? 'text-green-400' : data.avg_coverage >= 70 ? 'text-amber-400' : 'text-red-400')}>
                                        {data.avg_coverage}%
                                    </span>
                                    <span className="text-gray-500 text-xs w-28 text-right">{data.total_doses?.toLocaleString()} doses</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">District Coverage</h2>
                <div className="space-y-3">
                    {districtCoverage.sort((a, b) => a.coverage - b.coverage).map((d, i) => {
                        const color = d.coverage >= 90 ? 'bg-green-500' : d.coverage >= 70 ? 'bg-amber-500' : 'bg-red-500';
                        return (
                            <div key={i} className="flex items-center gap-4 p-3 bg-background-primary rounded-lg border border-gray-800">
                                <span className="text-white font-medium w-32 text-sm">{d.name}</span>
                                <div className="flex-1 bg-gray-700 h-3 rounded-full overflow-hidden">
                                    <div className={`h-full ${color} transition-all`} style={{ width: `${d.coverage}%` }} />
                                </div>
                                <span className={clsx('text-sm font-medium w-16 text-right', d.coverage >= 90 ? 'text-green-400' : d.coverage >= 70 ? 'text-amber-400' : 'text-red-400')}>
                                    {d.coverage}%
                                </span>
                                <span className="text-gray-500 text-xs w-24 text-right">{d.cases} cases</span>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
