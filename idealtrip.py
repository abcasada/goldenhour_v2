import csv
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import elevation

PRECISION = 0.1 # minutes

# Read the dates and latitudes from the CSV file
latitude_dates = []
with open('latitude_dates.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        date = datetime.strptime(row[0], '%m/%d/%Y')
        latitude = float(row[1].replace('Â°', '').strip())
        latitude_dates.append((date, latitude))

# Calculate the golden hour times and store them in a dictionary
golden_hours = {}
for date, latitude in latitude_dates:
    location = LocationInfo(name="Custom Location", region="Custom Region", latitude=latitude, longitude=0)
    start_time = datetime.combine(date, datetime.min.time())
    end_time = datetime.combine(date, datetime.max.time())
    
    current_time = start_time
    total_minutes = 0

    gh_times = []
    
    while current_time <= end_time:
        current_elevation = elevation(location.observer, current_time)
        
        if current_time == start_time and -4 <= current_elevation <= 6:
            gh_times.append(current_time)
        
        if len(gh_times) % 2 == 0 and current_elevation >= -4 and current_elevation <= 6:
            gh_times.append(current_time)
        elif len(gh_times) % 2 == 1 and (current_elevation < -4 or current_elevation > 6):
            gh_times.append(current_time)
        
        current_time += timedelta(minutes=PRECISION)
    
    if -4 <= elevation(location.observer, end_time) <= 6:
        gh_times.append(end_time)
    
    golden_hours[date] = {
        'morning_start': gh_times[0] if len(gh_times) > 0 else '',
        'morning_end'  : gh_times[1] if len(gh_times) > 1 else '',
        'evening_start': gh_times[2] if len(gh_times) > 2 else '',
        'evening_end'  : gh_times[3] if len(gh_times) > 3 else ''
    }

# Write the results to a new CSV file
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
with open(f'golden_hour_by_day_{timestamp}.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    header = ['Date', 'Morning Start', 'Morning End', 'Evening Start', 'Evening End']
    writer.writerow(header)
    for date, times in golden_hours.items():
        writer.writerow([
            date.strftime('%Y-%m-%d'),
            times['morning_start'].strftime('%H:%M') if times['morning_start'] else '',
            times['morning_end'].strftime('%H:%M') if times['morning_end'] else '',
            times['evening_start'].strftime('%H:%M') if times['evening_start'] else '',
            times['evening_end'].strftime('%H:%M') if times['evening_end'] else ''
        ])