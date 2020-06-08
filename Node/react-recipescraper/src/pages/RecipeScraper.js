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
import MaterialTable from 'material-table';


import { forwardRef } from 'react';

import AddBox from '@material-ui/icons/AddBox';
import ArrowDownward from '@material-ui/icons/ArrowDownward';
import Check from '@material-ui/icons/Check';
import ChevronLeft from '@material-ui/icons/ChevronLeft';
import ChevronRight from '@material-ui/icons/ChevronRight';
import Clear from '@material-ui/icons/Clear';
import DeleteOutline from '@material-ui/icons/DeleteOutline';
import Edit from '@material-ui/icons/Edit';
import FilterList from '@material-ui/icons/FilterList';
import FirstPage from '@material-ui/icons/FirstPage';
import LastPage from '@material-ui/icons/LastPage';
import Remove from '@material-ui/icons/Remove';
import SaveAlt from '@material-ui/icons/SaveAlt';
import Search from '@material-ui/icons/Search';
import ViewColumn from '@material-ui/icons/ViewColumn';

var Qty = require('js-quantities');


const tableIcons = {
    Add: forwardRef((props, ref) => <AddBox {...props} ref={ref} />),
    Check: forwardRef((props, ref) => <Check {...props} ref={ref} />),
    Clear: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
    Delete: forwardRef((props, ref) => <DeleteOutline {...props} ref={ref} />),
    DetailPanel: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
    Edit: forwardRef((props, ref) => <Edit {...props} ref={ref} />),
    Export: forwardRef((props, ref) => <SaveAlt {...props} ref={ref} />),
    Filter: forwardRef((props, ref) => <FilterList {...props} ref={ref} />),
    FirstPage: forwardRef((props, ref) => <FirstPage {...props} ref={ref} />),
    LastPage: forwardRef((props, ref) => <LastPage {...props} ref={ref} />),
    NextPage: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
    PreviousPage: forwardRef((props, ref) => <ChevronLeft {...props} ref={ref} />),
    ResetSearch: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
    Search: forwardRef((props, ref) => <Search {...props} ref={ref} />),
    SortArrow: forwardRef((props, ref) => <ArrowDownward {...props} ref={ref} />),
    ThirdStateCheck: forwardRef((props, ref) => <Remove {...props} ref={ref} />),
    ViewColumn: forwardRef((props, ref) => <ViewColumn {...props} ref={ref} />)
  };

const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
  table: {
    minWidth: 650,
  },
}));

const unitsLookup = {}
const ingredientsLookup = {}

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
  await this.initializeUnits();
  await this.initializeIngredients();
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

initializeUnits = async () => {
  if(Object.keys(unitsLookup).length === 0)
  {
    fetch(`${API}/units`)
    .then(response => 
      {
        return response.json();
      })
      .then(data => 
      {
        Object.assign(unitsLookup, data.units);
      })
  }
};

initializeIngredients = async () => {
  if(Object.keys(ingredientsLookup).length === 0)
  {
    fetch(`${API}/ingredients`)
    .then(response => 
      {
        return response.json();
      })
      .then(data => 
      {
        Object.assign(ingredientsLookup, data.ingredients);
      })
  }
};

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
            <Typography align="center" variant="h6" component="div">
              <a href={this.state.url}>  {this.state.url.length > 50 ? this.state.url.substring(0,50) + "..." : this.state.url}</a>
            </Typography>
            <TableContainer>
            <MaterialTable
              options={{
                search: false,
                pageSize: 10
              }}
              title="Recipe"
              columns={[{title:"Quantity", field:"qty", type:"numeric"}, {title:"Unit", field:"unit", lookup: unitsLookup}, {title:"Ingredient", field:"ingr"}, {title:"Original Listing", field:"list", readonly: true}]}
              icons = {tableIcons}
              data={this.state.data}
              editable={{
                onRowAdd: (newData) =>
                  new Promise((resolve) => {
                    setTimeout(() => {
                      resolve();
                      this.setState((prevState) => {
                        const data = [...prevState.data];
                        data.push(newData);
                        return { ...prevState, data };
                      });
                    }, 600);
                  }),
                onRowUpdate: (newData, oldData) =>
                  new Promise((resolve) => {
                    setTimeout(() => {
                      resolve();
                      if (oldData) {
                        this.setState((prevState) => {
                          const data = [...prevState.data];
                          data[data.indexOf(oldData)] = newData;
                          return { ...prevState, data };
                        });
                      }
                    }, 600);
                  }),
                onRowDelete: (oldData) =>
                  new Promise((resolve) => {
                    setTimeout(() => {
                      resolve();
                      this.setState((prevState) => {
                        const data = [...prevState.data];
                        data.splice(data.indexOf(oldData), 1);
                        return { ...prevState, data };
                      });
                    }, 600);
                  }),
              }}
            />
            </TableContainer>
          </Paper>
        )}
      </Grid>
    </Fragment>
  )
}
}

export default (recipeScraper);