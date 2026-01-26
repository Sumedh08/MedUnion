import clsx from 'clsx';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function MetricCard({ title, value, trend, trendValue, icon: Icon, color = "blue" }) {
    const trendColor = trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-500';
    const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;

    return (
        <div className="bg-background-secondary p-5 rounded-xl border border-gray-800 hover:border-gray-700 transition-colors">
            <div className="flex justify-between items-start mb-4">
                <div className={clsx("p-2 rounded-lg", `bg-${color}-500/10 text-${color}-500`)}>
                    {Icon && <Icon className="w-5 h-5" />}
                </div>
                {trend && (
                    <div className={clsx("flex items-center gap-1 text-xs font-medium", trendColor)}>
                        <TrendIcon className="w-3 h-3" />
                        <span>{trendValue}</span>
                    </div>
                )}
            </div>
            <div>
                <p className="text-gray-400 text-sm font-medium">{title}</p>
                <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
            </div>
        </div>
    );
}
