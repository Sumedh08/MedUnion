import { useLocation } from 'react-router-dom'
import { Bell, Activity } from 'lucide-react'

const pageTitles = {
    '/app/hospital': 'Hospital Operations Intelligence',
    '/app/hospital/occupancy': 'Bed Occupancy',
    '/app/hospital/admissions': 'Patient Flow',
    '/app/hospital/inventory': 'Medicine Inventory',
    '/app/community': 'Community Health Intelligence',
    '/app/community/diseases': 'Disease Surveillance',
    '/app/community/vaccinations': 'Vaccination Coverage',
    '/app/copilot': 'AI Health Copilot',
    '/app/simulation': 'Digital Twin Simulator',
    '/app/settings': 'System Configuration',
}

export default function Header() {
    const location = useLocation()
    const title = pageTitles[location.pathname] || 'AI Health Intelligence Platform'

    return (
        <header className="h-16 bg-background-secondary border-b border-gray-800 flex items-center justify-between px-6">
            <h2 className="text-lg font-semibold text-white">{title}</h2>

            <div className="flex items-center gap-4">
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full">
                    <Activity className="w-4 h-4 text-green-500" />
                    <span className="text-xs font-medium text-green-500">All Systems Nominal</span>
                </div>

                <div className="h-8 w-px bg-gray-700 mx-2"></div>

                <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-full transition-colors relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full indicator"></span>
                </button>
            </div>
        </header>
    )
}
