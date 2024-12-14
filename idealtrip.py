import csv
from datetime import datetime
from astral import LocationInfo
from astral.sun import golden_hour, SunDirection

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
    location = LocationInfo(latitude=latitude, longitude=0)  # Assuming longitude is 0
    try:
        gh_morning = golden_hour(location.observer, date=date, direction=SunDirection.RISING, tzinfo=location.timezone)
    except ValueError:
        gh_morning = (None, None)
    try:
        gh_evening = golden_hour(location.observer, date=date, direction=SunDirection.SETTING, tzinfo=location.timezone)
    except ValueError:
        gh_evening = (None, None)
    
    golden_hours[date] = {
        'morning_start': gh_morning[0] if gh_morning[0] else '',
        'morning_end': gh_morning[1] if gh_morning[1] else '',
        'evening_start': gh_evening[0] if gh_evening[0] else '',
        'evening_end': gh_evening[1] if gh_evening[1] else ''
    }

# Write the results to a new CSV file
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
with open(f'golden_hour_by_day_{timestamp}.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    header = ['Date', 'Morning Start', 'Morning End', 'Evening Start', 'Evening End']
    writer.writerow(header)
    for date, times in golden_hours.items():
        writer.writerow([date.strftime('%Y-%m-%d'), times['morning_start'], times['morning_end'], times['evening_start'], times['evening_end']])