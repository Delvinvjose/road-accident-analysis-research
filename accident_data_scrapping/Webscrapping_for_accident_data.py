import pandas as pd
import requests
import time
from tqdm import tqdm

# Input / Output paths
INPUT_FILE = r"D:\resecarch\aaa uk offical dataset\fatal_vs_slight\serious_fatal.csv"
OUTPUT_FILE = r"D:\resecarch\aaa uk offical dataset\fatal_vs_slight\accident_fatal_slight_exact_weather_fast.csv"

# Load dataset
df = pd.read_csv(INPUT_FILE)

# Combine date and time into a datetime column
df["datetime"] = pd.to_datetime(
    df["date"].astype(str) + " " + df["time"].astype(str),
    dayfirst=True,
    errors="coerce"
)

# Drop invalid rows
df = df.dropna(subset=["latitude", "longitude", "datetime"])
print(f"Loaded {len(df)} valid accident records")


def fetch_weather(lat, lon, date, datetime_str, retries=3, max_offset=0.02, step=0.01):
    """Fetch weather for given lat/lon/date. Try fallback if missing (±2 km)."""
    offsets = [0.0]
    for d in range(1, int(max_offset / step) + 1):
        for dx in [-d, d]:
            offsets.append(dx * step)

    for dlat in offsets:
        for dlon in offsets:
            trial_lat, trial_lon = round(lat + dlat, 2), round(lon + dlon, 2)
            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={trial_lat}&longitude={trial_lon}&start_date={date}&end_date={date}"
                "&hourly=temperature_2m,apparent_temperature,precipitation,rain,snowfall,"
                "weathercode,surface_pressure,cloudcover,cloudcover_low,cloudcover_mid,"
                "cloudcover_high,et0_fao_evapotranspiration,evapotranspiration,windgusts_10m,"
                "windspeed_10m,winddirection_10m,relative_humidity_2m,dewpoint_2m,visibility"
                "&timezone=auto"
            )

            for attempt in range(retries):
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json().get("hourly", {})
                        times = data.get("time", [])
                        if datetime_str in times:
                            i = times.index(datetime_str)
                            weather = {k: data[k][i] for k in data if k != "time"}
                            weather["used_lat"] = trial_lat
                            weather["used_lon"] = trial_lon
                            return weather
                except:
                    time.sleep(2 ** attempt)
    return {}


# --- Caching to avoid duplicate API calls ---
weather_cache = {}
all_records = []

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Fetching weather"):
    lat, lon, dt = row["latitude"], row["longitude"], row["datetime"]

    date = dt.strftime('%Y-%m-%d')
    datetime_str = dt.strftime('%Y-%m-%dT%H:00')

    # Round coordinates to increase cache hits (~2 km grid)
    cache_key = (round(lat, 2), round(lon, 2), date)

    if cache_key not in weather_cache:
        weather_cache[cache_key] = fetch_weather(lat, lon, date, datetime_str)

    weather_data = weather_cache[cache_key]

    record = {**row.to_dict(), **weather_data}
    record["weather_datetime"] = datetime_str
    all_records.append(record)

# Convert to DataFrame
result_df = pd.DataFrame(all_records)

# Save to CSV
result_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Weather data saved to {OUTPUT_FILE}")
