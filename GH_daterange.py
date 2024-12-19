from idealtrip import calculate_golden_hours
from datetime import datetime, timedelta
from typing import Dict

def format_golden_hours(date: datetime, times: Dict) -> str:
    """Format golden hours into a single line with AM/PM times."""
    morning = f"{times['morning_start'].strftime('%I:%M %p')} to {times['morning_end'].strftime('%I:%M %p')}" if times['morning_start'] else "No morning golden hour"
    evening = f"{times['evening_start'].strftime('%I:%M %p')} to {times['evening_end'].strftime('%I:%M %p')}" if times['evening_start'] else "No evening golden hour"
    
    return f"{date.strftime('%Y-%m-%d')}: {morning}; {evening}"

def main():
    while True:
        try:
            start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), '%Y-%m-%d')
            end_date = datetime.strptime(input("Enter end date (YYYY-MM-DD): "), '%Y-%m-%d')
            if end_date < start_date:
                print("End date must be after start date")
                continue
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
            
    latitude = float(input("Enter latitude in degrees (47.3456): "))

    print("\n======================================================\n")
    print("Following are the periods of time where the sun is \nbetween -4 and 6 degrees elevation:\n")
    while start_date <= end_date:
        times = calculate_golden_hours(start_date, latitude)
        print(format_golden_hours(start_date, times))
        start_date += timedelta(days=1)
    print("\n======================================================\n")

if __name__ == '__main__':
    main()