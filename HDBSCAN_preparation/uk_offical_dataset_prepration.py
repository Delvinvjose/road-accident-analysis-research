import pandas as pd

# Load input file
input_path = r"D:\resecarch\aaa uk offical dataset\dft-road-casualty-statistics-collision-last-5-years.csv"

data = pd.read_csv(input_path)
print(f" Loaded: {len(data)} rows")

#Group by lat/lon
data_grouped = data.groupby(['longitude', 'latitude']).size().reset_index(name='accident_count')

#Keep spots with 2+ accidents
hotspots = data_grouped[data_grouped['accident_count'] >= 2].copy().reset_index(drop=True)

#Add blackspot ID and radius
hotspots['blackspot_id'] = range(1, len(hotspots) + 1)
hotspots['radius_m'] = 100

#Merge back
data = data.merge(hotspots[['longitude', 'latitude', 'blackspot_id']], on=['longitude', 'latitude'], how='left')
data['blackspot_id'] = data['blackspot_id'].fillna(0).astype(int)

#Save or preview
output_path = r"D:\resecarch\aaa uk offical dataset\dft-road-casualty-blackspots.csv"
data.to_csv(output_path, index=False)

print(f" Done! File saved: {output_path}")
print(data.head())
