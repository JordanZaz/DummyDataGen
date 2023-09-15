import * as React from 'react';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import StorageIcon from '@mui/icons-material/Storage';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import jsYaml from 'js-yaml';
import { Select, MenuItem, InputLabel, FormControl } from "@mui/material";
import { exampleYaml } from './exampleYaml';
import GenerateDatasetButton from './ProgressButton';
import Popover from '@mui/material/Popover';
import Paper from '@mui/material/Paper';
import api from '../api';


function Copyright(props) {
  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {'Copyright © '}
      <Link color="inherit" href="https://improvado.io/docs-section-topic/data-dictionary-available-report-types">
        Improvado.io
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}


const defaultTheme = createTheme();

export default function SignUp() {
  const [yaml, setYaml] = React.useState("");
  const [defaultYaml, setDefaultYaml] = React.useState("");
  const [tableName, setTableName] = React.useState("");
  const [ErrorMessage, setErrorMessage] = React.useState("");
  const [datasources, setDatasources] = React.useState([]);
  const [reportTypes, setReportTypes] = React.useState([]);
  const [selectedDatasource, setSelectedDatasource] = React.useState("");
  const [selectedReportType, setSelectedReportType] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [generatedQuery, setGeneratedQuery] = React.useState("");
  const [generatedYaml, setGeneratedYaml] = React.useState("");
  const [refreshCount, setRefreshCount] = React.useState(0);

  const [queryPopoverOpen, setQueryPopoverOpen] = React.useState(false);
  const [queryPopoverAnchor, setQueryPopoverAnchor] = React.useState(null);

  const [YamlPopoverOpen, setYamlPopoverOpen] = React.useState(false);
  const [YamlPopoverAnchor, setYamlPopoverAnchor] = React.useState(null);

  const [TableNamePopoverOpen, setTableNamePopoverOpen] = React.useState(false);
  const [TableNamePopoverAnchor, setTableNamePopoverAnchor] = React.useState(null);

  const [readmePopoverOpen, setReadmePopoverOpen] = React.useState(false);
  const [readmePopoverAnchor, setReadmePopoverAnchor] = React.useState(null);


  // Refresh command
  const refreshData = () => {
      setRefreshCount(refreshCount + 1);
  };


  React.useEffect(() => {
      // Fetch datasources from backend
      api.get('/get_datasources')
          .then(response => {
              const sortedDatasources = response.data.sort();
              setDatasources(sortedDatasources);
          })
          .catch(error => {
              // console.log(error);
          });
  }, []);

  React.useEffect(() => {
      if (selectedDatasource) {
          // Fetch report types from backend
          api.get(`/get_report_types/${selectedDatasource}`)
              .then(response => {
                  const sortedReportTypes = response.data.sort();
                  setReportTypes(sortedReportTypes);
              })
              .catch(error => {
                  // console.log(error);
              });
      }
  }, [selectedDatasource]);

  React.useEffect(() => {
    // if (selectedDatasource && selectedReportType) {
      // Clear the error message
      setErrorMessage("");
      // Update the state to reflect that the start button has been clicked
      setGeneratedQuery("");
      setGeneratedYaml("");

      api.post('/generate', {
        dataSource: selectedDatasource,
        reportType: selectedReportType,
        tableName: tableName,
      })
      .then(response => {
        setTableName(response.data.tableName);

        // Make a copy of the response data
        let dataToYaml = {...response.data};

        // Remove format and tableName from the copy
        delete dataToYaml.format;
        delete dataToYaml.tableName;

        // Convert JSON to YAML
        const generatedYaml = jsYaml.dump(dataToYaml, {
          sortKeys: (a, b) => {
            const order = ["name", "dataType", "generator", "params"];
            const paramOrder = ["min", "max", "length"];
            if (paramOrder.includes(a) && paramOrder.includes(b)) {
              // if both keys are in params, sort them according to paramOrder
              return paramOrder.indexOf(a) - paramOrder.indexOf(b);
            }
            // else sort them according to main order
            return order.indexOf(a) - order.indexOf(b);
          },
        });
        setDefaultYaml(generatedYaml);
        setYaml("\nrows: 100");
      })
      .catch(error => {
        // Handle error
        if (error.response && error.response.data && error.response.data.error) {
          const errorMessage = error.response.data.error;
          // Update the state to store the error message
          setErrorMessage(errorMessage);
        } else {
          // console.log(error);
        }
      });
    // }
  }, [selectedDatasource, selectedReportType, refreshCount]);




  const loadExample = () => {
    setYaml(exampleYaml);
  };


  const handleSubmit = (event) => {
    event.preventDefault();
      // Clear the error message
    setErrorMessage("");

    // Indicate that the data is being processed
    setLoading(true);

    api.post('/generate_edited', {
      defaultYaml: defaultYaml,
      yaml: yaml,
      tableName: tableName,
      dataSource: selectedDatasource,
      reportType: selectedReportType,
    })
    .then(response => {
      // The operation was successful, you can now stop the loading
      setLoading(false);

      const queryFromYaml = response.data.query_from_yaml;
      const yamlStringWithTableName = response.data.yaml_string_with_table_name;

      // Update table name
      const newTableName = response.data.parsed_yaml.tableName;
      setTableName(newTableName);

      // Now, set the generated data
      setGeneratedQuery(queryFromYaml);
      setGeneratedYaml(yamlStringWithTableName);
    })
    .catch(error => {
      setLoading(false);
      // Handle error
      if (error.response && error.response.data && error.response.data.error) {
        const errorMessage = error.response.data.error;
        // Update the state to store the error message
        setErrorMessage(errorMessage);
      } else {
        // console.log(error);
      }
    });
  };


  const clearInput = () => {
    setYaml("");
    setDefaultYaml("");
    setTableName("");
    setErrorMessage("");
    setGeneratedQuery("");
    setGeneratedYaml("");
    refreshData();
    setSelectedDatasource("");
    setSelectedReportType("");
  };



  return (
    <ThemeProvider theme={defaultTheme}>
      <Container component="main" maxWidth="sm">
        <CssBaseline />
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
            <StorageIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Dummy Data Generator
          </Typography>
          <Box component="form" noValidate onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                  <FormControl variant="outlined" fullWidth required>
                    <InputLabel id="datasource-label">Data Source</InputLabel>
                    <Select
                      labelId="datasource-label"
                      id="dataSource"
                      value={selectedDatasource}
                      onChange={e => {
                        setSelectedDatasource(e.target.value);

                      }}
                      label="Data Source" // This is required for outlined variant
                    >
                      {datasources.map((datasource, index) => (
                        <MenuItem key={index} value={datasource}>{datasource}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                  <FormControl variant="outlined" fullWidth required>
                    <InputLabel id="reportType-label">Report Type</InputLabel>
                    <Select
                      labelId="reportType-label"
                      id="reportType"
                      value={selectedReportType}
                      onChange={e => {
                        setSelectedReportType(e.target.value);

                      }}
                      label="Report Type" // This is required for outlined variant
                    >
                      {reportTypes.map((reportType, index) => (
                        <MenuItem key={index} value={reportType}>{reportType}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
              </Grid>
              <Grid item xs={12} sx={{ mt: 3 }}>
                <TextField
                  required
                  fullWidth
                  id="yaml"
                  label="Add Generated Table Params YML"
                  name="yaml"
                  autoComplete="yaml"
                  multiline
                  value={yaml}
                  onChange={e => setYaml(e.target.value)}
                  rows={4}
                  inputProps={{
                      style: {
                          resize: "both",
                          minHeight: "50px",
                          minWidth: "500px",
                          maxWidth: "800px"
                      }
                  }}
              />
              </Grid>
              <Grid item xs={12}>
              <Typography color="error">{ErrorMessage}</Typography>
              </Grid>
            </Grid>
            <Grid container spacing={2} justifyContent="space-between">
              <Grid item xs={6} sm={4} sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                <Button
                  type="button"
                  onClick={loadExample}
                >
                  Load Example
                </Button>
              </Grid>
              <Grid item xs={6} sm={4} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  type="button"
                  onClick={clearInput}
                >
                  Clear Input
                </Button>
              </Grid>
            </Grid>
            <GenerateDatasetButton loading={loading} />
          </Box>
          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-start' }}>
            {generatedQuery &&
              <Button
                size="small"
                color="secondary"
                sx={{ fontSize: 10 }}
                onClick={(event) => {
                  setQueryPopoverOpen(true);
                  setQueryPopoverAnchor(event.currentTarget);
                }}
              >
                Show ClickHouse Query
              </Button>
            }
            <Popover
              open={queryPopoverOpen}
              anchorEl={queryPopoverAnchor}
              onClose={() => setQueryPopoverOpen(false)}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
            >
              <Paper sx={{ padding: 2, maxWidth: 800, wordWrap: 'break-word' }}>
                <Typography sx={{ whiteSpace: 'pre-wrap' }}>{generatedQuery}</Typography>
              </Paper>
            </Popover>

          </Grid>
          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-start' }}>
            {generatedYaml &&
              <Button
                size="small"
                color="secondary"
                sx={{ fontSize: 10 }}
                onClick={(event) => {
                  setYamlPopoverOpen(true);
                  setYamlPopoverAnchor(event.currentTarget);
                }}
              >
                Show Generated Params Yml
              </Button>
            }
            <Popover
              open={YamlPopoverOpen}
              anchorEl={YamlPopoverAnchor}
              onClose={() => setYamlPopoverOpen(false)}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
            >
              <Paper sx={{ padding: 2, maxWidth: 800, wordWrap: 'break-word' }}>
                <Typography sx={{ whiteSpace: 'pre-wrap' }}>{generatedYaml}</Typography>
              </Paper>
            </Popover>
          </Grid>
          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-start' }}>
            {tableName &&
              <Button
                size="small"
                color="secondary"
                sx={{ fontSize: 10 }}
                onClick={(event) => {
                  setTableNamePopoverOpen(true);
                  setTableNamePopoverAnchor(event.currentTarget);
                }}
              >
                Show Table Name
              </Button>
            }
            <Popover
              open={TableNamePopoverOpen}
              anchorEl={TableNamePopoverAnchor}
              onClose={() => setTableNamePopoverOpen(false)}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
            >
              <Paper sx={{ padding: 2, maxWidth: 800, wordWrap: 'break-word' }}>
                <Typography sx={{ whiteSpace: 'pre-wrap' }}>{tableName}</Typography>
              </Paper>
            </Popover>
          </Grid>
          <Grid container spacing={2} justifyContent="space-between">
            <Grid item xs={12} mt={4} sx={{ display: 'flex', justifyContent: 'flex-start' }}>
              <Link
                component="button"
                variant="body2"
                onClick={(event) => {
                  setReadmePopoverOpen(true);
                  setReadmePopoverAnchor(event.currentTarget);
                }}
              >
                Readme
              </Link>
              <Popover
                open={readmePopoverOpen}
                anchorEl={readmePopoverAnchor}
                onClose={() => setReadmePopoverOpen(false)}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'left',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'left',
                }}
              >
                <Paper sx={{ padding: 2, maxWidth: 1600, wordWrap: 'break-word' }}>
                  <iframe src="https://docs.google.com/document/d/1GLDGNLwdek5VjCJex_eHOVcy6ZGAq6svaLoGIPnLYCE/edit?usp=sharing" width="1000" height="600"></iframe>
                </Paper>
              </Popover>

            </Grid>
          </Grid>


        </Box>
        <Copyright sx={{ mt: 5, mb: 5 }} />
      </Container>
    </ThemeProvider>
  );
}
