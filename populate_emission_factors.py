"""
Script to populate emission factors from UK GHG Conversion Factors 2025
Run with: python populate_emission_factors.py

This script extracts emission factors from the official UK Government
GHG Conversion Factors spreadsheet and inserts them into the carbon_accounting database.
"""

import pandas as pd
import requests
import sys

BASE_URL = 'http://127.0.0.1:8000'
EXCEL_FILE = 'ghg-conversion-factors-2025-full-set.xlsx'

def create_emission_factor(data):
    """Create an emission factor via API."""
    try:
        response = requests.post(f"{BASE_URL}/emission-factors/", json=data)
        if response.status_code == 201:
            return True
        else:
            print(f"   ✗ Failed: {data['category']} - {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {data['category']} - {e}")
        return False


def extract_fuels(excel_file):
    """Extract fuel emission factors."""
    print("\n📊 Extracting Fuels...")
    
    df = pd.read_excel(excel_file, sheet_name='Fuels', header=21)
    
    factors = []
    current_activity = None
    current_fuel = None
    
    for _, row in df.iterrows():
        # Update activity if present
        if pd.notna(row['Activity']):
            current_activity = str(row['Activity']).strip()
        
        # Update fuel if present
        if pd.notna(row['Fuel']):
            current_fuel = str(row['Fuel']).strip()
        
        # Skip if no fuel or unit
        if not current_fuel or pd.isna(row['Unit']) or pd.isna(row['kg CO2e']):
            continue
        
        try:
            value = float(row['kg CO2e'])
            unit = str(row['Unit']).strip()
            
            factors.append({
                'category': f"{current_fuel}",
                'region': 'UK',
                'unit': f"kg CO2e/{unit}",
                'value': value,
                'valid_from': '2025-01-01',
                'valid_to': '2025-12-31'
            })
        except (ValueError, TypeError):
            continue
    
    return factors


def extract_refrigerants(excel_file):
    """Extract refrigerant GWP factors."""
    print("\n📊 Extracting Refrigerants...")
    
    df = pd.read_excel(excel_file, sheet_name='Refrigerant & other', header=18)
    
    factors = []
    
    for _, row in df.iterrows():
        emission = row.get('Emission') or row.get(df.columns[1])
        
        if pd.isna(emission):
            continue
        
        # Get the total kg CO2e value (last column with values)
        try:
            # Try different column names
            value = None
            for col in df.columns:
                if 'Total' in str(col) or col == df.columns[-2]:
                    if pd.notna(row[col]):
                        value = float(row[col])
                        break
            
            if value is None:
                # Try the 5th column (index 4) which usually has the total
                value = float(row[df.columns[5]]) if pd.notna(row[df.columns[5]]) else None
            
            if value is None:
                continue
                
            emission_name = str(emission).strip()
            
            factors.append({
                'category': emission_name,
                'region': 'Global',
                'unit': 'kg CO2e/kg',
                'value': value,
                'valid_from': '2025-01-01',
                'valid_to': '2025-12-31'
            })
        except (ValueError, TypeError):
            continue
    
    return factors


def extract_uk_electricity(excel_file):
    """Extract UK electricity emission factors."""
    print("\n📊 Extracting UK Electricity...")
    
    factors = [{
        'category': 'UK Electricity',
        'region': 'UK',
        'unit': 'kg CO2e/kWh',
        'value': 0.177,  # 2025 value from the spreadsheet
        'valid_from': '2025-01-01',
        'valid_to': '2025-12-31'
    }]
    
    return factors


def extract_passenger_vehicles(excel_file):
    """Extract passenger vehicle emission factors."""
    print("\n📊 Extracting Passenger Vehicles...")
    
    df = pd.read_excel(excel_file, sheet_name='Passenger vehicles', header=None)
    
    # Find header row
    header_row = None
    for i, row in df.iterrows():
        if 'kg CO2e' in str(row.values):
            header_row = i
            break
    
    if header_row is None:
        return []
    
    df = pd.read_excel(excel_file, sheet_name='Passenger vehicles', header=header_row)
    
    factors = []
    current_vehicle = None
    
    for _, row in df.iterrows():
        # Get vehicle type
        vehicle_col = df.columns[1] if len(df.columns) > 1 else None
        if vehicle_col and pd.notna(row[vehicle_col]):
            current_vehicle = str(row[vehicle_col]).strip()
        
        if not current_vehicle:
            continue
        
        # Get unit and value
        unit_col = df.columns[2] if len(df.columns) > 2 else None
        value_col = 'kg CO2e' if 'kg CO2e' in df.columns else df.columns[3] if len(df.columns) > 3 else None
        
        if not unit_col or not value_col:
            continue
            
        if pd.isna(row[unit_col]) or pd.isna(row[value_col]):
            continue
        
        try:
            value = float(row[value_col])
            unit = str(row[unit_col]).strip()
            
            # Only include km-based factors for simplicity
            if 'km' in unit.lower():
                factors.append({
                    'category': f"Vehicle - {current_vehicle}",
                    'region': 'UK',
                    'unit': f"kg CO2e/{unit}",
                    'value': value,
                    'valid_from': '2025-01-01',
                    'valid_to': '2025-12-31'
                })
        except (ValueError, TypeError):
            continue
    
    return factors


