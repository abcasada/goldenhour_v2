import pytest
from datetime import datetime

@pytest.fixture
def sample_date():
    return datetime(2023, 6, 21)  # Summer solstice

@pytest.fixture
def sample_latitudes():
    return [0, 45, 90]  # Equator, mid-latitude, pole

@pytest.fixture
def sample_golden_hours():
    return {
        'morning_start': datetime(2023, 6, 21,  5, 30),
        'morning_end':   datetime(2023, 6, 21,  6, 30),
        'evening_start': datetime(2023, 6, 21, 20, 30),
        'evening_end':   datetime(2023, 6, 21, 21, 30)
    }
