import clsx from 'clsx';
import { AlertTriangle, CheckCircle, AlertOctagon } from 'lucide-react';

const riskConfig = {
    GREEN: { color: 'text-risk-green', bg: 'bg-risk-green/10', border: 'border-risk-green/20', icon: CheckCircle, label: 'Low Risk' },
    AMBER: { color: 'text-risk-amber', bg: 'bg-risk-amber/10', border: 'border-risk-amber/20', icon: AlertTriangle, label: 'Medium Risk' },
    RED: { color: 'text-risk-red', bg: 'bg-risk-red/10', border: 'border-risk-red/20', icon: AlertOctagon, label: 'High Risk' },
    CRITICAL: { color: 'text-risk-critical', bg: 'bg-risk-critical/10', border: 'border-risk-critical/20', icon: AlertOctagon, label: 'Critical' },
};

export default function RiskCard({ facility, type }) {
    const risk = facility.risk_score?.level || 'GREEN';
    const config = riskConfig[risk];
    const Icon = config.icon;

    return (
        <div className={clsx("p-4 rounded-xl border transition-all cursor-pointer hover:bg-background-tertiary",
            "bg-background-secondary border-gray-800",
            risk !== 'GREEN' && config.border
        )}>
            <div className="flex justify-between items-start">
                <div>
                    <h4 className="font-semibold text-white">{facility.name}</h4>
                    <p className="text-xs text-gray-400 mt-1">ID: {facility.id}</p>
                </div>
                <div className={clsx("px-2 py-1 rounded text-xs font-bold flex items-center gap-1", config.bg, config.color)}>
                    <Icon className="w-3 h-3" />
                    {config.label}
                </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                <div>
                    <span className="text-gray-500 text-xs block">Last Updated</span>
                    <span className="text-gray-300">{new Date(facility.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <div>
                    <span className="text-gray-500 text-xs block">Active Alerts</span>
                    <span className={clsx("font-medium", facility.active_alerts > 0 ? "text-white" : "text-gray-300")}>{facility.active_alerts}</span>
                </div>
            </div>

            {facility.recommendations && facility.recommendations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-800">
                    <p className="text-xs text-blue-400 font-medium">
                        {facility.recommendations.length} Action(s) Recommended
                    </p>
                </div>
            )}
        </div>
    );
}
