import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import VaccineColdChain from './pages/VaccineColdChain'
import EssentialMedicines from './pages/EssentialMedicines'
import BloodOrganTransport from './pages/BloodOrganTransport'
import AmbulanceReadiness from './pages/AmbulanceReadiness'
import AlertCenter from './pages/AlertCenter'
import Settings from './pages/Settings'

// Simple Protected Route Component
const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('token');
    if (!token) return <Navigate to="/" replace />;
    return children;
};

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/dashboard" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                    <Route index element={<Dashboard />} />
                    <Route path="vaccines" element={<VaccineColdChain />} />
                    <Route path="medicines" element={<EssentialMedicines />} />
                    <Route path="blood" element={<BloodOrganTransport />} />
                    <Route path="ambulance" element={<AmbulanceReadiness />} />
                    <Route path="alerts" element={<AlertCenter />} />
                    <Route path="settings" element={<Settings />} />
                </Route>
            </Routes>
        </Router>
    )
}

export default App
