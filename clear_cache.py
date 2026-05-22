"""One-shot script to purge ECB/Eurostat cached rows so they re-fetch with fixed YYYY-MM-DD dates."""
import sys
sys.path.insert(0, ".")
from backend.db import _con_get, _lock

with _lock:
    con = _con_get()
    # Remove any series whose date values are YYYY-MM format (7-char)
    # Simpler: just wipe the whole cache so everything re-fetches fresh
    rows = con.execute("SELECT COUNT(*) FROM series_cache").fetchone()[0]
    con.execute("DELETE FROM series_cache")
    print(f"Cleared {rows} cached series — all will re-fetch on next request.")
    con.close()
