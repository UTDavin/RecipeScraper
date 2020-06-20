import React from 'react';
import {
  TextField,
} from '@material-ui/core';
import Autocomplete from '@material-ui/lab/Autocomplete';
import AwesomeDebouncePromise from 'awesome-debounce-promise';

export default function AutoCompleteForm(props){
  const [inputValue, setInputValue] = React.useState(props.input);
  const [value, setValue] = React.useState(props.value);
  const [options, setOptions] = React.useState(props.options);
  const [label, setLabel] = React.useState(props.label);
  const searchAPI = text => searchForIngredientsAsync(text);
  const searchAPIDebounced = AwesomeDebouncePromise(searchAPI, 500);
  
  const searchForIngredientsAsync = async (value) =>
  {
    if(value.length === 0 || options.find(e => e[label] === value) !== undefined)
    {
      return;
    }
    fetch(`${API}/ingredients?startsWith=${value}`)
      .then(response => 
      {
        return response.json();
      })
      .then(data =>
      {
        setOptions(data.ingredients);
      })
  }
  const API = process.env.REACT_APP_API || 'http://localhost:3001';

  const handleIngrInputChange = async (event, value) => {  
    await searchAPIDebounced(value);
    setInputValue(value);
  }

  return (<Autocomplete
            id="size-small-outlined"
            size="small"
            style= {{width:200}}
            autoComplete
            value={inputValue}
            onInputChange ={handleIngrInputChange}
            getOptionSelected = {(option, value) => {return typeof option === 'string' ? option == value: option[label] == value[label]}}
            options={options}
            getOptionLabel={option => typeof option === 'string' ? option : option[label]}
            onChange={(event, value) => setValue(value)}
            renderInput={params => (
            <TextField
              {...params}
              variant="outlined"
              placeholder="ingredient name"
              margin="normal"
              fullWidth
            />)}
          />);
}