"""
Sample Data Population Script for Carbon Accounting API - SCOPE 1 ONLY
Run with: python populate_sample_data.py

This script populates the database with Scope 1 emission data and demonstrates
the auto-calculation of CO2e emissions using UK GHG Conversion Factors 2025.
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"


def check_api():
    """Check if API is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Connected\n")
            return True
    except:
        pass
    print("❌ API is not running!")
    print("   Start it with: uvicorn main:app --reload")
    return False


def create_organizations():
    """Create sample organizations."""
    print("📁 Creating Organizations...")
    
    organizations = [
        {"name": "Green Energy Corp", "sector": "Energy", "country": "United Kingdom"},
        {"name": "EcoTech Manufacturing", "sector": "Manufacturing", "country": "Germany"},
        {"name": "Sustainable Logistics Ltd", "sector": "Transport", "country": "United Kingdom"},
    ]
    
    org_ids = []
    for org in organizations:
        response = requests.post(f"{BASE_URL}/organizations/", json=org)
        if response.status_code == 201:
            org_id = response.json()["organization_id"]
            org_ids.append(org_id)
            print(f"   ✓ {org['name']} (ID: {org_id})")
        else:
            print(f"   ✗ Failed: {org['name']} - {response.text}")
    
    return org_ids


def create_users(org_ids):
    """Create sample users."""
    print("\n👥 Creating Users...")
    
    users = [
        {"name": "John Smith", "email": "john.smith@greenenergy.com", "role": "Manager", "organization_id": org_ids[0]},
        {"name": "Sarah Johnson", "email": "sarah.j@greenenergy.com", "role": "Analyst", "organization_id": org_ids[0]},
        {"name": "Hans Mueller", "email": "hans.mueller@ecotech.de", "role": "Manager", "organization_id": org_ids[1]},
        {"name": "Emma Wilson", "email": "emma.w@sustainlog.co.uk", "role": "Employee", "organization_id": org_ids[2]},
    ]
    
    for user in users:
        response = requests.post(f"{BASE_URL}/users/", json=user)
        if response.status_code == 201:
            print(f"   ✓ {user['name']} ({user['role']})")
        else:
            print(f"   ✗ Failed: {user['name']}")


def create_facilities(org_ids):
    """Create sample facilities."""
    print("\n🏭 Creating Facilities...")
    
    facilities = [
        {"name": "London Head Office", "location_region": "London, UK", "type": "office", "organization_id": org_ids[0]},
        {"name": "Cardiff Power Station", "location_region": "Cardiff, Wales", "type": "plant", "organization_id": org_ids[0]},
        {"name": "Berlin Factory", "location_region": "Berlin, Germany", "type": "plant", "organization_id": org_ids[1]},
        {"name": "Manchester Warehouse", "location_region": "Manchester, UK", "type": "warehouse", "organization_id": org_ids[2]},
        {"name": "Bristol Distribution Centre", "location_region": "Bristol, UK", "type": "warehouse", "organization_id": org_ids[2]},
    ]
    
    facility_ids = []
    for facility in facilities:
        response = requests.post(f"{BASE_URL}/facilities/", json=facility)
        if response.status_code == 201:
            fac_id = response.json()["facility_id"]
            facility_ids.append(fac_id)
            print(f"   ✓ {facility['name']} (ID: {fac_id})")
        else:
            print(f"   ✗ Failed: {facility['name']}")
    
    return facility_ids


def create_suppliers():
    """Create sample suppliers."""
    print("\n🚚 Creating Suppliers...")
    
    suppliers = [
        {"name": "British Gas Supply", "category": "Energy"},
        {"name": "Shell Fuel Cards", "category": "Fuel"},
        {"name": "BOC Industrial Gases", "category": "Industrial Gas"},
        {"name": "Calor Gas Ltd", "category": "LPG Supplier"},
    ]
    
    supplier_ids = []
    for supplier in suppliers:
        response = requests.post(f"{BASE_URL}/suppliers/", json=supplier)
        if response.status_code == 201:
            sup_id = response.json()["supplier_id"]
            supplier_ids.append(sup_id)
            print(f"   ✓ {supplier['name']} (ID: {sup_id})")
        else:
            print(f"   ✗ Failed: {supplier['name']}")
    
    return supplier_ids


