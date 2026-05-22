import yaml
from pathlib import Path

_BASE = Path(__file__).parent.parent / "terminal1_macro"

_catalog: list[dict] | None = None
_geo: dict | None = None


def load_catalog() -> list[dict]:
    global _catalog
    if _catalog is None:
        with open(_BASE / "macro_catalog.yml", "r", encoding="utf-8") as f:
            _catalog = yaml.safe_load(f)
    return _catalog


def load_geo_profiles() -> dict:
    global _geo
    if _geo is None:
        with open(_BASE / "geo_profiles.yml", "r", encoding="utf-8") as f:
            _geo = yaml.safe_load(f)
    return _geo
