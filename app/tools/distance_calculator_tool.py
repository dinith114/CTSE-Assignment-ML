"""
Custom Tool for Distance and Travel Risk Assessment
Uses OpenStreetMap Nominatim API (free, no API key) to geocode locations and calculate distances.
"""

import requests
import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TravelInfo:
    """Structured output for travel information."""
    distance_km: float
    travel_time_minutes: int
    route_advice: str
    warning_message: Optional[str]
    source_city: str
    destination_city: str


class DistanceCalculatorTool:
    """
    Tool to calculate travel distance and time between locations using OpenStreetMap Nominatim API.
    
    Features:
    - Geocoding via nominatim.openstreetmap.org (free, no API key)
    - Haversine formula for distance calculation
    - Estimated travel time based on average speeds
    - Urgency-aware warnings for high-severity patients
    - Caching to avoid repetitive API calls
    """
    
    # Average speeds in km/h for different travel modes
    SPEEDS = {
        "car": 60,      # Highway + city average
        "train": 80,    # Inter-city train average  
        "bus": 50,      # Slower than car
        "default": 55   # Conservative estimate
    }
    
    def __init__(self, cache_file: str = "app/data/city_distances/city_coordinates.json"):
        """
        Initialize the distance calculator with optional cache.
        
        Args:
            cache_file: Path to JSON file for caching geocoding results
        """
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.base_url = "https://nominatim.openstreetmap.org/search"
        
    def _load_cache(self) -> Dict:
        """Load cached coordinates from JSON file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self) -> None:
        """Save coordinates cache to JSON file."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _geocode_city(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        Convert city name to coordinates using Photon Komoot API.
        
        Args:
            city_name: Name of the city (e.g., "Colombo, Sri Lanka")
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
            
        Raises:
            requests.RequestException: If API call fails
        """
        # Check cache first
        if city_name.lower() in self.cache:
            coords = self.cache[city_name.lower()]
            logger.info(f"Cache hit for {city_name}: {coords}")
            return tuple(coords)
        
        # Query Nominatim API
        params = {
            'q': city_name,
            'limit': 1,
            'format': 'json'
        }
        
        try:
            headers = {'User-Agent': 'E-Channeling-System/1.0 (+https://github.com)'}
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                
                # Cache the result
                self.cache[city_name.lower()] = [lat, lon]
                self._save_cache()
                
                logger.info(f"Geocoded {city_name} → ({lat}, {lon})")
                return (lat, lon)
            else:
                logger.warning(f"City not found: {city_name}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"API request failed for {city_name}: {e}")
            raise
    
    def _get_road_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> Optional[float]:
        """
        Get actual road distance using OpenStreetMap Routing Machine (OSRM).
        
        Args:
            lat1, lon1: Starting coordinates (degrees)
            lat2, lon2: Destination coordinates (degrees)
            
        Returns:
            Distance in kilometers or None if API fails
        """
        try:
            osrm_url = f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
            headers = {'User-Agent': 'E-Channeling-System/1.0'}
            response = requests.get(osrm_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('routes') and len(data['routes']) > 0:
                distance_meters = data['routes'][0].get('distance', 0)
                distance_km = distance_meters / 1000.0
                logger.info(f"Road distance from ({lat1}, {lon1}) to ({lat2}, {lon2}): {distance_km:.1f} km")
                return distance_km
            else:
                logger.warning("OSRM: No route found")
                return None
        except Exception as e:
            logger.warning(f"OSRM API failed, falling back to haversine: {e}")
            return None
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two points using haversine formula (fallback).
        
        Args:
            lat1, lon1: Coordinates of first point (degrees)
            lat2, lon2: Coordinates of second point (degrees)
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2)**2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _estimate_travel_time(self, distance_km: float, mode: str = "default") -> int:
        """
        Estimate travel time in minutes based on distance and mode.
        
        Args:
            distance_km: Distance in kilometers
            mode: Travel mode ("car", "train", "bus", "default")
            
        Returns:
            Estimated time in minutes
        """
        speed = self.SPEEDS.get(mode, self.SPEEDS["default"])
        hours = distance_km / speed
        minutes = int(hours * 60)
        return max(minutes, 5)  # Minimum 5 minutes for very short distances
    
    def _generate_route_advice(self, distance_km: float) -> str:
        """Generate contextual route advice based on distance."""
        if distance_km < 10:
            return "Local travel within city. Consider taxi or rideshare."
        elif distance_km < 50:
            return "Short distance. Car or bus recommended."
        elif distance_km < 150:
            return "Medium distance. Train or car recommended for best time."
        elif distance_km < 300:
            return "Long distance. Train recommended for comfort and reliability."
        else:
            return "Very long distance. Consider breaking journey or overnight stay."
    
    def _generate_warning(self, distance_km: float, travel_time_minutes: int, 
                         severity: str = "medium") -> Optional[str]:
        """
        Generate urgency-aware warning for high-severity patients.
        
        Args:
            distance_km: Travel distance in kilometers
            travel_time_minutes: Estimated travel time in minutes
            severity: Patient severity level ("low", "medium", "high", "urgent")
            
        Returns:
            Warning message or None if no warning needed
        """
        travel_hours = travel_time_minutes / 60
        
        if severity.lower() in ["high", "urgent"]:
            if travel_hours > 2:
                return f"⚠️ URGENT WARNING: {severity.upper()} severity patient with {travel_hours:.1f}h travel time. Recommend immediate local care or ambulance transport."
            elif travel_hours > 1:
                return f"⚠️ CAUTION: {severity.capitalize()} severity patient requires {travel_hours:.1f}h travel. Consider teleconsultation or nearest facility."
        elif severity.lower() == "medium" and travel_hours > 4:
            return f"Note: {travel_hours:.1f}h travel time for medium severity. Plan accordingly."
        
        return None
    
    def calculate_travel(self, patient_city: str, hospital_city: str, 
                        severity: str = "medium", travel_mode: str = "default") -> Dict[str, Any]:
        """
        Main method to calculate travel distance, time, and risk assessment.
        
        Args:
            patient_city: Patient's current city (e.g., "Kandy, Sri Lanka")
            hospital_city: Hospital's city (e.g., "Colombo, Sri Lanka")
            severity: Patient severity ("low", "medium", "high", "urgent")
            travel_mode: Travel mode ("car", "train", "bus", "default")
            
        Returns:
            Dictionary with travel information, warnings, and route advice
            
        Raises:
            ValueError: If city names are invalid or cannot be geocoded
        """
        logger.info(f"Calculating travel from {patient_city} to {hospital_city} for {severity} severity")
        
        # Geocode both cities
        patient_coords = self._geocode_city(patient_city)
        hospital_coords = self._geocode_city(hospital_city)
        
        if patient_coords is None:
            raise ValueError(f"Could not geocode patient city: {patient_city}")
        if hospital_coords is None:
            raise ValueError(f"Could not geocode hospital city: {hospital_city}")
        
        # Calculate actual road distance using OSRM; fall back to haversine if API fails
        distance = self._get_road_distance(
            patient_coords[0], patient_coords[1],
            hospital_coords[0], hospital_coords[1]
        ) or self._haversine_distance(
            patient_coords[0], patient_coords[1],
            hospital_coords[0], hospital_coords[1]
        )
        
        # Estimate travel time
        travel_time_minutes = self._estimate_travel_time(distance, travel_mode)
        
        # Generate route advice
        route_advice = self._generate_route_advice(distance)
        
        # Generate warning based on severity
        warning = self._generate_warning(distance, travel_time_minutes, severity)
        
        result = {
            "distance_km": round(distance, 1),
            "estimated_travel_time_minutes": travel_time_minutes,
            "travel_time_hours": round(travel_time_minutes / 60, 1),
            "route_advice": route_advice,
            "warning_message": warning,
            "source_city": patient_city,
            "destination_city": hospital_city,
            "severity_assessed": severity,
            "travel_mode_used": travel_mode
        }
        
        logger.info(f"Travel calculation complete: {result}")
        return result


# Standalone function for easier integration with agent frameworks
def distance_calculator_tool(patient_city: str, hospital_city: str, 
                            severity: str = "medium") -> dict:
    """
    Wrapper function for the DistanceCalculatorTool for use in agent workflows.
    
    Args:
        patient_city: Patient's current city
        hospital_city: Hospital's city  
        severity: Patient severity level
        
    Returns:
        Dictionary with travel information
    """
    tool = DistanceCalculatorTool()
    return tool.calculate_travel(patient_city, hospital_city, severity)