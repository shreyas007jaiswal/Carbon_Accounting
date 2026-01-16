"""
Emission Calculation Service
Automatically matches emission factors and calculates CO2e values
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import EmissionFactor, EmissionActivity, EmissionCalculation
from ..models import StationaryFuel, CompanyVehicle, RefrigerantLeak, ProcessEmission


def find_matching_factor(
    db: Session,
    category: str,
    unit: str,
    region: str = "UK"
) -> Optional[EmissionFactor]:
    """
    Find the best matching emission factor for given parameters.
    Uses fuzzy matching on category name.
    """
    # Normalize inputs
    category_lower = category.lower().strip()
    unit_lower = unit.lower().strip()
    
    # Try exact match first
    factor = db.query(EmissionFactor).filter(
        func.lower(EmissionFactor.category) == category_lower,
        func.lower(EmissionFactor.unit).contains(unit_lower)
    ).first()
    
    if factor:
        return factor
    
    # Try partial match on category
    factor = db.query(EmissionFactor).filter(
        func.lower(EmissionFactor.category).contains(category_lower),
        func.lower(EmissionFactor.unit).contains(unit_lower)
    ).first()
    
    if factor:
        return factor
    
    # Try matching just the key part of category
    keywords = category_lower.replace('-', ' ').replace('_', ' ').split()
    for keyword in keywords:
        if len(keyword) > 3:  # Skip short words
            factor = db.query(EmissionFactor).filter(
                func.lower(EmissionFactor.category).contains(keyword),
                func.lower(EmissionFactor.unit).contains(unit_lower)
            ).first()
            if factor:
                return factor
    
    return None


def calculate_co2e(quantity: float, factor_value: float) -> float:
    """Calculate CO2e value from quantity and emission factor."""
    return round(quantity * factor_value, 6)


def calculate_activity_emissions(
    db: Session,
    activity: EmissionActivity,
    auto_create_calculation: bool = True
) -> Tuple[Optional[float], Optional[str], Optional[EmissionFactor]]:
    """
    Calculate emissions for an activity based on its category and unit.
    
    Returns:
        Tuple of (co2e_value, calculation_method, matched_factor)
    """
    if not activity.quantity or not activity.unit:
        return None, None, None
    
    # Try to find matching factor
    factor = find_matching_factor(
        db,
        category=activity.category,
        unit=activity.unit
    )
    
    if not factor:
        return None, "No matching factor found", None
    
    # Calculate CO2e
    co2e_value = calculate_co2e(float(activity.quantity), float(factor.value))
    calculation_method = f"Activity × Factor ({factor.category})"
    
    # Auto-create calculation record if requested
    if auto_create_calculation:
        existing = db.query(EmissionCalculation).filter(
            EmissionCalculation.activity_id == activity.activity_id
        ).first()
        
        if not existing:
            calc = EmissionCalculation(
                activity_id=activity.activity_id,
                co2e_value=co2e_value,
                calculation_method="Emission Factor",
                factor_used=f"{factor.category} ({factor.value} {factor.unit})"
            )
            db.add(calc)
            db.commit()
    
    return co2e_value, calculation_method, factor


def calculate_stationary_fuel_emissions(
    db: Session,
    fuel: StationaryFuel,
    auto_create_calculation: bool = True
) -> Tuple[Optional[float], Optional[str], Optional[EmissionFactor]]:
    """Calculate emissions for stationary fuel combustion."""
    if not fuel.quantity or not fuel.unit:
        return None, None, None
    
    # Try to find matching factor based on fuel type
    factor = find_matching_factor(
        db,
        category=fuel.fuel_type,
        unit=fuel.unit
    )
    
    if not factor:
        return None, "No matching factor found", None
    
    co2e_value = calculate_co2e(float(fuel.quantity), float(factor.value))
    
    # Update the fuel record with the factor
    if fuel.factor_id is None:
        fuel.factor_id = factor.factor_id
        db.commit()
    
    return co2e_value, f"Fuel × Factor ({factor.category})", factor


def calculate_vehicle_emissions(
    db: Session,
    vehicle: CompanyVehicle
) -> Tuple[Optional[float], Optional[str], Optional[EmissionFactor]]:
    """Calculate emissions for company vehicles."""
    # Try distance-based calculation first
    if vehicle.distance_travelled:
        factor = find_matching_factor(
            db,
            category=vehicle.vehicle_type,
            unit="km"
        )
        
        if factor:
            co2e_value = calculate_co2e(float(vehicle.distance_travelled), float(factor.value))
            return co2e_value, f"Distance × Factor ({factor.category})", factor
    
    # Try fuel-based calculation
    if vehicle.fuel_consumed:
        # Assume diesel for delivery vehicles
        factor = find_matching_factor(
            db,
            category="Diesel",
            unit="litres"
        )
        
        if factor:
            co2e_value = calculate_co2e(float(vehicle.fuel_consumed), float(factor.value))
            return co2e_value, f"Fuel × Factor ({factor.category})", factor
    
    return None, "Insufficient data", None


def calculate_refrigerant_emissions(
    db: Session,
    leak: RefrigerantLeak
) -> Tuple[Optional[float], Optional[str], Optional[EmissionFactor]]:
    """Calculate emissions for refrigerant leaks using GWP."""
    if not leak.leak_quantity_kg:
        return None, None, None
    
    # If GWP factor is provided directly, use it
    if leak.gwp_factor:
        co2e_value = calculate_co2e(float(leak.leak_quantity_kg), float(leak.gwp_factor))
        return co2e_value, f"Quantity × GWP ({leak.gwp_factor})", None
    
    # Try to find matching refrigerant factor
    factor = find_matching_factor(
        db,
        category=leak.refrigerant_type,
        unit="kg"
    )
    
    if factor:
        co2e_value = calculate_co2e(float(leak.leak_quantity_kg), float(factor.value))
        return co2e_value, f"Quantity × GWP ({factor.category})", factor
    
    return None, "No matching GWP factor found", None


def get_emissions_summary(db: Session, organization_id: Optional[int] = None) -> dict:
    """
    Get a summary of emissions by scope for an organization or all organizations.
    """
    query = db.query(
        EmissionActivity.scope,
        func.sum(EmissionCalculation.co2e_value).label('total_co2e'),
        func.count(EmissionActivity.activity_id).label('activity_count')
    ).join(
        EmissionCalculation,
        EmissionActivity.activity_id == EmissionCalculation.activity_id
    )
    
    if organization_id:
        query = query.filter(EmissionActivity.organization_id == organization_id)
    
    query = query.group_by(EmissionActivity.scope)
    
    results = query.all()
    
    summary = {
        'scope_1': {'total_co2e': 0, 'activity_count': 0},
        'scope_2': {'total_co2e': 0, 'activity_count': 0},
        'scope_3': {'total_co2e': 0, 'activity_count': 0},
        'total': {'total_co2e': 0, 'activity_count': 0}
    }
    
    for scope, total_co2e, count in results:
        scope_key = f'scope_{scope}'
        if scope_key in summary:
            summary[scope_key]['total_co2e'] = float(total_co2e) if total_co2e else 0
            summary[scope_key]['activity_count'] = count
            summary['total']['total_co2e'] += float(total_co2e) if total_co2e else 0
            summary['total']['activity_count'] += count
    
    return summary


def recalculate_all_emissions(db: Session) -> dict:
    """
    Recalculate emissions for all activities that don't have calculations.
    Returns a summary of calculations created.
    """
    # Get activities without calculations
    activities = db.query(EmissionActivity).outerjoin(
        EmissionCalculation
    ).filter(
        EmissionCalculation.calculation_id == None
    ).all()
    
    created = 0
    failed = 0
    
    for activity in activities:
        co2e, method, factor = calculate_activity_emissions(db, activity, auto_create_calculation=True)
        if co2e is not None:
            created += 1
        else:
            failed += 1
    
    return {
        'activities_processed': len(activities),
        'calculations_created': created,
        'calculations_failed': failed
    }
