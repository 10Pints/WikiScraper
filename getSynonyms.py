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
def getSynonyms(table):
    synonyms = ''
    status = None
    print('getSynonyms 000: starting, looking for the taxonlist')
         
    if table == None:
        print('getSynonyms 010: table not supplied')
        #if synonyms == None: synonyms='<not found>'
        return None,'010: table not supplied'
    
    # look for an a tag title="Synonym (taxonomy)"
    a_tag = table.find('a', attrs={'title':'Synonym (taxonomy)'})
    if a_tag == None:
        print('getSynonyms 020: Synonym (taxonomy) not found')
        #if synonyms == None: synonyms='<not found>'
        return None, '020: Synonym (taxonomy) row not found>'
    
    #get its tr parent
    tr = a_tag.find_parent('tr')
    # get next tr
    tr = tr.find_next_sibling('tr')
    # get its li items
    li_items = tr.findAll('li')
    
    if len(li_items) == 0:
        li_items = tr.findAll('i')
   
    if li_items == None:
        print('<synonyms not found>')
        return None, '030: synonyms items found>'
 
    for item in li_items:
        syns = item.text.split()
        limit = len(syns)
        
        # just want the bi name, ignore the author and possible date
        if limit>2: limit=2
        
        genus = syns[0]
        species = f' {syns[1]}' if limit == 2 else ''
               
        #for i in range(0, limit, 1):
        synonyms = f'{synonyms},{genus}{species}'
            
    # look for a <ul> with <ul class="taxonlist">
    #ul = table.find('ul', attrs={'class':'taxonlist'})
    
    # get its list of <i> tags
    #tds = ul.findAll('i')
    
    # create a list of the texts from each list item 
    #for item in tds:
    #    synonyms = f'{synonyms},{item.text}'
        
    # return it#,Pyroderces simplex Walsingham, 1891,Amneris flexiloquella Riedl, 1993,Stagmatophora gossypiella Walsingham, 1906,Anatrachyntis hemizopha Meyrick, 1916,Anatrachyntis repandatella (Legrand, 1966)
    synonyms = synonyms.lstrip(',')
    if synonyms == None: synonyms='<not found>'
    print(f'synonyms: {synonyms}')
    return synonyms, None
