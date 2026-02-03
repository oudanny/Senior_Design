import pandas as pd

df = pd.read_csv(r'C:\Users\txjam\Documents\homework\design\forecasting\ResEcon_MoProd.csv')
print(f'Columns: {df.columns.tolist()}')
well_API = df['API_UWI'].unique().tolist()
print(f'\nAPIs: {well_API}')

LATLONG_csv = df[['API_UWI', 'Latitude', 'Longitude']]
LATLONG_csv = LATLONG_csv.groupby('API_UWI').first().reset_index()
LATLONG_csv.to_csv('TempleFork_LATLONG.csv')