import pandas as pd
import folium

# read data from csv file
df = pd.read_csv('Police_Department_Incidents_-_Previous_Year__2016_.csv', index_col=0)

df_criminal = df.drop(df[(df.Category=="NON-CRIMINAL") | (df.Category=="MISSING PERSON") | (df.Category=="SUICIDE")].index)

ds_district=df_criminal["PdDistrict"].value_counts()

df_district=pd.DataFrame({'Neighborhood':ds_district.index, 'Count':ds_district.values})

# load map data from json file
sanfrancisco_geo=r'world_countries.json'
sanfrancisco_map = folium.Map(location=[37.77,-122.42], zoom_start=11, tiles='Mapbox Bright')
# format using choropleth
sanfrancisco_map.choropleth(
    geo_data=sanfrancisco_geo,
    data=df_district,
    columns=['Neighborhood', 'Count'],
    key_on='feature.properties.DISTRICT',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Crime Rate in San Francisco'
)

# display map
sanfrancisco_map