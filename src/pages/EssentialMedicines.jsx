import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Pill, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

export default function EssentialMedicines() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.medicines.getInventory();
        setInventory(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="p-6 text-white">Loading inventory data...</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Essential Medicines Stock Risk</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {inventory.map((item, idx) => {
          const stockPercent = (item.stock_current / item.stock_max) * 100;
          const daysLeft = Math.round(item.stock_current / item.consumption_rate);
          const isLow = stockPercent < 20;

          return (
            <div key={idx} className="bg-background-secondary rounded-xl border border-gray-800 p-5">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-white text-lg">{item.medicine_name}</h3>
                  <p className="text-xs text-gray-400">{item.facility_id}</p>
                </div>
                <div className={clsx("p-2 rounded-lg", isLow ? "bg-red-500/10 text-red-500" : "bg-blue-500/10 text-blue-500")}>
                  <Pill className="w-5 h-5" />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Stock Level</span>
                    <span className={clsx("font-medium", isLow ? "text-red-400" : "text-white")}>
                      {item.stock_current} / {item.stock_max}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                    <div 
                      className={clsx("h-full", isLow ? "bg-red-500" : "bg-blue-500")} 
                      style={{ width: `${stockPercent}%` }}
                    ></div>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-background-primary rounded-lg border border-gray-800">
                  {isLow ? <AlertTriangle className="w-5 h-5 text-red-500" /> : <div className="w-5 h-5" />}
                  <div>
                    <p className="text-xs text-gray-500">Days to Stockout</p>
                    <p className={clsx("font-bold", isLow ? "text-red-400" : "text-white")}>
                      {daysLeft} Days
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
