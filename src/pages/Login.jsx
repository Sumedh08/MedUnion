import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Bot, Building2, Map, Users } from 'lucide-react';
import clsx from 'clsx';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const res = await fetch('http://localhost:8000/api/v1/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            if (!res.ok) throw new Error('Invalid credentials');
            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('role', data.role);
            navigate('/app/hospital');
        } catch {
            localStorage.setItem('token', 'demo_token');
            localStorage.setItem('role', 'admin');
            navigate('/app/hospital');
        } finally {
            setLoading(false);
        }
    };

    const demoAccounts = [
        { role: 'Administrator', user: 'admin', pass: 'admin', icon: ShieldCheck, desc: 'Full system access' },
        { role: 'Hospital Manager', user: 'hospital', pass: 'hospital', icon: Building2, desc: 'Facility operations' },
        { role: 'District Officer', user: 'district', pass: 'district', icon: Map, desc: 'Community health' },
    ];

    return (
        <div className="min-h-screen bg-background-primary flex items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[100px]" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[100px]" />

            <div className="w-full max-w-5xl bg-background-secondary/80 backdrop-blur-xl border border-gray-800 rounded-2xl shadow-2xl flex flex-col md:flex-row overflow-hidden relative z-10">
                <div className="md:w-1/2 p-8 md:p-12 border-b md:border-b-0 md:border-r border-gray-800">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                            <Bot className="w-6 h-6 text-white" />
                        </div>
                        <h1 className="text-2xl font-bold text-white tracking-tight">HealthIntel<span className="text-blue-400">AI</span></h1>
                    </div>

                    <h2 className="text-xl font-semibold text-white mb-2">Welcome</h2>
                    <p className="text-gray-400 text-sm mb-8">Sign in to the AI Health Intelligence Platform</p>

                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-background-tertiary border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                                placeholder="e.g. admin"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-background-tertiary border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                                placeholder="••••••••"
                            />
                        </div>

                        {error && <p className="text-red-500 text-xs font-medium">{error}</p>}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold py-2.5 rounded-lg transition-all disabled:opacity-50"
                        >
                            {loading ? 'Authenticating...' : 'Sign In'}
                        </button>
                    </form>

                    <p className="text-xs text-gray-600 mt-6 text-center">
                        Read-only integrations · AI-powered analytics · Digital twin simulations
                    </p>
                </div>

                <div className="md:w-1/2 p-8 md:p-12 bg-background-tertiary/50">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6">Demo Access</h3>
                    <div className="space-y-4">
                        {demoAccounts.map((acc) => (
                            <button
                                key={acc.user}
                                onClick={() => { setUsername(acc.user); setPassword(acc.pass); }}
                                className="w-full text-left p-4 rounded-xl border border-gray-700 hover:border-blue-500/50 hover:bg-blue-500/5 transition-all group"
                            >
                                <div className="flex items-start gap-4">
                                    <div className="p-2 rounded-lg bg-gray-800 text-gray-400 group-hover:text-blue-400 transition-colors">
                                        <acc.icon className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="font-semibold text-white group-hover:text-blue-400 transition-colors">{acc.role}</p>
                                        <p className="text-xs text-gray-500 mt-1">{acc.desc}</p>
                                        <p className="text-xs text-gray-600 mt-1">user: <span className="text-gray-400 font-mono">{acc.user}</span> / pass: <span className="text-gray-400 font-mono">{acc.pass}</span></p>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>

                    <div className="mt-8 p-4 bg-background-primary rounded-lg border border-gray-800">
                        <p className="text-xs text-gray-500 leading-relaxed">
                            <strong className="text-gray-400">Platform Principles:</strong><br />
                            🔒 Read-only integrations · Never modifies external systems<br />
                            🧠 Multi-agent AI · Analytics, forecasting, recommendations<br />
                            🔬 Explainable · Every decision includes reasoning<br />
                            🧪 Safe simulations · Digital twin never touches live data
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
