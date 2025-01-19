# GetPage.py
import wikipedia as w

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
