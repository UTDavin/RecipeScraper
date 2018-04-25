import csv
import re
_unitDict = []
_ingrDict = []
_dp = re.compile('(?<!\/)\d+\.*\d*(?=[a-zA-Z]*(\s|[^\/]))') #decimal quantity identifier
_fp = re.compile('(\d\s)*\d+\/\d+(?=\s)') #fractional quantity identifier. assumption - ingredients using fractional quantities put spacing between fraction and unit
_dup = re.compile('(?<=\d|\s)([a-zA-Z]+)') #unit (optionally preceded by decimal) identifier
_wp = re.compile('(?:(?<=^)|(?<=\s))([a-zA-Z]+)(?=[^a-zA-Z]|$)') #alphabetic word identifier

with open('units.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        _unitDict.append(row['unit'])

with open('ingredients.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        _ingrDict.append(row['ingredient'])
        
# Purpose: process a listed ingredient into subset of primarily three pieces of data: ingredient, quantity, unit
# Possibly categorize rest of listed item as "miscellaneous"
# 
# Considerations:
#   Without a massive ingredients database, much of the ingredients will not be identifiable. It may be possible to infer where the ingredients are
#   located based on the relative positioning of tokens within a listed item. Some clues may be the usage of non-alphanumerics such as '(', ')', ',', ':', '-'
#   
#   for example: paprika - 10 ounces
#                paprika, 10 ounces
#   
#   token before the non-alphanumeric characters IS the ingredient
# 
#
# Strategies:
#   a. Tokenization using non-alphanumerics as delimiter
#       1. tokenize list
#       2. classify tokens using regex
#       3. bundle data together based on relative positioning of classified tokens
#   
#   rules used:if there are no tokens between a pair of (quantity + unit), they are associated with the same ingredient
#   
#   Example: 1 bunch (10oz) of spinach
#   Tokens: ["1", "bunch", "10oz", "of", "spinach"]
#   classified: quantity, unit, quantity, unit, misc, ? or ingredient (based on what the database contains)
#   bundling of data:  1 bunch / 10oz spinach
#
#   CONSIDER THIS: non-alphanumeric delimiters are being removed in this approach. Maybe the locations should be noted in cases the 
#                   positioning of ingredients may need to be guessed when database does not contain the ingredient
#
#

def __containsUnit__(inputString):
    #TODO: reformat decimal_quantity to include 2nd capture group containing a unit (i.e. 'g' in 100g) and add to this method
    p = re.compile(r'\W+')
    tokens = p.split(inputString)
    found = False
    foundUnits = []
    for token in tokens:
        if token.lower() in _unitDict:
            found = True
            foundUnits.append(token.lower())
        else:
            decUnit = re.match('(?<=\d+\.*)([a-zA-Z]+)')
            print(decUnit)
    if found:
        print("found %s in '%s'" % (foundUnits, inputString))
    return found         

def __containsQuantity__(inputString):
    #quantity = re.search('\d+(?=[a-zA-Z]\s)', inputString) # basic quantifier: [number] + whitespace
    decimal_quantity = re.search('\d+\.*\d*(?=[a-zA-Z]*\s)', inputString) # basic decimal (optional .) quantifier: [decimal number][optional unit] + whitespace
                                                                            # i.e.
                                                                            # 1 cup, 1g
                                                                            # 1.5 cups, 1.5g
    fractional_quantity = re.search('\d*\s*\d+\/\d+(?=\s)', inputString)  # basic fractional quantifier: [fractional] + whitespace. 1/3 cup, 1 1/3 cup
                                                                            # i.e.
                                                                            # 1/3 cup
                                                                            # 1 1/3 cup
    #decimal_range_quantity  1.2-1.5 lb
    #decimal romanized range quantity 1 to 1.5 ?
    #fractional_range_quantity 1/3-2/3 cup
    #compound fractional quantity 1 and 1/2 cup
    #romanized quantities one, two, third, etc.

    #if quantity:
    #    print("found quantity match")
    #    print(quantity.group(0))
    if decimal_quantity:
        print("found decimal quantity match '%s' in '%s'" % (decimal_quantity.group(0), inputString))
    if fractional_quantity:
        print("found fractional quantity match '%s' in '%s'" % (fractional_quantity.group(0).strip(), inputString))
    if decimal_quantity or fractional_quantity:
        return True
    return False

def extractQuantities(inputString):
    quantities_list = []
    quantities_list.extend(_dp.finditer(inputString))
    quantities_list.extend(_fp.finditer(inputString))
    return quantities_list

def extractUnits(inputString):
    units_list = []
    dupmat = _dup.finditer(inputString)
    for m in dupmat:
        if m.group() in _unitDict:
            units_list.append(m)
    return units_list

def extractIngredients(inputString):
    ingred_list = []
    ingredmat = _wp.finditer(inputString)
    for m in ingredmat:
        if m.group() in _ingrDict:
            ingred_list.append(m)
    return ingred_list
