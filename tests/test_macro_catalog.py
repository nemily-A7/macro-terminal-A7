import pytest
import yaml
from pathlib import Path
from terminal1_macro.scripts.validate_catalog import load_catalog, validate, CATALOG_PATH

def test_catalog_load():
    """Ensure YAML loads and is a list."""
    catalog = load_catalog(CATALOG_PATH)
    assert isinstance(catalog, list)

def test_catalog_keys_unique():
    """Ensure strict uniqueness of keys."""
    catalog = load_catalog(CATALOG_PATH)
    keys = [item["key"] for item in catalog]
    assert len(keys) == len(set(keys))

def test_coverage_nonzero():
    """Ensure we have mapped indicators."""
    catalog = load_catalog(CATALOG_PATH)
    mapped = [i for i in catalog if i["status"] == "MAPPED"]
    assert len(mapped) > 0
    
def test_validation_script_runs():
    """Run the main validation logic without error."""
    try:
        validate()
    except SystemExit as e:
        if e.code != 0:
            pytest.fail("Validation script exited with error.")
