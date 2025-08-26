from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from . import model as model_svc
from . import weather as wx
import datetime as dt

@require_http_methods(["GET"])
def index(request):
    return render(request, "index.html")

@require_http_methods(["POST"])
def predict(request):
    try:
        lat = float(request.POST['latitude'])
        lon = float(request.POST['longitude'])
        when = dt.datetime.fromisoformat(f"{request.POST['date']}T{request.POST['time']}")

        # numeric user inputs
        age_of_driver      = float(request.POST['age_of_driver'])
        engine_capacity_cc = float(request.POST['engine_capacity_cc'])
        age_of_vehicle     = float(request.POST['age_of_vehicle'])
        driver_imd_decile  = float(request.POST['driver_imd_decile'])

        # helper to parse select values as numeric codes (incl. -1)
        def fnum(name):
            v = request.POST.get(name, "")
            return float(v) if v not in ("", None) else -1.0

        # categorical code inputs
        towing_and_articulation   = fnum('towing_and_articulation')
        driver_home_area_type     = fnum('driver_home_area_type')
        vehicle_type              = fnum('vehicle_type')
        driver_distance_banding   = fnum('driver_distance_banding')
        sex_of_driver             = fnum('sex_of_driver')
        journey_purpose_of_driver = fnum('journey_purpose_of_driver')
        age_band_of_driver        = fnum('age_band_of_driver')

        # weather & time
        W = wx.get_weather(lat, lon, when)
        time_group = when.hour + 1          # 1..24
        day_of_week = when.isoweekday()     # 1..7

        features = {
            # weather
            'snowfall': W.get('snowfall'),
            'towing_and_articulation': towing_and_articulation,  # categorical code
            'precipitation': W.get('precipitation'),
            'driver_home_area_type': driver_home_area_type,      # categorical code
            'relative_humidity_2m': W.get('relative_humidity_2m'),
            'time_group': time_group,
            'vehicle_type': vehicle_type,                        # categorical code
            'rain': W.get('rain'),
            'surface_pressure': W.get('surface_pressure'),
            'temperature_2m': W.get('temperature_2m'),
            'driver_distance_banding': driver_distance_banding,  # categorical code
            'windgusts_10m': W.get('windgusts_10m'),
            'driver_imd_decile': driver_imd_decile,
            'apparent_temperature': W.get('apparent_temperature'),
            'cloudcover': W.get('cloudcover'),
            'cloudcover_low': W.get('cloudcover_low'),
            'sex_of_driver': sex_of_driver,                      # categorical code
            'winddirection_10m': W.get('winddirection_10m'),
            'windspeed_10m': W.get('windspeed_10m'),
            'journey_purpose_of_driver': journey_purpose_of_driver,  # cat code
            'cloudcover_high': W.get('cloudcover_high'),
            'cloudcover_mid': W.get('cloudcover_mid'),
            'day_of_week': day_of_week,
            'dewpoint_2m': W.get('dewpoint_2m'),
            'age_of_vehicle': age_of_vehicle,
            'engine_capacity_cc': engine_capacity_cc,
            'age_of_driver': age_of_driver,
            'age_band_of_driver': age_band_of_driver,            # categorical code
        }

        y, proba = model_svc.predict(features)
        label_text = "Accident risk (class 1)" if y == 1.0 else "No accident (class 0)"
        risk_band = None
        if proba is not None:
            risk_band = ("Very High" if proba >= 0.85 else
                         "High" if proba >= 0.65 else
                         "Medium" if proba >= 0.45 else
                         "Low" if proba >= 0.25 else "Very Low")

        return render(request, "index.html", {
            "result": y, "proba": proba, "label_text": label_text,
            "risk_band": risk_band, "features": features
        })
    except Exception as e:
        return render(request, "index.html", {"error": str(e)})
