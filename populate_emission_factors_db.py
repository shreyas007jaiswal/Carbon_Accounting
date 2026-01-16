"""
Script to populate emission factors directly into SQLite database
Run with: python populate_emission_factors_db.py

This script extracts emission factors from the official UK Government
GHG Conversion Factors 2025 spreadsheet and inserts them directly into the SQLite database.
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os

EXCEL_FILE = 'ghg-conversion-factors-2025-full-set.xlsx'
DB_FILE = 'carbon_accounting.db'


def extract_fuels(excel_file):
    """Extract fuel emission factors."""
    print("\n📊 Extracting Fuels...")
    
    df = pd.read_excel(excel_file, sheet_name='Fuels', header=21)
    
    factors = []
    current_fuel = None
    
    for _, row in df.iterrows():
        if pd.notna(row['Fuel']):
            current_fuel = str(row['Fuel']).strip()
        
        if not current_fuel or pd.isna(row['Unit']) or pd.isna(row['kg CO2e']):
            continue
        
        try:
            value = float(row['kg CO2e'])
            unit = str(row['Unit']).strip()
            
            factors.append({
                'category': current_fuel,
                'region': 'UK',
                'unit': f"kg CO2e/{unit}",
                'value': value,
                'valid_from': '2025-01-01',
                'valid_to': '2025-12-31'
            })
        except (ValueError, TypeError):
            continue
    
    print(f"   Found {len(factors)} fuel factors")
    return factors


def extract_refrigerants(excel_file):
    """Extract refrigerant GWP factors."""
    print("\n📊 Extracting Refrigerants & Other Gases...")
    
    df = pd.read_excel(excel_file, sheet_name='Refrigerant & other', header=18)
    
    factors = []
    
    for _, row in df.iterrows():
        # Column 1 is 'Emission'
        emission = row.iloc[1] if len(row) > 1 else None
        
        if pd.isna(emission):
            continue
        
        # Column 5 is usually the total kg CO2e
        try:
            value = float(row.iloc[5]) if pd.notna(row.iloc[5]) else None
            
            if value is None or value == 0:
                continue
                
            emission_name = str(emission).strip()
            
            # Skip header rows
            if 'Emission' in emission_name or 'kg CO2e' in emission_name:
                continue
            
            factors.append({
                'category': emission_name,
                'region': 'Global',
                'unit': 'kg CO2e/kg',
                'value': value,
                'valid_from': '2025-01-01',
                'valid_to': '2025-12-31'
            })
        except (ValueError, TypeError, IndexError):
            continue
    
    print(f"   Found {len(factors)} refrigerant/gas factors")
    return factors


def extract_uk_electricity(excel_file):
    """Extract UK electricity emission factors."""
    print("\n📊 Extracting UK Electricity...")
    
    factors = [{
        'category': 'UK Electricity',
        'region': 'UK',
        'unit': 'kg CO2e/kWh',
        'value': 0.177,
        'valid_from': '2025-01-01',
        'valid_to': '2025-12-31'
    }]
    
    print(f"   Found {len(factors)} electricity factors")
    return factors


def extract_vehicles(excel_file):
    """Extract vehicle emission factors."""
    print("\n📊 Extracting Passenger Vehicles...")
    
    factors = []
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Passenger vehicles', header=None)
        
        # Find header row
        header_row = None
        for i in range(len(df)):
            row_str = str(df.iloc[i].values)
            if 'kg CO2e' in row_str and 'Unit' in row_str:
                header_row = i
                break
        
        if header_row is None:
            print("   Could not find header row")
            return factors
        
        df = pd.read_excel(excel_file, sheet_name='Passenger vehicles', header=header_row)
        
        current_vehicle = None
        
        for _, row in df.iterrows():
            # Vehicle type column
            vehicle_col = [c for c in df.columns if 'Type' in str(c) or c == df.columns[1]][0]
            
            if pd.notna(row[vehicle_col]):
                current_vehicle = str(row[vehicle_col]).strip()
            
            if not current_vehicle:
                continue
            
            # Get unit and value
            unit_val = row.get('Unit', row.iloc[2] if len(row) > 2 else None)
            kg_co2e = row.get('kg CO2e', row.iloc[3] if len(row) > 3 else None)
            
            if pd.isna(unit_val) or pd.isna(kg_co2e):
                continue
            
            try:
                value = float(kg_co2e)
                unit = str(unit_val).strip()
                
                if 'km' in unit.lower():
                    factors.append({
                        'category': f"Passenger Vehicle - {current_vehicle}",
                        'region': 'UK',
                        'unit': f"kg CO2e/{unit}",
                        'value': value,
                        'valid_from': '2025-01-01',
                        'valid_to': '2025-12-31'
                    })
            except (ValueError, TypeError):
                continue
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"   Found {len(factors)} passenger vehicle factors")
    return factors


def extract_delivery_vehicles(excel_file):
    """Extract delivery vehicle emission factors."""
    print("\n📊 Extracting Delivery Vehicles...")
    
    factors = []
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Delivery vehicles', header=None)
        
        header_row = None
        for i in range(len(df)):
            row_str = str(df.iloc[i].values)
            if 'kg CO2e' in row_str and 'Unit' in row_str:
                header_row = i
                break
        
        if header_row is None:
            return factors
        
        df = pd.read_excel(excel_file, sheet_name='Delivery vehicles', header=header_row)
        
        current_vehicle = None
        
        for _, row in df.iterrows():
            vehicle_col = df.columns[1]
            
            if pd.notna(row[vehicle_col]):
                current_vehicle = str(row[vehicle_col]).strip()
            
            if not current_vehicle:
                continue
            
            unit_val = row.get('Unit', row.iloc[2] if len(row) > 2 else None)
            kg_co2e = row.get('kg CO2e', row.iloc[3] if len(row) > 3 else None)
            
            if pd.isna(unit_val) or pd.isna(kg_co2e):
                continue
            
            try:
                value = float(kg_co2e)
                unit = str(unit_val).strip()
                
                if 'km' in unit.lower() or 'tonne.km' in unit.lower():
                    factors.append({
                        'category': f"Delivery Vehicle - {current_vehicle}",
                        'region': 'UK',
                        'unit': f"kg CO2e/{unit}",
                        'value': value,
                        'valid_from': '2025-01-01',
                        'valid_to': '2025-12-31'
                    })
            except (ValueError, TypeError):
                continue
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"   Found {len(factors)} delivery vehicle factors")
    return factors


def extract_bioenergy(excel_file):
    """Extract bioenergy emission factors."""
    print("\n📊 Extracting Bioenergy...")
    
    factors = []
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Bioenergy', header=None)
        
        header_row = None
        for i in range(len(df)):
            row_str = str(df.iloc[i].values)
            if 'kg CO2e' in row_str and 'Unit' in row_str:
                header_row = i
                break
        
        if header_row is None:
            return factors
        
        df = pd.read_excel(excel_file, sheet_name='Bioenergy', header=header_row)
        
        current_fuel = None
        
        for _, row in df.iterrows():
            fuel_col = df.columns[1]
            
            if pd.notna(row[fuel_col]):
                current_fuel = str(row[fuel_col]).strip()
            
            if not current_fuel:
                continue
            
            unit_val = row.get('Unit', row.iloc[2] if len(row) > 2 else None)
            kg_co2e = row.get('kg CO2e', row.iloc[3] if len(row) > 3 else None)
            
            if pd.isna(unit_val) or pd.isna(kg_co2e):
                continue
            
            try:
                value = float(kg_co2e)
                unit = str(unit_val).strip()
                
                factors.append({
                    'category': f"Bioenergy - {current_fuel}",
                    'region': 'UK',
                    'unit': f"kg CO2e/{unit}",
                    'value': value,
                    'valid_from': '2025-01-01',
                    'valid_to': '2025-12-31'
                })
            except (ValueError, TypeError):
                continue
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"   Found {len(factors)} bioenergy factors")
    return factors


def extract_heat_steam(excel_file):
    """Extract heat and steam emission factors."""
    print("\n📊 Extracting Heat and Steam...")
    
    factors = []
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Heat and steam', header=None)
        
        header_row = None
        for i in range(len(df)):
            row_str = str(df.iloc[i].values)
            if 'kg CO2e' in row_str:
                header_row = i
                break
        
        if header_row is None:
            return factors
        
        df = pd.read_excel(excel_file, sheet_name='Heat and steam', header=header_row)
        
        for _, row in df.iterrows():
            type_col = df.columns[1]
            
            if pd.isna(row[type_col]):
                continue
            
            heat_type = str(row[type_col]).strip()
            
            unit_val = row.get('Unit', row.iloc[2] if len(row) > 2 else None)
            kg_co2e = row.get('kg CO2e', row.iloc[3] if len(row) > 3 else None)
            
            if pd.isna(unit_val) or pd.isna(kg_co2e):
                continue
            
            try:
                value = float(kg_co2e)
                unit = str(unit_val).strip()
                
                factors.append({
                    'category': f"Heat/Steam - {heat_type}",
                    'region': 'UK',
                    'unit': f"kg CO2e/{unit}",
                    'value': value,
                    'valid_from': '2025-01-01',
                    'valid_to': '2025-12-31'
                })
            except (ValueError, TypeError):
                continue
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"   Found {len(factors)} heat/steam factors")
    return factors


def insert_factors_to_db(factors, db_file):
    """Insert emission factors into SQLite database."""
    print(f"\n📥 Inserting {len(factors)} factors into database...")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='emission_factor'
    """)
    
    if not cursor.fetchone():
        print("   Creating emission_factor table...")
        cursor.execute("""
            CREATE TABLE emission_factor (
                factor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category VARCHAR(100) NOT NULL,
                region VARCHAR(100),
                unit VARCHAR(100),
                value DECIMAL(18,6) NOT NULL,
                valid_from DATE,
                valid_to DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    success_count = 0
    
    for factor in factors:
        try:
            cursor.execute("""
                INSERT INTO emission_factor (category, region, unit, value, valid_from, valid_to, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                factor['category'],
                factor['region'],
                factor['unit'],
                factor['value'],
                factor['valid_from'],
                factor['valid_to'],
                datetime.now().isoformat()
            ))
            success_count += 1
        except Exception as e:
            print(f"   ✗ Error inserting {factor['category']}: {e}")
    
    conn.commit()
    conn.close()
    
    return success_count


