# MIT License
# Copyright (c) 2025 Adam Casada

import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from typing import List, Tuple, Dict, Optional, NamedTuple
import folium
import time
from functools import lru_cache
from pathlib import Path
import logging

# Add constants at top of file after imports
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "geocoding_cache.sqlite"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitedGeocoder:
    def __init__(self, cache_ttl: int = 86400):
        self.cache_ttl = cache_ttl
        # Create cache directory if it doesn't exist
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        self.geolocator = Nominatim(
            user_agent="trip_planner/1.0",
            timeout=3,  # Reduced to 3 seconds - balance between reliability and user experience
            cache=True,
            cache_path=str(CACHE_FILE)
        )
        self.last_call = 0
        self.min_delay = 1.1  # Slightly over 1 second to ensure compliance

    def _wait_if_needed(self):
        """Ensure we wait appropriate time between calls"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_call = time.time()

    @lru_cache(maxsize=128)  # Cache results to avoid duplicate calls
    def geocode(self, address: str, max_retries: int = 3) -> Tuple[float, float]:
        """Geocode address with retries"""
        for attempt in range(max_retries):
            try:
                self._wait_if_needed()
                location = self.geolocator.geocode(address, timeout=3)
                if location:
                    return (location.latitude, location.longitude)
            except GeocoderTimedOut:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        raise ValueError(f"Could not find coordinates for address: {address}")
        
    def _cleanup_old_cache(self):
        """Cleanup cache files older than TTL"""
        if CACHE_FILE.exists():
            if CACHE_FILE.stat().st_mtime < time.time() - self.cache_ttl:
                try:
                    CACHE_FILE.unlink()
                except OSError as e:
                    logger.warning(f"Could not clean cache: {e}")

def get_coordinates(addresses: List[str]) -> List[Tuple[float, float]]:
    """Get coordinates for a list of addresses using OpenStreetMap."""
    geocoder = RateLimitedGeocoder()
    coordinates = []
    
    for address in addresses:
        try:
            coord = geocoder.geocode(address)
            coordinates.append(coord)
        except ValueError as e:
            logger.error(f"Error geocoding address {address}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error geocoding address {address}: {str(e)}")
            raise
            
    return coordinates

@ox.utils.decorators.cache
def get_road_network(north: float, south: float, east: float, west: float) -> nx.MultiDiGraph:
    """Get cached road network"""
    return ox.graph_from_bbox(north, south, east, west, network_type='drive')

class RouteSection(NamedTuple):
    coordinates: List[List[float]]
    estimated_time: float

def validate_coordinates(coordinates: List[Tuple[float, float]]) -> None:
    """Validate coordinate inputs"""
    if len(coordinates) < 2:
        raise ValueError("At least 2 coordinates are required")
    for lat, lon in coordinates:
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError(f"Invalid coordinates: {lat}, {lon}")

def get_route(coordinates: List[Tuple[float, float]]) -> Tuple[List[List[float]], float]:
    """Find the route between coordinates and calculate total time."""
    validate_coordinates(coordinates)
    try:
        # Get road network for the area
        lats, lons = zip(*coordinates)
        north, south = max(lats), min(lats)
        east, west = max(lons), min(lons)
        G = get_road_network(north, south, east, west)
        
        # Convert coordinates to nearest nodes
        nodes = []
        for coord in coordinates:
            node = ox.nearest_nodes(G, coord[1], coord[0])
            nodes.append(node)
        
        # Get route between consecutive points
        route_coords = []
        total_time = 0
        
        for i in range(len(nodes)-1):
            try:
                route = nx.shortest_path(G, nodes[i], nodes[i+1], weight='travel_time')
                path_coords = [[G.nodes[node]['y'], G.nodes[node]['x']] for node in route]
                route_coords.extend(path_coords)
                
                segment_time = nx.shortest_path_length(G, nodes[i], nodes[i+1], weight='travel_time')
                total_time += segment_time
            except nx.NetworkXNoPath:
                logger.error(f"No route found between points {i} and {i+1}")
                raise ValueError(f"No route found between points {i} and {i+1}")
                
        return route_coords, total_time
    except Exception as e:
        logger.error(f"Error calculating route: {str(e)}")
        raise

def split_route(
    route_coords: List[List[float]], 
    total_time: float, 
    num_sections: int
) -> List[RouteSection]:
    """Split the route into sections with equal estimated driving time."""
    if num_sections < 1:
        raise ValueError("Number of sections must be positive")
    if not route_coords:
        raise ValueError("Route coordinates cannot be empty")

    time_per_section = total_time / num_sections
    sections = []
    current_section = []
    current_time = 0
    
    for coord in route_coords:
        current_section.append(coord)
        current_time = (len(current_section) / len(route_coords)) * total_time
        
        if current_time >= time_per_section:
            sections.append(RouteSection(
                coordinates=current_section,
                estimated_time=current_time
            ))
            current_section = [coord]
            current_time = 0
    
    if current_section:
        sections.append(RouteSection(
            coordinates=current_section,
            estimated_time=current_time
        ))
    
    return sections

def visualize_route(
    sections: List[RouteSection], 
    output_file: str = 'route_map.html',
    zoom: int = 12,
    colors: Optional[List[str]] = None
) -> None:
    """Create a folium map visualizing the split route."""
    if not sections:
        raise ValueError("No sections to visualize")
        
    m = folium.Map(location=sections[0].coordinates[0], zoom_start=zoom)
    
    if colors is None:
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen']
    
    for i, section in enumerate(sections):
        color = colors[i % len(colors)]
        folium.PolyLine(
            section.coordinates,
            weight=3,
            color=color,
            opacity=0.8,
            popup=f"Estimated time: {section.estimated_time:.2f}s"
        ).add_to(m)
        
    m.save(output_file)

def main():
    addresses = [
        "701 Rittgers Lane, Salina, KS",
        "707 Rittgers Lane, Salina, KS",
        "713 Rittgers Lane, Salina, KS"
    ]
    num_sections = 2
    
    # Get coordinates for addresses
    try:
        coordinates = get_coordinates(addresses)
        route_coords, total_time = get_route(coordinates)
        sections = split_route(route_coords, total_time, num_sections)
        visualize_route(sections)
        print(f"Route split into {num_sections} sections of approximately {total_time/num_sections:.2f} seconds each")
    except Exception as e:
        logger.error(f"Error in route planning: {str(e)}")
        raise

if __name__ == "__main__":
    main()