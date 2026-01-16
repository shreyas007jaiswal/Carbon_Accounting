"""
Test Cases for Carbon Accounting API
Run with: pytest test_api.py -v
Or run individual tests with: pytest test_api.py::test_create_organization -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date

from carbon_api.app import app
from carbon_api.database import Base, engine

# Create test client
client = TestClient(app)


# ==============================================================================
# FIXTURES - Setup and Teardown
# ==============================================================================

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ==============================================================================
# SAMPLE DATA
# ==============================================================================

SAMPLE_ORGANIZATION = {
    "name": "Green Energy Corp",
    "sector": "Energy",
    "country": "United Kingdom"
}

SAMPLE_ORGANIZATION_2 = {
    "name": "EcoTech Industries",
    "sector": "Manufacturing",
    "country": "Germany"
}

SAMPLE_USER = {
    "name": "John Smith",
    "email": "john.smith@greenenergy.com",
    "role": "Manager"
}

SAMPLE_USER_2 = {
    "name": "Jane Doe",
    "email": "jane.doe@greenenergy.com",
    "role": "Analyst"
}

SAMPLE_FACILITY = {
    "name": "Cardiff Manufacturing Plant",
    "location_region": "Wales, UK",
    "type": "plant"
}

SAMPLE_FACILITY_2 = {
    "name": "London Head Office",
    "location_region": "London, UK",
    "type": "office"
}

SAMPLE_SUPPLIER = {
    "name": "Steel Solutions Ltd",
    "category": "Raw Materials"
}

SAMPLE_EMISSION_FACTOR = {
    "category": "Natural Gas",
    "region": "UK",
    "unit": "kg CO2e/kWh",
    "value": 0.18387,
    "valid_from": "2024-01-01",
    "valid_to": "2024-12-31"
}

SAMPLE_EMISSION_FACTOR_2 = {
    "category": "Diesel",
    "region": "UK",
    "unit": "kg CO2e/liter",
    "value": 2.68787,
    "valid_from": "2024-01-01",
    "valid_to": "2024-12-31"
}

SAMPLE_EMISSION_ACTIVITY = {
    "scope": 1,
    "category": "Fuel Combustion",
    "activity_date": "2024-06-15",
    "quantity": 1000.5,
    "unit": "kWh",
    "source_reference": "Invoice #INV-2024-001"
}

SAMPLE_STATIONARY_FUEL = {
    "fuel_type": "Natural Gas",
    "quantity": 5000.00,
    "unit": "kWh"
}

SAMPLE_COMPANY_VEHICLE = {
    "vehicle_type": "Delivery Van",
    "distance_travelled": 15000.00,
    "fuel_consumed": 1800.50
}

SAMPLE_REFRIGERANT_LEAK = {
    "refrigerant_type": "R-410A",
    "leak_quantity_kg": 2.5,
    "gwp_factor": 2088.0
}

SAMPLE_PROCESS_EMISSION = {
    "material_type": "Cementiteite",
    "quantity_processed": 500.00
}


# ==============================================================================
# ORGANIZATION TESTS
# ==============================================================================

def test_create_organization():
    """Test creating a new organization."""
    response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == SAMPLE_ORGANIZATION["name"]
    assert data["sector"] == SAMPLE_ORGANIZATION["sector"]
    assert data["country"] == SAMPLE_ORGANIZATION["country"]
    assert "organization_id" in data
    assert "created_at" in data


def test_get_organizations():
    """Test retrieving all organizations."""
    # Create two organizations
    client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    client.post("/organizations/", json=SAMPLE_ORGANIZATION_2)
    
    response = client.get("/organizations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_organization_by_id():
    """Test retrieving a specific organization."""
    create_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = create_response.json()["organization_id"]
    
    response = client.get(f"/organizations/{org_id}")
    assert response.status_code == 200
    assert response.json()["name"] == SAMPLE_ORGANIZATION["name"]


def test_get_organization_not_found():
    """Test retrieving non-existent organization."""
    response = client.get("/organizations/9999")
    assert response.status_code == 404


def test_delete_organization():
    """Test deleting an organization."""
    create_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = create_response.json()["organization_id"]
    
    delete_response = client.delete(f"/organizations/{org_id}")
    assert delete_response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/organizations/{org_id}")
    assert get_response.status_code == 404


# ==============================================================================
# USER TESTS
# ==============================================================================

def test_create_user():
    """Test creating a new user."""
    # First create an organization
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    user_data = {**SAMPLE_USER, "organization_id": org_id}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == SAMPLE_USER["name"]
    assert data["email"] == SAMPLE_USER["email"]


def test_create_user_invalid_org():
    """Test creating user with non-existent organization."""
    user_data = {**SAMPLE_USER, "organization_id": 9999}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 404


def test_get_users():
    """Test retrieving all users."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    client.post("/users/", json={**SAMPLE_USER, "organization_id": org_id})
    client.post("/users/", json={**SAMPLE_USER_2, "organization_id": org_id})
    
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ==============================================================================
# FACILITY TESTS
# ==============================================================================

