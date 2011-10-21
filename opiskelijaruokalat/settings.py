# Scrapy settings for opiskelijaruokalat project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'opiskelijaruokalat'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['opiskelijaruokalat.spiders']
NEWSPIDER_MODULE = 'opiskelijaruokalat.spiders'
DEFAULT_ITEM_CLASS = 'opiskelijaruokalat.items.OpiskelijaruokalatItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

# Feed settings
FEED_URI = 'opiskelijaruokalat.kml'
#FEED_URI = 'stdout:'
FEED_FORMAT = 'kml'
FEED_EXPORTERS = {
    'kml' : 'opiskelijaruokalat.exporter.KmlItemExporter'
}
