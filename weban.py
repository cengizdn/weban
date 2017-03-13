#from bs4 import BeautifulSoup
from lxml import html
import requests
import simplejson
import re
#from io import StringIO

def delFirstLastChars(sString,cString):
    i,j=0,len(sString)
    for c in sString:
        if c in cString: i=i+1
        else: break
    for c in reversed(sString):
        if c in cString: j=j-1
        else: break
    return sString[i:j]


def getHBCategoryLinks():
    hepsi_burada_url = "http://www.hepsiburada.com"
    link=hepsi_burada_url
    thb=html.fromstring((requests.get(link)).content)
    lCategoryLink=thb.xpath('//div[@class="footer-middle-left"]/section[2]/ul/li/a/@href')
    lCategoryTitle=thb.xpath('//div[@class="footer-middle-left"]/section[2]/ul/li/a/@title')

    dCategories={}
    for i in range(len(lCategoryLink)):
        if not lCategoryLink[i].startswith('http'):
            print("%-40s" % (str(lCategoryTitle[i])),link+str(lCategoryLink[i]))
            dCategories.update({str(lCategoryTitle[i]): [link+str(lCategoryLink[i]),0]})
        else:
            print("%-40s" % (str(lCategoryTitle[i])),str(lCategoryLink[i]))
            dCategories.update({str(lCategoryTitle[i]): [str(lCategoryLink[i]),1]})
    return dCategories


def getCategryItemsLinks(link,mlink,iPageCount=2):
    print("LINK:",mlink+link)
    thb = html.fromstring((requests.get(mlink+link)).content)
    ln = int(thb.xpath('//div[@id="pagination"]/ul/li/a/text()')[7])         #get page count for categry Link.
    liLink=[]
    del thb
    if iPageCount > ln: iPageCount=ln
    for i in range(1,iPageCount+1):
        thb=html.fromstring((requests.get(mlink+link+"?siralama=coksatan&sayfa="+str(i))).content)
        ltLink=thb.xpath('//li[@class="search-item col lg-1 md-1 sm-1  custom-hover not-fashion-flex"]/div/a/@href') #get detailed products' links order by coksatan
        print(i,link+"?sayfa="+str(i))
        for lt in ltLink:
                liLink.append(lt)                       #Add all prduct item item links to ad List and return IT.
        del ltLink
        del thb
    return liLink

def saveCategoryItemLinks(liLink,fn):
    fp = open('/home/john/prj/weban/'+fn+'.dmp','w')
    simplejson.dump(liLink,fp)
    fp.close()

def getItemInfo(link,mlink):
    dInfo={'Link':link}

    thb = html.fromstring((requests.get(mlink+link)).content)

    lProductName = thb.xpath('//h1[@itemprop="name"]/text()')          #get item name
    dInfo.update({'Name':delFirstLastChars(lProductName[0]," \n\r")})

    lBrandName = thb.xpath('//div[@class="product-information col lg-5 sm-1"]/span[@class="brand-name"]/a/text()')     #get item brand name
    dInfo.update({'Brand':delFirstLastChars(lBrandName[0]," \n\r")})


    lItemCategory = thb.xpath('//div[@class="breadcrumbs-wrapper container"]/ul/li/a/span/text()') #get item category path
    for i in range(1,len(lItemCategory)):
        dInfo.update({"Category" + str(i): delFirstLastChars(lItemCategory[i],' \n\r')})


    lOriginalPrice = (thb.xpath('//div[@itemprop="offers"]/del[@id="originalPrice"]/text()'))[0].split()   #get original price and split currency from it-['599,00', 'TL']
    dInfo.update({'oCurrency':lOriginalPrice[1]})
    dInfo.update({'oPrice':float("{0:.2f}".format(float(lOriginalPrice[0].replace(",","."))))})        #convert str to float. to do this, first "," is converted to "."


    fDiscountPrice = float("{0:.2f}".format(float(thb.xpath('//div[@itemprop="offers"]/span[@itemprop="price"]/@content')[0])))
    dInfo.update({'dPrice':fDiscountPrice})

    lDiscountPriceCurrency=thb.xpath('//div[@itemprop="offers"]/span[@itemprop="price"]/span[3]/text()')
    dInfo.update({'dCurrency':lDiscountPriceCurrency[0]})

    #l_CampainRibbon = thb.xpath('//a[@id="first-campaign-ribbon"]/span/text()')

    lRatingText = thb.xpath('//div[@class="ratings-table"]/a/div/div[@class="rating-text-col"]/div/text()')
    print(lRatingText)
    lRatingValue =thb.xpath('//div[@class="ratings-table"]/a/div/div[@class="rating-text-col"]/span/text()')
    fRemark=0.0
    iRemark=0
    dRemark={'Mükemmel':5,'Çok İyi':4,'İyi':3,'Fena Değil':2,'Çok Kötü':1}
    for i in range(len(lRatingText)):                   #Calculate Average Rating
        tRemark=int(delFirstLastChars(lRatingValue[i],"()"))
        dInfo.update({lRatingText[i]:tRemark })           #deleted '(' and ')' chars int strins then converted to int.
        fRemark =fRemark+tRemark*dRemark[lRatingText[i]]
        iRemark =iRemark+tRemark

    dInfo.update({'Remark': float("{0:.2f}".format(fRemark / iRemark))})

    lMerchant=thb.xpath('//table[@id="merchant-list"]/tbody/tr/td[@class="merchantName"]/div[@class="merchant-info"]/a/text()')






    del thb
    return dInfo,lMerchant

