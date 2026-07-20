import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import DataSourceBadge from '../../components/badge/DataSourceBadge';
import { Pill, AlertTriangle, Clock } from 'lucide-react';
import clsx from 'clsx';

export default function HospitalInventory() {
    const [hospitals, setHospitals] = useState([]);
    const [selected, setSelected] = useState(null);
    const [inventory, setInventory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.hospital.list()
            .then(data => {
                setHospitals(data || []);
                if (data?.length) {
                    setSelected(data[0].id);
                }
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        if (!selected) return;
        api.hospital.inventory(selected).then(setInventory).catch(() => setInventory([]));
    }, [selected]);

    if (loading) return <div className="p-6 text-white animate-pulse">Loading inventory...</div>;

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Medicine Inventory</h1>
                    <p className="text-gray-400 text-sm mt-1">Stock levels and reorder alerts</p>
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

            {inventory.length === 0 && (
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-8 text-center">
                    <p className="text-gray-500">No inventory data available for this facility</p>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {inventory.map((item, i) => {
                    const pct = item.stock_max ? Math.min((item.stock_current / item.stock_max) * 100, 100) : 0;
                    const critical = pct < 15;
                    const warning = pct < 30;
                    return (
                        <div key={i} className="bg-background-secondary rounded-xl border border-gray-800 p-5 hover:border-gray-700 transition-all">
                            <div className="flex justify-between items-start mb-3">
                                <div>
                                    <h3 className="font-semibold text-white">{item.medicine_name}</h3>
                                    <p className="text-xs text-gray-500">{item.unit || ''}</p>
                                </div>
                                <div className={clsx('p-2 rounded-lg', critical ? 'bg-red-500/10' : warning ? 'bg-amber-500/10' : 'bg-blue-500/10')}>
                                    <Pill className={clsx('w-5 h-5', critical ? 'text-red-500' : warning ? 'text-amber-500' : 'text-blue-500')} />
                                </div>
                            </div>

                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400">Stock</span>
                                        <span className={clsx('font-medium', critical ? 'text-red-400' : 'text-white')}>
                                            {item.stock_current} / {item.stock_max}
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                        <div
                                            className={clsx('h-full transition-all', critical ? 'bg-red-500' : warning ? 'bg-amber-500' : 'bg-blue-500')}
                                            style={{ width: `${pct}%` }}
                                        />
                                    </div>
                                </div>

                                <div className="flex items-center gap-2 p-3 bg-background-primary rounded-lg border border-gray-800">
                                    {critical ? <AlertTriangle className="w-5 h-5 text-red-500" /> : <Clock className="w-5 h-5 text-gray-500" />}
                                    <div>
                                        <p className="text-xs text-gray-500">Days to Stockout</p>
                                        <p className={clsx('font-bold', critical ? 'text-red-400' : 'text-white')}>
                                            {item.days_until_stockout?.toFixed(0) || 'N/A'} Days
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