def create_scope1_activities(org_ids, facility_ids):
    """Create Scope 1 emission activities with auto-calculation."""
    print("\n🔥 Creating SCOPE 1 Emission Activities (with Auto-Calculation)...")
    print("   Using UK GHG Conversion Factors 2025\n")
    
    activities = [
        # Stationary Combustion - Natural Gas
        {
            "organization_id": org_ids[0],
            "facility_id": facility_ids[0],
            "scope": 1,
            "category": "Natural Gas",
            "activity_date": "2025-01-15",
            "quantity": 50000,
            "unit": "kWh (Net CV)",
            "source_reference": "Gas Bill - London Office Jan 2025"
        },
        {
            "organization_id": org_ids[0],
            "facility_id": facility_ids[1],
            "scope": 1,
            "category": "Natural Gas",
            "activity_date": "2025-01-31",
            "quantity": 150000,
            "unit": "kWh (Net CV)",
            "source_reference": "Gas Bill - Cardiff Power Station Jan 2025"
        },
        # Stationary Combustion - LPG
        {
            "organization_id": org_ids[1],
            "facility_id": facility_ids[2],
            "scope": 1,
            "category": "LPG",
            "activity_date": "2025-01-20",
            "quantity": 2000,
            "unit": "litres",
            "source_reference": "LPG Invoice - Berlin Factory"
        },
        # Mobile Combustion - Diesel Fleet
        {
            "organization_id": org_ids[2],
            "facility_id": facility_ids[3],
            "scope": 1,
            "category": "Diesel",
            "activity_date": "2025-01-31",
            "quantity": 5000,
            "unit": "litres",
            "source_reference": "Fleet Fuel Log - Manchester Jan 2025"
        },
        {
            "organization_id": org_ids[2],
            "facility_id": facility_ids[4],
            "scope": 1,
            "category": "Diesel",
            "activity_date": "2025-01-31",
            "quantity": 3500,
            "unit": "litres",
            "source_reference": "Fleet Fuel Log - Bristol Jan 2025"
        },
        # Mobile Combustion - Petrol
        {
            "organization_id": org_ids[0],
            "facility_id": facility_ids[0],
            "scope": 1,
            "category": "Petrol",
            "activity_date": "2025-01-31",
            "quantity": 800,
            "unit": "litres",
            "source_reference": "Company Car Fuel - Jan 2025"
        },
        # Gas Oil for backup generators
        {
            "organization_id": org_ids[1],
            "facility_id": facility_ids[2],
            "scope": 1,
            "category": "Gas Oil",
            "activity_date": "2025-01-25",
            "quantity": 500,
            "unit": "litres",
            "source_reference": "Backup Generator Fuel"
        },
    ]
    
    activity_ids = []
    for activity in activities:
        response = requests.post(f"{BASE_URL}/emission-activities/", json=activity)
        if response.status_code == 201:
            data = response.json()
            act_id = data["activity_id"]
            activity_ids.append(act_id)
            print(f"   ✓ {activity['category']} - {activity['quantity']:,} {activity['unit']}")
            
            # Check if calculation was auto-created
            calc_response = requests.get(f"{BASE_URL}/emission-calculations/")
            if calc_response.status_code == 200:
                calcs = calc_response.json()
                for calc in calcs:
                    if calc["activity_id"] == act_id:
                        co2e_val = float(calc['co2e_value']) if calc['co2e_value'] else 0
                        print(f"     → Auto-calculated: {co2e_val:,.2f} kg CO2e")
                        print(f"     → Factor: {calc['factor_used']}")
                        break
        else:
            print(f"   ✗ Failed: {activity['category']} - {response.text}")
    
    return activity_ids


