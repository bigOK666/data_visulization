import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import folium
from sklearn.cluster import KMeans

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

print(map_toronto)
# define Foursquare service
CLIENT_ID = '' # your Foursquare ID
CLIENT_SECRET = '' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)

# define function to get nearby venues
def getNearbyVenues(names, latitudes, longitudes, radius=500):
    venues_list = []
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)

        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID,
            CLIENT_SECRET,
            VERSION,
            lat,
            lng,
            radius,
            LIMIT)

        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']

        # return only relevant information for each nearby venue
        venues_list.append([(
            name,
            lat,
            lng,
            v['venue']['name'],
            v['venue']['location']['lat'],
            v['venue']['location']['lng'],
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighbourhood',
                             'Neighbourhood Latitude',
                             'Neighbourhood Longitude',
                             'Venue',
                             'Venue Latitude',
                             'Venue Longitude',
                             'Venue Category']

    return (nearby_venues)
# get nearby 50 venues of every neighbourhood
LIMIT = 50
toronto_venues = getNearbyVenues(names=df_borough_toronto['Neighbourhood'],
                                   latitudes=df_borough_toronto['Latitude'],
                                   longitudes=df_borough_toronto['Longitude']
                                  )
# examine size of toronto venues
print(toronto_venues.shape)
print(toronto_venues.head())

print(toronto_venues.groupby('Neighbourhood').count())

# onehot encoding
toronto_onehot = pd.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
toronto_onehot['Neighbourhood'] = toronto_venues['Neighbourhood']

# move neighborhood column to the first column
fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
toronto_onehot = toronto_onehot[fixed_columns]

print(toronto_onehot.head())

# group the data
toronto_grouped = toronto_onehot.groupby('Neighbourhood').mean().reset_index()
print(toronto_grouped)

# define a function to return most commen venues
def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)

    return row_categories_sorted.index.values[0:num_top_venues]

num_top_venues = 5

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighbourhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighbourhood'] = toronto_grouped['Neighbourhood']

for ind in np.arange(toronto_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)

print(neighborhoods_venues_sorted.head())

#cluster neighbourhood

# set number of clusters
kclusters = 5

toronto_grouped_clustering = toronto_grouped.drop('Neighbourhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

# check cluster labels generated for each row in the dataframe
print(kmeans.labels_[0:10])

# add clustering labels
neighborhoods_venues_sorted.insert(1, 'Cluster Labels', kmeans.labels_)

toronto_merged = df_borough_toronto

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
toronto_merged = toronto_merged.join(neighborhoods_venues_sorted.set_index('Neighbourhood'), on='Neighbourhood')

#toronto_merged.head() # check the last columns!

import matplotlib.cm as cm
import matplotlib.colors as colors

# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i * x) ** 2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'],
                                  toronto_merged['Neighbourhood'], toronto_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster - 1],
        fill=True,
        fill_color=rainbow[cluster - 1],
        fill_opacity=0.7).add_to(map_clusters)

print(map_clusters)