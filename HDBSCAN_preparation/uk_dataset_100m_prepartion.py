import pandas as pd
import numpy as np

#Load CSV
input_path = r"D:\resecarch\aaa uk offical dataset\dft-road-casualty-blackspots.csv"
data = pd.read_csv(input_path)

print(f" Loaded: {len(data)} rows")

#Split into clusters and non-clusters
blackspots = data[data['blackspot_id'] > 0].copy()
non_blackspots = data[data['blackspot_id'] == 0].copy()

print(f" Blackspot points: {len(blackspots)}")
print(f" Non-blackspot points: {len(non_blackspots)}")

#Prepare blackspot centers
centers = blackspots.groupby('blackspot_id').agg({
    'latitude': 'mean',
    'longitude': 'mean'
}).reset_index()

print(f" Blackspot centers: {len(centers)}")

#Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

#Snap each non-blackspot point
updated_ids = []

centers_coords = centers[['latitude', 'longitude', 'blackspot_id']].values

for idx, row in non_blackspots.iterrows():
    lat, lon = row['latitude'], row['longitude']

    # Calculate distances to all centers
    dists = haversine(lat, lon, centers_coords[:, 0], centers_coords[:, 1])

    within_radius = dists <= 100

    if np.any(within_radius):
        nearest_idx = np.argmin(dists)
        nearest_id = int(centers_coords[nearest_idx, 2])
    else:
        nearest_id = 0

    updated_ids.append(nearest_id)

    if idx % 50000 == 0:
        print(f" Processed {idx} points")

#Update non-blackspots
non_blackspots['blackspot_id'] = updated_ids

#Merge back
final_data = pd.concat([blackspots, non_blackspots], ignore_index=True)

print(f" Final dataset: {len(final_data)} rows")

#Save
output_path = r"D:\resecarch\aaa uk offical dataset\dft-road-casualty-blackspots-snapped_100.csv"
final_data.to_csv(output_path, index=False)
print(f" Saved: {output_path}")