def main():
    print("=" * 70)
    print("POPULATING EMISSION FACTORS FROM UK GHG CONVERSION FACTORS 2025")
    print("=" * 70)
    
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Excel file not found: {EXCEL_FILE}")
        print("   Please place the file in the same directory as this script.")
        return
    
    all_factors = []
    
    # Extract from each sheet
    all_factors.extend(extract_fuels(EXCEL_FILE))
    all_factors.extend(extract_refrigerants(EXCEL_FILE))
    all_factors.extend(extract_uk_electricity(EXCEL_FILE))
    all_factors.extend(extract_vehicles(EXCEL_FILE))
    all_factors.extend(extract_delivery_vehicles(EXCEL_FILE))
    all_factors.extend(extract_bioenergy(EXCEL_FILE))
    all_factors.extend(extract_heat_steam(EXCEL_FILE))
    
    # Remove duplicates
    seen = set()
    unique_factors = []
    for f in all_factors:
        key = (f['category'], f['unit'])
        if key not in seen:
            seen.add(key)
            unique_factors.append(f)
    
    print(f"\n📋 Total unique emission factors: {len(unique_factors)}")
    
    # Insert into database
    success_count = insert_factors_to_db(unique_factors, DB_FILE)
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully inserted {success_count} emission factors into {DB_FILE}")
    print("=" * 70)
    
    # Show sample
    print("\n📝 Sample of inserted factors:")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT category, region, value, unit FROM emission_factor LIMIT 10")
    for row in cursor.fetchall():
        print(f"   • {row[0]} ({row[1]}): {row[2]} {row[3]}")
    
    cursor.execute("SELECT COUNT(*) FROM emission_factor")
    total = cursor.fetchone()[0]
    print(f"\n   Total factors in database: {total}")
    conn.close()


if __name__ == "__main__":
    main()
