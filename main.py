"""
Calculate golden hour durations throughout the year for multiple latitudes.

This script processes a list of latitudes and generates a CSV file containing
the daily duration of golden hour periods (when the sun is between -4 and 6 
degrees elevation) for an entire year. It uses multiprocessing to improve 
performance when calculating multiple latitudes.

The output file includes:
- Daily golden hour durations for each latitude
- Dates in YYYY-MM-DD format
- Durations in decimal hours
"""

import multiprocessing
from astral import LocationInfo
from astral.sun import elevation
from datetime import datetime, timedelta
import csv  # todo: use pandas for xlsx
import os
import psutil

PRECISION = 1  # minutes
DESIRED_LATITUDES = [59.91, 59.13, 59.97, 61.9, 63.25, 65.46, 66.74, 67.96, 69.49, 70.51, 70.2,
                     70.2, 68.55, 65.32, 62.52, 60.99, 59.91]

def twilight_hours_day(latitude: float, date: datetime) -> float:
    """
    Calculate total golden hour duration for a specific date and latitude.
    
    Args:
        latitude: Location's latitude in degrees (-90 to 90)
        date: Date to calculate golden hour for
    
    Returns:
        float: Total hours of golden hour conditions, rounded to 2 decimals
    """
    
    # Create a location to pass to astral.sun.elevation
    location = LocationInfo(
        name="Custom Location",
        region="Custom Region", 
        latitude=latitude,
        longitude=0
    )
    start_time = datetime.combine(date, datetime.min.time())
    end_time = datetime.combine(date, datetime.max.time())
    
    current_time = start_time
    total_minutes = 0
    
    #loop through the day in increments of PRECISION minutes
    while current_time <= end_time:
        # todo: add refraction correction. Can only be accurately done
        # when sun is 5 or more degrees above the horizon, so will only
        # help with calculating when sun crosses the 6 degree point
        
        # find the elevation of the sun at the current time
        elev = elevation(location.observer, current_time)  
        
        # if the sun is currently in the range, add the time slice to the sum
        if -4 <= elev <= 6:
            total_minutes += PRECISION
            
        # move to the next time slice
        current_time += timedelta(minutes=PRECISION)
    
    return round(total_minutes / 60, 2)

def twilight_hours_year(latitude: float) -> list:
    """
    Calculate golden hour durations for an entire year at given latitude.
    Uses 2023 as the base year.
    
    Args:
        latitude: Location's latitude in degrees (-90 to 90)
    
    Returns:
        list: 365 entries of [date, latitude, hours] for each day of year
    """
    data = []
    for x in range(365):
        date = datetime(2023, 1, 1) + timedelta(x)
        hours_in_range = twilight_hours_day(latitude, date)
        data.append([date.strftime('%Y-%m-%d'), latitude, hours_in_range])
    return data

def process_latitude(latitude: float) -> list:
    """
    Wrapper function for parallel processing of latitudes.
    
    Args:
        latitude: Location's latitude in degrees (-90 to 90)
    
    Returns:
        list: Results from twilight_hours_year for the given latitude
    """
    return twilight_hours_year(latitude)

def create_filename() -> str:
    """
    Create output directory and generate timestamped filename.
    
    Creates 'data_output' directory if it doesn't exist and generates a 
    unique filename using current timestamp.
    
    Returns:
        str: Full path to output CSV file
    """
    # Create output directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "data_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(output_dir, f"GH_duration_fullyear_{timestamp}.csv")
    
    return filename

def main():
    """
    Main program execution.
    
    1. Sets up multiprocessing pool based on CPU count
    2. Processes all latitudes in parallel
    3. Combines results into a single dataset
    4. Writes results to CSV with timestamps
    5. Reports total execution time
    """
    start_time = datetime.now()
    latitudes = DESIRED_LATITUDES
    
    # Use 80% of available CPUs, but at least 1
    num_cpus = max(1, int(psutil.cpu_count() * 0.8))
    
    with multiprocessing.Pool(processes=num_cpus) as pool:
        results = pool.map(process_latitude, latitudes)
    
    # Combine results into a single dataset
    all_data = {}
    for data in results:
        for entry in data:
            date, latitude, hours = entry[0], entry[1], entry[2]
            if date not in all_data:
                all_data[date] = {}
            all_data[date][latitude] = hours
    
    # Write results to CSV
    with open(create_filename(), mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ["Date"] + [f"{lat}\u00B0" for lat in latitudes]
        writer.writerow(header)
        
        for date, lat_data in all_data.items():
            row = [date] + [lat_data.get(lat, 0) for lat in latitudes]
            writer.writerow(row)
    
    # Report total execution time
    end_time = datetime.now()
    print(f"Elapsed time: {end_time - start_time}")

if __name__ == "__main__":
    main()