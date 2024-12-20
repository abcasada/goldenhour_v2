"""
This script calculates golden hour times for a given date range and 
latitude. It defines golden hour as periods when the sun is between -4 
and 6 degrees elevation, producing great lighting conditions for 
photography.
"""

from idealtrip import calculate_golden_hours
from datetime import datetime, timedelta
from typing import Dict

def format_golden_hours(date: datetime, times: Dict) -> str:
    """
    Formats golden hour times into a human-readable string.
    
    Args:
        date (datetime): The date for which golden hours were calculated
        times (Dict): Dictionary containing morning_start, morning_end, 
                      evening_start, and evening_end times
    
    Returns:
        str: Formatted string containing date and golden hour periods in 
             AM/PM format. Example: 
             "2024-01-01: 7:30 AM to 8:45 AM; 4:15 PM to 5:30 PM"
    """
    # Format morning golden hour if it exists
    if times['morning_start']:
        morning = (
            f"{times['morning_start'].strftime('%I:%M %p')} to "
            f"{times['morning_end'].strftime('%I:%M %p')}"
        )
    else:
        morning = "No morning golden hour"
    
    # Format evening golden hour if it exists
    if times['evening_start']:
        evening = (
            f"{times['evening_start'].strftime('%I:%M %p')} to "
            f"{times['evening_end'].strftime('%I:%M %p')}"
        )
    else:
        evening = "No evening golden hour"
    
    return f"{date.strftime('%Y-%m-%d')}: {morning}; {evening}"

def main():
    """
    Main program execution:
    1. Prompts user for date range and latitude
    2. Validates input
    3. Calculates and displays golden hours for each day in range
    """
    
    print("\nThis program will display the time ranges for golden hour "
          "\n(using a definition of 4 degrees below the horizon to "
          "\n6 degrees above) for a given date range and latitude.\n")
    
    # Get and validate date range from user
    while True:
        try:
            prompt = "Enter start date  (YYYY-MM-DD): "  # Extra space for alignment
            start_date = datetime.strptime(input(prompt), '%Y-%m-%d')
            
            prompt = "Enter end date    (YYYY-MM-DD): "  # Extra spaces for alignment
            end_date = datetime.strptime(input(prompt), '%Y-%m-%d')
            
            if end_date < start_date:
                print("End date must be after start date")
                continue
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
    
    # Get and convert latitude to float
    while True:
        latitude = float(input("Enter latitude in degrees (47.3456): "))
        if not -90 <= latitude <= 90:
            print("Latitude must be between -90 and 90 degrees\n")
            continue
        break

    print("\n" + "=" * 54 + "\n")
    print("Here are your golden hour times:\n")
    
    # Calculate and display golden hours for each day in range
    current_date = start_date
    while current_date <= end_date:
        times = calculate_golden_hours(current_date, latitude)
        print(format_golden_hours(current_date, times))
        current_date += timedelta(days=1)
    
    print("\n" + "=" * 54 + "\n")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()