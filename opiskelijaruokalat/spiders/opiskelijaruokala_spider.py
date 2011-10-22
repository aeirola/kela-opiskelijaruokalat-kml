from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy import log

from urlparse import urlparse

from opiskelijaruokalat.items import OpiskelijaruokalaItem

AREA_URL_PREFIX = 'http://www.kela.fi/in/internet/suomi.nsf/alias/'
KARTTALINKKI_URL_PREFIX = 'http://asiointi.kela.fi/opruoka_app/OpruokaApplication?karttalinkki='
RAVINTOLA_URL_PREFIX = 'http://asiointi.kela.fi/opruoka_app/'

class OpiskelijaruokalaSpider(BaseSpider):
    name = "opiskelijaruokala"
    allowed_domains = ["www.kela.fi", "asiointi.kela.fi"]
    start_urls = [AREA_URL_PREFIX + 'suo00000000']
    
    def parse(self, response):
        """Parse finland"""
        self.log("Parsing Finland", level=log.INFO)
        hxs = HtmlXPathSelector(response)
        maakuntas = hxs.select("//map[@id='idx_map']/area")
        seen_codes = set()
        
        if False:
            # For testing
            ruokala = OpiskelijaruokalaItem()
            ruokala['name'] = 'Testiruokala'
            ruokala['address'] = 'Aleksis Kiven katu 5, Helsinki'
            yield ruokala
            return
        
        if False:
            # For testing 
            yield Request('http://asiointi.kela.fi/opruoka_app/OpruokaApplication?karttalinkki=suo08000109', self.parseKunta)
            #yield Request('http://asiointi.kela.fi/opruoka_app/OpruokaApplication/Show?ravinro=20083082', self.parseOpiskelijaruokala)
            return
        
        for maakunta in maakuntas:
            code = str.split(str(maakunta.select('@href').extract()[0]), "'")[1]
            if code not in seen_codes:
                self.log("Found maakunta code %s" % code, level=log.INFO)
                yield Request(AREA_URL_PREFIX + code, self.parseMaakunta)
                seen_codes.add(code)
            
        
    
    def parseMaakunta(self, response):
        """docstring for parseMaakunta"""
        hxs = HtmlXPathSelector(response)
        kuntas = hxs.select("//map[@id='idx_map']/area")
        seen_codes = set()
        for kunta in kuntas:
            code = str.split(str(kunta.select('@href').extract()[0]), "'")[1]
            if code not in seen_codes:
                self.log("Found kunta code %s" % code, level=log.INFO)
                yield Request(KARTTALINKKI_URL_PREFIX + code, self.parseKunta)
                seen_codes.add(code)
            
        
    
    def parseKunta(self, response):
        """docstring for parseKunta"""
        hxs = HtmlXPathSelector(response)
        
        # Check if KELA is okay
        if not hxs.select("//div[@id='content']/div/table"):
            self.log(hxs.select("//div[@id='content']/div/p/text()")[0].extract(), level=log.ERROR)
            return
            
        restaurants = hxs.select("//div[@id='content']/div/table/tr/td/a")
        for restaurant in restaurants:
            self.log("Found restaurant %s" % restaurant.select('text()').extract()[0], level=log.INFO)
            yield Request(RAVINTOLA_URL_PREFIX + restaurant.select('@href').extract()[0], self.parseOpiskelijaruokala)
    
    def parseOpiskelijaruokala(self, response):
        """docstring for parseOpiskelijaruokala"""
        hxs = HtmlXPathSelector(response)
        
        # Check if KELA is okay
        if not hxs.select("//div[@id='content']/div/table"):
            self.log(hxs.select("//div[@id='content']/div/p/text()")[0].extract(), level=log.ERROR)
            return
        
        # Check if data is missing
        nameSelectors = hxs.select("//div[@id='content']/div/table/tr/td/b/text()")
        if not nameSelectors:
            self.log("No restaurant data found", level=log.WARNING)
            return
        
        self.log("Parsing restaurant %s" % nameSelectors[0].extract(), level=log.INFO)
        
        item = OpiskelijaruokalaItem()
        item['name'] = nameSelectors[0].extract().strip()
        item['address_street'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[6].extract().strip()
        item['address_postalcode'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[9].extract().strip()
        item['address_city'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[12].extract().strip()
        item['owner'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[19].extract().strip()
        
        urlSelectors = hxs.select("//div[@id='content']/div/table/tr/td/a/@href")
        if len(urlSelectors) >= 1:
            item['restaurant_url'] = hxs.select("//div[@id='content']/div/table/tr/td/a/@href")[0].extract().strip()
        else:
            item['restaurant_url'] = ""
        
        if len(urlSelectors) >= 2:
            item['owner_url'] = hxs.select("//div[@id='content']/div/table/tr/td/a/@href")[1].extract().strip()
        else:
            item['owner_url'] = ""
        
        return item
    

