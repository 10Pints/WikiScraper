import urllib.request as url
import urllib.error as urlError
import wikipedia as w
from bs4 import BeautifulSoup# as bs
import pandas as pd
import DbConnect
import getTaxonomyString
import getSynonyms
import getPage
import getTaxonomyString
import getBinomialName

#************ main code ************
print('MnRtn 000: starting, connecting to sql server db')
conn = DbConnect.DbConnect()
rows = conn.cursor()
i = 0

# open a file to hold the references found
print('MnRtn 020:opening pathogens_wiki_urls.txt file to hold the references found') 
f = open('pathogens_wiki_urls.txt', 'w')
f.write(f'id\tpathogen_nm\turl\timage\ttaxonomy\tbinomial_nm\tsynonyms\tstatus\n')
row_cnt = len(rows)

#for row in rows:
for i in range (0, row_cnt, 1):
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
    
    while True:
        try:
            pathogen_id=row[0]
            pathogen_nm = row[1]   
            latin_nm = row[2]

            print('\n\n\n-----------------------------------------------------------------------------')
            print(f'MnRtn 030: loop [{i}] pid: {pathogen_id} pnm: {pathogen_nm}  latin: {latin_nm}')
            print('-----------------------------------------------------------------------------\n\n')
            print(f'MnRtn 040: pathogen_nm: [{pathogen_nm}] latin_nm:[{latin_nm}] calling getPage')
            page, status_msg = getPage.getPage( latin_nm, pathogen_nm, status_msg)
            msg = '' if page != None else ' not'
            print(f'MnRtn 050:ret frm getPage page{msg} found')
                 
            if page == None: # Cant get page
                break
       
            #------------------------------------------------
            # ASSERTION 1: if here then we have the wiki page
            #------------------------------------------------
            print('MnRtn 060: ASSERTION 1: we have the wiki page, making some soup')
            soup = BeautifulSoup(page.html(), features='html5lib')
            url = page.url
            images=page.images

            if len(images) > 0:
                image_path = images[0] 
            else :
                print(f'MnRtn 100: image file not found') 
                image_path = None

            msg = '' if soup != None else ' not'
            print(f'MnRtn 070: looking for the infobox biota table')
            table = soup.find('table', attrs = {'class':'infobox biota'})
            msg = '' if table != None else ' not'
            print(f'MnRtn 080: table{msg} found')

            if(table != None):
                binomial_nm = getBinomialName.getBinomialName(table)
                msg = '' if binomial_nm != None else ' not'
                print(f'MnRtn 090: binomial_nm{msg} found')
                print(f'MnRtn 100: Calling getTaxonomyString()')
                taxonomy, status_msg = getTaxonomyString.getTaxonomyString(table)

                if taxonomy == '' and latin_nm != None:
                    status_msg = f"{status_msg} There is no taxonomy table in the wiki page for {latin_nm} - trying common nm: {pathogen_nm}"
                    print(f'MnRtn 110: status_msg: {status_msg}')

                    # try the common name
                    page, status_msg = getPage.getPage(soup, latin_nm, pathogen_nm, status_msg)

                    if page == None: # Cant get page
                        status_msg = f'Cant get page for the common pathogen name:  {pathogen_nm}  {status_msg} '
                        print(f'MnRtn 120: Cant get page for the common pathogen name {status_msg} - not trying any more')
                        break

                    url = page.url
                    taxonomy, status_msg = getTaxonomyString(table)

                    if taxonomy == '':
                        status_msg = f"{status_msg}. There is no taxonomy table in the wiki page for either the latin name {latin_nm} or the common nm: {pathogen_nm}"
                        print(f'MnRtn 130: status_msg: {status_msg}')                
                        break

                if taxonomy == '':
                    break
                
                #--------------------------------------------------
                # ASSERTION 2: if here then we have the tax string
                #--------------------------------------------------
                print(f'MnRtn 140: ASSERTION 3: we have the taxonomy string')
                print(f'MnRtn 150: taxonomy: {taxonomy}')
            break
    
        except w.exceptions.PageError as error:
            status_msg =f'[{pathogen_id}]: caught page error ex: {error}'
            print(f'MnRtn 160: caught ex: status_msg: {status_msg}')
            break

        except Exception as error:
            status_msg =f'[{pathogen_id}]: caught ex: {type(error).__name__}: {error}'
            print(f'MnRtn 170: caught ex: status_msg: {status_msg}')

            try:
                status_msg = f'{status_msg}.\n[{pathogen_nm}] has no page in wikipedia trying latin name [{latin_nm}]'
                print(f'MnRtn 180: status_msg: {status_msg}')
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
                            print(status_msg)

                except Exception as error:
                    status_msg = f'{status_msg}.\ncaught ex: {type(error).__name__} {error}'
                    print(status_msg)
                    page = w.page(latin_nm)
                    url = page.url
            except Exception as error:
                status_msg = f"[{pathogen_id}]: There is no reference in wikipedia for either [{pathogen_nm}] or [{latin_nm}] caught ex: {type(error).__name__} {error}"
                print(status_msg)
                break
            
        status_msg = 'OK'
        break #do while once loop

    #---------------------------------------------------------------------
    # ASSERTION 3: we are ready to output the data we found in wikipedia
    #---------------------------------------------------------------------

    # fixup null values
    if status_msg  == None: status_msg  = ''
    if binomial_nm == None: binomial_nm = ''
    synonyms, status_msg2 = getSynonyms.getSynonyms(table)
    synonyms, status_msg2 = getSynonyms.getSynonyms(table)
    
    if synonyms == None:
        synonyms = ''
        status_msg = f'{status_msg} {status_msg2}'
        
    line = f"{pathogen_id}\t{pathogen_nm}\t{url}\t{image_path}\t{taxonomy}\t{binomial_nm}\t{synonyms}\t{status_msg}"
    print(f'[{pathogen_id}]: {line}')
    line = f"{line}\n"
    f.write(line)
    f.flush()

conn.close()
f.close()


