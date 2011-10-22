# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class OpiskelijaruokalaItem(Item):
    # define the fields for your item here like:
    name = Field()
    address_street = Field()
    address_postalcode = Field()
    address_city = Field()
    restaurant_url = Field()
    owner = Field()
    owner_url = Field()
    kela_url = Field()
