from bs4 import BeautifulSoup
import tkinter
import codecs
from tkinter.filedialog import askopenfilename
import urllib.request
import re
request = ""

# Note: many websites use the easy-recipes style CSS plug-in (?). Classes begin with "ERS" i.e. ERSIngredients, ERSHeadings
#Could leverage this for scraping, but may not be a long-term solution
#Points to consider:
#Ingredients header is usually a single tag consistenting of the string "Ingredients", but NOT ALWAYS
#Often times, the ingredients are encapsulated within tags of classes containing the word "ingredient(s)" - may be more robust than string search
# Ingredient items are usually encapsulated within <li> tags, OR within <span> tags WITHIN <li> tags

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
            if ingr.string:
                ingredientslist.append(ingr.string)
                print(__containsQuantity__(ingr.string))
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
                if ingr.string:
                    ingredients.append(ingr.string)
                    print(__containsQuantity__(ingr.string))
            return ingredients

def __generalScrape__(souparg):

    #general case: need to verify list as ingredients list
    generalRecipe = souparg.find_all(['ol', 'ul'])
    print("generic scraping")
    for listCandidate in generalRecipe:
        listItems = listCandidate.find_all("li")
        num_good_items = 0
        filteredList = []
        for item in listItems:
            if item.string:
                filteredList.append(item.string)
                if len(item.string) > 100: #let's just say an enumerated ingredient string should not exceed 100 chars
                    break
                if __containsQuantity__(item.string):
                    num_good_items += 1
        if num_good_items > len(listItems)/2: #looks like a good list because over half of the list items had a quantity in them
            return filteredList
    print("No good ingredients list candidates found")
    return []

def __containsQuantity__(inputString):
    #quantifier = re.search('\d+(?=[a-zA-Z]\s)', inputString) # basic quantifier: [number] + whitespace
    decimal_quantifier = re.search('\d+\.*\d*(?=[a-zA-Z]*\s)', inputString) # basic decimal (optional .) quantifier: [decimal number][optional unit] + whitespace
    fractional_quantifier = re.search('\d*\s*\d+\/\d+(?=\s)', inputString) # basic fractional quantifier: [fractional] + whitespace
    #if quantifier:
    #    print("found quantity match")
    #    print(quantifier.group(0))
    if decimal_quantifier:
        print("found decimal quantity match")
        print(decimal_quantifier.group(0))
    if fractional_quantifier:
        print("found fractional quantity match")
        print(fractional_quantifier.group(0).strip())
    if decimal_quantifier or fractional_quantifier:
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
    print(__ERSScrape__(soup))
    print(__ingrCSSScrape__(soup))
    print(__generalScrape__(soup))
