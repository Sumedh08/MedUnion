import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea } from 'recharts';

export default function TimeSeriesChart({ data, xKey, yKey, color = "#3b82f6", thresholdMin, thresholdMax, height = 300 }) {
    if (!data || data.length === 0) return <div className="h-[300px] flex items-center justify-center text-gray-500">No Data Available</div>;

    return (
        <div style={{ width: '100%', height: height }}>
            <ResponsiveContainer>
                <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                    <XAxis
                        dataKey={xKey}
                        stroke="#9ca3af"
                        tick={{ fill: '#9ca3af' }}
                        tickFormatter={(time) => new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    />
                    <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} domain={['auto', 'auto']} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#f9fafb' }}
                        labelFormatter={(label) => new Date(label).toLocaleString()}
                    />

                    {thresholdMin !== undefined && thresholdMax !== undefined && (
                        <ReferenceArea y1={thresholdMin} y2={thresholdMax} fill="#10b981" fillOpacity={0.1} />
                    )}

                    <Line
                        type="monotone"
                        dataKey={yKey}
                        stroke={color}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 6 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
