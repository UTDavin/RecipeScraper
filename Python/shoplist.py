from flask import Flask, render_template, url_for, request
from flask_table import Table, Col
import web_recipescraper
from IngredientProcessing import ingredient_processor
app = Flask(__name__)

class IngrTable(Table):
    _string=Col('Listing')
    ingredient=Col("Ingredient")
    quantity=Col("Qty")
    unit=Col("unit")


processedList = []

@app.route('/')
def home():
    return render_template('template.html', table=processedList)

@app.route('/process', methods=['GET', 'POST'])
def process():
    url = request.form['recipeurl']
    print(url)
    ingredientslist = web_recipescraper.getIngredients(url)
    if ingredientslist:
        for ingred in ingredientslist:
            processed = ingredient_processor.processIngredient(ingred)
            processedList.append(processed)
        print(processedList)
    return render_template('template.html', table=processedList, url=url)
