const API_BASE_URL = 'http://localhost:8000/api/v1';

async function request(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    };
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

export const api = {
    get: (endpoint) => request(endpoint),
    post: (endpoint, data) => request(endpoint, { method: 'POST', body: JSON.stringify(data) }),

    auth: {
        login: (username, password) =>
            request('/auth/token', { method: 'POST', body: JSON.stringify({ username, password }) }),
    },

    workspace: {
        current: () => request('/workspace/current'),
        switch: (type) => request(`/workspace/switch?workspace_type=${type}`, { method: 'POST' }),
        list: () => request('/workspace'),
        capabilities: () => request('/workspace/capabilities'),
        dataSource: (workspace) => request(`/workspace/data-source?workspace=${workspace}`).catch(() => ({ type: 'synthetic_simulation', label: 'Synthetic Simulation', icon: '🔵' })),
    },

    hospital: {
        list: () => request('/hospital').catch(() => []),
        detail: (id) => request(`/hospital/${id}`).catch(() => null),
        occupancy: (id) => request(`/hospital/${id}/occupancy`).catch(() => []),
        admissions: (id, days = 30) => request(`/hospital/${id}/admissions?days=${days}`).catch(() => []),
        kpis: (id) => request(`/hospital/${id}/kpis`).catch(() => ({})),
        kpiSummary: () => request('/hospital/kpi/summary').catch(() => ({})),
        equipment: (id) => request(`/hospital/${id}/equipment`).catch(() => ({})),
        staff: (id) => request(`/hospital/${id}/staff`).catch(() => ({})),
        alerts: () => request('/hospital/alerts/all').catch(() => []),
        inventory: (id) => request(`/hospital/${id}/inventory`).catch(() => []),
    },

    community: {
        districts: () => request('/community/districts').catch(() => []),
        districtDetail: (id) => request(`/community/districts/${id}`).catch(() => null),
        diseaseReports: (districtId) =>
            districtId ? request(`/community/districts/${districtId}/disease-reports`).catch(() => []) : request('/community/disease-reports').catch(() => []),
        vaccinations: (districtId) =>
            districtId ? request(`/community/districts/${districtId}/vaccinations`).catch(() => ({})) : request('/community/vaccinations').catch(() => ({})),
        medicineStock: (districtId) => request(`/community/districts/${districtId}/medicine-stock`).catch(() => ({})),
        healthWorkers: (districtId) => request(`/community/districts/${districtId}/health-workers`).catch(() => ({})),
        kpis: (districtId) => districtId ? request(`/community/districts/${districtId}/kpis`).catch(() => ({})) : request('/community/kpis').catch(() => []),
        kpiSummary: () => request('/community/kpi/summary').catch(() => ({})),
        outbreaks: () => request('/community/outbreaks').catch(() => []),
        alerts: () => request('/community/alerts').catch(() => []),
    },

    intelligence: {
        query: (message, context) =>
            request('/intelligence/query', { method: 'POST', body: JSON.stringify({ message, context }) }),
        agents: () => request('/intelligence/agents'),
    },

    simulation: {
        createScenario: (name, description, parameters) =>
            request('/simulation/scenarios', { method: 'POST', body: JSON.stringify({ name, description, parameters }) }),
        listScenarios: () => request('/simulation/scenarios'),
        getScenario: (id) => request(`/simulation/scenarios/${id}`),
        run: (id) => request(`/simulation/run/${id}`, { method: 'POST' }),
        getResult: (id) => request(`/simulation/result/${id}`),
        listActive: () => request('/simulation/active'),
    },

    knowledge: {
        summary: () => request('/knowledge/summary'),
        nodeTypes: () => request('/knowledge/node-types'),
        edgeTypes: () => request('/knowledge/edge-types'),
        getNode: (id) => request(`/knowledge/nodes/${id}`),
        neighbors: (nodeId, depth = 1) => request(`/knowledge/neighbors/${nodeId}?depth=${depth}`),
        findPath: (source, target) => request('/knowledge/path', { method: 'POST', body: JSON.stringify({ source, target }) }),
        getNodesByType: (type) => request(`/knowledge/nodes/type/${type}`),
    },

    health: {
        ping: () => request('/health/ping'),
        connectors: () => request('/health/connectors'),
    },
};


