import { useState, useEffect } from 'react'
import { api } from '../../services/api'

const BADGE_CONFIG = {
    live_readonly: {
        icon: '🟢',
        label: 'Live Read-Only',
        color: 'text-green-400',
        bg: 'bg-green-500/10',
        border: 'border-green-500/20',
    },
    cached_snapshot: {
        icon: '🟡',
        label: 'Cached Snapshot',
        color: 'text-yellow-400',
        bg: 'bg-yellow-500/10',
        border: 'border-yellow-500/20',
    },
    synthetic_simulation: {
        icon: '🔵',
        label: 'Synthetic Simulation',
        color: 'text-blue-400',
        bg: 'bg-blue-500/10',
        border: 'border-blue-500/20',
    },
};

export default function DataSourceBadge({ workspace, type, size = 'sm' }) {
    const [badgeType, setBadgeType] = useState(type || 'synthetic_simulation');
    const [label, setLabel] = useState('Loading...');

    useEffect(() => {
        if (type) {
            setBadgeType(type);
            return;
        }
        if (!workspace) return;
        api.workspace.dataSource(workspace).then(data => {
            setBadgeType(data.type || 'synthetic_simulation');
            setLabel(data.label || 'Synthetic Simulation');
        }).catch(() => {
            setBadgeType('synthetic_simulation');
        });
    }, [workspace, type]);

    const config = BADGE_CONFIG[badgeType] || BADGE_CONFIG.synthetic_simulation;
    const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';
    const displayLabel = label !== 'Loading...' ? label : config.label;

    return (
        <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizeClasses} ${config.color} ${config.bg} ${config.border}`}>
            <span>{config.icon}</span>
            <span>{displayLabel}</span>
        </span>
    );
}