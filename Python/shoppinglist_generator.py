from Generic import web_recipescraper
from IngredientProcessing import ingredient_processor
#from IngredientCollator import ingredientcollator
from enum import Enum

class prgState(Enum):
    INIT = 0
    OBTAINEDLIST = 1
    PROCESSEDLIST = 2
    EDITINGLIST = 3

state = prgState.INIT
ingredientList = []
while True:
#1. scrape ingredients list from web
    if state == prgState.INIT:
        ingredientslist = web_recipescraper.getIngredients()
        if ingredientslist == None:
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
        state = prgState.PROCESSEDLIST
        continue
    elif state == prgState.PROCESSEDLIST:
        print(ingredientList)
        userChoice = input("1. correct entry 2. add another recipe 3. make shopping list (or enter 'q' to quit): ")
        if userChoice == 1 or userChoice == 2 or userChoice == 3:
            print("valid choice %s" % userChoice)
        elif userChoice == "q":
            quit()
        else:
            print("invalid choice")

#3. display results of processing
#   options: 1) correct entry 2) add another recipe 3) make shopping list
