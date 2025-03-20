# getSynonyms.py
# Description: returns the list of synonyms in the table
# if they exist
# 
# Method:  
# look for a <tr> with a <th> with an <a> with the title: 'Synonym (taxonomy)'
#  <a href="/wiki/Synonym_(taxonomy)" title="Synonym (taxonomy)">Synonyms</a>
# get the next tr
# get the list of i-tags
# get the texts from all the itags
# 
# OR
# 
# look for a <ul> with <ul class="taxonlist">
# get its list of <i> tags
# create a list of the texts from each list item 
# return it
# 
# Example HTML:  
# <ul>
#   <li>
#     <i>Coccinella 28-punctata</i>
#     <small>Fabricius, 1775</small>
#   </li>
#   <li>
#     <i>Coccinella sparsa</i>
#     <small>Herbst, 1786</small>
#   </li>
#   <li>
#     <i>Epilachna gradaria</i>
#     <small>Mulsant, 1850</small>
#   </li>
#   <li>
#     <i>Epilachna territa</i>
#     <small>Mulsant, 1850#</small>
#   </li>
#   <li>
#     <i>Epilachna vigintioctopunctata</i>
#     <small>Auctt.</small>
#   </li>
#   <li>
#     <i>Epilachna sparsa</i>
#     <small>Auctt.</small>
#   </li>
# </ul>
import logging.config
logger = logging.getLogger("my_app")

def getSynonyms(table):
    synonyms = ''
    status = None
    logger.info('getSynonyms 000: starting, looking for the taxonlist')
    
    try:        
        if table == None:
            logger.warning('getSynonyms 010: table not supplied')
            #if synonyms == None: synonyms='<not found>'
            return '','getSynonyms 010: table not supplied'
        
        # look for an a tag title="Synonym (taxonomy)"
        a_tag = table.find('a', attrs={'title':'Synonym (taxonomy)'})
        
        if a_tag == None:
            msg = 'getSynonyms 020: Synonyms not found'
            logger.info(msg)
            #if synonyms == None: synonyms='<not found>'
            return '', msg
        
        #get its tr parent
        tr = a_tag.find_parent('tr')
        # get next tr
        tr = tr.find_next_sibling('tr')
        # get its li items
        li_items = tr.findAll('li')
        
        if len(li_items) == 0:
            li_items = tr.findAll('i')
    
        if li_items == None:
            msg = 'getSynonyms 030: synonyms li_items not found'
            logger.debug(msg)
            return '', msg
    
        for item in li_items:
            syns  = item.text.split()
            limit = len(syns)
            
            # just want the bi name, ignore the author and possible date
            if limit>2: limit=2
            
            genus    = syns[0]
            species  = f' {syns[1]}' if limit == 2 else ''
            synonyms = f'{synonyms},{genus}{species}'
            
        synonyms = synonyms.lstrip(',')
    except Exception as e:
        logger.exception(f'getSynonyms 040: caught exception {e}')
        return synonyms, e.message
        
    if synonyms == None:
        logger.info(f'getSynonyms 050: synonyms not found')
        return synonyms, 'getSynonyms 050: synonyms not found' 
    else:
        logger.info(f'getSynonyms 060: synonyms: {synonyms}')
        
    return synonyms, None
