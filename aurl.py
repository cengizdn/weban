from bs4 import BeautifulSoup
from lxml import html
import requests
import re
#from io import StringIO

def getHepsiBuradaCategoriesLinks():
    hepsi_burada_url = "http://www.hepsiburada.com"
    soup = BeautifulSoup(requests.get(hepsi_burada_url).text, "lxml")
    categories = soup.body.footer.contents[5].contents[1].contents[3]
    #soup.findAll('a', attrs={'href': re.compile("^http://")})
    #print(url)
    print("...")
    for link in categories.findAll('a', attrs={'href': re.compile("^http://")}):            #start with http://
        print(link.get('href')+"?siralama=coksatan")
    print("------------")
    for link in categories.findAll('a', attrs={'href': re.compile("^(?!http://).+")}):      #not strat with http://
        print(hepsi_burada_url+link.get('href')+"?siralama=coksatan")

#//*[@id="f1903ab5-272e-4a21-b3e2-0bd88c9b2667"]/div/ul
#<div class="breadcrumbs-wrapper container
#http://www.hepsiburada.com/awox-2271-22-56-ekran-full-hd-led-ekran-p-EVAWOX2272
#xpath('//div[@class="breadcrumbs-wrapper container"]/ul/li/a/text()')


def getHBFullCategoryLists(link):               #get full category path for an item.
    #link="http://www.hepsiburada.com/awox-2271-22-56-ekran-full-hd-led-ekran-p-EVAWOX2272"
    r=requests.get(link)
    t = html.fromstring(r.content)
    t.xpath('//div[@class="breadcrumbs-wrapper container"]/ul/li/a/span/text()')
'''
['Ana Sayfa',
 'Ev Elektronik Ürünleri',
 'Ses Görüntü Sistemleri',
 'Televizyonlar, LED Ekranlar',
 'Awox Televizyonlar, LED Ekranlar']
'''

def getHPPageCount(link):                       #get page count for a category link.
    r=requests.get(link)
    t = html.fromstring(r.content)
    return int(t.xpath('//div[@id="pagination"]/ul/li/a/text()')[7])
'''
443
''
