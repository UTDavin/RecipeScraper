import React, { Component, Fragment } from 'react';
//import { withAuth } from '@okta/okta-react';
import { withRouter, Route, Redirect, Link } from 'react-router-dom';
import {
  withStyles,
  Typography,
  Fab,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@material-ui/core';
import { Delete as DeleteIcon, Add as AddIcon } from '@material-ui/icons';
import moment from 'moment';
import { find, orderBy } from 'lodash';
import { compose } from 'recompose';
import PostEditor from '../components/PostEditor';
import ErrorSnackbar from '../components/ErrorSnackbar';

const styles = theme => ({
  recipes: {
    marginTop: theme.spacing(2),
  },
  fab: {
    position: 'absolute',
    bottom: theme.spacing(3),
    right: theme.spacing(3),
    [theme.breakpoints.down('xs')]: {
      bottom: theme.spacing(2),
      right: theme.spacing(2),
    },
  },
});

const API = process.env.REACT_APP_API || 'http://localhost:3001';

class recipesManager extends Component {
  state = {
    loading: true,
    post: null,
    recipes: [],
    error: null,
  };

  componentDidMount() {
    this.getrecipes();
  }

  async fetch(method, endpoint, body) {
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

  async getrecipes() {
    this.setState({ loading: false, recipes: (await this.fetch('get', '/recipes')) || [] });
  }

  savePost = async (recipe) => {
    if (recipe.id) {
      await this.fetch('put', `/recipes/${recipe.id}`, recipe);
    } else {
      await this.fetch('post', '/recipes', recipe);
    }

    this.props.history.goBack();
    this.getrecipes();
  }

  async deletePost(recipe) {
    if (window.confirm(`Are you sure you want to delete "${recipe.title}"`)) {
      await this.fetch('delete', `/recipes/${recipe.id}`);
      this.getrecipes();
    }
  }

  renderPostEditor = ({ match: { params: { id } } }) => {
    if (this.state.loading) return null;
    const recipe = find(this.state.recipes, { id: Number(id) });

    if (!recipe && id !== 'new') return <Redirect to="/recipes" />;

    return <PostEditor recipe={recipe} onSave={this.savePost} />;
  };

  render() {
    const { classes } = this.props;

    return (
      <Fragment>
        <Typography variant="h4">Recipes Manager</Typography>
        {this.state.recipes.length > 0 ? (
          <Paper elevation={1} className={classes.recipes}>
            <List>
              {orderBy(this.state.recipes, ['updatedAt', 'title'], ['desc', 'asc']).map(recipe => (
                <ListItem key={recipe.id} button component={Link} to={`/recipes/${recipe.id}`}>
                  <ListItemText
                    primary={recipe.title}
                    secondary={recipe.updatedAt && `Updated ${moment(recipe.updatedAt).fromNow()}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton onClick={() => this.deletePost(recipe)} color="inherit">
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        ) : (
          !this.state.loading && <Typography variant="subtitle1">No recipes to display</Typography>
        )}
        <Fab
          color="secondary"
          aria-label="add"
          className={classes.fab}
          component={Link}
          to="/recipes/new"
        >
          <AddIcon />
        </Fab>
        <Route exact path="/recipes/:id" render={this.renderPostEditor} />
        {this.state.error && (
          <ErrorSnackbar
            onClose={() => this.setState({ error: null })}
            message={this.state.error.message}
          />
        )}
      </Fragment>
    );
  }
}

export default compose(
  withRouter,
  withStyles(styles),
)(recipesManager);