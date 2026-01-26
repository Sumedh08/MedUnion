import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard,
    ThermometerSnowflake,
    Pill,
    Droplet,
    Ambulance,
    BellRing,
    Settings
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/dashboard/vaccines', label: 'Vaccine Cold-Chain', icon: ThermometerSnowflake },
    { to: '/dashboard/medicines', label: 'Essential Medicines', icon: Pill },
    { to: '/dashboard/blood', label: 'Blood & Organ', icon: Droplet },
    { to: '/dashboard/ambulance', label: 'Ambulance', icon: Ambulance },
    { to: '/dashboard/alerts', label: 'Alert Center', icon: BellRing },
    { to: '/dashboard/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
    return (
        <aside className="w-64 bg-background-secondary border-r border-gray-800 flex flex-col">
            <div className="h-16 flex items-center px-6 border-b border-gray-800">
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
                    TN Health<span className="font-light text-white ml-2">Grid</span>
                </h1>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) => clsx(
                            'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                            'hover:bg-background-tertiary text-gray-400 hover:text-white',
                            isActive && 'bg-blue-600/10 text-blue-400 border border-blue-600/20 shadow-sm'
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium text-sm">{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-gray-800">
                <div className="bg-gray-800/50 rounded-lg p-3">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold ring-2 ring-blue-400/30">
                            TS
                        </div>
                        <div>
                            <p className="text-sm font-medium text-white">Dr. T.S. Selvavinayagam</p>
                            <p className="text-xs text-gray-500">Director, Public Health (TN)</p>
                        </div>
                    </div>
                </div>
            </div>
        </aside>
    )
}
