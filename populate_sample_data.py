"""
Sample Data Population Script
Run with: python populate_sample_data.py

This script populates the database with sample data for testing.
"""

import requests

BASE_URL = "http://127.0.0.1:8000"


def create_sample_data():
    """Populate the database with sample data."""
    
    print("=" * 60)
    print("POPULATING CARBON ACCOUNTING DATABASE WITH SAMPLE DATA")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # 1. CREATE ORGANIZATIONS
    # -------------------------------------------------------------------------
    print("\n1. Creating Organizations...")
    
    organizations = [
        {"name": "Green Energy Corp", "sector": "Energy", "country": "United Kingdom"},
        {"name": "EcoTech Industries", "sector": "Manufacturing", "country": "Germany"},
        {"name": "Sustainable Logistics Ltd", "sector": "Transport", "country": "France"},
    ]
    
    org_ids = []
    for org in organizations:
        response = requests.post(f"{BASE_URL}/organizations/", json=org)
        if response.status_code == 201:
            org_id = response.json()["organization_id"]
            org_ids.append(org_id)
            print(f"   ✓ Created: {org['name']} (ID: {org_id})")
        else:
            print(f"   ✗ Failed to create: {org['name']}")
    
    # -------------------------------------------------------------------------
    # 2. CREATE USERS
    # -------------------------------------------------------------------------
    print("\n2. Creating Users...")
    
    users = [
        {"name": "John Smith", "email": "john.smith@greenenergy.com", "role": "Manager", "organization_id": org_ids[0]},
        {"name": "Jane Doe", "email": "jane.doe@greenenergy.com", "role": "Analyst", "organization_id": org_ids[0]},
        {"name": "Hans Mueller", "email": "hans.mueller@ecotech.de", "role": "Manager", "organization_id": org_ids[1]},
        {"name": "Marie Dupont", "email": "marie.dupont@sustainable.fr", "role": "Employee", "organization_id": org_ids[2]},
    ]
    
    for user in users:
        response = requests.post(f"{BASE_URL}/users/", json=user)
        if response.status_code == 201:
            print(f"   ✓ Created: {user['name']} ({user['role']})")
        else:
            print(f"   ✗ Failed to create: {user['name']}")
    
    # -------------------------------------------------------------------------
    # 3. CREATE FACILITIES
    # -------------------------------------------------------------------------
    print("\n3. Creating Facilities...")
    
    facilities = [
        {"name": "Cardiff Power Plant", "location_region": "Wales, UK", "type": "plant", "organization_id": org_ids[0]},
        {"name": "London Head Office", "location_region": "London, UK", "type": "office", "organization_id": org_ids[0]},
        {"name": "Berlin Factory", "location_region": "Berlin, Germany", "type": "plant", "organization_id": org_ids[1]},
        {"name": "Munich Warehouse", "location_region": "Munich, Germany", "type": "warehouse", "organization_id": org_ids[1]},
        {"name": "Paris Distribution Center", "location_region": "Paris, France", "type": "warehouse", "organization_id": org_ids[2]},
    ]
    
    facility_ids = []
    for facility in facilities:
        response = requests.post(f"{BASE_URL}/facilities/", json=facility)
        if response.status_code == 201:
            fac_id = response.json()["facility_id"]
            facility_ids.append(fac_id)
            print(f"   ✓ Created: {facility['name']} (ID: {fac_id})")
        else:
            print(f"   ✗ Failed to create: {facility['name']}")
    
    # -------------------------------------------------------------------------
    # 4. CREATE SUPPLIERS
    # -------------------------------------------------------------------------
    print("\n4. Creating Suppliers...")
    
    suppliers = [
        {"name": "Steel Solutions Ltd", "category": "Raw Materials"},
        {"name": "Global Plastics Inc", "category": "Raw Materials"},
        {"name": "FastFreight Logistics", "category": "Transport"},
        {"name": "CleanPower Utilities", "category": "Energy"},
    ]
    
    supplier_ids = []
    for supplier in suppliers:
        response = requests.post(f"{BASE_URL}/suppliers/", json=supplier)
        if response.status_code == 201:
            sup_id = response.json()["supplier_id"]
            supplier_ids.append(sup_id)
            print(f"   ✓ Created: {supplier['name']} (ID: {sup_id})")
        else:
            print(f"   ✗ Failed to create: {supplier['name']}")
    
    # -------------------------------------------------------------------------
    # 5. CREATE EMISSION FACTORS
    # -------------------------------------------------------------------------
    print("\n5. Creating Emission Factors...")
    
    emission_factors = [
        {"category": "Natural Gas", "region": "UK", "unit": "kg CO2e/kWh", "value": 0.18387, "valid_from": "2024-01-01", "valid_to": "2024-12-31"},
        {"category": "Diesel", "region": "UK", "unit": "kg CO2e/liter", "value": 2.68787, "valid_from": "2024-01-01", "valid_to": "2024-12-31"},
        {"category": "Petrol", "region": "UK", "unit": "kg CO2e/liter", "value": 2.31485, "valid_from": "2024-01-01", "valid_to": "2024-12-31"},
        {"category": "Electricity", "region": "UK", "unit": "kg CO2e/kWh", "value": 0.20707, "valid_from": "2024-01-01", "valid_to": "2024-12-31"},
        {"category": "Electricity", "region": "Germany", "unit": "kg CO2e/kWh", "value": 0.38500, "valid_from": "2024-01-01", "valid_to": "2024-12-31"},
        {"category": "R-410A", "region": "Global", "unit": "kg CO2e/kg", "value": 2088.0, "valid_from": "2024-01-01", "valid_to": "2024-12-31"},
    ]
    
    factor_ids = []
    for factor in emission_factors:
        response = requests.post(f"{BASE_URL}/emission-factors/", json=factor)
        if response.status_code == 201:
            fac_id = response.json()["factor_id"]
            factor_ids.append(fac_id)
            print(f"   ✓ Created: {factor['category']} - {factor['region']} (ID: {fac_id})")
        else:
            print(f"   ✗ Failed to create: {factor['category']}")
    
    # -------------------------------------------------------------------------
    # 6. CREATE EMISSION ACTIVITIES
    # -------------------------------------------------------------------------
    print("\n6. Creating Emission Activities...")
    
    activities = [
        {"organization_id": org_ids[0], "facility_id": facility_ids[0], "scope": 1, "category": "Fuel Combustion", "activity_date": "2024-01-15", "quantity": 50000, "unit": "kWh", "source_reference": "Invoice #GE-2024-001"},
        {"organization_id": org_ids[0], "facility_id": facility_ids[0], "scope": 1, "category": "Fuel Combustion", "activity_date": "2024-02-15", "quantity": 48000, "unit": "kWh", "source_reference": "Invoice #GE-2024-002"},
        {"organization_id": org_ids[0], "facility_id": facility_ids[1], "scope": 1, "category": "Transport", "activity_date": "2024-01-31", "quantity": 2500, "unit": "liters", "source_reference": "Fleet Log Jan 2024"},
        {"organization_id": org_ids[1], "facility_id": facility_ids[2], "scope": 1, "category": "Fuel Combustion", "activity_date": "2024-01-15", "quantity": 75000, "unit": "kWh", "source_reference": "Invoice #ET-2024-001"},
        {"organization_id": org_ids[1], "facility_id": facility_ids[2], "scope": 1, "category": "Refrigerant", "activity_date": "2024-03-10", "quantity": 5.5, "unit": "kg", "source_reference": "Maintenance Log #ML-2024-015"},
        {"organization_id": org_ids[2], "facility_id": facility_ids[4], "scope": 1, "category": "Transport", "activity_date": "2024-01-31", "quantity": 8500, "unit": "liters", "source_reference": "Fleet Report Q1"},
    ]
    
    activity_ids = []
    for activity in activities:
        response = requests.post(f"{BASE_URL}/emission-activities/", json=activity)
        if response.status_code == 201:
            act_id = response.json()["activity_id"]
            activity_ids.append(act_id)
            print(f"   ✓ Created: Scope {activity['scope']} - {activity['category']} (ID: {act_id})")
        else:
            print(f"   ✗ Failed to create activity: {response.text}")
    
    # -------------------------------------------------------------------------
    # 7. CREATE SCOPE 1 SUBTABLE RECORDS
    # -------------------------------------------------------------------------
    print("\n7. Creating Scope 1 Subtable Records...")
    
    # Stationary Fuels
    stationary_fuels = [
        {"activity_id": activity_ids[0], "fuel_type": "Natural Gas", "quantity": 50000, "unit": "kWh", "factor_id": factor_ids[0]},
        {"activity_id": activity_ids[1], "fuel_type": "Natural Gas", "quantity": 48000, "unit": "kWh", "factor_id": factor_ids[0]},
        {"activity_id": activity_ids[3], "fuel_type": "Natural Gas", "quantity": 75000, "unit": "kWh", "factor_id": factor_ids[0]},
    ]
    
    for fuel in stationary_fuels:
        response = requests.post(f"{BASE_URL}/scope1/stationary-fuels/", json=fuel)
        if response.status_code == 201:
            print(f"   ✓ Created Stationary Fuel: {fuel['fuel_type']} - {fuel['quantity']} {fuel['unit']}")
        else:
            print(f"   ✗ Failed to create stationary fuel: {response.text}")
    
    # Company Vehicles
    company_vehicles = [
        {"activity_id": activity_ids[2], "vehicle_type": "Company Car Fleet", "distance_travelled": 15000, "fuel_consumed": 1200, "factor_id": factor_ids[2]},
        {"activity_id": activity_ids[5], "vehicle_type": "Delivery Trucks", "distance_travelled": 45000, "fuel_consumed": 8500, "factor_id": factor_ids[1]},
    ]
    
    for vehicle in company_vehicles:
        response = requests.post(f"{BASE_URL}/scope1/company-vehicles/", json=vehicle)
        if response.status_code == 201:
            print(f"   ✓ Created Company Vehicle: {vehicle['vehicle_type']}")
        else:
            print(f"   ✗ Failed to create company vehicle: {response.text}")
    
    # Refrigerant Leaks
    refrigerant_leaks = [
        {"activity_id": activity_ids[4], "refrigerant_type": "R-410A", "leak_quantity_kg": 5.5, "gwp_factor": 2088.0},
    ]
    
    for leak in refrigerant_leaks:
        response = requests.post(f"{BASE_URL}/scope1/refrigerant-leaks/", json=leak)
        if response.status_code == 201:
            print(f"   ✓ Created Refrigerant Leak: {leak['refrigerant_type']} - {leak['leak_quantity_kg']} kg")
        else:
            print(f"   ✗ Failed to create refrigerant leak: {response.text}")
    
    # -------------------------------------------------------------------------
    # 8. CREATE EMISSION CALCULATIONS
    # -------------------------------------------------------------------------
    print("\n8. Creating Emission Calculations...")
    
    calculations = [
        {"activity_id": activity_ids[0], "co2e_value": 9.19, "calculation_method": "Emission Factor", "factor_used": "UK Natural Gas 2024"},
        {"activity_id": activity_ids[1], "co2e_value": 8.83, "calculation_method": "Emission Factor", "factor_used": "UK Natural Gas 2024"},
        {"activity_id": activity_ids[2], "co2e_value": 2.78, "calculation_method": "Emission Factor", "factor_used": "UK Petrol 2024"},
        {"activity_id": activity_ids[3], "co2e_value": 13.79, "calculation_method": "Emission Factor", "factor_used": "UK Natural Gas 2024"},
        {"activity_id": activity_ids[4], "co2e_value": 11.48, "calculation_method": "GWP Factor", "factor_used": "R-410A GWP"},
        {"activity_id": activity_ids[5], "co2e_value": 22.85, "calculation_method": "Emission Factor", "factor_used": "UK Diesel 2024"},
    ]
    
    for calc in calculations:
        response = requests.post(f"{BASE_URL}/emission-calculations/", json=calc)
        if response.status_code == 201:
            print(f"   ✓ Created Calculation: {calc['co2e_value']} tonnes CO2e ({calc['calculation_method']})")
        else:
            print(f"   ✗ Failed to create calculation: {response.text}")
    
    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SAMPLE DATA POPULATION COMPLETE!")
    print("=" * 60)
    print("\nSummary:")
    print(f"  - Organizations: {len(org_ids)}")
    print(f"  - Users: {len(users)}")
    print(f"  - Facilities: {len(facility_ids)}")
    print(f"  - Suppliers: {len(supplier_ids)}")
    print(f"  - Emission Factors: {len(factor_ids)}")
    print(f"  - Emission Activities: {len(activity_ids)}")
    print(f"  - Emission Calculations: {len(calculations)}")
    print("\nYou can now test the API at: http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    create_sample_data()