from bs4 import BeautifulSoup
import tkinter
import codecs
from tkinter.filedialog import askopenfilename
import urllib.request
import re
request = ""

_unitDict = [
                "ounce",
                "ounces",
                "oz",
                "cup",
                "cups",
                "pound",
                "pounds",
                "lb",
                "lbs",
                "pt",
                "kg",
                "kilogram",
                "kilograms",
                "g",
                "gram",
                "grams",
                "pint",
                "pints",
                "gallon",
                "gallons",
                "gal",
                "package",
                "packages",
                "pkg",
                "teaspoon",
                "teaspoons",
                "tsp",
                "tablespoon",
                "tablespoons",
                "tbsp",
                "quart",
                "quarts",
                "liter",
                "liters",
                "ltr",
                "clove",
                "cloves",
                "bunch",
                "bunches",
                "container",
                "containers",
                "pack",
                "packs",
                "bottle",
                "bottles",
                "can",
                "cans",
                "stick",
                "sticks"
            ]

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
        print("ERS plugin detected")
        ingredientslist = []
        for ingr in ingredients:
            ingredient = __processLiString__(ingr)
            if ingredient:
                ingredientslist.append(ingredient)
                print(__containsQuantity__(ingredient))
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
            print("list items of class 'ingredient'")
            print(ingrClass)    
            ingredients = []
            for ingr in ingrClass:
                ingredient = __processLiString__(ingr)
                if ingredient:
                    ingredients.append(ingredient)
                    print(__containsQuantity__(ingredient))
            return ingredients

def __generalScrape__(souparg):
    #general case: need to verify list as ingredients list
    generalRecipe = souparg.find_all(['ol', 'ul'])
    print("generic scraping")
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
        if num_quantity_items > len(listItems)/2 and num_unit_items > len(listItems)/2: #looks like a good list because over half of the list items had a quantity in them and/or had a unit
            fullList.extend(filteredList)
    if len(fullList) == 0:
        print("No good ingredients list candidates found")
        return []
    else:
        return fullList

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
    #decimal romanized quantity 1 to 1.5 ?
    #fractional_range_quantity 1/3-2/3 cup
    #compound fractional quantity 1 and 1/2 cup

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
