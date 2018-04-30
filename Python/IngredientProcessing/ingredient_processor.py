import csv
import re
import operator
from enum import Enum
import unicodedata
import fractions
from pint import UnitRegistry

ureg = UnitRegistry()
_unitDict = []
_ingrDict = []
_dp = re.compile('(?<!\/)\d+\.*\d*(?=[a-zA-Z]*(\s|[^\/]))') #decimal quantity identifier
_fp = re.compile('(\d\s)*\d+\/\d+(?=\s)') #fractional quantity identifier. assumption - ingredients using fractional quantities put spacing between fraction and unit
_dup = re.compile('(?<=\d|\s)([a-zA-Z]+)') #unit (optionally preceded by decimal) identifier
_wp = re.compile('(?:(?<=^)|(?<=\s))([a-zA-Z\s]+)(?=[^a-zA-Z]|$)') #alphabetic word identifier

class TokenType(Enum):
    QTY = 0
    UNIT = 1
    INGR = 2
    CONJ = 3

class Token:
    def __init__(self, tokentype, value, start, end):
        self.tokentype = tokentype
        self.value = value
        self.start = start
        self.end = end
    def __str__(self):
        return "string: %s tokentype: %s position: (%s,%s)" % (self.string, self.tokentype.name, self.start, self.end) 
    def __repr__(self):
        return "string: %s tokentype: %s position: (%s,%s)" % (self.string, self.tokentype.name, self.start, self.end) 

class Ingredient:
    def __init__(self, _string="", ingredient=None, quantity=None, unit=None):
        self._string = _string
        self.ingredient = ingredient
        self.quantity = quantity
        self.unit = unit
    def __add__(self, another):
        if not self.ingredient or not another.ingredient or not self.unit or not another.unit or not self.quantity or not another.quantity:
            return None
        if self.ingredient != another.ingredient:
            return None
        try:
            ingredSum = self.quantity * self.unit + another.quantity * another.unit
        except:
            return None
        if ingredSum:
            return Ingredient("", self.ingredient, ingredSum.magnitude, ingredSum.units)
    def __str__(self):
        return "string: %s\ningredient: %s quantity: %s unit: %s\n" % (self._string, self.ingredient, self.quantity, self.unit)
    def __repr__(self):
        return "string: %s\ningredient: %s quantity: %s unit: %s\n" % (self._string, self.ingredient, self.quantity, self.unit)
    def combine(ingr_list):
        ingr_dict = {}
        incomplete_ingr = []
        for ingr in ingr_list:
            if ingr.ingredient:
                if ingr.ingredient not in ingr_dict:
                    ingr_dict[ingr.ingredient] = ingr
                else:
                    combined = ingr_dict[ingr.ingredient] + ingr
                    if combined:
                        ingr_dict[ingr.ingredient] = combined
                    else:
                        incomplete_ingr.append(ingr)
            else:
                incomplete_ingr.append(ingr)
        combined_list = list(ingr_dict.values())
        combined_list.extend(incomplete_ingr)
        return combined_list

    def changeUnit(self, s):
        try:
            newUnit = ureg[s]
            if newUnit:
                self.unit = newUnit
                return newUnit
        except:
            return None
#with open('units.csv', newline='') as csvfile:
#    reader = csv.DictReader(csvfile)
#    for row in reader:
#        _unitDict.append(row['unit'])

with open('ingredients.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        _ingrDict.append(row['ingredient'])
    _ingrDict.sort(key=len, reverse=True)        

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

def extractQuantities(inputString):
    quantities_list = []
    for i in range(len(inputString)):
        c = inputString[i]
        try:
            name = unicodedata.name(c)
        except ValueError:
            continue
        if name.startswith('VULGAR FRACTION'):
            normalized = unicodedata.normalize('NFKC', c).replace(u"\u2044", '/')
            repl = '%s%s%s'
            if i>0:
                if inputString[i-1].isdigit():
                    repl = '%s %s%s'
            inputString = repl % (inputString[:i], normalized, inputString[i+1:])
    fpmat = _fp.finditer(inputString)
    for mat in fpmat:
        if mat:
            repl = ""
            for i in range(mat.start(), mat.end()):
                repl += "_"
            inputString = inputString[:mat.start()] + repl + inputString[mat.end():]
            frac = mat.group()
            frac_flt = float(sum(fractions.Fraction(term) for term in frac.split()))
            quantities_list.append(Token(TokenType.QTY, frac_flt, mat.start(), mat.end()))
    dpmat = _dp.finditer(inputString)
    for mat in dpmat:
        quantities_list.append(Token(TokenType.QTY, float(mat.group()), mat.start(), mat.end()))
    quantities_list.sort(key=operator.attrgetter('start'))
    return quantities_list

def extractUnits(inputString):
    inputString = inputString.lower()
    units_list = []
    dupmat = _dup.finditer(inputString)
    for m in dupmat:
        try:
            qty = ureg(m.group())
        except:
            continue
        if qty:
            units_list.append(Token(TokenType.UNIT, qty.units, m.start(), m.end()))
    units_list.sort(key=operator.attrgetter('start'))
    return units_list

def extractIngredients(inputString):
    inputString = inputString.lower()
    ingred_list = []
    for ingred in _ingrDict:
        pattern = r"\b" + ingred + r"\b"
        im = re.finditer(pattern, inputString)
        for imat in im:
            if imat:
                repl = ""
                for i in range(imat.start(), imat.end()):
                    repl += "_"
                inputString = inputString[:imat.start()] + repl + inputString[imat.end():]
                ingred_list.append(Token(TokenType.INGR, imat.group(), imat.start(), imat.end()))
    ingred_list.sort(key=operator.attrgetter('start'))
    return ingred_list

def processIngredient(inputString):
    tokens_list = []
    ingred_list = []
    ingred=None
    qty=None
    unit=None
    qtys = extractQuantities(inputString)
    if len(qtys) > 0:
        qty = qtys[0].value
    units = extractUnits(inputString)
    if len(units) > 0:
        unit = units[0].value
    ingreds = extractIngredients(inputString)
    if len(ingreds) > 0:
        ingred = ingreds[0].value
    tokens_list.extend(qtys)
    tokens_list.extend(units)
    tokens_list.extend(ingreds)
    tokens_list.sort(key=operator.attrgetter('start'))
    #token patterns
    return Ingredient(_string=inputString, ingredient=ingred, quantity=qty, unit=unit) 
