from fastapi import APIRouter, Query
from backend.data.fred import fetch_calendar

router = APIRouter()

ZONE_COUNTRIES = {
    "US": ["United States"],
    "EU": ["Euro Area", "Germany", "France", "Italy", "Spain", "Netherlands"],
    "ASIA": ["China", "Japan", "India", "South Korea", "Singapore", "Australia"],
}


@router.get("/calendar")
def get_calendar(
    zones: str = Query(default="US,EU,ASIA"),
    days_back: int = Query(default=3),
    days_ahead: int = Query(default=14),
):
    zone_list = [z.strip() for z in zones.split(",")]
    allowed_countries: set[str] = set()
    for z in zone_list:
        allowed_countries.update(ZONE_COUNTRIES.get(z, []))

    events = fetch_calendar(days_back=days_back, days_ahead=days_ahead)

    if allowed_countries:
        events = [e for e in events if e["country"] in allowed_countries]

    return {"events": events}
