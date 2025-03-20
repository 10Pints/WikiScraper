import pytest   # The test framework
import wikipedia as w
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from WikiScraper import WikiScraper

class test_GetSynonyms1():
    def test_1(self):
        url = 'https://en.wikipedia.org/wiki/Henosepilachna_vigintioctopunctata'
        req = Request(url)
        html_page = urlopen(req).read()
        soup = BeautifulSoup(html_page, features='html5lib')
        table = soup.find('table', attrs = {'class':'infobox biota'})
        items = WikiScraper.getSynonyms(table)
        assert(items != None)
  


#if __name__ == '__main__':
#    unittest.main()