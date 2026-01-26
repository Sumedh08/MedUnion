import clsx from 'clsx';

export default function AlertBadge({ severity, count }) {
    if (!count || count === 0) return null;

    const colors = {
        RED: 'bg-risk-red text-white',
        AMBER: 'bg-risk-amber text-black',
        GREEN: 'bg-risk-green text-white',
    };

    return (
        <span className={clsx("px-2 py-0.5 rounded-full text-xs font-bold", colors[severity] || 'bg-gray-500')}>
            {count}
        </span>
    );
}
