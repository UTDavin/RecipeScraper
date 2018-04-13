from bs4 import BeautifulSoup
import tkinter
import codecs
import time
from tkinter.filedialog import askopenfilename
import csv
import re
filename = askopenfilename(filetypes=[('HTML files', '*.html')])
f=codecs.open(filename, 'r', "utf-8")
kalguksutext = f.read()
kalguksusoup = BeautifulSoup(kalguksutext, "html.parser")
ingredientslist = kalguksusoup.find_all("li", "ingredient")
for element in ingredientslist:
    if element.string:
        print(element.string)
timestr = time.strftime("%Y%m%d-%H%M%S")
with open(timestr+'.csv', 'w', newline='') as csvfile:
    fieldnames = ['ingredient', 'quantity']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for element in ingredientslist:
        if element.string:
            writer.writerow({'ingredient': element.string, 'quantity': element.string})

