var osmosis = require('osmosis');
var Qty = require('js-quantities');

class Scraper {

async scrape(recipeUrl)
{
  var results = await this.scrapeRecipes(recipeUrl);
  return results;
}

async scrapeRecipes(recipeUrl)
{
  var ingredients = [];
  var results = await this.scrapeLists(recipeUrl);
  results.forEach(element => {
    var ingr = this.processIngredient(element);
    if(ingr != null) ingredients.push(ingr);
  });
  return ingredients;
}

scrapeLists(url)
{
  return new Promise((resolve, reject) => {
    let results = [];
    osmosis
    .get(url)
    .find('ol')
    .find('ul')
    .set(
      {
        list: 'li'
      }
    )
    .data(function(listing) {
      results.push(listing);
    })
    .log(console.log)
    .error(console.log)
    .debug(console.log)
    .done(() => resolve(results));
  });
}

processIngredient(listing)
{
  var orig = listing.list;
  var tokens = orig.split(" ");
  var i=0;
  var qtys=[];
  while(i < tokens.length)
  {
    //TODO:ingredient check

    //quantity + unit check
    if(i+1 < tokens.length)
    {
      try
      {
        var qty = Qty(tokens[i] + " " + tokens[i+1]);//see if quantity + unit can be extracted using 2 tokens
        if(qty !== null)
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
      if(qty !== null) qtys.push(qty);
    }
    catch{}
    i++;
  }

  console.log(qtys);
  return {
    list: listing,
    qtys: qtys.join(',')
  };
}

}

module.exports = Scraper