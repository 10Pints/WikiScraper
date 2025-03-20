# GetPage.py
import wikipedia as w
import logging.config

logger = logging.getLogger("my_app")
# Tries to get the wiki page for the srch_key
#
# Returns:
# if name is not specified then throws exception 
#   'getPage2() Precondition violation PRE01: name must be specified'
#
# if found page returns (page, None)
# if error getting page then print the error and return (None, error msg)
#
# Preconditions: 
# PRE01: name must be specified or exception raised: 'getPage2() Precondition violation PRE01: name must be specified'
def getPage2( name, status_msg):
    logger.debug(f'getPage2 000: starting name: {name}')
    title = None
    srchResults = None
    page = None
    msg = ''

    while True:
        # PRE01: latin_nm or pathogen_nm must be specified
        if ((name == None) or (name == '')):
            logger.error('getPage2 010: name must specifed')
            raise Exception('getPage2() Precondition violation PRE01: name must be specified')

        try:
            srchResults = w.search(name)
            msg = '' if srchResults != None else ' not'        
            #print(f'getPage2: 030: ret frm w.search{msg} ok')

            if srchResults == None:
                msg = f'w.search({name}) returned null'
                logger.error(f'getPage2 020: w.search({name}) returned null')
                raise( msg)

            # ASSERTION: we have the page
            #print(f'getPage: 040: ASSERTION: we have the page')

            for x in srchResults:
                if x == name:
                    title = x
                    break

            #print(f'getPage: 050: title: {title}')

            # # chk we got an exact title match
            if title != None:
                # got an exact match so use it
                logger.info(f'getPage2 050: got an exact title match for {name}')
                break
            else:
                logger.info(f'getPage2 060: Did not find a page whose title exactly matches {name}')
                
                # dont ttry to depluralise grass or virus
                if name[-1] == 's' and name[-2:] != 'ss' and (len(name)<5 or name[-5:] != 'virus'):
                    logger.info(f'getPage2 70: looking for de-pluralised match')
                    de_pluralised_nm = name.rstrip('s')
                
                    logger.info(f'getPage2 80 looking for a match for [{de_pluralised_nm}]')
                    
                    if de_pluralised_nm in srchResults:
                        title = de_pluralised_nm
                        logger.info(f'getPage2 090: going with de-pluralised name [{de_pluralised_nm}]')
                    else:
                        logger.info(f'getPage2 100: no exact match for the de-pluralised name[{de_pluralised_nm}]')
                    break 
                 
                status_msg = 'getPage2 110: did not find exact or de-pluralised match'
                logger.info(status_msg)   
                break      

        except w.exceptions.PageError as error:
            if status_msg != '': 
                status_msg = status_msg + '. \n'

            status_msg =f'{status_msg} Caught page error ex: {error}'
            logger.exception(f'getPage2: 500: ERROR: {status_msg}')
            break

        except Exception as error:
            if status_msg != '': 
                status_msg = status_msg + '.\n '

            status_msg =f'{status_msg} caught ex: {type(error).__name__}: {error}'
            logger.exception(f'getPage2: 520:  ERROR: {status_msg}') 
            page = None
            break

        break 
        
    logger.info(f'getPage2: 999: leaving {status_msg}')
    return page, status_msg

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
    logger.debug(f'getPage 000: starting latin_nm: {latin_nm}, pathogen_nm: {pathogen_nm}')
    title = None
    srchResults = None
    page = None
    msg = ''

    while True:
        # PRE01: latin_nm or pathogen_nm must be specified
        if ((latin_nm == None) and (pathogen_nm == None)):
            logger.exception('getPage 010: ERROR latin_nm and pathogen_nm not specifed')
            raise Exception('getPage() Precondition violation PRE01: at least 1 one of(latin_nm, pathogen_nm) must be specified')

        #latin name first if defined
        key_nm = 'latin_nm 'if latin_nm !=None else 'pathogen_nm'
        srch_key = latin_nm if latin_nm !=None else pathogen_nm
        logger.debug(f'getPage 020: search key: {key_nm}: {srch_key} calling w.search(key)')

        try:
            srchResults = w.search(srch_key)
            msg = '' if srchResults != None else ' not'        
            logger.debug(f'getPage 030: ret frm w.search{msg} ok')

            if srchResults == None:
                logger.exception('w.search({srch_key}) returned null')
                raise(f'w.search(getPage 040: {srch_key}) returned null')

            # ASSERTION: we have the page
            #print(f'getPage: 040: ASSERTION: we have the page')

            for x in srchResults:
                if x == srch_key:
                    title = x
                    break

            #print(f'getPage: 050: title: {title}')

            # # chk we got an exact title match
            if title != None:
                # got an exact match so use it
                logger.info(f'getPage: 060: got an exact title match for {srch_key}')
                break
            else:
                logger.info(f'getPage: 070: Did not find a page whose title exactly matches {srch_key}')

                if((latin_nm != None) and (pathogen_nm != None)):
                    # We have both latin_nm and pathogen_nm
                    # try the pathogen_nm
                    logger.debug(f'getPage: 080: We have both latin_nm and pathogen_nm so trying to find page whose title exactly matches the common name: {pathogen_nm}')
                    #title = srchResults.get(pathogen_nm, None)
                    for x in srchResults:
                        if x == pathogen_nm:
                            title = x
                            break

                    if title != None:
                        # got an exact match on the pathogen_nm so use that
                        logger.info(f'getPage: 090: got an exact title match for the common name: {pathogen_nm}')
                        break
                    else:
                        # neither gave an exact match so take the best
                        logger.info(f'getPage: 100: Neither gave an exact match, so take the first title in the following list (see log):')
                        logger.debug(f'{srchResults}')
                        
                        if len(srchResults) > 0:
                            title = srchResults[0]
                    break
                
                logger.debug(f'getPage: 110: did not find exact math and only {key_nm} specified')
                
                #look for plurals but not names ending 'virus'
                if srch_key[-1] == 's' and (len(srch_key)<5 or srch_key[-5:] != 'virus' or srch_key[-5:] != 'ss'):
                    logger.debug(f'getPage: 120: looking for de-pluralised match')
                    de_pluralised_nm = srch_key.rstrip('s')
                
                    logger.debug(f'getPage: 130: looking for a match for [{de_pluralised_nm}]')
                    
                    if de_pluralised_nm in srchResults:
                        title = de_pluralised_nm
                        logger.debug(f'getPage: 140: going with de-pluralised name [{de_pluralised_nm}]')
                    else:
                        logger.debug(f'getPage: 150: no exact match for the de-pluralised name[{de_pluralised_nm}]')
                    break 
                 
                print(f'logger.debug: 170: did not find exact or de-pluralised match and only {key_nm} specified')   
                break      

        except w.exceptions.PageError as error:
            if status_msg != '': 
                status_msg = status_msg + '. \n'

            status_msg =f'{status_msg} Caught page error ex: {error}'
            logger.exception(f'getPage: 500: ERROR: {status_msg}')
            break

        except Exception as error:
            if status_msg != '': 
                status_msg = status_msg + '.\n '

            status_msg =f'{status_msg} caught ex: {type(error).__name__}: {error}'
            logger.exception(f'getPage: 520:  ERROR: {status_msg}') 
            page = None
            break

        logger.error('getPage: 200: oops')
        break 

    if title == None:
        logger.info(f'getPage 200: title not found')
    else:
        try:
            # try to get the wiki page
            logger.debug(f'getPage: 210: trying to get the page titled: {title}')
            page = w.page(title, auto_suggest=False) if title != None else None # may throw  
            status_msg = status_msg + '' if page != None else f'{status_msg} page not found'

        except w.exceptions.DisambiguationError as error: 
            if status_msg != '': 
                status_msg = status_msg + '. '

            status_msg =f'{status_msg} caught DisambiguationError exception: {error.options}'
            logger.exception(f'getPage: 550:  ERROR: {status_msg}')

            # void the page
            page = None
        
    logger.debug(f'getPage: 999: leaving {status_msg}')
    return page, status_msg
