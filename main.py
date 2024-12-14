import multiprocessing
from astral import LocationInfo
from astral.sun import elevation
from datetime import datetime, timedelta
import csv #todo: use pandas for xlsx

PRECISION = 1 # minutes

def twilight_minutes_day(latitude, date):
    location = LocationInfo(name="Custom Location", region="Custom Region", latitude=latitude, longitude=0)
    start_time = datetime.combine(date, datetime.min.time())
    end_time = datetime.combine(date, datetime.max.time())
    
    current_time = start_time
    total_minutes = 0
    
    while current_time <= end_time:
        elev = elevation(location.observer, current_time) #todo: add diffraction correction? or not really relevant for twilight?
        if -4 <= elev <= 6:
            total_minutes += PRECISION
        current_time += timedelta(minutes=PRECISION)
    
    return total_minutes

def twilight_minutes_year(latitude):
    data = []

    for x in range(365):
        date = datetime(2023,1,1) + timedelta(x) # or timedelta(days=x)?
        minutes_in_range = twilight_minutes_day(latitude, date)
        data.append([date.strftime('%Y-%m-%d'), latitude, minutes_in_range])
    
    return data

def process_latitude(latitude):
    return twilight_minutes_year(latitude)

def main():
    start_time = datetime.now()
    latitudes = [59.91, 59.13, 59.97, 61.9, 63.25, 65.46, 66.74, 67.96, 69.49, 70.51, 70.2, 70.2, 68.55, 65.32, 62.52, 60.99, 59.91]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"sun_elevation_minutes_{timestamp}.csv"
    
    with multiprocessing.Pool() as pool:
        results = pool.map(process_latitude, latitudes)
    
    all_data = {}
    for data in results:
        for entry in data:
            date = entry[0]
            minutes_in_range = entry[2]
            if date not in all_data:
                all_data[date] = {}
            all_data[date][entry[1]] = minutes_in_range
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date"] + [f"{lat}\u00B0" for lat in latitudes])
        for date, lat_data in all_data.items():
            row = [date] + [lat_data.get(lat, 0) for lat in latitudes]
            writer.writerow(row)
    
    end_time = datetime.now()
    print(f"Elapsed time: {end_time - start_time}")

if __name__ == "__main__":
    main()