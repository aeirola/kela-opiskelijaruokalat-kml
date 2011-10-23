from scrapy.contrib.exporter import BaseItemExporter
from xml.sax.saxutils import XMLGenerator
from geopy import geocoders

class KmlItemExporter(BaseItemExporter):
    """docstring for KmlItemExporter"""
    
    KML_NAME = """KELA Opiskelijaruokalat"""
    KML_DESCRIPTION = """Lista KELAn opiskelijaruokaloista."""
    
    def __init__(self, out_file, **kwargs):
        self._configure(kwargs)
        self.xg = XMLGenerator(out_file, encoding=self.encoding)
        self.gc = geocoders.Google(domain='maps.google.fi', format_string="%s, Suomi")
    
    def start_exporting(self):
        self.xg.startDocument()
        self.xg.startElement('kml', {'xmlns':"http://www.opengis.net/kml/2.2"})
        self.xg.startElement('Document', {})
        self._export_xml_field('name', self.KML_NAME)
        self._export_xml_field('description', self.KML_DESCRIPTION)
        self.xg.startElement('Style', {})
        self.xg.endElement('Style')
    
    def export_item(self, item):
        self.xg.startElement('Placemark', {})
        # Name
        self._export_xml_field('name', item['name'])
        
        # Description
        description = item['owner'] + ' ' + item['restaurant_url']
        self._export_xml_field('description', description)
        
        # Address
        address = item['address_street'] + ' ' + item['address_postalcode'] + ' ' + item['address_city']
        self._export_xml_field('address', address)
        
        # Point
        # The city field doesn't always hold a city but may be some university campus name that google doesn't
        # recognize, luckily the postal code with country name should be enough
        geocode_address = item['address_street'] + ' ' + item['address_postalcode']
        try:
            geocode_results = self.gc.geocode(self._to_str_if_unicode(geocode_address), exactly_one=False)
            if geocode_results:
                _, (lat, lng) = geocode_results[0]
                # Check that we are in finland
                if 59<lat and lat<71 and 19<lng and lng<33:
                    self.xg.startElement('Point', {})
                    self._export_xml_field('coordinates', "%s,%s" % (lng, lat))
                    self.xg.endElement('Point')
        except:
            pass
        
        self.xg.endElement('Placemark')
    
    def _export_xml_field(self, name, serialized_value):
        self.xg.startElement(name, {})
        self.xg.characters(self._to_str_if_unicode(serialized_value))
        self.xg.endElement(name)
    
    def finish_exporting(self):
        self.xg.endElement('Document')
        self.xg.endElement('kml')
        self.xg.endDocument()
    

