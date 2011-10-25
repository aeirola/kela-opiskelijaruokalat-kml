from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy import log

from opiskelijaruokalat.items import OpiskelijaruokalaItem

AREA_URL_PREFIX = 'http://www.kela.fi/in/internet/suomi.nsf/alias/'
KARTTALINKKI_URL_PREFIX = 'http://asiointi.kela.fi/opruoka_app/OpruokaApplication?karttalinkki='
RAVINTOLA_URL_PREFIX = 'http://asiointi.kela.fi/opruoka_app/'

class OpiskelijaruokalaSpider(BaseSpider):
    """Spider for crawling the student restaurants form the KELA interface"""
    
    name = "opiskelijaruokala"
    allowed_domains = ["www.kela.fi", "asiointi.kela.fi"]
    start_urls = [AREA_URL_PREFIX + 'suo00000000']
    # Since the KELA site is stateful, in the way that restaurant info doesn't show unless the previous kunta
    # requested was the kunta of the restaurant, we need to take extra measures to order them up
    kunta_priority = 1000000
    
    def parse(self, response):
        """Parse finland"""
        self.log("Parsing Finland", level=log.INFO)
        hxs = HtmlXPathSelector(response)
        maakuntas = hxs.select("//map[@id='idx_map']/area")
        seen_codes = set()
        
        for maakunta in maakuntas:
            code = str.split(str(maakunta.select('@href').extract()[0]), "'")[1]
            if code not in seen_codes:
                self.log("Found maakunta code %s" % (code), level=log.INFO)
                yield Request(AREA_URL_PREFIX + code, self.parse_maakunta)
                seen_codes.add(code)
            
        
    
    def parse_maakunta(self, response):
        """docstring for parseMaakunta"""
        hxs = HtmlXPathSelector(response)
        kuntas = hxs.select("//map[@id='idx_map']/area")
        seen_codes = set()
        for kunta in kuntas:
            code = str.split(str(kunta.select('@href').extract()[0]), "'")[1]
            if code not in seen_codes:
                self.log("Found kunta code %s" % (code), level=log.INFO)
                seen_codes.add(code)
                yield Request(KARTTALINKKI_URL_PREFIX + code, self.parse_kunta)
            
        
    
    def parse_kunta(self, response):
        """docstring for parseKunta"""
        hxs = HtmlXPathSelector(response)
        
        # Check if KELA is okay
        if not hxs.select("//div[@id='content']/div/table"):
            self.log(hxs.select("//div[@id='content']/div/p/text()")[0].extract(), level=log.ERROR)
            return
        
        # Store the priority for this kunta so that all for this kunta will be in order
        current_priority = self.kunta_priority
        # Decrement for next kunta
        self.kunta_priority -= 2
        # Re-request this kunta with priority one above the restaurants
        yield Request(response.request.url, self.empty, priority=current_priority, dont_filter=True)
        
        # Get restaurants
        restaurants = hxs.select("//div[@id='content']/div/table/tr/td/a")
        for restaurant in restaurants:
            self.log("Found restaurant %s" % (restaurant.select('text()').extract()[0]), level=log.INFO)
            # Request restaurants with one priority below that of the kunta
            yield Request(RAVINTOLA_URL_PREFIX + restaurant.select('@href').extract()[0], self.parse_opiskelijaruokala, priority=current_priority-1)
            
    
    def parse_opiskelijaruokala(self, response):
        """docstring for parseOpiskelijaruokala"""
        hxs = HtmlXPathSelector(response)
        
        # Check if KELA is okay
        if not hxs.select("//div[@id='content']/div/table"):
            self.log(hxs.select("//div[@id='content']/div/p/text()")[0].extract(), level=log.ERROR)
            return
        
        # Check if data is missing
        name_selectors = hxs.select("//div[@id='content']/div/table/tr/td/b/text()")
        if not name_selectors:
            self.log("No restaurant data found", level=log.WARNING)
            return
        
        self.log("Parsing restaurant %s" % name_selectors[0].extract(), level=log.INFO)
        
        item = OpiskelijaruokalaItem()
        item['name'] = name_selectors[0].extract().strip()
        item['address_street'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[6].extract().strip()
        item['address_postalcode'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[9].extract().strip()
        item['address_city'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[12].extract().strip()

        # Not all restaurants have url fields set
        url_selectors = hxs.select("//div[@id='content']/div/table/tr/td/a/@href")
        if len(url_selectors) >= 1:
            item['restaurant_url'] = url_selectors[0].extract().strip()
        else:
            item['restaurant_url'] = ""
            
        # Owner name shifted if no restaurant url
        if len(url_selectors) >= 1:
            item['owner'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[19].extract().strip()
        else:
            item['owner'] = hxs.select("//div[@id='content']/div/table/tr/td/text()")[18].extract().strip()
        
        if len(url_selectors) >= 2:
            item['owner_url'] = url_selectors[1].extract().strip()
        else:
            item['owner_url'] = ""
        
        return item
    
    def empty(self, response):
        """docstring for empty"""
        pass