def create_scope1_details(org_ids):
    """Create Scope 1 subtable records (Stationary Fuels, Vehicles, Refrigerants, Process)."""
    print("\n📋 Creating SCOPE 1 Detail Records...")
    
    # =====================
    # STATIONARY FUELS
    # =====================
    print("\n   🔥 Stationary Fuels:")
    
    # Create activity for boiler
    activity_response = requests.post(f"{BASE_URL}/emission-activities/", json={
        "organization_id": org_ids[0],
        "scope": 1,
        "category": "Stationary Combustion - Boiler",
        "activity_date": "2025-02-01",
        "quantity": 25000,
        "unit": "kWh",
        "source_reference": "Main Boiler Gas Usage Feb 2025"
    })
    
    if activity_response.status_code == 201:
        act_id = activity_response.json()["activity_id"]
        
        fuel_response = requests.post(f"{BASE_URL}/scope1/stationary-fuels/", json={
            "activity_id": act_id,
            "fuel_type": "Natural Gas",
            "quantity": 25000,
            "unit": "kWh (Net CV)"
        })
        
        if fuel_response.status_code == 201:
            print(f"      ✓ Natural Gas Boiler: 25,000 kWh")
            calc_response = requests.get(f"{BASE_URL}/emission-calculations/")
            for calc in calc_response.json():
                if calc["activity_id"] == act_id:
                    co2e_val = float(calc['co2e_value']) if calc['co2e_value'] else 0
                    print(f"        → CO2e: {co2e_val:,.2f} kg")
                    break

    # Create activity for LPG heating
    activity_response = requests.post(f"{BASE_URL}/emission-activities/", json={
        "organization_id": org_ids[1],
        "scope": 1,
        "category": "Stationary Combustion - Heating",
        "activity_date": "2025-02-01",
        "quantity": 1500,
        "unit": "litres",
        "source_reference": "LPG Heating System Feb 2025"
    })
    
    if activity_response.status_code == 201:
        act_id = activity_response.json()["activity_id"]
        
        fuel_response = requests.post(f"{BASE_URL}/scope1/stationary-fuels/", json={
            "activity_id": act_id,
            "fuel_type": "LPG",
            "quantity": 1500,
            "unit": "litres"
        })
        
        if fuel_response.status_code == 201:
            print(f"      ✓ LPG Heating: 1,500 litres")
            calc_response = requests.get(f"{BASE_URL}/emission-calculations/")
            for calc in calc_response.json():
                if calc["activity_id"] == act_id:
                    co2e_val = float(calc['co2e_value']) if calc['co2e_value'] else 0
                    print(f"        → CO2e: {co2e_val:,.2f} kg")
                    break

    # =====================
    # COMPANY VEHICLES
    # =====================
    print("\n   🚗 Company Vehicles:")
    
    vehicles = [
        {"type": "Delivery Van - Diesel", "distance": 5000, "fuel": 450, "org": org_ids[2]},
        {"type": "Company Car - Petrol", "distance": 2500, "fuel": 200, "org": org_ids[0]},
        {"type": "HGV - Diesel", "distance": 8000, "fuel": 1200, "org": org_ids[2]},
    ]
    
    for vehicle in vehicles:
        activity_response = requests.post(f"{BASE_URL}/emission-activities/", json={
            "organization_id": vehicle["org"],
            "scope": 1,
            "category": f"Mobile Combustion - {vehicle['type']}",
            "activity_date": "2025-02-15",
            "quantity": vehicle["fuel"],
            "unit": "litres",
            "source_reference": f"Vehicle Log - {vehicle['type']}"
        })
        
        if activity_response.status_code == 201:
            act_id = activity_response.json()["activity_id"]
            
            veh_response = requests.post(f"{BASE_URL}/scope1/company-vehicles/", json={
                "activity_id": act_id,
                "vehicle_type": vehicle["type"],
                "distance_travelled": vehicle["distance"],
                "fuel_consumed": vehicle["fuel"]
            })
            
            if veh_response.status_code == 201:
                print(f"      ✓ {vehicle['type']}: {vehicle['distance']:,} km, {vehicle['fuel']} L fuel")

    # =====================
    # REFRIGERANT LEAKS
    # =====================
    print("\n   ❄️  Refrigerant Leaks:")
    
    refrigerants = [
        {"type": "R-410A", "quantity": 3.5, "org": org_ids[0], "location": "Office AC Units"},
        {"type": "R-134a", "quantity": 2.0, "org": org_ids[1], "location": "Factory Chillers"},
        {"type": "R-404A", "quantity": 5.0, "org": org_ids[2], "location": "Warehouse Refrigeration"},
    ]
    
    for ref in refrigerants:
        activity_response = requests.post(f"{BASE_URL}/emission-activities/", json={
            "organization_id": ref["org"],
            "scope": 1,
            "category": f"Fugitive Emissions - {ref['type']}",
            "activity_date": "2025-02-20",
            "quantity": ref["quantity"],
            "unit": "kg",
            "source_reference": f"Refrigerant Top-up Log - {ref['location']}"
        })
        
        if activity_response.status_code == 201:
            act_id = activity_response.json()["activity_id"]
            
            leak_response = requests.post(f"{BASE_URL}/scope1/refrigerant-leaks/", json={
                "activity_id": act_id,
                "refrigerant_type": ref["type"],
                "leak_quantity_kg": ref["quantity"]
            })
            
            if leak_response.status_code == 201:
                data = leak_response.json()
                gwp = data.get("gwp_factor", "N/A")
                print(f"      ✓ {ref['type']}: {ref['quantity']} kg (GWP: {gwp})")
                
                calc_response = requests.get(f"{BASE_URL}/emission-calculations/")
                for calc in calc_response.json():
                    if calc["activity_id"] == act_id:
                        co2e_val = float(calc['co2e_value']) if calc['co2e_value'] else 0
                        print(f"        → CO2e: {co2e_val:,.2f} kg")
                        break

    # =====================
    # PROCESS EMISSIONS
    # =====================
    print("\n   ⚙️  Process Emissions:")
    
    activity_response = requests.post(f"{BASE_URL}/emission-activities/", json={
        "organization_id": org_ids[1],
        "scope": 1,
        "category": "Process Emissions - Cement",
        "activity_date": "2025-02-25",
        "quantity": 100,
        "unit": "tonnes",
        "source_reference": "Production Log Feb 2025"
    })
    
    if activity_response.status_code == 201:
        act_id = activity_response.json()["activity_id"]
        
        process_response = requests.post(f"{BASE_URL}/scope1/process-emissions/", json={
            "activity_id": act_id,
            "material_type": "Iteite clinite",
            "quantity_processed": 100
        })
        
        if process_response.status_code == 201:
            print(f"      ✓ite clinite processing: 100 tonnes")


