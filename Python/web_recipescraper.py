from bs4 import BeautifulSoup
import tkinter
import codecs
from tkinter.filedialog import askopenfilename
import urllib.request
import re
import csv
import unicodedata
import sys

_dp = re.compile('(?<!\/)\d+\.*\d*(?=[a-zA-Z]*(\s|[^\/]))') #decimal quantity identifier
_fp = re.compile('(\d\s)*\d+\/\d+(?=\s)') #fractional quantity identifier. assumption - ingredients using fractional quantities put spacing between fraction and unit
_dup = re.compile('(?<=\d|\s)([a-zA-Z]+)') #unit (optionally preceded by decimal) identifier
_unitDict = []
#_ingrDict = []

with open('units.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        _unitDict.append(row['unit'])

#with open('ingredients.csv', newline='') as csvfile:
#    reader = csv.DictReader(csvfile)
#    for row in reader:
#        _ingrDict.append(row['ingredient'])
#    _ingrDict.sort(key=len, reverse=True)     
			
# Note: many websites use the easy-recipes style CSS plug-in (?). Classes begin with "ERS" i.e. ERSIngredients, ERSHeadings
#Could leverage this for scraping, but may not be a long-term solution
#Points to consider:
#Ingredients header is usually a single tag consistenting of the string "Ingredients", but NOT ALWAYS
#Often times, the ingredients are encapsulated within tags of classes containing the word "ingredient(s)" - may be more robust than string search
# Ingredient items are usually encapsulated within <li> tags, OR within <span> tags WITHIN <li> tags

def __processLiString__(soupli):
    if soupli.string:
        return soupli.string
    fullString = ""
    for item in soupli.find_all():
        if item.string:
            fullString = fullString + " " + item.string
    return fullString.strip()

def __ERSScrape__(souparg):
    #Common case 1: EasyRecipe plugin
    easyRecipe = souparg.find(class_="ERSIngredients")
    if easyRecipe == None:
        return []
    else:
        ingredients = easyRecipe.find_all("li")
        #print("ERS plugin detected")
        ingredientslist = []
        for ingr in ingredients:
            ingredient = __processLiString__(ingr)
            if ingredient:
                ingredientslist.append(ingredient)
                #print(__containsQuantity__(ingredient))
        return ingredientslist

def __ingrCSSScrape__(souparg): 
    #Common case 2: list items with CSS class name = "ingredient"
    ingrClass = souparg.find_all("li", "ingredient")
    if ingrClass == None:
        return []
    else:
        if len(ingrClass) == 0:
            return []
        else:
            #print("list items of class 'ingredient'")
            #print(ingrClass)    
            ingredients = []
            for ingr in ingrClass:
                ingredient = __processLiString__(ingr)
                if ingredient:
                    ingredients.append(ingredient)
                    #print(__containsQuantity__(ingredient))
            return ingredients

def __generalScrape__(souparg):
    #general case: need to verify list as ingredients list
    generalRecipe = souparg.find_all(['ol', 'ul'])
    #print("generic scraping")
    fullList = []
    for listCandidate in generalRecipe:
        listItems = listCandidate.find_all("li")
        num_quantity_items = 0
        num_unit_items = 0
        filteredList = []
        for item in listItems:
            ingredient = __processLiString__(item)
            if ingredient:
                filteredList.append(ingredient)
                if len(ingredient) > 100: #let's just say an enumerated ingredient string should not exceed 100 chars
                    break
                if __containsQuantity__(ingredient):
                    num_quantity_items += 1
                if __containsUnit__(ingredient):
                    num_unit_items += 1
        if num_quantity_items + num_unit_items > len(listItems)/2: #looks like a good list because over half of the list items had a quantity in them and/or had a unit
            fullList.extend(filteredList)
    if len(fullList) == 0:
        print("No good ingredients list candidates found")
        return []
    else:
        return fullList

def __containsUnit__(inputString):    
    inputString = inputString.lower()
    dupmat = _dup.finditer(inputString)
    for m in dupmat:
        if m.group() in _unitDict:
            return True
    return False  

def __containsQuantity__(inputString):
    dec = False
    frac = False
    fpmat = _fp.search(inputString)
    if not fpmat:
        for i in range(len(inputString)):
            c = inputString[i]
            try:
                name = unicodedata.name(c)
            except ValueError:
                continue
            if name.startswith('VULGAR FRACTION'):
                frac = True
                break
    else:
        frac = True
    dpmat = _dp.search(inputString)
    if dpmat:
        dec = True
    #decimal_range_quantity  1.2-1.5 lb
    #decimal romanized quantity 1 to 1.5 ?
    #fractional_range_quantity 1/3-2/3 cup
    #compound fractional quantity 1 and 1/2 cup
    if dec or frac:
        return True
    return False

def getIngredients(url):
    try:
        response = urllib.request.urlopen(url)
    except:
        print(sys.exc_info()[0])
        print("something went wrong with request")
        return None
    responsetext = response.read()
    soup = BeautifulSoup(responsetext, "html.parser")
    list1 = __ERSScrape__(soup)
    if len(list1) > 0:
        return list1
    list2 = __ingrCSSScrape__(soup)
    if len(list2) > 0:
        return list2
    list3 = __generalScrape__(soup)
    if len(list3) > 0:
        return list3
    return []

def test():
    while request != "q":
        request = input("Enter URL of recipe (or enter q to quit): ")
        if request == "q":
            quit()
        try:
            response = urllib.request.urlopen(request)
        except:
            print("something went wrong with request")
            quit()
        responsetext = response.read()
        soup = BeautifulSoup(responsetext, "html.parser")
        list1 = __ERSScrape__(soup)
        list2 = __ingrCSSScrape__(soup)
        list3 = __generalScrape__(soup)
        print("Results of EasyRecipe scrape: ")
        if len(list1) > 0:
            for item in list1:
                print(item)
        print("Results of CSS ingredients class scrape: ")
        if len(list2) > 0:
            for item in list2:
                print(item)
        print("Results of Generic scrape: ")
        if len(list3) > 0:
            for item in list3:
                print(item)
