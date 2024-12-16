import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from typing import List, Tuple
import folium
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEOCODING_API_KEY = os.getenv('GEOCODING_API_KEY')

def get_coordinates(addresses: List[str]) -> List[Tuple[float, float]]:
    """Get coordinates for a list of addresses using OpenStreetMap."""
    coordinates = []
    geolocator = Nominatim(user_agent="goldenhour_v2_trip_planner/1.0 (your@email.com)")
    
    for address in addresses:
        try:
            # Rate limiting to comply with OSM usage policy
            time.sleep(1)
            location = geolocator.geocode(address)
            
            if location:
                coordinates.append((location.latitude, location.longitude))
            else:
                raise ValueError(f"Could not find coordinates for address: {address}")
                
        except GeocoderTimedOut:
            print(f"Timeout for address: {address}, retrying...")
            time.sleep(2)
            try:
                location = geolocator.geocode(address)
                if location:
                    coordinates.append((location.latitude, location.longitude))
            except Exception as e:
                raise Exception(f"Failed to geocode address after retry: {address}") from e
        except Exception as e:
            raise Exception(f"Error geocoding address {address}: {str(e)}") from e
            
    return coordinates

def get_route(coordinates: List[Tuple[float, float]]) -> Tuple[List[List[float]], float]:
    """Find the route between coordinates and calculate total time."""
    # Get road network for the area
    G = ox.graph_from_points(coordinates, network_type='drive')
    
    # Convert coordinates to nearest nodes
    nodes = []
    for coord in coordinates:
        node = ox.nearest_nodes(G, coord[1], coord[0])
        nodes.append(node)
    
    # Get route between consecutive points
    route_coords = []
    total_time = 0
    
    for i in range(len(nodes)-1):
        route = nx.shortest_path(G, nodes[i], nodes[i+1], weight='travel_time')
        path_coords = [[G.nodes[node]['y'], G.nodes[node]['x']] for node in route]
        route_coords.extend(path_coords)
        
        # Calculate time for this segment
        segment_time = nx.shortest_path_length(G, nodes[i], nodes[i+1], weight='travel_time')
        total_time += segment_time
    
    return route_coords, total_time

def split_route(route_coords: List[List[float]], total_time: float, num_sections: int) -> List[List[List[float]]]:
    """Split the route into sections with equal estimated driving time."""
    time_per_section = total_time / num_sections
    sections = []
    current_section = []
    current_time = 0
    
    for coord in route_coords:
        current_section.append(coord)
        # Approximate time based on position in route
        current_time = (len(current_section) / len(route_coords)) * total_time
        
        if current_time >= time_per_section:
            sections.append(current_section)
            current_section = [coord]  # Start new section with overlap point
            current_time = 0
    
    # Add any remaining coordinates to the last section
    if current_section:
        sections.append(current_section)
    
    return sections

def visualize_route(sections: List[List[List[float]]], output_file: str = 'route_map.html'):
    """Create a folium map visualizing the split route."""
    # Create map centered on first coordinate
    m = folium.Map(location=sections[0][0], zoom_start=12)
    
    # Different colors for different sections
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen']
    
    for i, section in enumerate(sections):
        color = colors[i % len(colors)]
        folium.PolyLine(
            section,
            weight=3,
            color=color,
            opacity=0.8
        ).add_to(m)
        
    m.save(output_file)

def main():
    # Example usage
    addresses = [
        "123 Main St, City, State",
        "456 Oak Ave, City, State",
        "789 Pine Rd, City, State"
    ]
    num_sections = 2
    
    # Get coordinates for addresses
    coordinates = get_coordinates(addresses)
    
    # Get route and total time
    route_coords, total_time = get_route(coordinates)
    
    # Split route into sections
    sections = split_route(route_coords, total_time, num_sections)
    
    # Visualize the route
    visualize_route(sections)
    
    print(f"Route split into {num_sections} sections of approximately {total_time/num_sections:.2f} seconds each")

if __name__ == "__main__":
    main()