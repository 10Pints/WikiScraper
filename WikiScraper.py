import urllib.request as url
import urllib.error as urlError
import wikipedia as w
import csv
import os
from bs4 import BeautifulSoup# as bs
import re
import pyodbc as pyodbc
import pandas as pd

# Gets the wiki page for the srch_key
#
# Returns:
# if srch_key is None the returns (None, '')
# if found page returns (page, None)
# if error getting page then print the error and return (none, error)
#
# Preconditions: 
# PRE01: at least 1 one of(latin_nm, pathogen_nm) must be specified
def getPage( latin_nm, pathogen_nm, status_msg):
    print(f'getPage: 000: starting latin_nm: {latin_nm}, pathogen_nm: {pathogen_nm}')
    title = None
    srchResults = None
    page = None
    msg = ''

    while True:
        # PRE01: latin_nm or pathogen_nm must be specified
        if ((latin_nm == None) and (pathogen_nm == None)):
            print('getPage: 010: ERROR latin_nm and pathogen_nm not specifed')
            raise Exception('getPage() Precondition violation PRE01: at least 1 one of(latin_nm, pathogen_nm) must be specified')

        #latin name first if defined
        srch_key = latin_nm if latin_nm !=None else pathogen_nm
        key_nm = 'latin_nm 'if latin_nm !=None else 'pathogen_nm'
        print(f'getPage: 020: search key: {key_nm}: {srch_key} calling w.search(key)')

        try:
            srchResults = w.search(srch_key)
            msg = '' if srchResults != None else ' not'        
            print(f'getPage: 030: ret frm w.search{msg} ok')

            if srchResults == None:
                raise(f'w.search({srch_key}) returned null')

            # ASSERTION: we have the page
            print(f'getPage: 040: ASSERTION: we have the page')

            for x in srchResults:
                if x == srch_key:
                    title = x
                    break

            print(f'getPage: 050: title: {title}')

            # # chk we got an exact title match
            if title != None:
                # got an exact match so use it
                print(f'getPage: 060: got an exact title match for {srch_key}')
                break
            else:
                print(f'getPage: 070: Did not find a page whose title exactly matches {srch_key}')

                if((latin_nm != None) and (pathogen_nm != None)):
                    # We have both latin_nm and pathogen_nm
                    # try the pathogen_nm
                    print(f'getPage: 080: We have both latin_nm and pathogen_nm so trying to find page whose title exactly matches the common name: {pathogen_nm}')
                    #title = srchResults.get(pathogen_nm, None)
                    for x in srchResults:
                        if x == pathogen_nm:
                            title = x
                            break

                    if title != None:
                        # got an exact match on the pathogen_nm so use that
                        print(f'getPage: 090: got an exact title match for the common name: {pathogen_nm}')
                        break
                    else:
                        # neither gave an exact match so take the best
                        print(f'getPage: 100: Niether gave an exact match, so take the first title in the following list:')
                        print(f'{srchResults}')
                        title = srchResults[0]
                    break

        except w.exceptions.PageError as error:
            if status_msg != '': 
                status_msg = status_msg + '. \n'

            status_msg =f'{status_msg} Caught page error ex: {error}'
            print(f'getPage: 500: ERROR: {status_msg}')

            break

        except Exception as error:
            if status_msg != '': 
                status_msg = status_msg + '.\n '

            status_msg =f'{status_msg} caught ex: {type(error).__name__}: {error}'
            print(f'getPage: 520:  ERROR: {status_msg}') 
            page = None
            break

        print('getPage: 110: oops')
        break 

    try:
        page = w.page(title, auto_suggest=False) if title != None else None # may throw  
        status_msg = status_msg + '' if page != None else f'{status_msg} page not found'
        print(f'getPage: 999: leaving {status_msg}')

    except w.exceptions.DisambiguationError as error: 
        if status_msg != '': 
            status_msg = status_msg + '.\n'

        status_msg =f'{status_msg} caught ex: {type(error).__name__}:\n{error.options}'
        print(f'getPage: 550:  ERROR: {status_msg}')

        # void the page
        page = None
        
    return page, status_msg

