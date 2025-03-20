# GetAlternariaSp.py
# Gets the list of Alternaria species
import logging.config
import wikipedia as w
from bs4 import BeautifulSoup
import requests
import logging.config
import os

logger = logging.getLogger("my_app")

def GetAlternariaSp():
    logger.info('GetAlternariaSp 000: starting')
    out_file = 'Alternaria species.txt'
    # open a file to hold the references found
    if os.path.exists(out_file):
        os.remove(out_file)
        
    logger.info(f"GetAlternariaSp 010: output file '{out_file}' deleted successfully.")
    logger.info(f'MnRtn 020:opening {out_file} to hold the species found') 

    f = open(out_file, 'w')
    f.write(f'id\tpathogen_nm\turl\timage\ttaxonomy\tbinomial_nm\tsynonyms\tstatus\n')
    url = 'https://en.wikipedia.org/wiki/List_of_Alternaria_species'
    r = requests.get(url)
    print(r.content)
    soup = BeautifulSoup(r.content, features='html5lib')
    #<div class="mw-heading mw-heading2">
    # <h2 id="C">C</h2><span class="mw-editsection"><span class="mw-editsection-bracket">
    # [</span><a href="/w/index.php?title=List_of_Alternaria_species&amp;action=edit&amp;section=3" title="Edit section: C">
    # <span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>
    
    # get the list of species groups (by first letter of second name)
    #spieces_grps = soup.find_all('div', attrs = {'class':'mw-heading mw-heading2'})
    
    # for each one get its list of divs class: 'div-col'
    #for spieces_grp in spieces_grps:
    species_cols = soup.find_all('div', attrs = {'class':'div-col'})
    
    # for each div_col get its i-tags
    for species_col in species_cols:
        i_tags = species_col.find_all('i')
        # they contain 2 elements: <a  href> species name</a> and a span with the author
        a_tags = species_col.find_all('a')
        
        for a_tag in a_tags:
            if a_tag != None:
                binomial_nm = a_tag.text
                #binomial_nm = f'Alternata.{name}'
                sp_url = ''
                title = a_tag['title']

                if '(page does not exist)' not in title:
                    sp_url = a_tag['href']
                    
                logger.info(F'{binomial_nm} url:{sp_url}')
                f.write(f'{binomial_nm}\t{sp_url}\n')
        
    logger.info('GetAlternariaSp(): leaving')
    f.close()    
    
if __name__ == '__main__':
    GetAlternariaSp() 