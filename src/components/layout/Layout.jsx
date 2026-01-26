import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout() {
    return (
        <div className="flex h-screen w-full bg-background-primary overflow-hidden">
            <Sidebar />
            <div className="flex flex-col flex-1 min-h-0">
                <Header />
                <main className="flex-1 overflow-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}
