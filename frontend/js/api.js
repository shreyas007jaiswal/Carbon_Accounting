/**
 * API Service for Carbon Accounting
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = 'http://127.0.0.1:8000';

// Generic API call function
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (method === 'DELETE' && response.status === 204) {
            return { success: true };
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error (${method} ${endpoint}):`, error);
        throw error;
    }
}

// Health Check
async function checkApiHealth() {
    return apiCall('/health');
}

// ============================================
// Organizations API
// ============================================
const OrganizationsAPI = {
    getAll: () => apiCall('/organizations/'),
    getById: (id) => apiCall(`/organizations/${id}`),
    create: (data) => apiCall('/organizations/', 'POST', data),
    delete: (id) => apiCall(`/organizations/${id}`, 'DELETE'),
};

// ============================================
// Users API
// ============================================
const UsersAPI = {
    getAll: () => apiCall('/users/'),
    getById: (id) => apiCall(`/users/${id}`),
    create: (data) => apiCall('/users/', 'POST', data),
};

// ============================================
// Facilities API
// ============================================
const FacilitiesAPI = {
    getAll: () => apiCall('/facilities/'),
    getById: (id) => apiCall(`/facilities/${id}`),
    create: (data) => apiCall('/facilities/', 'POST', data),
};

// ============================================
// Suppliers API
// ============================================
const SuppliersAPI = {
    getAll: () => apiCall('/suppliers/'),
    getById: (id) => apiCall(`/suppliers/${id}`),
    create: (data) => apiCall('/suppliers/', 'POST', data),
};

// ============================================
// Emission Factors API
// ============================================
const EmissionFactorsAPI = {
    getAll: () => apiCall('/emission-factors/'),
    getById: (id) => apiCall(`/emission-factors/${id}`),
    create: (data) => apiCall('/emission-factors/', 'POST', data),
};

// ============================================
// Emission Activities API
// ============================================
const ActivitiesAPI = {
    getAll: (scope = null) => {
        const params = scope ? `?scope=${scope}` : '';
        return apiCall(`/emission-activities/${params}`);
    },
    getById: (id) => apiCall(`/emission-activities/${id}`),
    create: (data) => apiCall('/emission-activities/', 'POST', data),
    delete: (id) => apiCall(`/emission-activities/${id}`, 'DELETE'),
};

// ============================================
// Emission Calculations API
// ============================================
const CalculationsAPI = {
    getAll: () => apiCall('/emission-calculations/'),
    create: (data) => apiCall('/emission-calculations/', 'POST', data),
    getSummary: () => apiCall('/emission-calculations/summary'),
    getByScope: () => apiCall('/emission-calculations/by-scope'),
    getByCategory: () => apiCall('/emission-calculations/by-category'),
    getWithDetails: () => apiCall('/emission-calculations/with-details'),
    recalculateAll: () => apiCall('/emission-calculations/recalculate-all', 'POST'),
};

// ============================================
// Scope 1 Subtables API
// ============================================
const StationaryFuelsAPI = {
    getAll: (activityId = null) => {
        const params = activityId ? `?activity_id=${activityId}` : '';
        return apiCall(`/scope1/stationary-fuels/${params}`);
    },
    getById: (id) => apiCall(`/scope1/stationary-fuels/${id}`),
    create: (data) => apiCall('/scope1/stationary-fuels/', 'POST', data),
};

const CompanyVehiclesAPI = {
    getAll: (activityId = null) => {
        const params = activityId ? `?activity_id=${activityId}` : '';
        return apiCall(`/scope1/company-vehicles/${params}`);
    },
    getById: (id) => apiCall(`/scope1/company-vehicles/${id}`),
    create: (data) => apiCall('/scope1/company-vehicles/', 'POST', data),
};

const RefrigerantLeaksAPI = {
    getAll: (activityId = null) => {
        const params = activityId ? `?activity_id=${activityId}` : '';
        return apiCall(`/scope1/refrigerant-leaks/${params}`);
    },
    getById: (id) => apiCall(`/scope1/refrigerant-leaks/${id}`),
    create: (data) => apiCall('/scope1/refrigerant-leaks/', 'POST', data),
};

const ProcessEmissionsAPI = {
    getAll: (activityId = null) => {
        const params = activityId ? `?activity_id=${activityId}` : '';
        return apiCall(`/scope1/process-emissions/${params}`);
    },
    getById: (id) => apiCall(`/scope1/process-emissions/${id}`),
    create: (data) => apiCall('/scope1/process-emissions/', 'POST', data),
};