import pytest
from datetime import datetime
from main import twilight_hours_day, twilight_hours_year, process_latitude

@pytest.fixture
def sample_date():
    return datetime(2023, 6, 21)  # Summer solstice as example date

def test_twilight_hours_day(sample_date):
    """Test twilight_hours_day with various latitudes"""
    # Test equator (should be roughly same year-round)
    hours = twilight_hours_day(0, sample_date)
    assert 1.5 <= hours <= 2.5
    
    # Test polar region in summer (should be long)
    hours = twilight_hours_day(80, sample_date)
    assert hours > 4

def test_twilight_hours_year():
    """Test twilight_hours_year returns correct data structure"""
    result = twilight_hours_year(45)
    assert len(result) == 365
    assert len(result[0]) == 3
    assert isinstance(result[0][0], str)
    assert isinstance(result[0][1], float)
    assert isinstance(result[0][2], float)

def test_invalid_latitude():
    """Test handling of invalid latitudes"""
    with pytest.raises(ValueError):
        twilight_hours_day(91, sample_date)

def test_invalid_latitude_type():
    """Test handling of non-numeric latitude"""
    with pytest.raises(TypeError):
        twilight_hours_day("45", sample_date)

def test_invalid_date_type():
    """Test handling of invalid date type"""
    with pytest.raises(TypeError):
        twilight_hours_day(45, "2023-06-21")
