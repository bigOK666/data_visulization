import requests
from bs4 import BeautifulSoup
import pandas as pd

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
df.head()