def getItemRemarks(link,mlink,iPageCount=2):
    thb = html.fromstring((requests.get(mlink+link+"-yorumlari")).content)
    lPagination = thb.xpath('//div[@id="pagination"]/ul/li/a/text()')
    ln=int(lPagination[len(lPagination)-1])
    lRemarks=[]
    if iPageCount > ln: iPageCount= ln
    for i in range(iPageCount):
        thb=html.fromstring((requests.get(mlink+link+"-yorumlari?sayfa="+str(i))).content)
        #lkRemarks = thb.xpath('//ul[@class="chevron-list-container col lg-5 md-4 sm-3 box-container"]/li/dev[@class="ratings-container"]/text()')
        liRemarks=thb.xpath('//ul[@class="chevron-list-container col lg-5 md-4 sm-3 box-container"]/li/strong/text()')
        lRatingValue=thb.xpath('//ul[@class="chevron-list-container col lg-5 md-4 sm-3 box-container"]/li/div[@class="ratings-container"]/div/div/@style')
        lReviewRespons = thb.xpath('//ul[@class="chevron-list-container col lg-5 md-4 sm-3 box-container"]/li/div[@class ="reveiw-response"]/p/a/b/text()')

        for j in range(len(liRemarks)):

            lRatingUserName = thb.xpath('//ul[@class="chevron-list-container col lg-5 md-4 sm-3 box-container"]/li['+str(j)+']/div[@class="comment-provider"]/span[@class="user-info"]/text()')
            iAge=0
            if len(lRatingUserName)<1 :
                lRatingUserName.append('noUser')
                iAge=-1
            else:
                sTmp=re.findall('\d+', lRatingUserName[0])
                if len(sTmp) > 0: iAge=int(sTmp[0])

            lRatingUserLocation = thb.xpath('//ul[@class="chevron-list-container col lg-5 md-4 sm-3 box-container"]/li['+str(j)+']/div[@class="comment-provider"]/span[@class="location"]/text()')
            if len(lRatingUserLocation)<1 : lRatingUserLocation.append('noLocation')

            lText = thb.xpath('//ul[@class="chevron-list-container col lg-5 md-4 sm-3 box-container"]/li['+str(j)+']/p/text()')
            if len(lText) < 1 : lText.append('noText')

            iResponseYes=0
            sTmp = re.findall('\d+', lReviewRespons[j*2])
            if len(sTmp) > 0: iResponseYes = int(sTmp[0])

            iResponseNo=0
            sTmp = re.findall('\d+', lReviewRespons[j*2+1])
            if len(sTmp) > 0: iResponseNo = int(sTmp[0])

            lRemarks.append((liRemarks[j], lText[0], int(lRatingValue[j].replace('%','').split()[1])/20,lRatingUserName[0],iAge,lRatingUserLocation[0],iResponseYes,iResponseNo))

        print('.',end='',flush=True)
        del thb
    return lRemarks



def getHBFullCategoryLists(link):               #get full category path for an item. wasn't used
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

def getCategoryPageCount(link):                       #get page count for a category link. wasn't used
    r=requests.get(link)
    t = html.fromstring(r.content)
    return int(t.xpath('//div[@id="pagination"]/ul/li/a/text()')[7])

def getCategoryItemlinks(link):
    thb = html.fromstring((requests.get(link)).content)
    return thb.xpath('//li[@class="search-item col lg-1 md-1 sm-1  custom-hover not-fashion-flex"]/div/a/@href') #get detailed product link. wasn't used


'''
    ic=10
    lILink=[]
    for i in range(ic):
        ltlLink=weban.getCategoryItemlinks(clink+"?sayfa="+str(i))
        for lt in ltlLink:
            lIlink.append(lt)
        del ltlLink
'''

'''
    soup = BeautifulSoup(requests.get(link).text, "lxml")
    categories = soup.body.footer.contents[5].contents[1].contents[3]
    soup.findAll('a', attrs={'href': re.compile("^http://")})

    for link in categories.findAll('a', attrs={'href': re.compile("^http://")}):            #start with http://
        print(link.get('href')+"?siralama=coksatan")
    for link in categories.findAll('a', attrs={'href': re.compile("^(?!http://).+")}):      #not strat with http://
        print(hepsi_burada_url+link.get('href')+"?siralama=coksatan")

    thb.xpath('//span[@class="brand-name"]/a/text()')   #get item brand name, not used. First I used it, then i found better one.
'''

