export default function RiskGauge({ value, size = 120 }) {
    // Value 0-100
    const radius = size / 2;
    const stroke = 8;
    const normalizedRadius = radius - stroke * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (value / 100) * circumference;

    let color = '#10b981'; // Green
    if (value > 40) color = '#f59e0b'; // Amber
    if (value > 60) color = '#ef4444'; // Red
    if (value > 80) color = '#dc2626'; // Critical

    return (
        <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
            <svg height={size} width={size} className="transform -rotate-90">
                <circle
                    stroke="#374151"
                    strokeWidth={stroke}
                    fill="transparent"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
                <circle
                    stroke={color}
                    strokeWidth={stroke}
                    strokeDasharray={circumference + ' ' + circumference}
                    style={{ strokeDashoffset }}
                    strokeLinecap="round"
                    fill="transparent"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                    className="transition-all duration-1000 ease-out"
                />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-white">
                <span className="text-2xl font-bold">{Math.round(value)}%</span>
                <span className="text-xs text-gray-400">RISK</span>
            </div>
        </div>
    );
}
