import pytest
from datetime import datetime
from idealtrip import calculate_golden_hours, read_latitude_data

@pytest.fixture
def sample_date():
    return datetime(2023, 6, 21)

def test_calculate_golden_hours(sample_date):
    """Test golden hour calculations"""
    result = calculate_golden_hours(sample_date, 45)
    assert 'morning_start' in result
    assert 'morning_end' in result
    assert 'evening_start' in result
    assert 'evening_end' in result
    
    # Test time order
    if result['morning_start'] and result['morning_end']:
        assert result['morning_start'] < result['morning_end']
    if result['evening_start'] and result['evening_end']:
        assert result['evening_start'] < result['evening_end']

def test_read_latitude_data(tmp_path):
    """Test CSV file reading"""
    # Create test CSV file
    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text(
        "Date,Latitude\n2023-06-21,45.0°\n2023-06-22,46.0°"
    )
    
    result = read_latitude_data(str(csv_path))
    assert len(result) == 2
    assert isinstance(result[0][0], datetime)
    assert isinstance(result[0][1], float)

def test_invalid_input_types():
    """Test handling of invalid input types"""
    with pytest.raises(TypeError):
        calculate_golden_hours("2023-06-21", 45)  # Invalid date type
    with pytest.raises(TypeError):
        calculate_golden_hours(sample_date, "45")  # Invalid latitude type
    with pytest.raises(ValueError):
        calculate_golden_hours(sample_date, 91)  # Invalid latitude value
