# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 22:36:49 2018

@author: Laci
"""

from bs4 import BeautifulSoup
import pandas as pd
import re    
import requests
import unidecode


#
#base = "https://www.jofogas.hu/oldalterkep"
#htmlfile = urllib.request.urlopen(base)
#soup = BeautifulSoup(htmlfile, 'lxml')
#


"""
url = 'https://www.jofogas.hu/oldalterkep'
r = requests.get(url)
data = r.content
soup = BeautifulSoup(data,'lxml')

try1 = soup.find('a', class_='region-link')
try2 = soup.select('a.region-link')

counties = []

for y in try2:
    counties.append(y.find(text=True))

# lowercase of 'counties' list items to manipulate target scraping links
counties_link = []
for county in counties:
    counties_link.append(unidecode.unidecode(county).lower())
 """


# number of links to scrape based on the last page's number
last_page_num = 'a.ad-list-pager-item.ad-list-pager-item-last.active-item.js_hist_li.js_hist'
link_start = 'https://ingatlan.jofogas.hu/budapest/ingatlan?o={}&st=s'

# target lists that'll be saved (to Excel, SQL, etc)
rooms = []
size = []
price = []
place = []
subject = []
price_full = []
photo = []


r_last_page = requests.get('https://ingatlan.jofogas.hu/budapest/ingatlan?o=1&st=s') # first page to get the last page's number
last_page_data = r_last_page.content
soup_last_page = BeautifulSoup(last_page_data, 'lxml')


last_page_div = 'a.ad-list-pager-item.ad-list-pager-item-last.active-item.js_hist_li.js_hist' # css selector of last page
last_page = soup_last_page.select(last_page_div)[0] # location of last page
last_page_link = last_page.get('href') # last page's url
last_page_num = re.findall(r'\d+',last_page_link)[0] # extracting digits with regex from the last page's url


for num in range(1,int(last_page_num)+1):
        r_temp = requests.get(link_start.format(num))
        data_temp = r_temp.content
        soup_temp = BeautifulSoup(data_temp, 'lxml')
        
        contentArea = soup_temp.select('div.contentArea')[1:]
        for x in contentArea:
            roomz = x.find('div', attrs={'class':'rooms'})
            rooms.append(roomz.text if roomz else "0 szoba")
            size_ = x.find('div', attrs={'class':'size'})
            size.append(size_.text if size_ else "NaN")
            price_=x.find('div', attrs={'class':'squareprice'})
            price.append(price_.text if price_ else "NaN")
            price_full_= x.find('div', attrs={'class':'priceBox'}).text.strip().strip('\xa0Ft')
            price_full.append(price_full_)
            photo_=x.find('span', attrs={'class':'picNumC'})
            photo.append(photo_.text if photo_ else "0")
        place_ = soup_temp.select('section.reLiSection.cityname')[1:]
        for i in place_:
            place.append(i.text)
        subject_ = soup_temp.select('a.subject')[1:]
        for i in subject_:
            subject.append(i.text)
            
# A few prints to see if every list items are the same lenght
print('Analytics:')
print('Rooms: ',len(rooms))
print('Size: ', len(size))
print('Price: ', len(price))
print('Place: ', len(place))
print('Subject: ', len(subject))
print('Full price: ', len(price_full))
print('Photos: ', len(photo))

details = {'subject': subject,
           'place': place,
           'size': size,
           'rooms': rooms,
           'price/m2': price,
           'full price':price_full,
           'photos':photo}


df = pd.DataFrame(details)

print('*'*10)

# 
writer = pd.ExcelWriter('Budapest.xlsx')
df.to_excel(writer, index=False)
writer.save()
