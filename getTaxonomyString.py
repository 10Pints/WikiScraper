#
# getTaxonomyString.py
#
# This fn can find the infobox biota table on the wiki page
# it returns the taxonomy string and a null error msg
# # or a null taxonomy string and an error msg if table not found
#
# Postconditions: returns either:
#  (taxonomy was found AND non null tax string AND a null msg) OR  
#  (taxonomy was not found AND null tax string AND a non null msg)
# i.e. one or other must be specified, but not both

wanted_keys = ['Domain','Kingdom','Clade','Phylum','Division','Class','Order','Infraorder','Family','','Subfamily','Genus','Section']

def getTaxonomyString( table):
    try:
        #wanted_keys = ['Domain','Kingdom','Clade','Phylum','Division','Class','Order','Infraorder','Family','','Subfamily','Genus','Section']

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

'''
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
'''