# This fn can find the infobox biota table on the wiki page
# it returns the taxonomy string and a null error msg
# # or a null taxonomy string and an error msg if table not found
#
# Postconditions: returns either:
#  (taxonomy was found AND non null tax string AND a null msg) OR  
#  (taxonomy was not found AND null tax string AND a non null msg)
# i.e. one or other must be specified, but not both
def getTaxonomyString( table):
    try:
        print('GtTaxstr 000: starting')
        taxonomy = ''
        #soup = BeautifulSoup(page.html(), 'html5lib')
        #table = soup.find('table', attrs = {'class':'infobox biota'})

        if table == None:
            print('GtTaxstr 010: leaving early: table is null')
            taxonomy = ''
            return taxonomy, 'Could not find the taxonomy table'
        
        #
        # Assertion 2: we have the tax table
        #
        print('GtTaxstr 020: ASSERTION: we have the taxonomy table')
        tds = table.findAll('td')
        len_tr = len(tds)

        for n in range (1, len_tr-1, 1):
            key = tds[n].text.strip().strip(':')

            if any(key in x for x in wanted_keys):
                val = tds[n+1].text.strip()
                taxonomy = f'{taxonomy},{key}:{val}'

        taxonomy = taxonomy.lstrip(',')

    except Exception as e:
        status_msg =f'{status_msg} caught ex: {type(error).__name__}: {error}'
        print(f'ERROR: GtTaxstr 030:{status_msg}') 
        raise # rethrow the exception

    print(f'GtTaxstr 999: leaving, tax str: {taxonomy}')
    return taxonomy, None


# desc: This rtn gets the binomial name
# method:
# in the info biotica table
# look for a span with class = 'binomial'
# get it's 1 <i> child text
def getBinomialName(table):
    try:
        print('GtBinm 000: starting')
        # look for a span with class = 'binomial'
        span = table.find('span', attrs={'class':'binomial'})

        if span == None:
            print('GtBinm 020: leaving eraly Table in nonw')
            return None

        # get it's 1 <i> child text
        i_tag = span.find('i')
        binomial_name = i_tag.text

    except Exception as e:
        status_msg =f'caught ex: {type(error).__name__}: {error}'
        print(f'GtBinm 500: {status_msg} rethrowing ex') 
        raise # rethrow the exception

    print(f'GtTaxstr 999: leaving, tax str: {taxonomy}')
    return binomial_name
    

print('MnRtn 000: starting, connecting to sql server db')

conn = pyodbc.connect( 'DRIVER={SQL Server};'
                       'SERVER=DevI9;'
                       'DATABASE=farming_dev;Trusted_Connection=yes;'
                    )

cursor = conn.cursor()

#with named parameters: cursor.execute('EXEC usp_get_user_data @name = ?, @username = ?', 'tim', 'flipperpa')
conn.autocommit = True
print('MnRtn 010: exec sql select pathogen data cmd ')
cursor.execute('Select pathogen_id, pathogen_nm,latin_nm FROM pathogen')
rows = cursor.fetchall()

i = 0
image_path = ''
key = ''
latin_nm = ''
# = 0
pathogen_id = 0
pathogen_nm = ''
pathogen_nm2 = ''
url = ''
val = ''
taxonomy = ''
status_msg = ''
wanted_keys = ['Domain','Kingdom','Clade','Phylum','Division','Class','Order','Infraorder','Family','','Subfamily','Genus','Section']

# open a file to hold the references found
print('MnRtn 020:opening pathogens_wiki_urls.txt file to hold the references found') 
f = open('pathogens_wiki_urls.txt', 'w')
f.write(f'id\pathogen_nm\turl\timage\ttaxonomy\tbinomial_nm\tstatus\n')
row_cnt = len(rows)

#for row in rows:
for i in range (0, row_cnt, 1):
    row = rows[i]
    url     =''
    status_msg = ''
    taxonomy = ''
    image_path = ''
    binomial_nm = ''
    
    while True:
        try:
            pathogen_id=row[0]
            pathogen_nm = row[1]   
            latin_nm = row[2]

            print('\n\n\n-----------------------------------------------------------------------------')
            print(f'MnRtn 030: loop [{i}] pid: {pathogen_id} pnm: {pathogen_nm}  latin: {latin_nm}')
            print('-----------------------------------------------------------------------------\n\n')
            print(f'MnRtn 040: pathogen_nm: [{pathogen_nm}] latin_nm:[{latin_nm}] calling getPage')
            page, status_msg = getPage( latin_nm, pathogen_nm, status_msg)
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
                binomial_nm = getBinomialName(table)
                msg = '' if binomial_nm != None else ' not'
                print(f'MnRtn 090: binomial_nm{msg} found')
                print(f'MnRtn 100: Calling getTaxonomyString()')
                taxonomy, status_msg = getTaxonomyString(table)

                if taxonomy == '' and latin_nm != None:
                    status_msg = f"{status_msg} There is no taxonomy table in the wiki page for {latin_nm} - trying common nm: {pathogen_nm}"
                    print(f'MnRtn 110: status_msg: {status_msg}')

                    # try the common name
                    page, status_msg = getPage(soup, latin_nm, pathogen_nm, status_msg)

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

    line = f"{pathogen_id}\t{pathogen_nm}\t{url}\t{image_path}\t{taxonomy}\t{binomial_nm}\t{status_msg}"
    print(f'[{pathogen_id}]: {line}')
    line = f"{line}\n"
    f.write(line)
    f.flush()

conn.close()
f.close()


