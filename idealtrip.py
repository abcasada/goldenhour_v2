import csv
import logging
import os
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from astral import LocationInfo
from astral.sun import elevation

# Constants
INPUT_DIR = "data_input"
OUTPUT_DIR = "data_output"
PRECISION = 0.1  # minutes
GOLDEN_HOUR_MIN_ELEVATION = -4
GOLDEN_HOUR_MAX_ELEVATION = 6
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%Y%m%d%H%M%S'
OUTPUT_TIME_FORMAT = '%H:%M'  # New constant for time output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_latitude_data(filepath: str) -> List[Tuple[datetime, float]]:
    """
    Read dates and latitudes from CSV file.
    Returns a list of tuples containing (date, latitude).
    """
    latitude_dates = []
    try:
        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                try:
                    date = datetime.strptime(row[0], DATE_FORMAT)
                    latitude = float(row[1].replace('Â°', '').strip())
                    if not -90 <= latitude <= 90:
                        raise ValueError(f"Invalid latitude value: {latitude}")
                    latitude_dates.append((date, latitude))
                except (ValueError, IndexError) as e:
                    logger.error(f"Error processing row {row}: {str(e)}")
    except FileNotFoundError:
        logger.error(f"Input file {filepath} not found")
        raise
    return latitude_dates

def validate_latitude(latitude: float) -> None:
    """Validate latitude is within valid range."""
    if not isinstance(latitude, (int, float)):
        raise TypeError("Latitude must be a number")
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90 degrees")

def calculate_golden_hours(date: datetime, latitude: float) -> Dict:
    """
    Calculate golden hour times for given date and latitude.
    Returns a dictionary with morning and evening start/end times.
    """
    if not isinstance(date, datetime):
        raise TypeError("Date must be a datetime object")
    validate_latitude(latitude)

    location = LocationInfo(
        name="Custom Location", 
        region="Custom Region", 
        latitude=latitude, 
        longitude=0
    )
    
    start_time = datetime.combine(date, datetime.min.time())
    end_time = datetime.combine(date, datetime.max.time())
    current_time = start_time
    gh_times = []

    while current_time <= end_time:
        current_elevation = elevation(location.observer, current_time)
        
        in_range = (GOLDEN_HOUR_MIN_ELEVATION <= current_elevation <= GOLDEN_HOUR_MAX_ELEVATION)
        out_of_range = (current_elevation < GOLDEN_HOUR_MIN_ELEVATION or 
                       current_elevation > GOLDEN_HOUR_MAX_ELEVATION)
        
        if current_time == start_time and in_range:
            gh_times.append(current_time)
        
        if len(gh_times) % 2 == 0 and in_range:
            gh_times.append(current_time)
        elif len(gh_times) % 2 == 1 and out_of_range:
            gh_times.append(current_time)
        
        current_time += timedelta(minutes=PRECISION)

    if (GOLDEN_HOUR_MIN_ELEVATION <= elevation(location.observer, end_time) <= 
        GOLDEN_HOUR_MAX_ELEVATION):
        gh_times.append(end_time)

    keys = ['morning_start', 'morning_end', 'evening_start', 'evening_end']
    return {k: t for k, t in zip(keys, gh_times + [''] * (4 - len(gh_times)))}

def main():
    """Main program execution."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_dir = os.path.join(script_dir, INPUT_DIR)
        output_dir = os.path.join(script_dir, OUTPUT_DIR)
        
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        input_file = os.path.join(input_dir, 'latitude_dates.csv')
        output_file = os.path.join(
            output_dir, 
            f'GH_times_{datetime.now().strftime(TIME_FORMAT)}.csv'
        )
        
        latitude_dates = read_latitude_data(input_file)
        golden_hours = {
            date: calculate_golden_hours(date, latitude) 
            for date, latitude in latitude_dates
        }
        
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            header = ['Date', 'Morning Start', 'Morning End', 'Evening Start', 'Evening End']
            writer.writerow(header)
            
            for date, times in golden_hours.items():
                fmt = OUTPUT_TIME_FORMAT
                row = [
                    date.strftime(DATE_FORMAT),
                    times['morning_start'].strftime(fmt) if times['morning_start'] else '',
                    times['morning_end'].strftime(fmt) if times['morning_end'] else '',
                    times['evening_start'].strftime(fmt) if times['evening_start'] else '',
                    times['evening_end'].strftime(fmt) if times['evening_end'] else ''
                ]
                writer.writerow(row)
            
            logger.info(f"Output written to {output_file}")
    except Exception as e:
        logger.error(f"Program failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()