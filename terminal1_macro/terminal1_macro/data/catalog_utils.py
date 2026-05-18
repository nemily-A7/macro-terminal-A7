import yaml
from pathlib import Path

CATALOG_PATH = Path(__file__).parents[2] / "macro_catalog.yml"

def load_catalog():
    with open(CATALOG_PATH, "r") as f:
        return yaml.safe_load(f)
