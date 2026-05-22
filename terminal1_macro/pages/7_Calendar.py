import streamlit as st
import pandas as pd
from datetime import date, timedelta, timezone

from terminal1_macro.components.layout import page_header
from terminal1_macro.data.te_calendar import get_calendar_for_zones
from terminal1_macro.data.fred_releases import fetch_fred_release_dates

IMPORTANCE_COLOR = {1: "🟢", 2: "🟡", 3: "🔴"}
IMPORTANCE_LABEL = {1: "Low", 2: "Medium", 3: "High"}

ZONE_OPTIONS = {
    "All Regions": ["US", "EU", "ASIA"],
    "United States": ["US"],
    "Euro Area": ["EU"],
    "Asia": ["ASIA"],
}

# Countries per zone used to filter FRED events by country field
ZONE_COUNTRIES = {
    "US":   ["United States"],
    "EU":   ["Euro Area", "Germany", "France", "Italy", "Spain", "Netherlands"],
    "ASIA": ["China", "Japan", "India", "South Korea", "Singapore", "Australia"],
}

WINDOW_OPTIONS = {
    "This week":                             (0, 7),
    "Next 2 weeks":                          (0, 14),
    "Past & upcoming (3d back / 14d ahead)": (3, 14),
    "This month":                            (0, 30),
}


def load_data(zones: list[str], days_back: int, days_ahead: int) -> pd.DataFrame:
    frames = []

    # Trading Economics (returns None when calendar not in subscription)
    te_df = get_calendar_for_zones(zones, days_back=days_back, days_ahead=days_ahead)
    if te_df is not None and not te_df.empty:
        frames.append(te_df)

    # FRED — always load, then filter by zone-relevant countries
    fred_df = fetch_fred_release_dates(days_back=days_back, days_ahead=days_ahead)
    if fred_df is not None and not fred_df.empty:
        allowed = []
        for z in zones:
            allowed.extend(ZONE_COUNTRIES.get(z, []))
        if allowed:
            fred_df = fred_df[fred_df["country"].isin(allowed)]
        if not fred_df.empty:
            frames.append(fred_df)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined["date_utc"] = pd.to_datetime(combined["date_utc"], utc=True, errors="coerce")
    combined = combined.dropna(subset=["date_utc"])

    now_utc = pd.Timestamp.now(tz=timezone.utc)
    cutoff_past = now_utc - timedelta(days=days_back)
    cutoff_future = now_utc + timedelta(days=days_ahead)
    combined = combined[
        (combined["date_utc"] >= cutoff_past) & (combined["date_utc"] <= cutoff_future)
    ]

    combined = combined.drop_duplicates(subset=["date_utc", "event", "country"])
    return combined.sort_values("date_utc")


def render_event_table(df: pd.DataFrame):
    if df.empty:
        st.info("No events found for this selection.")
        return

    display_cols = []

    df = df.copy()
    df["Date"] = df["date_utc"].dt.strftime("%Y-%m-%d")
    df["Time (UTC)"] = df["date_utc"].dt.strftime("%H:%M")
    display_cols += ["Date", "Time (UTC)"]

    if "importance_icon" in df.columns:
        df["!"] = df["importance_icon"]
        display_cols.append("!")

    for src_col, dst_col in [
        ("country", "Country"),
        ("event", "Event"),
        ("previous", "Previous"),
        ("forecast", "Forecast"),
        ("actual", "Actual"),
        ("source", "Source"),
    ]:
        if src_col in df.columns:
            df[dst_col] = df[src_col]
            display_cols.append(dst_col)

    st.dataframe(
        df[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "!":          st.column_config.TextColumn("!", width="small"),
            "Date":       st.column_config.TextColumn("Date", width="small"),
            "Time (UTC)": st.column_config.TextColumn("Time (UTC)", width="small"),
            "Country":    st.column_config.TextColumn("Country", width="medium"),
            "Event":      st.column_config.TextColumn("Event", width="large"),
            "Previous":   st.column_config.NumberColumn("Previous", width="small", format="%.2f"),
            "Forecast":   st.column_config.NumberColumn("Forecast", width="small", format="%.2f"),
            "Actual":     st.column_config.NumberColumn("Actual", width="small", format="%.2f"),
            "Source":     st.column_config.TextColumn("Source", width="small"),
        },
    )


def show():
    page_header("Economic Calendar", "Upcoming macro events & data releases")

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        zone_label = st.selectbox("Region", list(ZONE_OPTIONS.keys()), index=0)
        selected_zones = ZONE_OPTIONS[zone_label]

    with col2:
        window_label = st.selectbox("Window", list(WINDOW_OPTIONS.keys()), index=2)
        days_back, days_ahead = WINDOW_OPTIONS[window_label]

    with col3:
        min_importance = st.selectbox(
            "Min. Importance",
            options=[1, 2, 3],
            format_func=lambda x: f"{IMPORTANCE_COLOR[x]} {IMPORTANCE_LABEL[x]}",
            index=0,  # default = Low (show everything)
        )

    st.divider()

    with st.spinner("Loading calendar..."):
        df = load_data(selected_zones, days_back, days_ahead)

    if df.empty:
        st.info(
            "No calendar data found for this selection.\n\n"
            "**Note:** Live economic calendars (Trading Economics) require a premium subscription. "
            "US event dates are sourced from FRED. EU/Asia events are limited."
        )
        return

    if "importance" in df.columns:
        df = df[df["importance"] >= min_importance]

    if df.empty:
        st.info("No events match the selected importance level.")
        return

    # Split past vs upcoming — treat date-only (midnight UTC) events as upcoming on their day
    today_utc = pd.Timestamp.now(tz=timezone.utc).floor("D")
    upcoming = df[df["date_utc"] >= today_utc].sort_values("date_utc")
    past = df[df["date_utc"] < today_utc].sort_values("date_utc", ascending=False)

    # Summary KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Events", len(df))
    k2.metric("Upcoming", len(upcoming))
    k3.metric("Released", len(past))
    high_count = int((df["importance"] == 3).sum()) if "importance" in df.columns else 0
    k4.metric("High Impact", high_count)

    st.divider()

    tab_up, tab_past, tab_all = st.tabs(["Upcoming", "Recently Released", "All Events"])

    with tab_up:
        st.markdown(f"**{len(upcoming)} upcoming events**")
        render_event_table(upcoming.copy())

    with tab_past:
        st.markdown(f"**{len(past)} past events** (last {days_back} days)")
        render_event_table(past.copy())

    with tab_all:
        st.markdown(f"**{len(df)} total events**")
        render_event_table(df.sort_values("date_utc").copy())


show()
