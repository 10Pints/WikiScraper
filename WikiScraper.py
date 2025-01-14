import urllib.request as url
import urllib.error as urlError
import wikipedia as w
import csv
import os
from bs4 import BeautifulSoup# as bs
import re
import pyodbc as pyodbc
import pandas as pd

conn = pyodbc.connect( 'DRIVER={SQL Server};'
                       'SERVER=DevI9;'
                       'DATABASE=farming_dev;Trusted_Connection=yes;'
                    )

cursor = conn.cursor()

#with named parameters: cursor.execute('EXEC usp_get_user_data @name = ?, @username = ?', 'tim', 'flipperpa')
conn.autocommit = True
cursor.execute('Select pathogen_id, pathogen_nm,latin_nm FROM pathogen')
rows = cursor.fetchall()

i = 0
image_path = ''
key = ''
latin_nm = ''
ndx = 0
pathogen_nm = ''
pathogen_nm2 = ''
url = ''
val = ''
taxonomy = ''
status_msg = ''
wanted_keys = ['Domain','Kingdom','Clade','Phylum','Division','Class','Order','Infraorder','Family','','Subfamily','Genus','Section']

# open a file to hold the references found
f = open('pathogens_wiki_urls.txt', 'w')
f.write(f'id\pathogen_nm\turl\timage\ttaxonomy\tstatus\n')

for row in rows:
    i=row[0]
    quote   = {}
    url     =''
    status_msg = ''
    taxonomy = ''
    image_path = ''
    
    while True:
        try:
            pathogen_nm = row[1] #pathogen_nm = "Alternaria"    
            latin_nm = row[2]
            srch_key = latin_nm if latin_nm is not None else pathogen_nm
            srchResults = w.search(srch_key)
            srch_res = srchResults[0]

            # This needs restoring to the old way of doing it and handling the duplicate exception
            page = w.page(srch_res, auto_suggest=False) # may throw 
            url = page.url
            content=page.content
            summary=page.summary
            sections=page.sections
            images=page.images

            if len(images) > 0:
                image_path = images[0] 
            else :
                image_path = None

            soup = BeautifulSoup(page.html(), 'html5lib')
            table = soup.find('table', attrs = {'class':'infobox biota'}) 

            if table == None and latin_nm != None:
                status_msg = f"[{i}]: There is no taxonomy table in the wiki page for {latin_nm} - trying common nm: {pathogen_nm}"
                print(status_msg)
                srchResults = w.search(pathogen_nm)
                srch_res = srchResults[0]

                # try the common name
                page = w.page(srch_res, auto_suggest=False) # may throw 
                url = page.url
                soup = BeautifulSoup(page.html(), 'html5lib')
                table = soup.find('table', attrs = {'class':'infobox biota'}) 

                if table == None:
                    status_msg = f"[{i}]: There is no taxonomy table in the wiki page for either the latin name {latin_nm} or the common nm: {pathogen_nm}"
                    print(status_msg)                
                    break

            #------------------------------------------------
            # ASSERTION: if here then we have the tax table
            #------------------------------------------------
            tds=table.findAll('td')
            ndx = 0
            len_tr = len(tds)
    
            for n in range (1, len_tr, 2):
                key = tds[n].text.strip().strip(':')

                if any(key in x for x in wanted_keys):
                    val = tds[n+1].text.strip()
                    taxonomy = f'{taxonomy},{key}:{val}'

            print(f'taxonomy: {taxonomy}')
            break
    
        except w.exceptions.PageError as error:
            status_msg =f'[{i}]: caught page error ex: {error}'
            print(status_msg)
            break

        except Exception as error:
            status_msg =f'[{i}]: caught ex: {type(error).__name__}: {error} ndx: {ndx}'
            print(status_msg)

            try:
                status_msg = f'{status_msg}.\n[{pathogen_nm}] has no page in wikipedia trying latin name [{latin_nm}]'
                print(status_msg)
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
                    status_msg = f'{status_msg}.\ncaught ex: {type(error).__name__}'
                    print(status_msg)
                    page = w.page(latin_nm)
                    url = page.url
            except:
                status_msg = f"[{i}]: There is no reference in wikipedia for either [{pathogen_nm}] or [{latin_nm}]"
                print(status_msg)
                break
            
        taxonomy = taxonomy.strip(',')
        status_msg = 'OK'
        break #do while once loop

    line = f"{i}\t{pathogen_nm}\t{url}\t{image_path}\t{taxonomy}\t{status_msg}"
    print(f'[{i}]: {line}')
    line = f"{line}\n"
    f.write(line)
    f.flush()

conn.close()
f.close()


