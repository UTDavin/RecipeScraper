const numericQuantity = require('numeric-quantity');
var request = require('request');
var cheerio = require('cheerio');
var Qty = require('js-quantities');
const fetch = require("node-fetch");

//https://world.openfoodfacts.org/ingredients.json
//TODO: look at wikidata and other open-source ingredient collection alternatives
const ingr_set = new Set();
const initializeIngredients = async () => {
  await fetch('https://world.openfoodfacts.org/ingredients.json')
    .then(res => res.json())
    .then(data => data.tags.map(item => {
      let name = item.name.replace(/-/g," ").trim(); //correct name delimiter;
      if(!name.includes(":") && name.length > 0) //omit localized entries
      {
        ingr_set.add(name.toLowerCase());
      }
    }));
  ingr_set.delete("a"); //why is "a" an ingredient...?
  ingr_set.delete("and"); //why is "and" an ingredient?
}
class Scraper {

async scrape(recipeUrl)
{
  if(ingr_set.size == 0) await initializeIngredients();
  //ingr_set.forEach(element => console.log(element));
  var results = await this.scrapeRecipes(recipeUrl);
  return results;
}

async scrapeRecipes(recipeUrl)
{
  var ingredients = [];
  ingredients = await this.scrapeLists(recipeUrl);
  return ingredients;
}

async scrapeLists(url)
{
    let candidate = [];
    const response = await fetch(url);
    const body = await response.text();
    const $ = cheerio.load(body, {normalizeWhitespace: true});
    let lists = [];
    $('ul,ol').each(function(i, list){
      lists.push(list);
    });
    for(var i=0; i<lists.length;i++)
    {
      let results = [];
      let itemCount = $('li', lists[i]).length;
      let ingrCount=0;
      let qtyCount=0;
      $('li', lists[i]).each(function(j, item){
        let ingr = Scraper.processIngredient($(this).text().trim());
        if(ingr !== null)
        {
          ingrCount += ingr.ingrs.length;
          qtyCount += ingr.qtys.length;
          ingr.qtys = ingr.qtys.join(' ');
          ingr.ingrs = ingr.ingrs.join(' ');
          results.push(ingr);
        }
      });
      if(results.length > itemCount/2) // if over half of the list items are "valid ingredients", add as candidate
      {
        candidate.push({items:results, ratio: qtyCount/parseFloat(ingrCount), combinedCount:ingrCount+qtyCount});
      }
    }

    let result = [];
    let highestRatio = 0.0; //ratio of qtys to ingrs. highest pairing ratio = most likely candidate
    let highestCount = 0;
    candidate.forEach(element => {
      if(element.ratio > highestRatio || (element.ratio == highestRatio && element.combinedCount > highestCount))
      {
        highestRatio = element.ratio;
        highestCount = element.combinedCount;
        result = element.items;
      }
    });

    return result;
}

scrapeText(url)
{
  return new Promise((resolve, reject) => {
    let results = [];
    osmosis
    .get(url)
    .find('//div[p]')
    .set('listItem')
    .data(function(listing) {
      console.log(listing);
      results.push(listing);
    })
    .log(console.log)
    .error(console.log)
    .debug(console.log)
    .done(() => resolve(results));
  });
}

static processIngredient(listing)
{
  if(listing === undefined) return null;
  if(listing.length > 150) return null;
  var lower = listing.toLowerCase(); // TODO: check if lower case messes up quantity/units check
  var tokens = lower.split(" ");
  var i=0;
  while(i < tokens.length)
  {
    if(i+1 < tokens.length)
    {
      let candidate = numericQuantity(tokens[i] + " " + tokens[i+1]);
      if(!Number.isNaN(candidate))
      {
        tokens.splice(i, 2, candidate);
        i=i+1;
        continue;
      }
    }
    let candidate = numericQuantity(tokens[i]);
    if(!Number.isNaN(candidate))
    {
      tokens.splice(i, 1, candidate);
    }
    i=i+1;
  }
  i=0;
  var qtys=[];
  var ingrs=[];
  while(i < tokens.length)
  {
    //ingredients match
    let ingrMatch=false;
    let end = tokens.length;
    while(!ingrMatch && end > i)
    {
      let slice = tokens.slice(i, end);
      let candidate = slice.join(' ');
      if(ingr_set.has(candidate))
      {
        ingrMatch = true;
        ingrs.push(candidate);
        break;
      }
      end--;
    }
    if(ingrMatch)
    {
      i = end;
      continue;
    }
    //quantity + unit check
    if(i+1 < tokens.length)
    {
      try
      {
        var qty = Qty(tokens[i] + " " + tokens[i+1]);//see if quantity + unit can be extracted using 2 tokens
        if(qty !== null && (qty.kind() == 'mass'|| qty.kind() == 'volume') || qty.isUnitless())
        {
          qtys.push(qty);
          i=i+2;
          continue;
        }
      }
      catch{}
    }
    try
    {
      var qty = Qty(tokens[i]);
      if(qty !== null && (qty.kind() == 'mass'|| qty.kind() == 'volume') || qty.isUnitless()) 
      {
        qtys.push(qty);
      }
    }
    catch{}
    i++;
  }

  return ingrs.length > 0 ? {
    list: listing,
    qtys: qtys,
    ingrs: ingrs
  } : null;
}

}

module.exports = Scraper