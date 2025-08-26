import pandas as pd
import requests
from datetime import timedelta, datetime
import time
import random

# Input / Output paths
INPUT_FILE = r"D:\resecarch\aaa uk offical dataset\main+2\accident_full_weather_detailed.csv"
OUTPUT_FILE = r"D:\resecarch\aaa uk offical dataset\non-accident\non_accident_weather_balanced.csv"

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

# Function to fetch weather for a specific hour
def fetch_weather(lat, lon, datetime_str, retries=3):
    """Fetch hourly weather data for a given lat/lon and datetime string."""
    date = datetime_str.split("T")[0]
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={date}&end_date={date}"
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
                    return {k: data[k][i] for k in data if k != "time"}
        except Exception as e:
            print(f"Retry {attempt+1} failed for {lat},{lon} {datetime_str}: {e}")
            time.sleep(2 ** attempt)
    return {}  # Return empty dict if no data


# Collect single random non-accident weather record per accident
all_samples = []

for idx, row in df.iterrows():
    lat, lon, accident_dt = row["latitude"], row["longitude"], row["datetime"]

    # Pick a random datetime in the same year
    year = accident_dt.year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year, 12, 31, 23, 0)

    while True:
        random_days = random.randint(0, (end_of_year - start_of_year).days)
        random_hours = random.randint(0, 23)
        random_dt = start_of_year + timedelta(days=random_days, hours=random_hours)

        if random_dt != accident_dt:  # make sure not equal to accident datetime
            break

    datetime_str = random_dt.strftime('%Y-%m-%dT%H:00')
    weather_data = fetch_weather(lat, lon, datetime_str)

    sample_row = {**row.to_dict(), **weather_data}
    sample_row.update({
        "sample_type": "non_accident",
        "random_datetime": datetime_str
    })

    all_samples.append(sample_row)

    if idx % 50 == 0:
        print(f"Processed {idx}/{len(df)} records")

# Convert to DataFrame
result_df = pd.DataFrame(all_samples)

# Save to CSV
result_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Non-accident weather samples saved to {OUTPUT_FILE}")
