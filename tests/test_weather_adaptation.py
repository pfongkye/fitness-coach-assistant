import pytest
from mcp_servers.weather_service import WeatherAdaptationService
from tools.periodization_tools import PeriodizationEngine

def test_weather_service_parsing():
    # Test local city lookup
    report = WeatherAdaptationService.get_weather_by_city("Paris")
    assert "temperature_c" in report
    assert "heat_index_c" in report
    assert "training_adaptations" in report

def test_workout_heat_and_rain_adaptation():
    base_workout = {
        "title": "Metcon Helen",
        "description": "3 Rounds: 400m Run, 21 KB Swings, 12 Pull-ups"
    }
    
    # 1. Simulate Hot Weather
    hot_weather = {
        "temperature_c": 34.0,
        "heat_index_c": 36.0,
        "is_raining": False
    }
    readiness = {"volume_multiplier": 1.0, "soreness_hotspots": []}
    
    adapted = PeriodizationEngine.adapt_workout_for_conditions(
        base_workout=base_workout,
        readiness_data=readiness,
        weather_data=hot_weather
    )
    assert any("Heat Alert" in a for a in adapted["applied_adaptations"])
    assert "indoor_substitutions" in adapted
    assert "400m Run" in adapted["indoor_substitutions"]

    # 2. Simulate Rainy Weather
    rain_weather = {
        "temperature_c": 18.0,
        "heat_index_c": 18.0,
        "is_raining": True
    }
    adapted_rain = PeriodizationEngine.adapt_workout_for_conditions(
        base_workout=base_workout,
        readiness_data=readiness,
        weather_data=rain_weather
    )
    assert any("Rain detected" in a for a in adapted_rain["applied_adaptations"])
