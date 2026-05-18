import yaml
import sys
from collections import Counter
from pathlib import Path

# Config
CATALOG_PATH = Path("terminal1_macro/macro_catalog.yml")

REQUIRED_KEYS = {
    "key",
    "display_name",
    "category",
    "region",
    "source",
    "series_id",
    "frequency",
    "unit",
    "transform_default",
    "priority",
    "status",
}

VALID_CATEGORIES = {
    "Inflation", "Rates", "Labor", "Growth", "Money_Credit", 
    "Risk_Sentiment", "FX", "Commodities", "Housing", "Other"
}
VALID_REGIONS = {"US", "EU", "GLOBAL"}
VALID_SOURCES = {"FRED", "ECB_SDMX", "TRADING_ECONOMICS"}
VALID_STATUSES = {"MAPPED", "TODO_MAPPING"}

def load_catalog(path):
    if not path.exists():
        print(f"Error: Catalog not found at {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)

def validate():
    catalog = load_catalog(CATALOG_PATH)
    if not isinstance(catalog, list):
        print("Error: Catalog root must be a list.")
        sys.exit(1)

    print(f"Loaded {len(catalog)} indicators.")
    
    # 1. Check Uniqueness
    keys = [item.get("key") for item in catalog]
    duplicates = [k for k, v in Counter(keys).items() if v > 1]
    if duplicates:
        print(f"Error: Duplicate keys found: {duplicates}")
        sys.exit(1)
    print("✓ Keys are unique.")

    # 2. Check Schema
    errors = 0
    mapped_count = 0
    todo_count = 0
    
    for idx, item in enumerate(catalog):
        key = item.get("key", f"Index {idx}")
        
        # Missing keys
        missing = REQUIRED_KEYS - item.keys()
        if missing:
            print(f"Error [{key}]: Missing fields {missing}")
            errors += 1
            
        # Validation
        if item.get("category") not in VALID_CATEGORIES:
            print(f"Error [{key}]: Invalid category '{item.get('category')}'")
            errors += 1
            
        if item.get("region") not in VALID_REGIONS:
            print(f"Error [{key}]: Invalid region '{item.get('region')}'")
            errors += 1

        if item.get("source") not in VALID_SOURCES:
            print(f"Error [{key}]: Invalid source '{item.get('source')}'")
            errors += 1

        if item.get("status") not in VALID_STATUSES:
             print(f"Error [{key}]: Invalid status '{item.get('status')}'")
             errors += 1
        
        if item.get("status") == "MAPPED":
            mapped_count += 1
        else:
            todo_count += 1

    if errors > 0:
        print(f"Found {errors} validation errors.")
        sys.exit(1)
        
    print("✓ Schema validation passed.")
    print("-" * 30)
    print(f"Total Indicators: {len(catalog)}")
    print(f"Mapped: {mapped_count}")
    print(f"Todo: {todo_count}")
    print(f"Coverage: {mapped_count / len(catalog) * 100:.1f}%")

if __name__ == "__main__":
    validate()