def show_summary():
    """Display Scope 1 emissions summary."""
    print("\n" + "=" * 60)
    print("📈 SCOPE 1 EMISSIONS SUMMARY")
    print("=" * 60)
    
    # Get summary by scope
    response = requests.get(f"{BASE_URL}/emission-calculations/by-scope")
    if response.status_code == 200:
        scopes = response.json()
        
        for scope in scopes:
            if scope['scope'] == 1:
                print(f"\n   🔥 SCOPE 1 - Direct Emissions:")
                print(f"      Activities: {scope['activity_count']}")
                print(f"      Total CO2e: {scope['total_co2e_kg']:,.2f} kg")
                print(f"      Total CO2e: {scope['total_co2e_tonnes']:,.4f} tonnes")
    
    # Get by category
    print("\n\n📊 SCOPE 1 BY CATEGORY:")
    response = requests.get(f"{BASE_URL}/emission-calculations/by-category")
    if response.status_code == 200:
        categories = response.json()
        scope1_categories = [c for c in categories if c['scope'] == 1]
        for cat in scope1_categories:
            print(f"   • {cat['category']}: {cat['total_co2e_kg']:,.2f} kg CO2e ({cat['activity_count']} activities)")


def main():
    print("=" * 60)
    print("🌱 CARBON ACCOUNTING - SCOPE 1 SAMPLE DATA")
    print("=" * 60)
    print()
    
    if not check_api():
        sys.exit(1)
    
    # Create master data
    org_ids = create_organizations()
    if not org_ids:
        print("❌ Failed to create organizations. Exiting.")
        sys.exit(1)
    
    create_users(org_ids)
    facility_ids = create_facilities(org_ids)
    create_suppliers()
    
    # Create Scope 1 emission activities
    activity_ids = create_scope1_activities(org_ids, facility_ids)
    
    # Create Scope 1 detail records
    create_scope1_details(org_ids)
    
    # Show summary
    show_summary()
    
    print("\n" + "=" * 60)
    print("✅ SCOPE 1 SAMPLE DATA COMPLETE!")
    print("=" * 60)
    print("\n🌐 View your data:")
    print("   • Frontend: Open frontend/index.html in browser")
    print("   • API Docs: http://127.0.0.1:8000/docs")
    print("   • Scope 1 Summary: http://127.0.0.1:8000/emission-calculations/by-scope")


if __name__ == "__main__":
    main()