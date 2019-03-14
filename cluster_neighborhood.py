import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import folium

# get the content of wikipedia page
website_url = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup=BeautifulSoup(website_url, 'lxml')
#print(soup.prettify())

### since the table data is in table tag with class wikitable sortable so we can get them

My_table=soup.find('table', {'class':'wikitable sortable'})
#print(My_table)

### get headers as table column title
headers = [header.text for header in My_table.find_all('th')]
headers[2] = headers[2][:-1]
print(headers)

### get raw data from table content in td tag
rows = []
for row in My_table.find_all('tr'):
    rows.append([val.text for val in row.find_all('td')])

### create raw dataframe from webpage
df = pd.DataFrame(rows, columns = headers)
#df.head()

df_valid=df[df.Borough.notnull()]

#df_valid.head()

df_valid_borough = df_valid[df_valid.Borough != "Not assigned"]
#df_valid_borough.head()

df_valid_borough = df_valid_borough.replace("\n", "", regex=True)
#df_valid_borough


df_valid_borough['Neighbourhood'] = np.where(df_valid_borough['Neighbourhood']=="Not assigned", df_valid_borough['Borough'], df_valid_borough['Neighbourhood'])
#df_valid_borough

df_borough_grouped=df_valid_borough.groupby(['Postcode', 'Borough'], as_index=False).agg({'Neighbourhood':lambda x: ','.join(x)})
#df_borough_grouped
# read coordinates data from csv file and create dataframe
df_coordinate=pd.read_csv('Geospatial_Coordinates.csv')
# add the coordinate data to df_borough_grouped
df_borough_grouped['Latitude'] = df_coordinate['Latitude']
df_borough_grouped['Longitude'] = df_coordinate['Longitude']

print(df_borough_grouped)

### analyse only borough containing Toronto
df_borough_toronto=df_borough_grouped[df_borough_grouped['Borough'].str.contains("Toronto")].reset_index()

### get coordinate of Toronto
address = 'Toronto'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))



map_toronto = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(df_borough_toronto['Latitude'], df_borough_toronto['Longitude'],
                           df_borough_toronto['Neighbourhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)

map_toronto