def extract_delivery_vehicles(excel_file):
    """Extract delivery vehicle emission factors."""
    print("\n📊 Extracting Delivery Vehicles...")
    
    df = pd.read_excel(excel_file, sheet_name='Delivery vehicles', header=None)
    
    # Find header row
    header_row = None
    for i, row in df.iterrows():
        if 'kg CO2e' in str(row.values):
            header_row = i
            break
    
    if header_row is None:
        return []
    
    df = pd.read_excel(excel_file, sheet_name='Delivery vehicles', header=header_row)
    
    factors = []
    current_vehicle = None
    
    for _, row in df.iterrows():
        vehicle_col = df.columns[1] if len(df.columns) > 1 else None
        if vehicle_col and pd.notna(row[vehicle_col]):
            current_vehicle = str(row[vehicle_col]).strip()
        
        if not current_vehicle:
            continue
        
        unit_col = df.columns[2] if len(df.columns) > 2 else None
        value_col = 'kg CO2e' if 'kg CO2e' in df.columns else df.columns[3] if len(df.columns) > 3 else None
        
        if not unit_col or not value_col:
            continue
            
        if pd.isna(row[unit_col]) or pd.isna(row[value_col]):
            continue
        
        try:
            value = float(row[value_col])
            unit = str(row[unit_col]).strip()
            
            if 'km' in unit.lower() or 'tonne' in unit.lower():
                factors.append({
                    'category': f"Delivery - {current_vehicle}",
                    'region': 'UK',
                    'unit': f"kg CO2e/{unit}",
                    'value': value,
                    'valid_from': '2025-01-01',
                    'valid_to': '2025-12-31'
                })
        except (ValueError, TypeError):
            continue
    
    return factors


def extract_water(excel_file):
    """Extract water supply and treatment factors."""
    print("\n📊 Extracting Water Factors...")
    
    factors = []
    
    # Water supply
    try:
        df = pd.read_excel(excel_file, sheet_name='Water supply', header=None)
        for i, row in df.iterrows():
            if 'kg CO2e' in str(row.values):
                header_row = i
                break
        
        df = pd.read_excel(excel_file, sheet_name='Water supply', header=header_row)
        
        for _, row in df.iterrows():
            if pd.notna(row.get('kg CO2e')):
                try:
                    factors.append({
                        'category': 'Water Supply',
                        'region': 'UK',
                        'unit': 'kg CO2e/cubic metre',
                        'value': float(row['kg CO2e']),
                        'valid_from': '2025-01-01',
                        'valid_to': '2025-12-31'
                    })
                    break
                except:
                    pass
    except:
        pass
    
    # Water treatment
    try:
        df = pd.read_excel(excel_file, sheet_name='Water treatment', header=None)
        for i, row in df.iterrows():
            if 'kg CO2e' in str(row.values):
                header_row = i
                break
        
        df = pd.read_excel(excel_file, sheet_name='Water treatment', header=header_row)
        
        for _, row in df.iterrows():
            if pd.notna(row.get('kg CO2e')):
                try:
                    factors.append({
                        'category': 'Water Treatment',
                        'region': 'UK',
                        'unit': 'kg CO2e/cubic metre',
                        'value': float(row['kg CO2e']),
                        'valid_from': '2025-01-01',
                        'valid_to': '2025-12-31'
                    })
                    break
                except:
                    pass
    except:
        pass
    
    return factors


def main():
    print("=" * 70)
    print("POPULATING EMISSION FACTORS FROM UK GHG CONVERSION FACTORS 2025")
    print("=" * 70)
    
    # Check API connection
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API is not running. Start the API first with: uvicorn main:app --reload")
            sys.exit(1)
        print("✅ API Connected")
    except:
        print("❌ Cannot connect to API. Start the API first with: uvicorn main:app --reload")
        sys.exit(1)
    
    all_factors = []
    
    # Extract from each sheet
    all_factors.extend(extract_fuels(EXCEL_FILE))
    all_factors.extend(extract_refrigerants(EXCEL_FILE))
    all_factors.extend(extract_uk_electricity(EXCEL_FILE))
    all_factors.extend(extract_passenger_vehicles(EXCEL_FILE))
    all_factors.extend(extract_delivery_vehicles(EXCEL_FILE))
    all_factors.extend(extract_water(EXCEL_FILE))
    
    # Remove duplicates based on category + unit
    seen = set()
    unique_factors = []
    for f in all_factors:
        key = (f['category'], f['unit'])
        if key not in seen:
            seen.add(key)
            unique_factors.append(f)
    
    print(f"\n📋 Total unique emission factors to insert: {len(unique_factors)}")
    
    # Insert factors
    print("\n📥 Inserting emission factors into database...")
    success_count = 0
    
    for factor in unique_factors:
        if create_emission_factor(factor):
            print(f"   ✓ {factor['category']} ({factor['unit']})")
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully inserted {success_count} of {len(unique_factors)} emission factors")
    print("=" * 70)
    print("\nYou can view them at: http://127.0.0.1:8000/docs#/Emission%20Factors")


if __name__ == "__main__":
    main()
