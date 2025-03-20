import logging.config
logger = logging.getLogger("my_app")

# desc: This rtn gets the binomial name
# method:
# in the info biotica table
# look for a span with class = 'binomial'
# get it's 1 <i> child text
def getBinomialName(table):
    try:
        logger.debug('GtBiNm 000: starting')
        # look for a span with class = 'binomial'
        span = table.find('span', attrs={'class':'binomial'})

        if span == None:
            logger.warning('GtBinm 020: cant find a <span> called "binomial"')
        
            a_tag = table.find('a', text='Trionomial name')
            if a_tag == None : return None
            
            # ASSERTION we have the 'Trionomial name' marker
            # get the next tr, i tag text -> should be the binomial 
            tr = a_tag.find_parent('tr')
            tr = tr.find_next_sibling('tr')
            # or just get the next tr text - it should be the trinoial
            binomial_name = tr.txt
            logger.info(f'GtBinm 998: binomial_name: {binomial_name}')
            return binomial_name

        # ASSERTION we have the span class='binomial name' 
        # get it's 1 <i> child text
        i_tag = span.find('i')
        binomial_name = i_tag.text

    except Exception as error:
        status_msg =f'caught ex: {type(error).__name__}: {error}'
        logger.exception(f'GtBinm 500: {status_msg} rethrowing ex') 
        raise # rethrow the exception
    
    logger.info(f'GtBiNm 999: leaving, binomial_name: {binomial_name}')
    return binomial_name
