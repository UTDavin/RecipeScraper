from bs4 import BeautifulSoup
import requests

#jang kalguksu
testrecipe1 = "http://seonkyounglongest.com/jang-kalguksu/"
page = requests.get(testrecipe1).text
kalguksu = BeautifulSoup(page)

