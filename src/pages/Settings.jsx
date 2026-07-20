import { useEffect, useState } from 'react';
import { api } from '../services/api';
import DataSourceBadge from '../components/badge/DataSourceBadge';
import { Settings as SettingsIcon, Shield, Database, Bot, Link, Activity } from 'lucide-react';

export default function Settings() {
    const [connectors, setConnectors] = useState({});
    const [activeTab, setActiveTab] = useState('connectors');

    useEffect(() => {
        api.health.connectors().then(setConnectors).catch(() => {});
    }, []);

    const tabs = [
        { id: 'connectors', label: 'Connectors', icon: Link },
        { id: 'security', label: 'Security', icon: Shield },
        { id: 'data', label: 'Data Sources', icon: Database },
        { id: 'agents', label: 'AI Agents', icon: Bot },
    ];

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">System Configuration</h1>
                    <p className="text-gray-400 text-sm mt-1">Manage connectors, security, and AI agents</p>
                </div>
                <DataSourceBadge workspace="hospital" />
            </div>

            <div className="flex gap-2 border-b border-gray-800 pb-2">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                            activeTab === tab.id
                                ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20'
                                : 'text-gray-400 hover:text-white'
                        }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {activeTab === 'connectors' && (
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Read-Only Connectors</h2>
                    <div className="space-y-4">
                        {Object.keys(connectors).length === 0 ? (
                            <>
                                {['Synthetic (Active)', 'FHIR (Not Configured)', 'DHIS2 (Not Configured)', 'OpenMRS (Not Configured)'].map((name, i) => (
                                    <div key={i} className="flex items-center justify-between p-4 bg-background-primary rounded-lg border border-gray-800">
                                        <div className="flex items-center gap-3">
                                            <div className={`w-2 h-2 rounded-full ${i === 0 ? 'bg-green-500' : 'bg-gray-600'}`} />
                                            <span className="text-white font-medium">{name}</span>
                                        </div>
                                        <span className={`text-xs px-2 py-1 rounded-full ${i === 0 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
                                            {i === 0 ? 'Connected' : 'Not Configured'}
                                        </span>
                                    </div>
                                ))}
                            </>
                        ) : (
                            Object.entries(connectors).map(([name, status]) => (
                                <div key={name} className="flex items-center justify-between p-4 bg-background-primary rounded-lg border border-gray-800">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${status?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                                        <span className="text-white font-medium capitalize">{name}</span>
                                    </div>
                                    <span className="text-xs text-gray-400">{status?.mode || 'Unknown'}</span>
                                </div>
                            ))
                        )}
                        <p className="text-xs text-gray-500 mt-4 flex items-center gap-2">
                            <Shield className="w-4 h-4 text-green-400" />
                            All connectors enforce read-only mode. POST/PUT/PATCH/DELETE operations are forbidden.
                        </p>
                    </div>
                </div>
            )}

            {activeTab === 'security' && (
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Role-Based Access Control</h2>
                    <div className="space-y-3">
                        {[
                            { role: 'Admin', permissions: 'Full access: read, write, simulate, admin' },
                            { role: 'Hospital Manager', permissions: 'Read facility data, run simulations' },
                            { role: 'District Officer', permissions: 'Read district data, run simulations' },
                            { role: 'Analyst', permissions: 'Read-only access to all data' },
                            { role: 'Viewer', permissions: 'Read public dashboards only' },
                        ].map((r, i) => (
                            <div key={i} className="flex items-center justify-between p-4 bg-background-primary rounded-lg border border-gray-800">
                                <div>
                                    <span className="text-white font-medium">{r.role}</span>
                                    <p className="text-xs text-gray-500 mt-1">{r.permissions}</p>
                                </div>
                                <Shield className="w-5 h-5 text-gray-600" />
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {activeTab === 'data' && (
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Data Source Indicators</h2>
                    <div className="space-y-4">
                        <div className="flex items-center gap-4 p-4 bg-background-primary rounded-lg border border-gray-800">
                            <span className="text-2xl">🟢</span>
                            <div>
                                <p className="text-white font-medium">Live Read-only</p>
                                <p className="text-xs text-gray-500">Real-time data from connected healthcare systems via read-only APIs</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4 p-4 bg-background-primary rounded-lg border border-gray-800">
                            <span className="text-2xl">🟡</span>
                            <div>
                                <p className="text-white font-medium">Cached Snapshot</p>
                                <p className="text-xs text-gray-500">Data from periodic syncs, may be up to 24 hours old</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4 p-4 bg-background-primary rounded-lg border border-gray-800">
                            <span className="text-2xl">🔵</span>
                            <div>
                                <p className="text-white font-medium">Synthetic Simulation</p>
                                <p className="text-xs text-gray-500">AI-generated data for demo, testing, or what-if scenarios</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'agents' && (
                <div className="bg-background-secondary rounded-xl border border-gray-800 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">AI Agent Pipeline</h2>
                    <div className="space-y-3">
                        {[
                            { name: 'Data Retrieval', status: 'Active', desc: 'Fetches and indexes healthcare data' },
                            { name: 'Analytics', status: 'Active', desc: 'Computes KPIs, detects anomalies, trend analysis' },
                            { name: 'Forecasting', status: 'Active', desc: 'Predicts occupancy, demand, disease spread' },
                            { name: 'Recommendation', status: 'Active', desc: 'Suggests resource redistribution and actions' },
                            { name: 'Explainability', status: 'Active', desc: 'Provides reasoning for every recommendation' },
                            { name: 'Copilot', status: 'Active', desc: 'Natural language interface for all capabilities' },
                        ].map((agent, i) => (
                            <div key={i} className="flex items-center justify-between p-4 bg-background-primary rounded-lg border border-gray-800">
                                <div className="flex items-center gap-3">
                                    <Bot className="w-5 h-5 text-blue-400" />
                                    <div>
                                        <span className="text-white font-medium">{agent.name}</span>
                                        <p className="text-xs text-gray-500">{agent.desc}</p>
                                    </div>
                                </div>
                                <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">Active</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
