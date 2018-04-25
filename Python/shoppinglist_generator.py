from Generic import web_recipescraper
from IngredientProcessing import ingredient_processor
#from IngredientCollator import ingredientcollator
from enum import Enum
import re

class prgState(Enum):
    INIT = 0
    OBTAINEDLIST = 1
    PROCESSEDLIST = 2
    EDITINGLIST = 3

state = prgState.INIT
ingredientList = []
while True:
    print()
#1. scrape ingredients list from web
    if state == prgState.INIT:
        ingredientslist = web_recipescraper.getIngredients()
        if ingredientslist == None:
            userInput = (input("Try again? [Y/N]: ")).lower()
            if userInput == "y":
                continue
            else:
                quit()
        elif len(ingredientslist) == 0:
            print("Sorry, could not obtain ingredients list!")
            continue
        else:
            ingredientList.extend(ingredientslist)
            state = prgState.OBTAINEDLIST
            continue
    elif state == prgState.OBTAINEDLIST:        
#2. process ingredients from list
        #TODO: refine ingredient processor
        for ingred in ingredientList:
            quantities = ingredient_processor.extractQuantities(ingred)
            print("current ingredient: %s" % ingred)
            for q in quantities:
                print(q)
            units = ingredient_processor.extractUnits(ingred)
            for u in units:
                print(u)
            ingreds = ingredient_processor.extractIngredients(ingred)
            for i in ingreds:
                print(i)
        state = prgState.PROCESSEDLIST
        continue
    elif state == prgState.PROCESSEDLIST:
        print("%s\n" % ingredientList)
#3. display results of processing
        userChoice = input("1=correct entry 2=add another recipe 3=make shopping list (or enter 'q' to quit): ")
        if userChoice == "2":
            state = prgState.INIT
        elif userChoice == "1":
            state = prgState.EDITINGLIST
        elif userChoice == "3":
            print("make shopping list (to be implemented")
        elif userChoice.lower() == "q":
            quit()
        else:
            print("invalid choice")
    elif state == prgState.EDITINGLIST:
        for c, value in enumerate(ingredientList, 0):
            print(c, value)
        print()
        userInput = (input("'edit [entry number]'=edit specified entry 'return'=return to previous menu (or enter 'q' to quit): ")).lower()
        mat = re.match("(edit\s(\d+))", userInput)
        if mat:
            print(ingredientList[int(mat.group(2))])
        elif userInput == "return":
            state = prgState.PROCESSEDLIST
        elif userInput == "q":
            quit()
            
