import web_recipescraper
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
tmpList = []
processedList = []
while True:
    print()
#1. scrape ingredients list from web
    if state == prgState.INIT:
        tmpList = web_recipescraper.getIngredients()
        if tmpList == None:
            userInput = (input("Try again? [Y/N]: ")).lower()
            if userInput == "y":
                continue
            else:
                quit()
        elif len(tmpList) == 0:
            print("Sorry, could not obtain ingredients list!")
            continue
        else:
            state = prgState.OBTAINEDLIST
            continue
    elif state == prgState.OBTAINEDLIST:        
#2. process ingredients from list
        #TODO: refine ingredient processor
        for ingred in tmpList:
            processed = ingredient_processor.processIngredient(ingred)
            processedList.append(processed)
        state = prgState.PROCESSEDLIST
        continue
    elif state == prgState.PROCESSEDLIST:
        for item in processedList:
            print(item)
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
        for c, value in enumerate(processedList, 0):
            print(c, value)
        print()
        userInput = (input("'edit [entry number]'=edit specified entry\n combine [entry1] [entry2] = combine two entries \n'return'=return to previous menu (or enter 'q' to quit): ")).lower()
        mat = re.match("(edit\s(\d+))", userInput)
        cmat = re.match("(combine\s(\d+\s+\d+))", userInput)
        if mat:
            print(processedList[int(mat.group(2))])
        elif cmat:
            first, second = cmat.group(2).split(" ")
            print(processedList[int(first)] + processedList[int(second)])
        elif userInput == "return":
            state = prgState.PROCESSEDLIST
        elif userInput == "q":
            quit()
            
