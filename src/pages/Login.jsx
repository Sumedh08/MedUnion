import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, User, Truck, Building2 } from 'lucide-react';
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

        // MVP/Demo Mode: Bypass Backend Auth
        setTimeout(() => {
            localStorage.setItem('token', 'demo_token_mvp_123');
            localStorage.setItem('role', username.includes('dean') ? 'facility' : username.includes('108') ? 'logistics' : 'admin');
            navigate('/dashboard');
            setLoading(false);
        }, 800);
    };

    const demoAccounts = [
        { role: 'National Admin', user: 'tn_health_sec', pass: 'admin123', icon: User, desc: 'Full System AI View' },
        { role: 'Facility (Dean)', user: 'rgggh_dean', pass: 'hospital123', icon: Building2, desc: 'Manage RGGGH' },
        { role: 'Logistics (108)', user: '108_dispatch', pass: 'ambulance123', icon: Truck, desc: 'Route Optimization' },
    ];

    return (
        <div className="min-h-screen bg-background-primary flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Glow */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[100px]"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[100px]"></div>

            <div className="w-full max-w-4xl bg-background-secondary/80 backdrop-blur-xl border border-gray-800 rounded-2xl shadow-2xl flex flex-col md:flex-row overflow-hidden relative z-10">

                {/* Left Side: Form */}
                <div className="md:w-1/2 p-8 md:p-12 border-b md:border-b-0 md:border-r border-gray-800">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-500">
                            <ShieldCheck className="w-6 h-6" />
                        </div>
                        <h1 className="text-2xl font-bold text-white tracking-tight">TN Health Grid</h1>
                    </div>

                    <h2 className="text-xl font-semibold text-white mb-2">Welcome Back</h2>
                    <p className="text-gray-400 text-sm mb-8">Enter your credentials to access the intelligence platform.</p>

                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-background-tertiary border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                                placeholder="e.g. tn_health_sec"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-background-tertiary border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                                placeholder="••••••••"
                            />
                        </div>

                        {error && <p className="text-red-500 text-xs font-medium">{error}</p>}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Authenticating...' : 'Sign In'}
                        </button>
                    </form>
                </div>

                {/* Right Side: Demo Helper */}
                <div className="md:w-1/2 p-8 md:p-12 bg-background-tertiary/50">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6">Select a Role to Demo</h3>
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
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
