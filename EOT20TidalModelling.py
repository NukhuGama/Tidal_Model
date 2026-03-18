from eo_tides.model import model_tides
import pandas as pd
from datetime import datetime
import calendar
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from shapely.geometry import Point

# Define the Timor-Leste timezone
TL_TZ = ZoneInfo('Asia/Dili')

#now = datetime.now(TL_TZ)
#year = now.year
#month = now.month

now = datetime.now(TL_TZ)
year = 2025
# month = 11

# year = 2025   # We can hardcode year as per our requirements
# month = 3  # We can hardcode month as per our requirements

# start_time = datetime(year, month, 1, tzinfo=TL_TZ)
# last_day = calendar.monthrange(year, month)[1]
# end_time = datetime(year, month, last_day, 23, 0, tzinfo=TL_TZ)

start_time = datetime(year, 1, 1, 0, 0, tzinfo=TL_TZ)
end_time   = datetime(year, 12, 31, 23, 0, tzinfo=TL_TZ)

# ----------------------------------------------------------------------

forecast_points = [
    {'id': 1, 'latitude': -8.53003, 'longitude': 125.58268, 'name': 'Dili'},
    # {'id': 2, 'latitude': -8.541225, 'longitude': 125.548533, 'name': 'Pertamina'},
    # {'id': 3, 'latitude': -8.521669, 'longitude': 125.477173, 'name': 'Tibar'},
    # {'id': 4, 'latitude': -8.22228, 'longitude': 125.610474, 'name': 'Atuaro'},
    # {'id': 5, 'latitude': -9.18678, 'longitude': 124.39236, 'name': 'Raeoa'},
    # {'id': 6, 'latitude': -9.451748, 'longitude': 125.270481, 'name': 'Suai'},
    # {'id': 7, 'latitude': -9.216021, 'longitude': 125.732997, 'name': 'Betano'},
    # {'id': 8, 'latitude': -8.948649, 'longitude': 126.449963, 'name': 'Beaco'},
    # {'id': 9, 'latitude': -8.310848, 'longitude': 127.064086, 'name': 'Com'},
    # {'id': 10, 'latitude': -8.430359, 'longitude': 126.274638, 'name': 'Kairabela'},
    # {'id': 11, 'latitude': -8.533922, 'longitude': 125.681145, 'name': 'Hera'}
]

# ----------------------------------------------------------------------------------
# Map Plot Function
# ----------------------------------------------------------------------------------

def plot_forecast_locations(points):

    # -----------------------------
    # Static center of Timor-Leste
    # -----------------------------
    center_lat = -8.8
    center_lon = 125.7

    center_geom = Point(center_lon, center_lat)
    center_gdf = gpd.GeoDataFrame(geometry=[center_geom], crs="EPSG:4326").to_crs(epsg=3857)

    center_x = center_gdf.geometry.x.iloc[0]
    center_y = center_gdf.geometry.y.iloc[0]

    # Buffer distance (meters)
    buffer = 250000

    extent = [
        center_x - buffer,
        center_x + buffer,
        center_y - buffer,
        center_y + buffer
    ]

    # -----------------------------
    # Convert forecast stations
    # -----------------------------
    data = []

    for p in points:
        data.append({
            "name": p["name"],
            "geometry": Point(p["longitude"], p["latitude"])
        })

    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326").to_crs(epsg=3857)

    # -----------------------------
    # Plot map
    # -----------------------------
    fig, ax = plt.subplots(figsize=(10,8))

    gdf.plot(ax=ax, color="red", markersize=10)  # Set the markersize

    # Labels
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf["name"]):
        ax.text(x + 3000, y + 3000, label, fontsize=4) # Set the marker label size

    # Set bounds manually
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])

    # Basemap
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    ax.set_axis_off()

    plt.title("Tidal Forecast Locations - Timor Leste")

    plt.savefig("forecast_locations.png", dpi=300, bbox_inches="tight")

    plt.close()

    print("Map exported: forecast_locations.png")
# --------------------------------------------------------------------------
# Generate Map
# --------------------------------------------------------------------------
plot_forecast_locations(forecast_points)

# -------------------------------------------------------------------------
# Forecast Extraction
# -------------------------------------------------------------------------

forecast_run_time = now.strftime('%Y-%m-%d %H:%M:%S')

all_dataframes = []

for point in forecast_points:
    print(f"Initiating tidal data extraction for location: {point['name']}")

    times = pd.date_range(start=start_time, end=end_time, freq='1h', tz=TL_TZ)
    times_utc = times.tz_convert("UTC").tz_localize(None)

    df = model_tides(
        x=point['longitude'],
        y=point['latitude'],
        time=times_utc,
        # directory='D:/GCF/tide_models',
        # directory= 'D:/RIMES/2026/OCEAN TRAINING/Tidal_Model/tide_models/ocean_tides'
        # directory= r'D:\RIMES\2026\OCEAN TRAINING\Tidal_Model\tide_models\EOT20\ocean_tides'
        directory= 'tide_models/'
    )

    df.reset_index(inplace=True)

    df['time'] = df['time'].dt.tz_localize('UTC').dt.tz_convert(TL_TZ).dt.tz_localize(None)

    df.rename(columns={
        'time': 'valid_time',
        'tide_height': 'value'
    }, inplace=True)

    df['forecast_time'] = forecast_run_time
    df['location_name'] = point['name']

    # Define MSL for location with id 1 and 5
    msl_map = {
        1: 1.6279,
        5: 2.2165
    }

    df['value'] = df['value'] + msl_map.get(point['id'], 0)
    df['fday_id'] = df['valid_time'].dt.day

    # Keep all required columns
    clean_df = df[[
        'location_name',
        'fday_id',
        'forecast_time',
        'valid_time',
        'value'
    ]]

    all_dataframes.append(clean_df)

# ---------------------------------------------------------------
# Combine all locations into one dataframe
final_df = pd.concat(all_dataframes, ignore_index=True)

# Export to CSV
# csv_filename = f"tidal_forecast_{year}_{month}.csv"
csv_filename = "tidal_forecast_2025_full.csv"
# final_df.to_csv(csv_filename, index = False)
final_df = pd.concat(all_dataframes, ignore_index=True)
# final_df.to_csv("tidal_forecast_2025_full.csv", index=False)
final_df.to_csv(csv_filename, index=False)
print(f"CSV file exported successfully: {csv_filename}")