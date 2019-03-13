import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

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