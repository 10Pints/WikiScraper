import urllib.request as url
import urllib.error as urlError
import wikipedia as w
import csv
import os
from bs4 import BeautifulSoup# as bs
import re
# pip pyodbc
import pyodbc as pyodbc
import pandas as pd
#import wikipediaapi as api

conn = pyodbc.connect( 'DRIVER={SQL Server};'
                       'SERVER=DevI9;'
                       'DATABASE=farming_dev;Trusted_Connection=yes;'
                    )
cursor = conn.cursor()

#with named parameters: cursor.execute('EXEC usp_get_user_data @name = ?, @username = ?', 'tim', 'flipperpa')
cmd_prod_executesp = """EXEC dbo.sp_list_AppLog"""
conn.autocommit = True

#row = cursor.execute(cmd_prod_executesp)
cursor.execute('Select pathogen_nm,latin_nm FROM pathogen')
rows = cursor.fetchall()

#Create a map of pathogen_nm to url
d = {}
pathogen_nm = ""
pathogen_nm2 = ""
latin_nm = ""
url = ""
key = ''
val = ''
i = 0
# open a file to hold the references found
f = open("pathogens_wiki_urls.csv", "w")
f.write(f"pathogen_nm,url\timage")

for row in rows:
    i=i+1
    url=''
    quote = {}
    domain = ''

    try:
        pathogen_nm = row[0] #pathogen_nm = "Alternaria"    
        latin_nm = row[1]
        srch_key = latin_nm if latin_nm is not None else pathogen_nm
        srchResults = w.search(srch_key)
        srch_res = srchResults[0]
        page = w.page(srch_res, auto_suggest=False) # may throw 
        url = page.url
        content=page.content
        summary=page.summary
        sections=page.sections
        images=page.images
        soup = BeautifulSoup(page.html(), 'html5lib')
        pretty = soup.prettify()
        #
        table = soup.find('table', attrs = {'class':'infobox biota'}) 
        trs=table.findAll('tr')

        for tr in trs:
            contents = tr.contents

            if len(contents)>3:
                key = contents[1].contents
                kingdom = contents[3].text.strip()
                domain = tr.find(string=re.compile('Domain')).text.strip()

        image = page.images[0]

    except w.exceptions.PageError as error:
        print(f'caught page error ex: {error}')

    except Exception as error:
        print(f'caught ex: {type(error).__name__}: {error}')
        try:
            print(f"[{i}]: [{pathogen_nm}] has no page in wikipedia trying latin name [{latin_nm}]")
            srchResults = w.search(pathogen_nm)

            try:
                if pathogen_nm in srchResults:
                    ndx = srchResults.index(pathogen_nm)
                    page = w.page(srchResults[ndx])
                    url = page.url
                else:
                    # Try a trim
                    pathogen_nm2 = pathogen_nm.rstrip('s')

                    if pathogen_nm2 in srchResults:
                        ndx = srchResults.index(pathogen_nm2)
                        page = w.page(pathogen_nm2)
                        url = page.url
                    else:
                        print(f"[{i}]: problem [{pathogen_nm}] or [{latin_nm}]")
            except Exception as error:
                print(f'caught ex: {type(error).__name__}')
                page = w.page(latin_nm)
                #print(f"[{i}]: {latin_nm}\t{page.url}\t{image}")
                url = page.url
        except:
            print(f"[{i}]: There is no reference in wikipedia for either [{pathogen_nm}] or [{latin_nm}]")
            continue

    #srchResults = w.search(latin_nm)
    print(f"[{i}]: {pathogen_nm}\t{url}\t{image}")
    d[pathogen_nm] = url
    f.write(f"{pathogen_nm},{url}\t{image}")
    f.flush()

conn.close()
f.close()


