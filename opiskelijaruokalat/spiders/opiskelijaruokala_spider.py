from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy import log

from opiskelijaruokalat.items import OpiskelijaruokalaItem

AREA_URL_PREFIX = 'http://www.kela.fi/in/internet/suomi.nsf/alias/'
KARTTALINKKI_URL_PREFIX = 'http://asiointi.kela.fi/opruoka_app/OpruokaApplication?karttalinkki='
RAVINTOLA_URL_PREFIX = 'http://asiointi.kela.fi/opruoka_app/OpruokaApplication/Show?ravinro='

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
        
        if True:
            # For testing
            ruokala = OpiskelijaruokalaItem()
            ruokala['name'] = 'Testiruokala'
            ruokala['address'] = 'Aleksis Kiven katu 5, Helsinki'
            yield ruokala
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
        restaurants = hxs.select("//div[@id='content']/div/table/tbody/tr/td/a")
        for restaurant in restaurants:
            self.log("Found restaurant %s" % restaurant.select('text()'), level=log.INFO)
            yield Request(RAVINTOLA_URL_PREFIX + code, self.parseOpiskelijaruokala)
    
    def parseOpiskelijaruokala(self, repsonse):
        """docstring for parseOpiskelijaruokala"""
        self.log("What to do?", level=log.INFO)
    

