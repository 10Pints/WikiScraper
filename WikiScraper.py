import urllib.request as url
import urllib.error as urlError
import wikipedia as w
from bs4 import BeautifulSoup# as bs
import pandas as pd
import DbConnect
import getTaxonomyString
import getSynonyms
import getPage
import os
import getTaxonomyString
import getBinomialName
import logging.config
import pathlib
import json

logger = logging.getLogger("my_app")

def setup_logging():  
    config_file = pathlib.Path("config.json")
    
    with open(config_file) as f_in:
        config = json.load(f_in)
        
    logging.config.dictConfig(config)

#************ main code ************
setup_logging()

logger.info('MnRtn 000: starting, connecting to sql server db')
conn = DbConnect.DbConnect()
cursor = conn.cursor()
cursor.execute('Select pathogen_id, pathogen_nm,latin_nm,alt_latin_nms,alt_common_nms FROM pathogen')
rows = cursor.fetchall()
i = 0
url = ''
alt_latin_nms = ''
alt_common_nms = ''
out_file = 'pathogens_wiki_urls.txt'

# open a file to hold the references found
if os.path.exists(out_file):
    os.remove(out_file)
    logger.info(f"MnRtn 020: output file '{out_file}' deleted successfully.")

logger.info('MnRtn 020:opening pathogens_wiki_urls.txt file to hold the references found') 

f = open(out_file, 'w')
f.write(f'id\tpathogen_nm\turl\timage\ttaxonomy\tbinomial_nm\tsynonyms\tstatus\n')
row_cnt = len(rows)

