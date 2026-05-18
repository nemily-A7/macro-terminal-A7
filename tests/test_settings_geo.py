import pytest
from terminal1_macro.data.loader import get_series_for_zone

def test_zone_filtering_returns_different_keys():
    """Ensure US, EU, and ASIA return different sets of indicators."""
    us_data, us_profile = get_series_for_zone("US")
    eu_data, eu_profile = get_series_for_zone("EU")
    asia_data, asia_profile = get_series_for_zone("ASIA")
    
    # Check Profile Integrity
    assert us_profile["label"] == "United States"
    assert eu_profile["label"] == "Euro Area"
    assert asia_profile["label"] == "Asia"
    
    # Check Result Differentiation (US Keys vs EU Keys)
    us_keys = {item["meta"]["key"] for item in us_data}
    eu_keys = {item["meta"]["key"] for item in eu_data}
    asia_keys = {item["meta"]["key"] for item in asia_data}
    
    # Should be disjoint or at least different
    # (Some global indicators might theoretically overlap but likely not with current catalog)
    assert "us_gdp" in us_keys
    assert "eu_gdp_growth" in eu_keys
    assert "asia_gdp" in asia_keys
    
    assert "us_gdp" not in eu_keys
    assert "eu_gdp_growth" not in us_keys

def test_source_mapping():
    """Verify correct sources are mapped."""
    us_data, _ = get_series_for_zone("US")
    eu_data, _ = get_series_for_zone("EU")
    
    # US should be FRED
    for item in us_data:
        assert item["meta"]["source"] == "FRED"
        
    # EU should be TRADING_ECONOMICS (or ECB when mapped)
    for item in eu_data:
        assert item["meta"]["source"] in ["TRADING_ECONOMICS", "ECB_SDMX"]
