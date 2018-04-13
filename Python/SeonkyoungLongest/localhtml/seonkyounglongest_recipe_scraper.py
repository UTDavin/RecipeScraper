from bs4 import BeautifulSoup
import codecs
f=codecs.open("seonkyounglongest.com_jang-kalguksu.html", 'r', "utf-8")
kalguksu = BeautifulSoup(f.read())


