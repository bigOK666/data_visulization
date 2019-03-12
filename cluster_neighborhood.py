import requests
from bs4 import BeautifulSoup

# get the content of wikipedia page
website_url = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup=BeautifulSoup(website_url, 'lxml')
#print(soup.prettify())

### since the table data is in table tag with class wikitable sortable so we can get them

My_table=soup.find('table', {'class':'wikitable sortable'})
print(My_table)