def test_create_facility():
    """Test creating a new facility."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    facility_data = {**SAMPLE_FACILITY, "organization_id": org_id}
    response = client.post("/facilities/", json=facility_data)
    assert response.status_code == 201
    assert response.json()["name"] == SAMPLE_FACILITY["name"]


def test_get_facilities():
    """Test retrieving all facilities."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    client.post("/facilities/", json={**SAMPLE_FACILITY, "organization_id": org_id})
    client.post("/facilities/", json={**SAMPLE_FACILITY_2, "organization_id": org_id})
    
    response = client.get("/facilities/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ==============================================================================
# SUPPLIER TESTS
# ==============================================================================

def test_create_supplier():
    """Test creating a new supplier."""
    response = client.post("/suppliers/", json=SAMPLE_SUPPLIER)
    assert response.status_code == 201
    assert response.json()["name"] == SAMPLE_SUPPLIER["name"]


def test_get_suppliers():
    """Test retrieving all suppliers."""
    client.post("/suppliers/", json=SAMPLE_SUPPLIER)
    client.post("/suppliers/", json={"name": "Logistics Co", "category": "Transport"})
    
    response = client.get("/suppliers/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ==============================================================================
# EMISSION FACTOR TESTS
# ==============================================================================

def test_create_emission_factor():
    """Test creating a new emission factor."""
    response = client.post("/emission-factors/", json=SAMPLE_EMISSION_FACTOR)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == SAMPLE_EMISSION_FACTOR["category"]
    assert float(data["value"]) == SAMPLE_EMISSION_FACTOR["value"]


def test_get_emission_factors():
    """Test retrieving all emission factors."""
    client.post("/emission-factors/", json=SAMPLE_EMISSION_FACTOR)
    client.post("/emission-factors/", json=SAMPLE_EMISSION_FACTOR_2)
    
    response = client.get("/emission-factors/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ==============================================================================
# EMISSION ACTIVITY TESTS
# ==============================================================================

def test_create_emission_activity():
    """Test creating a new emission activity."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    activity_data = {**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id}
    response = client.post("/emission-activities/", json=activity_data)
    assert response.status_code == 201
    data = response.json()
    assert data["scope"] == 1
    assert data["category"] == "Fuel Combustion"


def test_create_emission_activity_with_facility():
    """Test creating emission activity linked to a facility."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    facility_response = client.post("/facilities/", json={**SAMPLE_FACILITY, "organization_id": org_id})
    facility_id = facility_response.json()["facility_id"]
    
    activity_data = {
        **SAMPLE_EMISSION_ACTIVITY,
        "organization_id": org_id,
        "facility_id": facility_id
    }
    response = client.post("/emission-activities/", json=activity_data)
    assert response.status_code == 201
    assert response.json()["facility_id"] == facility_id


def test_get_emission_activities_by_scope():
    """Test filtering emission activities by scope."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    # Create Scope 1 activity
    client.post("/emission-activities/", json={**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id})
    
    # Create Scope 2 activity
    scope2_activity = {**SAMPLE_EMISSION_ACTIVITY, "scope": 2, "organization_id": org_id}
    client.post("/emission-activities/", json=scope2_activity)
    
    # Filter by scope 1
    response = client.get("/emission-activities/?scope=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["scope"] == 1


# ==============================================================================
# EMISSION CALCULATION TESTS
# ==============================================================================

def test_create_emission_calculation():
    """Test creating an emission calculation."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    activity_response = client.post("/emission-activities/", json={**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id})
    activity_id = activity_response.json()["activity_id"]
    
    calculation_data = {
        "activity_id": activity_id,
        "co2e_value": 183.87,
        "calculation_method": "Emission Factor",
        "factor_used": "UK Grid 2024"
    }
    response = client.post("/emission-calculations/", json=calculation_data)
    assert response.status_code == 201
    assert float(response.json()["co2e_value"]) == 183.87


# ==============================================================================
# SCOPE 1 SUBTABLE TESTS
# ==============================================================================

def test_create_stationary_fuel():
    """Test creating a stationary fuel record."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    activity_response = client.post("/emission-activities/", json={**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id})
    activity_id = activity_response.json()["activity_id"]
    
    fuel_data = {**SAMPLE_STATIONARY_FUEL, "activity_id": activity_id}
    response = client.post("/scope1/stationary-fuels/", json=fuel_data)
    assert response.status_code == 201
    assert response.json()["fuel_type"] == "Natural Gas"


def test_create_company_vehicle():
    """Test creating a company vehicle record."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    activity_response = client.post("/emission-activities/", json={**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id})
    activity_id = activity_response.json()["activity_id"]
    
    vehicle_data = {**SAMPLE_COMPANY_VEHICLE, "activity_id": activity_id}
    response = client.post("/scope1/company-vehicles/", json=vehicle_data)
    assert response.status_code == 201
    assert response.json()["vehicle_type"] == "Delivery Van"


def test_create_refrigerant_leak():
    """Test creating a refrigerant leak record."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    activity_response = client.post("/emission-activities/", json={**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id})
    activity_id = activity_response.json()["activity_id"]
    
    leak_data = {**SAMPLE_REFRIGERANT_LEAK, "activity_id": activity_id}
    response = client.post("/scope1/refrigerant-leaks/", json=leak_data)
    assert response.status_code == 201
    assert response.json()["refrigerant_type"] == "R-410A"


def test_create_process_emission():
    """Test creating a process emission record."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    activity_response = client.post("/emission-activities/", json={**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id})
    activity_id = activity_response.json()["activity_id"]
    
    process_data = {**SAMPLE_PROCESS_EMISSION, "activity_id": activity_id}
    response = client.post("/scope1/process-emissions/", json=process_data)
    assert response.status_code == 201


def test_get_stationary_fuels_by_activity():
    """Test filtering stationary fuels by activity ID."""
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    activity_response = client.post("/emission-activities/", json={**SAMPLE_EMISSION_ACTIVITY, "organization_id": org_id})
    activity_id = activity_response.json()["activity_id"]
    
    client.post("/scope1/stationary-fuels/", json={**SAMPLE_STATIONARY_FUEL, "activity_id": activity_id})
    
    response = client.get(f"/scope1/stationary-fuels/?activity_id={activity_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1


# ==============================================================================
# HEALTH CHECK TEST
# ==============================================================================

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ==============================================================================
# CASCADE DELETE TESTS
# ==============================================================================

def test_cascade_delete_organization():
    """Test that deleting an organization cascades to related records."""
    # Create organization with user and facility
    org_response = client.post("/organizations/", json=SAMPLE_ORGANIZATION)
    org_id = org_response.json()["organization_id"]
    
    client.post("/users/", json={**SAMPLE_USER, "organization_id": org_id})
    client.post("/facilities/", json={**SAMPLE_FACILITY, "organization_id": org_id})
    
    # Delete organization
    client.delete(f"/organizations/{org_id}")
    
    # Verify users and facilities are also deleted
    users_response = client.get("/users/")
    facilities_response = client.get("/facilities/")
    
    assert len(users_response.json()) == 0
    assert len(facilities_response.json()) == 0


# ==============================================================================
# RUN TESTS
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
