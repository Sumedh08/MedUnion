import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Login from './pages/Login'

import HospitalDashboard from './pages/hospital/HospitalDashboard'
import HospitalOccupancy from './pages/hospital/HospitalOccupancy'
import HospitalAdmissions from './pages/hospital/HospitalAdmissions'
import HospitalInventory from './pages/hospital/HospitalInventory'

import CommunityDashboard from './pages/community/CommunityDashboard'
import DiseaseSurveillance from './pages/community/DiseaseSurveillance'
import VaccinationCoverage from './pages/community/VaccinationCoverage'

import CopilotPage from './pages/CopilotPage'
import SimulationPage from './pages/simulation/SimulationPage'
import SettingsPage from './pages/Settings'

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
                <Route path="/app" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                    <Route index element={<Navigate to="/app/hospital" replace />} />

                    <Route path="hospital" element={<HospitalDashboard />} />
                    <Route path="hospital/occupancy" element={<HospitalOccupancy />} />
                    <Route path="hospital/admissions" element={<HospitalAdmissions />} />
                    <Route path="hospital/inventory" element={<HospitalInventory />} />

                    <Route path="community" element={<CommunityDashboard />} />
                    <Route path="community/diseases" element={<DiseaseSurveillance />} />
                    <Route path="community/vaccinations" element={<VaccinationCoverage />} />

                    <Route path="copilot" element={<CopilotPage />} />
                    <Route path="simulation" element={<SimulationPage />} />
                    <Route path="settings" element={<SettingsPage />} />
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    )
}

export default App
