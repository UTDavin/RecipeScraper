const numericQuantity = require('numeric-quantity');
var request = require('request');
var cheerio = require('cheerio');
var Qty = require('js-quantities');
const fetch = require("node-fetch");
const fs = require('fs');
const lunr = require('lunr');

//https://world.openfoodfacts.org/ingredients.json
//TODO: look at wikidata and other open-source ingredient collection alternatives
const ingr_set = new Set();
const omitted_entries = new Set(["a", "and"]);
const initializeIngredients = async () => {
  if(ingr_set.size == 0) 
  {
    let loaded=false;
    let ingredients;
    try
    {
      let rawdata = fs.readFileSync(__dirname + '/ingredients.json');
      ingredients = JSON.parse(rawdata);
      loaded=true;
      console.log("loaded local data");
    }
    catch
    {
      console.log("unable to load local data. fetching from web");
    }

    if(!loaded)
    {
      await fetch('https://world.openfoodfacts.org/ingredients.json')
        .then(res => res.json()
                        .catch(error => {
                          console.log("error parsing data from web");
                          throw error;
                        }
        ))
        .then(data => {
          ingredients = data;
          loaded=true;
          console.log("loaded data from web");
        })
        .catch(error => console.log("error fetching from openfoodfacts: " + error))
    };
    if(loaded)
    {
      let index = 0;
      ingredients.tags.map(item => {
        let name = item.name.replace(/-/g," ").trim().toLowerCase(); //replace - w/ space, clean up entry;
        if(!name.includes(":") && name.length > 0 && !omitted_entries.has(name)) //omit localized entries
        {
          ingr_set.add(name);
        }
      });
    }
  }
}

const units = {};
const aliases = {};
const unitless = 'none';
const initializeUnits = () => {
  if(Object.keys(units).length == 0)
  {
    let index = 0;
    let arr =  [unitless].concat(Qty.getUnits('mass')).concat(Qty.getUnits('volume'));
    arr.forEach( e => {
      units[e] = index;
      try
      {
        Qty.getAliases(e).forEach( a => 
          {
            aliases[a] = e; //map all possible unit values to the default value
          }
        );
      }
      catch
      {
        console.log("could not get aliases for " + e);
      }
      index++;
    });
  }
}

class Scraper {

static async getIngredients(strQuery, top)
{
  await initializeIngredients();
  let entries = Array.from(ingr_set).map(m => {return {name: m}});
  return await this.queryIngredients(entries, strQuery);
}

static async queryIngredients(entries, strQuery)
{
  console.log("searching for: " + strQuery);
  let ret = [];
  var idx = lunr(function () {
    this.ref('name')
    this.field('name')
    entries.forEach(function (doc) {
      this.add(doc)
    }, this)
  });
  let results = idx.search("name:"+strQuery+"*");
  results.forEach(r => {
    ret.push({name:r.ref});
  });
  return ret;
}

static getUnits() //returns a lookup where key = index, value = unit name
{
  initializeUnits();
  var ret = {};
  for(var key in units){
    ret[units[key]] = key;
  }
  return ret;
}

async scrape(recipeUrl)
{
  await initializeIngredients();
  initializeUnits();
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
          if(ingr.ingr != null) ingrCount++;
          if(ingr.qty != null) qtyCount++;
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
  while(i < tokens.length) //pre-process string by replacing vulgar fractions with decimals
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
  var quantity=null;
  var ingr=null;
  var unit=units[unitless];
  while(i < tokens.length)
  {
    //ingredients match - only check if an ingredient hasn't been found yet
    if(ingr == null)
    {
      let ingrMatch=false;
      let end = tokens.length;
      while(!ingrMatch && end > i)
      {
        let slice = tokens.slice(i, end);
        let candidate = slice.join(' ');
        if(ingr_set.has(candidate))
        {
          ingrMatch = true;
          ingr=candidate; //use ingr name
          break;
        }
        end--;
      }
      if(ingrMatch)
      {
        i = end;
        continue;
      }
    }
    //quantity + unit check
    if(quantity==null)
    {
      if(i+1 < tokens.length)
      {
        try
        {
          var qty = Qty(tokens[i] + " " + tokens[i+1]);//see if quantity + unit can be extracted using 2 tokens
          if(qty!==null && ((qty.units() in aliases) || qty.isUnitless()))
          {
            if(!qty.isUnitless()) 
            {
              unit = units[aliases[qty.units()]];
            }
            quantity = qty.toPrec('.01').toString().split(" ")[0];
            i=i+2;
            continue;
          }
        }
        catch{}
      }

      try //see if quantity+unit can be extracted from 1 token
      {
        var qty = Qty(tokens[i]);
        if(qty !== null && ((qty.units() in aliases) || qty.isUnitless())) 
        {
          if(!qty.isUnitless())
          {
            unit = units[aliases[qty.units()]];
          }
          quantity = qty.toPrec('.01').toString().split(" ")[0];
        }
      }
      catch{}
    }
    i++;
  }
  return ingr != null ? {
    list: listing,
    qty: quantity,
    unit: unit,
    ingr: ingr
  } : null;
}

}

module.exports = Scraper