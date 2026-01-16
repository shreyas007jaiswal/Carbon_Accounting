/**
 * Main Application JavaScript
 * Handles UI interactions and data display
 */

// ============================================
// Global State
// ============================================
let organizationsCache = [];
let facilitiesCache = [];
let usersCache = [];
let suppliersCache = [];
let emissionFactorsCache = [];
let activitiesCache = [];

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initTabs();
    initApiStatus();
    loadDashboard();
});

// ============================================
// Navigation
// ============================================
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-links li');
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const section = link.dataset.section;
            
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            showSection(section);
            
            document.getElementById('page-title').textContent = 
                link.querySelector('span').textContent;
            
            loadSectionData(section);
            
            document.querySelector('.sidebar').classList.remove('open');
        });
    });
    
    document.querySelector('.menu-toggle').addEventListener('click', () => {
        document.querySelector('.sidebar').classList.toggle('open');
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

function loadSectionData(section) {
    switch (section) {
        case 'dashboard': loadDashboard(); break;
        case 'organizations': loadOrganizations(); break;
        case 'facilities': loadFacilities(); break;
        case 'users': loadUsers(); break;
        case 'suppliers': loadSuppliers(); break;
        case 'emission-factors': loadEmissionFactors(); break;
        case 'activities': loadActivities(); break;
        case 'scope1': loadScope1Data(); break;
    }
}

// ============================================
// Tabs
// ============================================
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tab}-tab`).classList.add('active');
        });
    });
}

// ============================================
// API Status
// ============================================
async function initApiStatus() {
    const statusDot = document.getElementById('api-status-dot');
    const statusText = document.getElementById('api-status-text');
    
    async function checkStatus() {
        try {
            await checkApiHealth();
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'API Connected';
        } catch (error) {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'API Disconnected';
        }
    }
    
    await checkStatus();
    setInterval(checkStatus, 30000);
}

// ============================================
// Dashboard
// ============================================
async function loadDashboard() {
    try {
        const [orgs, facilities, users, activities, emissionsByScope, emissionsByCategory, calculationsWithDetails] = await Promise.all([
            OrganizationsAPI.getAll(),
            FacilitiesAPI.getAll(),
            UsersAPI.getAll(),
            ActivitiesAPI.getAll(),
            CalculationsAPI.getByScope().catch(() => []),
            CalculationsAPI.getByCategory().catch(() => []),
            CalculationsAPI.getWithDetails().catch(() => [])
        ]);
        
        organizationsCache = orgs;
        facilitiesCache = facilities;
        usersCache = users;
        activitiesCache = activities;
        
        // Update stat cards
        document.getElementById('total-organizations').textContent = orgs.length;
        document.getElementById('total-facilities').textContent = facilities.length;
        document.getElementById('total-users').textContent = users.length;
        document.getElementById('total-emissions').textContent = activities.length;
        
        // Update emissions totals
        updateEmissionsTotals(emissionsByScope);
        
        // Update recent calculations table
        updateRecentCalculations(calculationsWithDetails.slice(-5).reverse());
        
        // Update scope bars with actual CO2e values
        updateScopeBars(emissionsByScope);
        
        // Update emissions by category table
        updateEmissionsByCategory(emissionsByCategory);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error loading dashboard data', 'error');
    }
}

function updateEmissionsTotals(emissionsByScope) {
    let totalCO2e = 0;
    let scope1CO2e = 0;
    let scope2CO2e = 0;
    let scope3CO2e = 0;
    
    emissionsByScope.forEach(scope => {
        const tonnes = parseFloat(scope.total_co2e_tonnes) || 0;
        totalCO2e += tonnes;
        
        if (scope.scope === 1) scope1CO2e = tonnes;
        else if (scope.scope === 2) scope2CO2e = tonnes;
        else if (scope.scope === 3) scope3CO2e = tonnes;
    });
    
    document.getElementById('total-co2e').textContent = totalCO2e.toFixed(2);
    document.getElementById('scope1-co2e').textContent = scope1CO2e.toFixed(2);
    document.getElementById('scope2-co2e').textContent = scope2CO2e.toFixed(2);
    document.getElementById('scope3-co2e').textContent = scope3CO2e.toFixed(2);
}

function updateRecentCalculations(calculations) {
    const tbody = document.getElementById('recent-activities-table');
    
    if (calculations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><p>No calculations yet</p></td></tr>';
        return;
    }
    
    tbody.innerHTML = calculations.map(calc => `
        <tr>
            <td>${formatDate(calc.activity_date)}</td>
            <td><span class="badge badge-scope${calc.scope}">Scope ${calc.scope}</span></td>
            <td>${calc.category}</td>
            <td>${parseFloat(calc.quantity).toLocaleString() || '-'} ${calc.unit || ''}</td>
            <td><strong>${parseFloat(calc.co2e_value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</strong></td>
        </tr>
    `).join('');
}

function updateScopeBars(emissionsByScope) {
    let scope1 = 0, scope2 = 0, scope3 = 0;
    
    emissionsByScope.forEach(scope => {
        const kg = parseFloat(scope.total_co2e_kg) || 0;
        if (scope.scope === 1) scope1 = kg;
        else if (scope.scope === 2) scope2 = kg;
        else if (scope.scope === 3) scope3 = kg;
    });
    
    const total = scope1 + scope2 + scope3 || 1;
    
    document.getElementById('scope1-count').textContent = formatCO2e(scope1);
    document.getElementById('scope2-count').textContent = formatCO2e(scope2);
    document.getElementById('scope3-count').textContent = formatCO2e(scope3);
    
    document.getElementById('scope1-bar').style.width = `${(scope1 / total) * 100}%`;
    document.getElementById('scope2-bar').style.width = `${(scope2 / total) * 100}%`;
    document.getElementById('scope3-bar').style.width = `${(scope3 / total) * 100}%`;
}

function updateEmissionsByCategory(categories) {
    const tbody = document.getElementById('emissions-by-category-table');
    
    if (categories.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><p>No emissions data yet</p></td></tr>';
        return;
    }
    
    tbody.innerHTML = categories.slice(0, 10).map(cat => `
        <tr>
            <td><strong>${cat.category}</strong></td>
            <td><span class="badge badge-scope${cat.scope}">Scope ${cat.scope}</span></td>
            <td>${cat.activity_count}</td>
            <td>${parseFloat(cat.total_co2e_kg).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            <td><strong>${parseFloat(cat.total_co2e_tonnes).toLocaleString(undefined, {minimumFractionDigits: 4, maximumFractionDigits: 4})}</strong></td>
        </tr>
    `).join('');
}

function formatCO2e(kg) {
    if (kg >= 1000) {
        return `${(kg / 1000).toFixed(2)} t`;
    }
    return `${kg.toFixed(2)} kg`;
}

function updateRecentActivities(activities) {
    const tbody = document.getElementById('recent-activities-table');
    
    if (activities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><p>No activities yet</p></td></tr>';
        return;
    }
    
    tbody.innerHTML = activities.map(activity => `
        <tr>
            <td>${formatDate(activity.activity_date)}</td>
            <td><span class="badge badge-scope${activity.scope}">Scope ${activity.scope}</span></td>
            <td>${activity.category}</td>
            <td>${activity.quantity || '-'} ${activity.unit || ''}</td>
            <td>-</td>
        </tr>
    `).join('');
}

// ============================================
// Organizations
// ============================================
async function loadOrganizations() {
    try {
        const organizations = await OrganizationsAPI.getAll();
        organizationsCache = organizations;
        
        const tbody = document.getElementById('organizations-table');
        
        if (organizations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No organizations yet</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = organizations.map(org => `
            <tr>
                <td>${org.organization_id}</td>
                <td><strong>${org.name}</strong></td>
                <td>${org.sector || '-'}</td>
                <td>${org.country || '-'}</td>
                <td>${formatDate(org.created_at)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view" onclick="viewOrganization(${org.organization_id})"><i class="fas fa-eye"></i></button>
                        <button class="action-btn delete" onclick="deleteOrganization(${org.organization_id})"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading organizations:', error);
        showToast('Error loading organizations', 'error');
    }
}

async function deleteOrganization(id) {
    if (!confirm('Delete this organization and all related data?')) return;
    
    try {
        await OrganizationsAPI.delete(id);
        showToast('Organization deleted', 'success');
        loadOrganizations();
        loadDashboard();
    } catch (error) {
        showToast('Error deleting organization', 'error');
    }
}

function viewOrganization(id) {
    const org = organizationsCache.find(o => o.organization_id === id);
    if (org) alert(`Organization: ${org.name}\nSector: ${org.sector || 'N/A'}\nCountry: ${org.country || 'N/A'}`);
}

// ============================================
// Facilities
// ============================================
async function loadFacilities() {
    try {
        const [facilities, organizations] = await Promise.all([
            FacilitiesAPI.getAll(),
            OrganizationsAPI.getAll()
        ]);
        
        facilitiesCache = facilities;
        organizationsCache = organizations;
        
        const tbody = document.getElementById('facilities-table');
        
        if (facilities.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No facilities yet</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = facilities.map(facility => {
            const org = organizations.find(o => o.organization_id === facility.organization_id);
            return `
                <tr>
                    <td>${facility.facility_id}</td>
                    <td><strong>${facility.name}</strong></td>
                    <td>${org ? org.name : '-'}</td>
                    <td>${facility.location_region || '-'}</td>
                    <td>${facility.type || '-'}</td>
                    <td>
                        <button class="action-btn view" onclick="viewFacility(${facility.facility_id})"><i class="fas fa-eye"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading facilities:', error);
        showToast('Error loading facilities', 'error');
    }
}

function viewFacility(id) {
    const facility = facilitiesCache.find(f => f.facility_id === id);
    if (facility) {
        const org = organizationsCache.find(o => o.organization_id === facility.organization_id);
        alert(`Facility: ${facility.name}\nOrganization: ${org ? org.name : 'N/A'}\nLocation: ${facility.location_region || 'N/A'}`);
    }
}

// ============================================
// Users
// ============================================
async function loadUsers() {
    try {
        const [users, organizations] = await Promise.all([
            UsersAPI.getAll(),
            OrganizationsAPI.getAll()
        ]);
        
        usersCache = users;
        organizationsCache = organizations;
        
        const tbody = document.getElementById('users-table');
        
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No users yet</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = users.map(user => {
            const org = organizations.find(o => o.organization_id === user.organization_id);
            return `
                <tr>
                    <td>${user.user_id}</td>
                    <td><strong>${user.name}</strong></td>
                    <td>${user.email}</td>
                    <td><span class="badge badge-role">${user.role}</span></td>
                    <td>${org ? org.name : '-'}</td>
                    <td>
                        <button class="action-btn view" onclick="viewUser(${user.user_id})"><i class="fas fa-eye"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        showToast('Error loading users', 'error');
    }
}

function viewUser(id) {
    const user = usersCache.find(u => u.user_id === id);
    if (user) alert(`User: ${user.name}\nEmail: ${user.email}\nRole: ${user.role}`);
}

// ============================================
// Suppliers
// ============================================
async function loadSuppliers() {
    try {
        const suppliers = await SuppliersAPI.getAll();
        suppliersCache = suppliers;
        
        const tbody = document.getElementById('suppliers-table');
        
        if (suppliers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><p>No suppliers yet</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = suppliers.map(supplier => `
            <tr>
                <td>${supplier.supplier_id}</td>
                <td><strong>${supplier.name}</strong></td>
                <td>${supplier.category || '-'}</td>
                <td>${formatDate(supplier.created_at)}</td>
                <td>
                    <button class="action-btn view" onclick="viewSupplier(${supplier.supplier_id})"><i class="fas fa-eye"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading suppliers:', error);
        showToast('Error loading suppliers', 'error');
    }
}

function viewSupplier(id) {
    const supplier = suppliersCache.find(s => s.supplier_id === id);
    if (supplier) alert(`Supplier: ${supplier.name}\nCategory: ${supplier.category || 'N/A'}`);
}

// ============================================
// Emission Factors
// ============================================
async function loadEmissionFactors() {
    try {
        const factors = await EmissionFactorsAPI.getAll();
        emissionFactorsCache = factors;
        
        const tbody = document.getElementById('emission-factors-table');
        
        if (factors.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><p>No emission factors yet</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = factors.map(factor => `
            <tr>
                <td>${factor.factor_id}</td>
                <td><strong>${factor.category}</strong></td>
                <td>${factor.region || '-'}</td>
                <td>${factor.value}</td>
                <td>${factor.unit || '-'}</td>
                <td>${factor.valid_from ? formatDate(factor.valid_from) + ' - ' + formatDate(factor.valid_to) : '-'}</td>
                <td>
                    <button class="action-btn view" onclick="viewEmissionFactor(${factor.factor_id})"><i class="fas fa-eye"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading emission factors:', error);
        showToast('Error loading emission factors', 'error');
    }
}

function viewEmissionFactor(id) {
    const factor = emissionFactorsCache.find(f => f.factor_id === id);
    if (factor) alert(`Category: ${factor.category}\nRegion: ${factor.region || 'N/A'}\nValue: ${factor.value} ${factor.unit || ''}`);
}

// ============================================
// Activities
// ============================================
async function loadActivities(scope = null) {
    try {
        const activities = await ActivitiesAPI.getAll(scope);
        activitiesCache = activities;
        
        const tbody = document.getElementById('activities-table');
        
        if (activities.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><p>No activities yet</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = activities.map(activity => `
            <tr>
                <td>${activity.activity_id}</td>
                <td>${formatDate(activity.activity_date)}</td>
                <td><span class="badge badge-scope${activity.scope}">Scope ${activity.scope}</span></td>
                <td>${activity.category}</td>
                <td>${activity.quantity || '-'}</td>
                <td>${activity.unit || '-'}</td>
                <td>${activity.source_reference || '-'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view" onclick="viewActivity(${activity.activity_id})"><i class="fas fa-eye"></i></button>
                        <button class="action-btn delete" onclick="deleteActivity(${activity.activity_id})"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading activities:', error);
        showToast('Error loading activities', 'error');
    }
}

function filterActivities() {
    const scope = document.getElementById('scope-filter').value;
    loadActivities(scope || null);
}

function viewActivity(id) {
    const activity = activitiesCache.find(a => a.activity_id === id);
    if (activity) alert(`Activity ID: ${activity.activity_id}\nScope: ${activity.scope}\nCategory: ${activity.category}\nQuantity: ${activity.quantity || 'N/A'} ${activity.unit || ''}`);
}

async function deleteActivity(id) {
    if (!confirm('Delete this activity?')) return;
    
    try {
        await ActivitiesAPI.delete(id);
        showToast('Activity deleted', 'success');
        loadActivities();
        loadDashboard();
    } catch (error) {
        showToast('Error deleting activity', 'error');
    }
}

// ============================================
// Scope 1 Data
// ============================================
async function loadScope1Data() {
    await Promise.all([
        loadStationaryFuels(),
        loadCompanyVehicles(),
        loadRefrigerantLeaks(),
        loadProcessEmissions()
    ]);
}

async function loadStationaryFuels() {
    try {
        const fuels = await StationaryFuelsAPI.getAll();
        const tbody = document.getElementById('stationary-fuels-table');
        
        if (fuels.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No records</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = fuels.map(fuel => `
            <tr>
                <td>${fuel.fuel_id}</td>
                <td>${fuel.activity_id}</td>
                <td>${fuel.fuel_type}</td>
                <td>${fuel.quantity}</td>
                <td>${fuel.unit}</td>
                <td><button class="action-btn view" onclick="alert('Fuel ID: ${fuel.fuel_id}')"><i class="fas fa-eye"></i></button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading stationary fuels:', error);
    }
}

async function loadCompanyVehicles() {
    try {
        const vehicles = await CompanyVehiclesAPI.getAll();
        const tbody = document.getElementById('company-vehicles-table');
        
        if (vehicles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No records</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = vehicles.map(vehicle => `
            <tr>
                <td>${vehicle.vehicle_id}</td>
                <td>${vehicle.activity_id}</td>
                <td>${vehicle.vehicle_type}</td>
                <td>${vehicle.distance_travelled || '-'}</td>
                <td>${vehicle.fuel_consumed || '-'}</td>
                <td><button class="action-btn view" onclick="alert('Vehicle ID: ${vehicle.vehicle_id}')"><i class="fas fa-eye"></i></button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading company vehicles:', error);
    }
}

async function loadRefrigerantLeaks() {
    try {
        const leaks = await RefrigerantLeaksAPI.getAll();
        const tbody = document.getElementById('refrigerant-leaks-table');
        
        if (leaks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No records</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = leaks.map(leak => `
            <tr>
                <td>${leak.refrigerant_id}</td>
                <td>${leak.activity_id}</td>
                <td>${leak.refrigerant_type}</td>
                <td>${leak.leak_quantity_kg}</td>
                <td>${leak.gwp_factor || '-'}</td>
                <td><button class="action-btn view" onclick="alert('Leak ID: ${leak.refrigerant_id}')"><i class="fas fa-eye"></i></button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading refrigerant leaks:', error);
    }
}

async function loadProcessEmissions() {
    try {
        const emissions = await ProcessEmissionsAPI.getAll();
        const tbody = document.getElementById('process-emissions-table');
        
        if (emissions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><p>No records</p></td></tr>';
            return;
        }
        
        tbody.innerHTML = emissions.map(emission => `
            <tr>
                <td>${emission.process_id}</td>
                <td>${emission.activity_id}</td>
                <td>${emission.material_type}</td>
                <td>${emission.quantity_processed}</td>
                <td><button class="action-btn view" onclick="alert('Process ID: ${emission.process_id}')"><i class="fas fa-eye"></i></button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading process emissions:', error);
    }
}

// ============================================
// Modal Functions
// ============================================
function openModal(type) {
    const modal = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');
    
    const forms = {
        'organization': {
            title: 'Add Organization',
            html: `
                <form onsubmit="submitOrganization(event)">
                    <div class="form-group">
                        <label>Organization Name *</label>
                        <input type="text" name="name" required placeholder="Enter organization name">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Sector</label>
                            <input type="text" name="sector" placeholder="e.g., Energy">
                        </div>
                        <div class="form-group">
                            <label>Country</label>
                            <input type="text" name="country" placeholder="e.g., UK">
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'user': {
            title: 'Add User',
            html: `
                <form onsubmit="submitUser(event)">
                    <div class="form-group">
                        <label>Organization *</label>
                        <select name="organization_id" required>
                            <option value="">Select Organization</option>
                            ${organizationsCache.map(org => `<option value="${org.organization_id}">${org.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Full Name *</label>
                        <input type="text" name="name" required placeholder="Enter full name">
                    </div>
                    <div class="form-group">
                        <label>Email *</label>
                        <input type="email" name="email" required placeholder="Enter email">
                    </div>
                    <div class="form-group">
                        <label>Role</label>
                        <select name="role">
                            <option value="Employee">Employee</option>
                            <option value="Analyst">Analyst</option>
                            <option value="Manager">Manager</option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'facility': {
            title: 'Add Facility',
            html: `
                <form onsubmit="submitFacility(event)">
                    <div class="form-group">
                        <label>Organization *</label>
                        <select name="organization_id" required>
                            <option value="">Select Organization</option>
                            ${organizationsCache.map(org => `<option value="${org.organization_id}">${org.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Facility Name *</label>
                        <input type="text" name="name" required placeholder="Enter facility name">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Location</label>
                            <input type="text" name="location_region" placeholder="e.g., London, UK">
                        </div>
                        <div class="form-group">
                            <label>Type</label>
                            <select name="type">
                                <option value="">Select</option>
                                <option value="office">Office</option>
                                <option value="plant">Plant</option>
                                <option value="warehouse">Warehouse</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'supplier': {
            title: 'Add Supplier',
            html: `
                <form onsubmit="submitSupplier(event)">
                    <div class="form-group">
                        <label>Supplier Name *</label>
                        <input type="text" name="name" required placeholder="Enter supplier name">
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <input type="text" name="category" placeholder="e.g., Raw Materials">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'emission-factor': {
            title: 'Add Emission Factor',
            html: `
                <form onsubmit="submitEmissionFactor(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Category *</label>
                            <input type="text" name="category" required placeholder="e.g., Natural Gas">
                        </div>
                        <div class="form-group">
                            <label>Region</label>
                            <input type="text" name="region" placeholder="e.g., UK">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Value *</label>
                            <input type="number" name="value" step="0.000001" required placeholder="0.00">
                        </div>
                        <div class="form-group">
                            <label>Unit</label>
                            <input type="text" name="unit" placeholder="e.g., kg CO2e/kWh">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Valid From</label>
                            <input type="date" name="valid_from">
                        </div>
                        <div class="form-group">
                            <label>Valid To</label>
                            <input type="date" name="valid_to">
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'activity': {
            title: 'Add Emission Activity',
            html: `
                <form onsubmit="submitActivity(event)">
                    <div class="form-group">
                        <label>Organization *</label>
                        <select name="organization_id" required>
                            <option value="">Select Organization</option>
                            ${organizationsCache.map(org => `<option value="${org.organization_id}">${org.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Scope *</label>
                            <select name="scope" required>
                                <option value="1">Scope 1</option>
                                <option value="2">Scope 2</option>
                                <option value="3">Scope 3</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Category *</label>
                            <input type="text" name="category" required placeholder="e.g., Fuel Combustion">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Activity Date *</label>
                        <input type="date" name="activity_date" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" name="quantity" step="0.0001" placeholder="0.00">
                        </div>
                        <div class="form-group">
                            <label>Unit</label>
                            <input type="text" name="unit" placeholder="e.g., kWh">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Source Reference</label>
                        <input type="text" name="source_reference" placeholder="e.g., Invoice #123">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'stationary-fuel': {
            title: 'Add Stationary Fuel',
            html: `
                <form onsubmit="submitStationaryFuel(event)">
                    <div class="form-group">
                        <label>Activity ID *</label>
                        <input type="number" name="activity_id" required placeholder="Enter activity ID">
                    </div>
                    <div class="form-group">
                        <label>Fuel Type *</label>
                        <input type="text" name="fuel_type" required placeholder="e.g., Natural Gas">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Quantity *</label>
                            <input type="number" name="quantity" step="0.0001" required placeholder="0.00">
                        </div>
                        <div class="form-group">
                            <label>Unit *</label>
                            <input type="text" name="unit" required placeholder="e.g., kWh">
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'company-vehicle': {
            title: 'Add Company Vehicle',
            html: `
                <form onsubmit="submitCompanyVehicle(event)">
                    <div class="form-group">
                        <label>Activity ID *</label>
                        <input type="number" name="activity_id" required placeholder="Enter activity ID">
                    </div>
                    <div class="form-group">
                        <label>Vehicle Type *</label>
                        <input type="text" name="vehicle_type" required placeholder="e.g., Delivery Van">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Distance (km)</label>
                            <input type="number" name="distance_travelled" step="0.01" placeholder="0.00">
                        </div>
                        <div class="form-group">
                            <label>Fuel (liters)</label>
                            <input type="number" name="fuel_consumed" step="0.01" placeholder="0.00">
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'refrigerant-leak': {
            title: 'Add Refrigerant Leak',
            html: `
                <form onsubmit="submitRefrigerantLeak(event)">
                    <div class="form-group">
                        <label>Activity ID *</label>
                        <input type="number" name="activity_id" required placeholder="Enter activity ID">
                    </div>
                    <div class="form-group">
                        <label>Refrigerant Type *</label>
                        <input type="text" name="refrigerant_type" required placeholder="e.g., R-410A">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Leak Quantity (kg) *</label>
                            <input type="number" name="leak_quantity_kg" step="0.0001" required placeholder="0.00">
                        </div>
                        <div class="form-group">
                            <label>GWP Factor</label>
                            <input type="number" name="gwp_factor" step="0.01" placeholder="e.g., 2088">
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        },
        'process-emission': {
            title: 'Add Process Emission',
            html: `
                <form onsubmit="submitProcessEmission(event)">
                    <div class="form-group">
                        <label>Activity ID *</label>
                        <input type="number" name="activity_id" required placeholder="Enter activity ID">
                    </div>
                    <div class="form-group">
                        <label>Material Type *</label>
                        <input type="text" name="material_type" required placeholder="e.g.,ite">
                    </div>
                    <div class="form-group">
                        <label>Quantity Processed *</label>
                        <input type="number" name="quantity_processed" step="0.0001" required placeholder="0.00">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add</button>
                    </div>
                </form>`
        }
    };
    
    const form = forms[type];
    if (form) {
        title.textContent = form.title;
        body.innerHTML = form.html;
        modal.classList.add('active');
    }
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

document.getElementById('modal-overlay').addEventListener('click', (e) => {
    if (e.target.id === 'modal-overlay') closeModal();
});

// ============================================
// Form Submissions
// ============================================
async function submitOrganization(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await OrganizationsAPI.create({
            name: form.name.value,
            sector: form.sector.value || null,
            country: form.country.value || null
        });
        showToast('Organization created', 'success');
        closeModal();
        loadOrganizations();
        loadDashboard();
    } catch (error) {
        showToast('Error creating organization', 'error');
    }
}

async function submitUser(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await UsersAPI.create({
            organization_id: parseInt(form.organization_id.value),
            name: form.name.value,
            email: form.email.value,
            role: form.role.value
        });
        showToast('User created', 'success');
        closeModal();
        loadUsers();
        loadDashboard();
    } catch (error) {
        showToast('Error creating user', 'error');
    }
}

async function submitFacility(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await FacilitiesAPI.create({
            organization_id: parseInt(form.organization_id.value),
            name: form.name.value,
            location_region: form.location_region.value || null,
            type: form.type.value || null
        });
        showToast('Facility created', 'success');
        closeModal();
        loadFacilities();
        loadDashboard();
    } catch (error) {
        showToast('Error creating facility', 'error');
    }
}

async function submitSupplier(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await SuppliersAPI.create({
            name: form.name.value,
            category: form.category.value || null
        });
        showToast('Supplier created', 'success');
        closeModal();
        loadSuppliers();
    } catch (error) {
        showToast('Error creating supplier', 'error');
    }
}

async function submitEmissionFactor(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await EmissionFactorsAPI.create({
            category: form.category.value,
            region: form.region.value || null,
            value: parseFloat(form.value.value),
            unit: form.unit.value || null,
            valid_from: form.valid_from.value || null,
            valid_to: form.valid_to.value || null
        });
        showToast('Emission factor created', 'success');
        closeModal();
        loadEmissionFactors();
    } catch (error) {
        showToast('Error creating emission factor', 'error');
    }
}

async function submitActivity(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await ActivitiesAPI.create({
            organization_id: parseInt(form.organization_id.value),
            scope: parseInt(form.scope.value),
            category: form.category.value,
            activity_date: form.activity_date.value,
            quantity: form.quantity.value ? parseFloat(form.quantity.value) : null,
            unit: form.unit.value || null,
            source_reference: form.source_reference.value || null
        });
        showToast('Activity created', 'success');
        closeModal();
        loadActivities();
        loadDashboard();
    } catch (error) {
        showToast('Error creating activity', 'error');
    }
}

async function submitStationaryFuel(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await StationaryFuelsAPI.create({
            activity_id: parseInt(form.activity_id.value),
            fuel_type: form.fuel_type.value,
            quantity: parseFloat(form.quantity.value),
            unit: form.unit.value
        });
        showToast('Stationary fuel record created', 'success');
        closeModal();
        loadStationaryFuels();
    } catch (error) {
        showToast('Error creating record', 'error');
    }
}

async function submitCompanyVehicle(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await CompanyVehiclesAPI.create({
            activity_id: parseInt(form.activity_id.value),
            vehicle_type: form.vehicle_type.value,
            distance_travelled: form.distance_travelled.value ? parseFloat(form.distance_travelled.value) : null,
            fuel_consumed: form.fuel_consumed.value ? parseFloat(form.fuel_consumed.value) : null
        });
        showToast('Company vehicle record created', 'success');
        closeModal();
        loadCompanyVehicles();
    } catch (error) {
        showToast('Error creating record', 'error');
    }
}

async function submitRefrigerantLeak(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await RefrigerantLeaksAPI.create({
            activity_id: parseInt(form.activity_id.value),
            refrigerant_type: form.refrigerant_type.value,
            leak_quantity_kg: parseFloat(form.leak_quantity_kg.value),
            gwp_factor: form.gwp_factor.value ? parseFloat(form.gwp_factor.value) : null
        });
        showToast('Refrigerant leak record created', 'success');
        closeModal();
        loadRefrigerantLeaks();
    } catch (error) {
        showToast('Error creating record', 'error');
    }
}

async function submitProcessEmission(event) {
    event.preventDefault();
    const form = event.target;
    try {
        await ProcessEmissionsAPI.create({
            activity_id: parseInt(form.activity_id.value),
            material_type: form.material_type.value,
            quantity_processed: parseFloat(form.quantity_processed.value)
        });
        showToast('Process emission record created', 'success');
        closeModal();
        loadProcessEmissions();
    } catch (error) {
        showToast('Error creating record', 'error');
    }
}

// ============================================
// Utility Functions
// ============================================
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const icon = toast.querySelector('i');
    
    toastMessage.textContent = message;
    toast.className = `toast ${type}`;
    icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
    
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});