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

@app.route('/')
def home():
    return render_template('template.html')

@app.route('/process', methods=['GET', 'POST'])
def process():
    url = request.form['recipeurl']
    ingredientslist = web_recipescraper.getIngredients(url)
    processedList = []
    for ingred in ingredientslist:
        processed = ingredient_processor.processIngredient(ingred)
        processedList.append(processed)
    table = IngrTable(processedList)
    return render_template('template.html', table=table)
