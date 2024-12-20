import pytest
from datetime import datetime
from GH_daterange import format_golden_hours

def test_format_golden_hours(sample_date, sample_golden_hours):
    """Test time formatting"""
    result = format_golden_hours(sample_date, sample_golden_hours)
    assert '2023-06-21' in result
    assert 'AM' in result
    assert 'PM' in result

def test_format_golden_hours_no_morning():
    """Test formatting when morning golden hour doesn't exist"""
    times = {
        'morning_start': None,
        'morning_end': None,
        'evening_start': datetime(2023, 6, 21, 20, 30),
        'evening_end': datetime(2023, 6, 21, 21, 30)
    }
    result = format_golden_hours(datetime(2023, 6, 21), times)
    assert 'No morning golden hour' in result
