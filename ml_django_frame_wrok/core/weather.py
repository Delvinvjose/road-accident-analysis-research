import datetime as dt, requests

HOURLY = [
    'temperature_2m','apparent_temperature','relative_humidity_2m','dewpoint_2m',
    'surface_pressure','cloudcover','cloudcover_low','cloudcover_mid','cloudcover_high',
    'windspeed_10m','winddirection_10m','windgusts_10m',
    'precipitation','rain','snowfall',
]
API = 'https://archive-api.open-meteo.com/v1/archive'

def _nearest_hour(ts: dt.datetime) -> dt.datetime:
    return (ts.replace(minute=0, second=0, microsecond=0)
            + (dt.timedelta(hours=1) if ts.minute >= 30 else dt.timedelta()))

def get_weather(lat: float, lon: float, when_local: dt.datetime, tz='Europe/Dublin') -> dict:
    target = _nearest_hour(when_local)
    day = target.date().isoformat()
    params = {
        'latitude': lat, 'longitude': lon,
        'start_date': day, 'end_date': day,
        'hourly': ','.join(HOURLY),
        'timezone': tz,
        'windspeed_unit': 'kmh',
        'temperature_unit': 'celsius',
        'pressure_unit': 'hPa',
        'precipitation_unit': 'mm',
    }
    r = requests.get(API, params=params, timeout=20)
    r.raise_for_status()
    H = r.json().get('hourly', {})
    times = H.get('time', [])
    tgt = target.replace(second=0, microsecond=0).isoformat(timespec='minutes')
    idx = times.index(tgt) if tgt in times else 0
    return {k: (H.get(k) or [None])[idx] for k in HOURLY}
