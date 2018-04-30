import web_recipescraper
from IngredientProcessing import ingredient_processor
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
        for c, value in enumerate(processedList, 0):
            print(c, value)
#3. display results of processing
        userChoice = input("1=edit list\n2=add another recipe\n3=make shopping list (or enter 'q' to quit): ")
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
        userInput = (input("""viewall = see full list of ingredients
comb [entry1] [entry2] = see result of combining two entries
comball=combine all (similar) ingredients
del [entry number]=delete specified entry
delall=delete all ingredients
set [entry number] ingr [newvalue]= change ingredient value of specified entry
set [entry number] qty [newvalue]= change quantity value of specified entry
set [entry number] unit [newvalue]= change unit value of specified entry
return=return to previous menu (or enter 'q' to quit): """)).lower()
        vmat = re.match("viewall", userInput)
        cmat = re.match("(comb\s+(\d+\s+\d+))", userInput)
        camat = re.match("comball", userInput)
        damat = re.match("delall", userInput)
        dmat = re.match("(del\s+(\d+))", userInput)
        simat = re.match("set\s+(\d+)\s+ingr\s+(.+)", userInput)
        sqmat = re.match("set\s+(\d+)\s+qty\s+(\w+)", userInput)
        sumat = re.match("set\s+(\d+)\s+unit\s+(\w+)", userInput)
        print("\n")
        if vmat:
            for c, value in enumerate(processedList, 0):
                print(c, value)
            print()
        elif cmat:
            first, second = cmat.group(2).split(" ")
            print(processedList[int(first)] + processedList[int(second)])
        elif camat:
            processedList = ingredient_processor.Ingredient.combine(processedList)
        elif damat:
            processedList.clear()
        elif dmat:
            del processedList[int(dmat.group(2))]
        elif simat:
            index = int(simat.group(1))
            newingr = simat.group(2)
            ingr = processedList[index]
            ingr.ingredient = newingr
            processedList[index] = ingr
            print(processedList[index])
        elif sqmat:
            index = int(sqmat.group(1))
            newqty = float(sqmat.group(2))
            ingr = processedList[index]
            ingr.quantity = newqty
            processedList[index] = ingr
            print(processedList[index])
        elif sumat:
            index = int(sumat.group(1))
            newunit = sumat.group(2)
            ingr = processedList[index]
            result = ingr.changeUnit(newunit)
            if result:
                processedList[index] = ingr
                print(processedList[index])
            else:
                print("invalid unit entered")
        elif userInput == "return":
            state = prgState.PROCESSEDLIST
        elif userInput == "q":
            quit()
            
