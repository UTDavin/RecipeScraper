from bs4 import BeautifulSoup
import tkinter
import codecs
from tkinter.filedialog import askopenfilename
import urllib.request
request = ""
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
    ingredientslist = soup.find_all("li", "ingredient")
    for element in ingredientslist:
        if element.string:
            print(element.string)

