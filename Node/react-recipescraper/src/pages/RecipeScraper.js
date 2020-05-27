import React, {Component, Fragment} from 'react';
import RestaurantMenuIcon from '@material-ui/icons/RestaurantMenu';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Button from '@material-ui/core/Button';
import Toolbar from '@material-ui/core/Toolbar';
import DeleteIcon from '@material-ui/icons/Delete';
import SaveIcon from '@material-ui/icons/Save';
import { makeStyles } from '@material-ui/core/styles';
import {
  Typography,
  TextField,
} from '@material-ui/core';
import { Form, Field } from 'react-final-form';

const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
  table: {
    minWidth: 650,
  },
}));

const API = process.env.REACT_APP_API || 'http://localhost:3001';

class recipeScraper extends Component {

state = {
  url: '',
  data: []
};

fetch = async (method, endpoint, body) => {
  try {
    const response = await fetch(`${API}${endpoint}`, {
      method,
      body: body && JSON.stringify(body),
      headers: {
        'content-type': 'application/json',
        accept: 'application/json',
        //authorization: `Bearer ${await this.props.auth.getAccessToken()}`,
      },
    });
    return await response.json();
  } catch (error) {
    console.error(error);

    this.setState({ error });
  }
}

reset = () => {
  this.setState({url: "", data: []});
}

scrapeUrl = async (value) => {
  fetch(`${API}/scrape/?url=${encodeURI(value.url)}`)
  .then(response => 
    {
      return response.json();
    })
    .then(data => 
    {
      this.setState({url: value.url, data: data.recipe});
    });
}

render() {
  return (
    <Fragment>
      <Typography variant="h4">Scrape a New Recipe</Typography>
      <Grid container direction="column" justify="center" alignItems="center">
        {this.state.data.length == 0 ? (
          <>
          <RestaurantMenuIcon style={{ fontSize: 240 }}></RestaurantMenuIcon>
          <Form initialValues={{url: this.state.url}} onSubmit={this.scrapeUrl}>
            {({ handleSubmit }) => (
              <form onSubmit={handleSubmit}>
              <Field name="url">
                {({ input }) => <TextField style = {{width: 600}} label="Enter Recipe URL" autoFocus {...input}/>}
              </Field>        
              </form>    
            )}
          </Form>
          </>
        ) : (
          <Paper style={{width:'60%'}}>
            <Toolbar>
              <div style={{flex: 1}}/>
              <Button
                onClick={this.reset}
                variant="contained"
                color="secondary"
                startIcon={<DeleteIcon />}
              >
                Start Over
              </Button>
              <Button
                variant="contained"
                color="primary"
                endIcon={<SaveIcon />}
              >
                Save Recipe
              </Button>
            </Toolbar>
            <Typography align="center" variant="h5" id="tableTitle" component="div">
              Looks Delicious!
            </Typography>
            <Typography align="center" variant="h6" component="div">
              url: <a href={this.state.url}>  {this.state.url.length > 50 ? this.state.url.substring(0,50) + "..." : this.state.url}</a>
            </Typography>
            <TableContainer>
              <Table aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell align="center">Qty</TableCell>
                    <TableCell align="center">Ingredient</TableCell>
                    <TableCell align="center">Listing</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {this.state.data.map((data) => (
                    <TableRow>
                      {/* <TableCell component="th" scope="row">
                        {row.name}
                      </TableCell> */}
                      <TableCell style={
                        {whiteSpace: "normal",
                        wordWrap: "break-word"}} align="center">{data.qtys}</TableCell>
                      <TableCell style={
                        {whiteSpace: "normal",
                        wordWrap: "break-word"}} align="center">{data.ingrs}</TableCell>
                      <TableCell style={
                        {whiteSpace: "normal",
                        wordWrap: "break-word"}} align="center">{data.list}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </Grid>
    </Fragment>
  )
}
}

export default (recipeScraper);