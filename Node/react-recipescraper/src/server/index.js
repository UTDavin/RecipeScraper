require('dotenv').config({ path: '.env.local' });
const Scraper = require('./scrape.js');
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const Sequelize = require('sequelize');
const epilogue = require('epilogue');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// app.use(async (req, res, next) => {
//   try {
//     if (!req.headers.authorization) throw new Error('Authorization header is required');

//     const accessToken = req.headers.authorization.trim().split(' ')[1];
//     await oktaJwtVerifier.verifyAccessToken(accessToken, 'api://default');
//     next();
//   } catch (error) {
//     next(error.message);
//   }
// });

const database = new Sequelize({
  dialect: 'sqlite',
  storage: './test.sqlite',
});

const Recipe = database.define('recipes', {
  title: Sequelize.STRING,
  url: Sequelize.TEXT,
  body: Sequelize.TEXT,
});

epilogue.initialize({ app, sequelize: database });

epilogue.resource({
  model: Recipe,
  endpoints: ['/recipes', '/recipes/:id'],
});


app.get('/scrape', async function (req, res)
{
  var decoded = decodeURI(req.query.url);
  // fetch url contents
  // pass to scraper
  var scraper = new Scraper();
  var contents = await scraper.scrape(decoded);
  res.send({url: decoded, recipe: contents});
});

app.get('/ingredients', async function (req, res)
{
  var ingredients = await Scraper.getIngredients();
  res.send({ingredients: ingredients});
})

app.get('/units', async function (req, res)
{
  var units = Scraper.getUnits();
  res.send({units: units});
})

const port = process.env.SERVER_PORT || 3001;

database.sync().then(() => {
  app.listen(port, () => {
    console.log(`Listening on port ${port}`);
  });
});