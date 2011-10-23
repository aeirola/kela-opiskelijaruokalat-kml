KELAn Opiskelijaruokaloiden KML scraperi
========================================
Pieni Scrapy projekti joka hakee KELAn sivuilta kaikkien Suomen opiskelijaruokaloiden tiedot ja tuottaa siitä Google Maps KML tiedoston karttakäyttöä varten.

Tiedot haetaan KELAn [Opiskelijaravintolahausta](http://www.kela.fi/in/internet/suomi.nsf/alias/suo00000000?Open&pal=http://asiointi.kela.fi/opruoka_app/OpruokaApplication).

Käyttö
------
1. Asenna vaaditut paketit:
	1. `sudo easy_install scrapy`
	2. `sudo easy_install geopy`
2. Aja komento: `scrapy crawl opiskelijaruokalat`
3. Huomaa `opiskelijaruokalat.kml` tiedosto

Rikki
-----
* Tietyt osoitteet annettu hankalassa muodossa jota Google ei osaa geokoodata, joten eivät saa koordinaatteja. Pitäisi esim poistaa sulut geokoodauspyynnöstä ja muut moiset.
* Tarkempi virheenkäsittely
