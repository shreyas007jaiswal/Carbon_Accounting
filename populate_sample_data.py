"""
Sample Data Population Script for Carbon Accounting API
Based on Data_Model_for_Carbon_Accounting.xlsx

Run with: python populate_sample_data.py

Creates sample data for:
- Master Tables: Organization, User, Facility, Supplier
- Scope 1 Activities and Subtables: Stationary Fuel, Company Vehicle, Refrigerant Leak, Process Emission
- Auto-calculates CO2e using UK GHG Conversion Factors 2025
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
    """Create sample organizations based on Excel example data."""
    print("=" * 60)
    print("📁 MASTER TABLE: Organization")
    print("=" * 60)
    
    # From Excel: organization_id, Name, Sector, Country
    organizations = [
        {"name": "GreenTech Ltd", "sector": "Manufacturing", "country": "USA"},
        {"name": "EcoEnergy Pvt Ltd", "sector": "Energy", "country": "India"},
        {"name": "Carbon Solutions UK", "sector": "Consulting", "country": "United Kingdom"},
    ]
    
    org_ids = []
    print(f"\n   {'ID':<4} {'Name':<25} {'Sector':<20} {'Country':<15}")
    print("   " + "-" * 64)
    
    for org in organizations:
        response = requests.post(f"{BASE_URL}/organizations/", json=org)
        if response.status_code == 201:
            org_id = response.json()["organization_id"]
            org_ids.append(org_id)
            print(f"   {org_id:<4} {org['name']:<25} {org['sector']:<20} {org['country']:<15}")
        else:
            print(f"   ✗ Failed: {org['name']} - {response.text}")
    
    return org_ids


def create_users(org_ids):
    """Create sample users based on Excel example data."""
    print("\n" + "=" * 60)
    print("👥 MASTER TABLE: User")
    print("=" * 60)
    
    # From Excel: user_id, organization_id, name, email, role
    users = [
        {"name": "John", "email": "john@greentech.com", "role": "Sustainability Manager", "organization_id": org_ids[0]},
        {"name": "Mary", "email": "mary@greentech.com", "role": "Sustainability Executive", "organization_id": org_ids[0]},
        {"name": "Raj", "email": "raj@ecoenergy.in", "role": "Analyst", "organization_id": org_ids[1]},
        {"name": "Sarah", "email": "sarah@carbonsolutions.uk", "role": "Manager", "organization_id": org_ids[2]},
    ]
    
    print(f"\n   {'ID':<4} {'Name':<15} {'Email':<30} {'Role':<25}")
    print("   " + "-" * 74)
    
    for user in users:
        response = requests.post(f"{BASE_URL}/users/", json=user)
        if response.status_code == 201:
            user_id = response.json()["user_id"]
            print(f"   {user_id:<4} {user['name']:<15} {user['email']:<30} {user['role']:<25}")
        else:
            print(f"   ✗ Failed: {user['name']}")


def create_facilities(org_ids):
    """Create sample facilities based on Excel example data."""
    print("\n" + "=" * 60)
    print("🏭 MASTER TABLE: Facility")
    print("=" * 60)
    
    # From Excel: facility_id, organization_id, name, location/Region, type
    facilities = [
        {"name": "Plant A", "location_region": "Texas", "type": "Manufacturing Plant", "organization_id": org_ids[0]},
        {"name": "HQ", "location_region": "New York", "type": "Office", "organization_id": org_ids[0]},
        {"name": "Solar Park", "location_region": "Rajasthan", "type": "Renewable Plant", "organization_id": org_ids[1]},
        {"name": "Data Centre", "location_region": "Mumbai", "type": "Office", "organization_id": org_ids[1]},
        {"name": "London Office", "location_region": "London", "type": "Office", "organization_id": org_ids[2]},
    ]
    
    facility_ids = []
    print(f"\n   {'ID':<4} {'Name':<20} {'Location':<15} {'Type':<20}")
    print("   " + "-" * 59)
    
    for facility in facilities:
        response = requests.post(f"{BASE_URL}/facilities/", json=facility)
        if response.status_code == 201:
            fac_id = response.json()["facility_id"]
            facility_ids.append(fac_id)
            print(f"   {fac_id:<4} {facility['name']:<20} {facility['location_region']:<15} {facility['type']:<20}")
        else:
            print(f"   ✗ Failed: {facility['name']}")
    
    return facility_ids


def create_suppliers():
    """Create sample suppliers based on Excel example data."""
    print("\n" + "=" * 60)
    print("🚚 MASTER TABLE: Supplier")
    print("=" * 60)
    
    # From Excel: supplier_id, name, Category
    suppliers = [
        {"name": "ABC Steel Corp", "category": "Procurement (steel)"},
        {"name": "Global Plastics", "category": "Procurement (plastic)"},
        {"name": "FastLogistics", "category": "Logistics"},
        {"name": "British Gas", "category": "Energy"},
    ]
    
    supplier_ids = []
    print(f"\n   {'ID':<4} {'Name':<25} {'Category':<25}")
    print("   " + "-" * 54)
    
    for supplier in suppliers:
        response = requests.post(f"{BASE_URL}/suppliers/", json=supplier)
        if response.status_code == 201:
            sup_id = response.json()["supplier_id"]
            supplier_ids.append(sup_id)
            print(f"   {sup_id:<4} {supplier['name']:<25} {supplier['category']:<25}")
        else:
            print(f"   ✗ Failed: {supplier['name']}")
    
    return supplier_ids


def create_scope1_stationary_fuels(org_ids, facility_ids):
    """Create Scope 1 Stationary Fuel activities."""
    print("\n" + "=" * 60)
    print("🔥 SCOPE 1: Stationary Fuel Combustion")
    print("=" * 60)
    
    stationary_fuels = [
        # Gaseous Fuels
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[0],
                "scope": 1,
                "category": "Stationary Combustion",
                "activity_date": "2025-01-31",
                "quantity": 100000,
                "unit": "kWh (Net CV)",
                "source_reference": "Gas Bill - Plant A Jan 2025"
            },
            "fuel": {
                "fuel_category": "Gaseous",
                "fuel_type": "Natural Gas",
                "quantity": 100000,
                "unit": "kWh (Net CV)"
            }
        },
        {
            "activity": {
                "organization_id": org_ids[1],
                "facility_id": facility_ids[3],
                "scope": 1,
                "category": "Stationary Combustion",
                "activity_date": "2025-01-31",
                "quantity": 5000,
                "unit": "litres",
                "source_reference": "LPG Invoice - Data Centre Jan 2025"
            },
            "fuel": {
                "fuel_category": "Gaseous",
                "fuel_type": "LPG",
                "quantity": 5000,
                "unit": "litres"
            }
        },
        # Liquid Fuels
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[0],
                "scope": 1,
                "category": "Stationary Combustion",
                "activity_date": "2025-01-31",
                "quantity": 2000,
                "unit": "litres",
                "source_reference": "Diesel Generator - Plant A Jan 2025"
            },
            "fuel": {
                "fuel_category": "Liquid",
                "fuel_type": "Diesel",
                "quantity": 2000,
                "unit": "litres"
            }
        },
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[1],
                "scope": 1,
                "category": "Stationary Combustion",
                "activity_date": "2025-01-31",
                "quantity": 500,
                "unit": "litres",
                "source_reference": "Gas Oil - HQ Backup Generator Jan 2025"
            },
            "fuel": {
                "fuel_category": "Liquid",
                "fuel_type": "Gas Oil",
                "quantity": 500,
                "unit": "litres"
            }
        },
    ]
    
    print(f"\n   {'Facility':<20} {'Fuel Category':<12} {'Fuel Type':<15} {'Quantity':<15} {'CO2e (kg)':<15}")
    print("   " + "-" * 77)
    
    for item in stationary_fuels:
        # Create activity
        act_response = requests.post(f"{BASE_URL}/emission-activities/", json=item["activity"])
        if act_response.status_code == 201:
            act_id = act_response.json()["activity_id"]
            
            # Create stationary fuel record
            item["fuel"]["activity_id"] = act_id
            fuel_response = requests.post(f"{BASE_URL}/scope1/stationary-fuels/", json=item["fuel"])
            
            if fuel_response.status_code == 201:
                # Get CO2e calculation
                calc_response = requests.get(f"{BASE_URL}/emission-calculations/")
                co2e = "-"
                for calc in calc_response.json():
                    if calc["activity_id"] == act_id:
                        co2e = f"{float(calc['co2e_value']):,.2f}"
                        break
                
                fac_name = f"Facility {item['activity']['facility_id']}"
                print(f"   {fac_name:<20} {item['fuel']['fuel_category']:<12} {item['fuel']['fuel_type']:<15} {item['fuel']['quantity']:>10} {item['fuel']['unit']:<5} {co2e:>12}")


def create_scope1_vehicles(org_ids, facility_ids):
    """Create Scope 1 Company Vehicle activities."""
    print("\n" + "=" * 60)
    print("🚗 SCOPE 1: Company Vehicles (Mobile Combustion)")
    print("=" * 60)
    
    vehicles = [
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[0],
                "scope": 1,
                "category": "Mobile Combustion",
                "activity_date": "2025-01-31",
                "quantity": 1500,
                "unit": "litres",
                "source_reference": "Fleet Fuel Card - Jan 2025"
            },
            "vehicle": {
                "vehicle_type": "Delivery Van",
                "vehicle_size": "Medium",
                "fuel_type": "Diesel",
                "distance_travelled": 12000,
                "fuel_consumed": 1500
            }
        },
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[1],
                "scope": 1,
                "category": "Mobile Combustion",
                "activity_date": "2025-01-31",
                "quantity": 300,
                "unit": "litres",
                "source_reference": "Company Car Fuel - HQ Jan 2025"
            },
            "vehicle": {
                "vehicle_type": "Company Car",
                "vehicle_size": "Medium",
                "fuel_type": "Petrol",
                "distance_travelled": 4000,
                "fuel_consumed": 300
            }
        },
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[0],
                "scope": 1,
                "category": "Mobile Combustion",
                "activity_date": "2025-01-31",
                "quantity": 3000,
                "unit": "litres",
                "source_reference": "HGV Fleet - Plant A Jan 2025"
            },
            "vehicle": {
                "vehicle_type": "HGV",
                "vehicle_size": "Large",
                "fuel_type": "Diesel",
                "distance_travelled": 8000,
                "fuel_consumed": 3000
            }
        },
        {
            "activity": {
                "organization_id": org_ids[2],
                "facility_id": facility_ids[4],
                "scope": 1,
                "category": "Mobile Combustion",
                "activity_date": "2025-01-31",
                "quantity": 150,
                "unit": "litres",
                "source_reference": "Pool Car - London Office Jan 2025"
            },
            "vehicle": {
                "vehicle_type": "Company Car",
                "vehicle_size": "Small",
                "fuel_type": "Petrol",
                "distance_travelled": 2000,
                "fuel_consumed": 150
            }
        },
    ]
    
    print(f"\n   {'Vehicle Type':<15} {'Size':<10} {'Fuel':<10} {'Distance (km)':<15} {'Fuel (L)':<12}")
    print("   " + "-" * 62)
    
    for item in vehicles:
        act_response = requests.post(f"{BASE_URL}/emission-activities/", json=item["activity"])
        if act_response.status_code == 201:
            act_id = act_response.json()["activity_id"]
            
            item["vehicle"]["activity_id"] = act_id
            veh_response = requests.post(f"{BASE_URL}/scope1/company-vehicles/", json=item["vehicle"])
            
            if veh_response.status_code == 201:
                v = item["vehicle"]
                print(f"   {v['vehicle_type']:<15} {v['vehicle_size']:<10} {v['fuel_type']:<10} {v['distance_travelled']:>12,.0f} {v['fuel_consumed']:>12,.0f}")


def create_scope1_refrigerants(org_ids, facility_ids):
    """Create Scope 1 Refrigerant Leak activities."""
    print("\n" + "=" * 60)
    print("❄️  SCOPE 1: Refrigerant Leaks (Fugitive Emissions)")
    print("=" * 60)
    
    refrigerants = [
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[1],
                "scope": 1,
                "category": "Fugitive Emissions",
                "activity_date": "2025-01-15",
                "quantity": 2.5,
                "unit": "kg",
                "source_reference": "AC Maintenance Log - HQ Jan 2025"
            },
            "refrigerant": {
                "refrigerant_category": "HFC",
                "refrigerant_type": "R-410A",
                "leak_quantity_kg": 2.5
            }
        },
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[0],
                "scope": 1,
                "category": "Fugitive Emissions",
                "activity_date": "2025-01-20",
                "quantity": 5.0,
                "unit": "kg",
                "source_reference": "Chiller Top-up - Plant A Jan 2025"
            },
            "refrigerant": {
                "refrigerant_category": "HFC",
                "refrigerant_type": "R-134a",
                "leak_quantity_kg": 5.0
            }
        },
        {
            "activity": {
                "organization_id": org_ids[1],
                "facility_id": facility_ids[3],
                "scope": 1,
                "category": "Fugitive Emissions",
                "activity_date": "2025-01-25",
                "quantity": 8.0,
                "unit": "kg",
                "source_reference": "Server Room Cooling - Data Centre Jan 2025"
            },
            "refrigerant": {
                "refrigerant_category": "HFC",
                "refrigerant_type": "R-404A",
                "leak_quantity_kg": 8.0
            }
        },
    ]
    
    print(f"\n   {'Refrigerant':<12} {'Category':<10} {'Leak (kg)':<12} {'GWP':<10} {'CO2e (kg)':<15}")
    print("   " + "-" * 59)
    
    for item in refrigerants:
        act_response = requests.post(f"{BASE_URL}/emission-activities/", json=item["activity"])
        if act_response.status_code == 201:
            act_id = act_response.json()["activity_id"]
            
            item["refrigerant"]["activity_id"] = act_id
            ref_response = requests.post(f"{BASE_URL}/scope1/refrigerant-leaks/", json=item["refrigerant"])
            
            if ref_response.status_code == 201:
                data = ref_response.json()
                gwp = data.get("gwp_factor", "-")
                
                # Get CO2e
                calc_response = requests.get(f"{BASE_URL}/emission-calculations/")
                co2e = "-"
                for calc in calc_response.json():
                    if calc["activity_id"] == act_id:
                        co2e = f"{float(calc['co2e_value']):,.2f}"
                        break
                
                r = item["refrigerant"]
                print(f"   {r['refrigerant_type']:<12} {r['refrigerant_category']:<10} {r['leak_quantity_kg']:>10,.1f} {str(gwp):>10} {co2e:>12}")


def create_scope1_process(org_ids, facility_ids):
    """Create Scope 1 Process Emission activities."""
    print("\n" + "=" * 60)
    print("⚙️  SCOPE 1: Process Emissions")
    print("=" * 60)
    
    processes = [
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[0],
                "scope": 1,
                "category": "Process Emissions",
                "activity_date": "2025-01-31",
                "quantity": 500,
                "unit": "tonnes",
                "source_reference": "Production Log - Plant A Jan 2025"
            },
            "process": {
                "material_category": "ite Clinker",
                "material_type": "Portlandite cliniter",
                "quantity_processed": 500,
                "unit": "tonnes"
            }
        },
        {
            "activity": {
                "organization_id": org_ids[0],
                "facility_id": facility_ids[0],
                "scope": 1,
                "category": "Process Emissions",
                "activity_date": "2025-01-31",
                "quantity": 200,
                "unit": "tonnes",
                "source_reference": "Chemical Process - Plant A Jan 2025"
            },
            "process": {
                "material_category": "Calcium Carbide",
                "material_type": "Calcium Carbide Production",
                "quantity_processed": 200,
                "unit": "tonnes"
            }
        },
    ]
    
    print(f"\n   {'Material Category':<20} {'Material Type':<25} {'Quantity':<15}")
    print("   " + "-" * 60)
    
    for item in processes:
        act_response = requests.post(f"{BASE_URL}/emission-activities/", json=item["activity"])
        if act_response.status_code == 201:
            act_id = act_response.json()["activity_id"]
            
            item["process"]["activity_id"] = act_id
            proc_response = requests.post(f"{BASE_URL}/scope1/process-emissions/", json=item["process"])
            
            if proc_response.status_code == 201:
                p = item["process"]
                print(f"   {p['material_category']:<20} {p['material_type']:<25} {p['quantity_processed']:>10,.0f} {p['unit']}")


def show_summary():
    """Display emissions summary."""
    print("\n" + "=" * 60)
    print("📈 SCOPE 1 EMISSIONS SUMMARY")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/emission-calculations/by-scope")
    if response.status_code == 200:
        scopes = response.json()
        
        for scope in scopes:
            if scope['scope'] == 1:
                print(f"\n   Total Scope 1 Emissions:")
                print(f"   ─────────────────────────────────")
                print(f"   Activities:     {scope['activity_count']}")
                print(f"   Total CO2e:     {scope['total_co2e_kg']:,.2f} kg")
                print(f"   Total CO2e:     {scope['total_co2e_tonnes']:,.4f} tonnes")
    
    print("\n   By Category:")
    print("   ─────────────────────────────────")
    response = requests.get(f"{BASE_URL}/emission-calculations/by-category")
    if response.status_code == 200:
        categories = response.json()
        scope1_cats = [c for c in categories if c['scope'] == 1]
        for cat in scope1_cats:
            print(f"   • {cat['category']:<30} {cat['total_co2e_kg']:>12,.2f} kg CO2e")


def main():
    print("\n" + "=" * 60)
    print("🌱 CARBON ACCOUNTING - SAMPLE DATA")
    print("   Based on Data_Model_for_Carbon_Accounting.xlsx")
    print("=" * 60)
    print()
    
    if not check_api():
        sys.exit(1)
    
    # Create Master Tables
    org_ids = create_organizations()
    if not org_ids:
        print("❌ Failed to create organizations. Exiting.")
        sys.exit(1)
    
    create_users(org_ids)
    facility_ids = create_facilities(org_ids)
    create_suppliers()
    
    # Create Scope 1 Activities and Subtables
    create_scope1_stationary_fuels(org_ids, facility_ids)
    create_scope1_vehicles(org_ids, facility_ids)
    create_scope1_refrigerants(org_ids, facility_ids)
    create_scope1_process(org_ids, facility_ids)
    
    # Show Summary
    show_summary()
    
    print("\n" + "=" * 60)
    print("✅ SAMPLE DATA POPULATION COMPLETE!")
    print("=" * 60)
    print("\n🌐 View your data:")
    print("   • Frontend: Open frontend/index.html in browser")
    print("   • API Docs: http://127.0.0.1:8000/docs")
    print("   • Summary:  http://127.0.0.1:8000/emission-calculations/by-scope")
    print()


if __name__ == "__main__":
    main()
