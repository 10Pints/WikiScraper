# desc: This rtn gets the binomial name
# method:
# in the info biotica table
# look for a span with class = 'binomial'
# get it's 1 <i> child text
def getBinomialName(table):
    try:
        #print('GtBinm 000: starting')
        # look for a span with class = 'binomial'
        span = table.find('span', attrs={'class':'binomial'})

        if span == None:
            print('GtBinm 020: leaving early undefined Table')
            return None

        # get it's 1 <i> child text
        i_tag = span.find('i')
        binomial_name = i_tag.text

    except Exception as error:
        status_msg =f'caught ex: {type(error).__name__}: {error}'
        print(f'GtBinm 500: {status_msg} rethrowing ex') 
        raise # rethrow the exception

    #print(f'GtTaxstr 999: leaving, binomial_name: {binomial_name}')
    return binomial_name
