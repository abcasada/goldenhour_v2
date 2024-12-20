from astral import LocationInfo
from astral.sun import sun, azimuth
from datetime import datetime, timedelta
from astral.geocoder import database, lookup
from heapq import nsmallest

def find_due_east_sunrises(location: LocationInfo, n: int = 6, year: int = datetime.now().year):
    """
    Find the n days of the year when sunrise azimuth is closest to due east (90 degrees)
    for a given location.
    
    Args:
        location: Astral LocationInfo object with latitude/longitude
        n: Number of days to return
        year: Year to check (defaults to current year)
    
    Returns:
        List of (date, difference) tuples for the n closest days
    """
    days = []
    
    # Check each day of the year
    start_date = datetime(year, 1, 1)
    for day_offset in range(365):
        current_date = start_date + timedelta(days=day_offset)
        
        # Get sun information for the day
        s = sun(location.observer, current_date)
        
        # Calculate absolute difference from 90 degrees (due east)
        difference = abs(azimuth(location.observer, s['sunrise']) - 90)
        days.append((current_date, difference))
    
    # Return n days with smallest difference
    return nsmallest(n, days, key=lambda x: x[1])

def main():
    # Get location input from user
    city = input("Enter city name: ")
    
    # Create LocationInfo object
    location = lookup(city, database())
    
    # Find 6 sunrise dates closest to due east
    closest_days = find_due_east_sunrises(location)
    
    # Print results
    print(f"\nDates with sunrise closest to due east:")
    for date, difference in closest_days:
        print(f"{date.strftime('%B %d, %Y')}: {difference:.2f} degrees from due east")

if __name__ == "__main__":
    main()
