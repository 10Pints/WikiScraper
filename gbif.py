# gbif.py
from pygbif import occurrences
from pygbif import species

def exp_1():
    key = species.name_backbone(name = 'Ursus americanus', rank='species')['usageKey']
    items = occurrences.search(taxonKey = key)
    len = len(items)
    print(items)

   
if __name__ == '__main__':
    exp_1()