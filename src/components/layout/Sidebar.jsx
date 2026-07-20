import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Building2,
    Map,
    Activity,
    Bot,
    FlaskConical,
    Settings,
    LogOut,
    ChevronLeft,
    ChevronRight,
    Users,
    Pill,
    AlertTriangle,
    Ambulance,
} from 'lucide-react';
import clsx from 'clsx';

const hospitalNav = [
    { to: '/app/hospital', label: 'Overview', icon: LayoutDashboard },
    { to: '/app/hospital/occupancy', label: 'Bed Occupancy', icon: Activity },
    { to: '/app/hospital/admissions', label: 'Patient Flow', icon: Users },
    { to: '/app/hospital/inventory', label: 'Medicine Inventory', icon: Pill },
];

const communityNav = [
    { to: '/app/community', label: 'Overview', icon: Map },
    { to: '/app/community/diseases', label: 'Disease Surveillance', icon: AlertTriangle },
    { to: '/app/community/vaccinations', label: 'Vaccination Coverage', icon: Activity },
];

const systemNav = [
    { to: '/app/copilot', label: 'AI Copilot', icon: Bot },
    { to: '/app/simulation', label: 'Digital Twin', icon: FlaskConical },
    { to: '/app/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        navigate('/');
    };

    const NavSection = ({ title, items }) => (
        <div className="mb-4">
            {!collapsed && (
                <p className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    {title}
                </p>
            )}
            <div className="space-y-1">
                {items.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                            clsx(
                                'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all',
                                'hover:bg-background-tertiary text-gray-400 hover:text-white',
                                isActive && 'bg-blue-600/15 text-blue-400 border border-blue-600/20',
                                collapsed && 'justify-center px-2'
                            )
                        }
                        title={collapsed ? item.label : undefined}
                    >
                        <item.icon className="w-5 h-5 shrink-0" />
                        {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
                    </NavLink>
                ))}
            </div>
        </div>
    );

    return (
        <aside
            className={clsx(
                'bg-background-secondary border-r border-gray-800 flex flex-col transition-all duration-300',
                collapsed ? 'w-16' : 'w-64'
            )}
        >
            <div className="h-16 flex items-center px-4 border-b border-gray-800 justify-between">
                {!collapsed && (
                    <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent truncate">
                        HealthIntel<span className="font-light text-white ml-1">AI</span>
                    </h1>
                )}
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="p-1.5 text-gray-500 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                >
                    {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                </button>
            </div>

            <nav className="flex-1 p-3 overflow-y-auto">
                <NavSection title="HOSPITAL OPS" items={hospitalNav} />
                <NavSection title="COMMUNITY" items={communityNav} />
                <NavSection title="SYSTEM" items={systemNav} />
            </nav>

            <div className="p-3 border-t border-gray-800">
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all"
                >
                    <LogOut className="w-5 h-5" />
                    {!collapsed && <span className="text-sm font-medium">Sign Out</span>}
                </button>
            </div>
        </aside>
    );
}
