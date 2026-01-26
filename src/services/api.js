const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
    get: async (endpoint) => {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) throw new Error('API Request Failed');
            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            throw error;
        }
    },

    dashboard: {
        getOverview: () => api.get('/dashboard/overview'),
    },

    vaccines: {
        getFacilities: () => api.get('/vaccines/facilities'),
    },

    medicines: {
        getInventory: () => api.get('/medicines/inventory'),
    },

    blood: {
        getTransports: () => api.get('/blood/active-transports'),
    },

    ambulance: {
        getFleetStatus: () => api.get('/ambulance/fleet-status'),
    }
};