#for row in rows:
for j in range (0, row_cnt, 1):
    i = j # allow setting to different value when debugging - e.g. to rerun the row
    binomial_nm = ''
    image_path = ''
    pathogen_nm2 = ''
    key = ''
    row = rows[i]
    status_msg = ''
    taxonomy = ''
    table = None
    taxonomy = ''
    url = ''
    val = ''
    alt_latin_nms = ''
    alt_common_nms = ''
    
    while True:
        try:
            pathogen_id    = row[0]
            pathogen_nm    = row[1]   
            latin_nm       = row[2]
            alt_latin_nms  = row[3]
            alt_common_nms = row[4]
            
            #strip any whitespace like \r
            if pathogen_nm    != None: pathogen_nm    = pathogen_nm   .strip('\r\n\xa0 ')   
            if latin_nm       != None: latin_nm       = latin_nm      .strip('\r\n\xa0 ')
            if alt_latin_nms  != None: alt_latin_nms  = alt_latin_nms .strip('\r\n\xa0 ')
            if alt_common_nms != None: alt_common_nms = alt_common_nms.strip('\r\n\xa0 ')
            crop_name      = ''     # this is the part of the pathogen name if a : is used e.g. 'Botrytis leaf spot: Legumes'
            
            #Remove :.* if it exists  from pathogen name e.g. 'Botrytis leaf spot: Legumes' -> 'Botrytis leaf spot'
            if pathogen_nm.find(':') > 0:
                ary = pathogen_nm.split(':')
                pathogen_nm = ary[0].strip('\r\n ')
                crop_name   = ary[1].strip('\r\n ')

            logger.info('\n\n-----------------------------------------------------------------------------')
            logger.info(f'MnRtn 030: loop [{i}] pid: {pathogen_id} pnm: {pathogen_nm} latin_nm: {latin_nm}')
            logger.info(f'MnRtn 033: alt_latin_nms : {alt_latin_nms}')
            logger.info(f'MnRtn 036: alt_common_nms: {alt_common_nms}')
            logger.info('-----------------------------------------------------------------------------\n\n')
            logger.debug(f'MnRtn 040: calling getPage')
            page, status_msg = getPage.getPage( latin_nm, pathogen_nm, status_msg)
            msg = '' if page != None else ' not'
            logger.info(f'MnRtn 050: ret frm getPage page{msg} found')
              
            # if not try alt_latin_nms and alt_common_nms
            if page == None: # Cant get page
                while True:   
                    # try alt_latin_nms
                    logger.info(f'MnRtn 050: trying alt_latin_nms')
                    
                    if alt_latin_nms != None:
                        for latin_nm in alt_latin_nms.split(','):
                            page, status_msg = getPage.getPage2( latin_nm, status_msg)
                            
                            if page != None:
                                logger.info(f'MnRtn 055: found alt latin nm: {latin_nm}')
                                break
                            
                    if page != None:
                        break
                    
                    # try alt_common_nms
                    logger.info(f'MnRtn 060: trying alt_common_nms')
                    
                    if alt_common_nms != None:
                        for common_nm in alt_common_nms.split(','):
                            page, status_msg = getPage.getPage2( common_nm, status_msg)
                                              
                            if page != None:
                                logger.info(f'MnRtn 065: found alt common nm: {common_nm}')
                                break
                        
                    if page != None:
                        break
                    break
                
            if page == None:
                break
            #------------------------------------------------
            # ASSERTION 1: if here then we have the wiki page
            #------------------------------------------------
            logger.debug('MnRtn 070: ASSERTION 1: we have the wiki page, making some soup')
            soup = BeautifulSoup(page.html(), features='html5lib')
            url = page.url
            images=page.images

            if len(images) > 0:
                image_path = images[0] 
            else :
                logger.info(f'MnRtn 080: image file not found') 
                image_path = None

            msg = '' if soup != None else ' not'
            logger.info(f'MnRtn 090: looking for the infobox biota table')
            table = soup.find('table', attrs = {'class':'infobox biota'})
            msg = '' if table != None else ' not'
            logger.info(f'MnRtn 100: table{msg} found')

            if(table != None):
                logger.info(f'MnRtn 100: table found, trying to get the binomial name')
                binomial_nm = getBinomialName.getBinomialName(table)
                msg = '' if binomial_nm != None else ' not'
                #print(f'MnRtn 090: binomial_nm{msg} found')
                #print(f'MnRtn 100: Calling getTaxonomyString()')
                taxonomy, status_msg = getTaxonomyString.getTaxonomyString(table)

                if taxonomy == '' and latin_nm != None:
                    status_msg = f"{status_msg} There is no taxonomy table in the wiki page for {latin_nm} - trying common nm: {pathogen_nm}"
                    logger.info(f'MnRtn 110: status_msg: {status_msg}')

                    # try the common name
                    page, status_msg = getPage.getPage(soup, latin_nm, pathogen_nm, status_msg)

                    if page == None: # Cant get page
                        status_msg = f'Cant get page for the common pathogen name:  {pathogen_nm}  {status_msg} '
                        logger.info(f'MnRtn 120: Cant get page for the common pathogen name {status_msg} - not trying any more')
                        break

                    url = page.url
                    taxonomy, status_msg = getTaxonomyString(table)

                    if taxonomy == '':
                        status_msg = f"{status_msg}. could not find the taxonomy table for either the latin name {latin_nm} or the common nm: {pathogen_nm}"
                        logger.info(f'MnRtn 130: status_msg: {status_msg}')                
                        break

                if taxonomy == '':
                    break
                
                #--------------------------------------------------
                # ASSERTION 2: if here then we have the tax string
                #--------------------------------------------------
                logger.info(f'MnRtn 140: ASSERTION 3: we have the taxonomy string')
            break
    
        except w.exceptions.PageError as error:
            status_msg =f'[{pathogen_id}]: caught page error ex: {error}'
            logger.exception(f'MnRtn 160: caught ex: status_msg: {status_msg}')
            break

        except Exception as error:
            status_msg =f'[{pathogen_id}]: caught ex: {type(error).__name__}: {error}'
            logger.exception(f'MnRtn 170: caught ex: status_msg: {status_msg}')

            try:
                status_msg = f'{status_msg}.\n[{pathogen_nm}] has no page in wikipedia trying latin name [{latin_nm}]'
                logger.info(f'MnRtn 180: status_msg: {status_msg}')
                srchResults = w.search(latin_nm)

                try:
                    if pathogen_nm in srchResults:
                        ndx = srchResults.index(pathogen_nm)
                        page= w.page(srchResults[ndx])
                        url = page.url
                    else:
                        # Try a trim
                        pathogen_nm2 = pathogen_nm.rstrip('s')

                        if pathogen_nm2 in srchResults:
                            ndx = srchResults.index(pathogen_nm2)
                            page= w.page(pathogen_nm2)
                            url = page.url
                        else:
                            status_msg = f'{status_msg}\nproblem wiki page not found for common nm [{pathogen_nm}] or latin name: [{latin_nm}]'
                            logger.warning(status_msg)

                except Exception as error:
                    status_msg = f'{status_msg}.\ncaught ex: {type(error).__name__} {error}'
                    logger.exception(status_msg)
                    page = w.page(latin_nm)
                    url = page.url
            except Exception as error:
                status_msg = f"[{pathogen_id}]: There is no reference in wikipedia for either [{pathogen_nm}] or [{latin_nm}] caught ex: {type(error).__name__} {error}"
                logger.exception(status_msg)
                break
            
        status_msg = 'OK'
        break #do while once loop

    #---------------------------------------------------------------------
    # ASSERTION 3: we are ready to output the data we found in wikipedia
    #---------------------------------------------------------------------

    # fixup null values
    if status_msg  == None: status_msg  = ''
    if binomial_nm == None: binomial_nm = ''
    synonyms = ''
    
    if table != None:
        synonyms, status_msg2 = getSynonyms.getSynonyms(table)
    
        if synonyms == '':
            status_msg = f'{status_msg} {status_msg2}'
        
    line = f"{pathogen_id}\t{pathogen_nm}\t{url}\t{image_path}\t{taxonomy}\t{binomial_nm}\t{synonyms}\t{status_msg}"
    logger.info(f"{line}")
    f.write(f"{line}\n")
    f.flush()

logger.info(f'Finished wiki pathogen scrape')
conn.close()
f.close()
