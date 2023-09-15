export const ReadmeContent = `
Dummy Data Generator Application

The Dummy Data Generator Application allows users to generate dummy data based on their chosen data source and report type. This readme document provides instructions on how to use the application effectively.

Table of Contents:
1. Introduction
2. Usage
   - Choosing a Data Source and Report Type
   - Adding Custom Columns
   - Specifying the Number of Rows
   - Available Generators
3. Examples

Introduction:
The Dummy Data Generator Application allows users to quickly generate dummy data for various purposes, such as testing, prototyping, or data analysis. The application offers a simple interface where users can select a data source and report type, add custom columns with specific parameters, and specify the number of rows to generate.

Usage
Choosing a Data Source and Report Type
To generate dummy data, follow these steps:

1. Open the application and locate the two drop-down menus labeled "Data Source" and "Report Type."
2. In the "Data Source" drop-down menu, select the desired data source from the available options.
3. In the "Report Type" drop-down menu, select the desired report type from the available options.

Adding Custom Columns
The Dummy Data Generator Application allows users to add custom columns to the generated data. To add custom columns, follow these steps:

1. Prepare a YAML structure that defines the custom columns and their parameters. The structure should adhere to the following format:


  - name: [column_name]
    dataType: [data_type]
    generator: [generator_type]
    params:
      [parameter_1]: [value_1]
      [parameter_2]: [value_2]
      ...

2. Copy the YAML structure into the "Add Generated Table Params YML" input field located above the "rows" field.
3. Modify the YAML structure to match your desired column configuration. Ensure that the indentation and parameter syntax are correct.
4. Optionally, repeat the above steps to add more custom columns.

Specifying the Number of Rows
To specify the number of rows to generate, follow these steps:

1. Locate the "rows" field in the application.
2. Enter the desired number of rows in the "rows" field.

Available Generators
The Dummy Data Generator Application supports the following generators:

- increment: Generates a sequence of incrementing numbers starting from the specified start value with a step of the specified value.
- random: Generates a random string of the specified length.
- email: Generates a random email address.
- date: Generates a random date in the format specified by the params.format parameter.
- range: Generates a random integer between the specified minimum and maximum values.
- default: Takes the same default value for each row.
- dictionary: Generates a random value from a specified data dictionary. The dictionary name is specified by the params.dictionary_type parameter. Available dictionary types include:
  - countries
  - customers
  - companies
Refer to the Examples section for sample usage of these generators.

Examples
Here are a few examples to demonstrate the usage of the Dummy Data Generator Application:

1. Generating basic dummy data:
yaml
Copy code
  - name: users
    dataType: string
    generator: dictionary
    params:
      dictionary_type: customers
  - name: page_views
    dataType: int
    generator: range
    params:
      min: 1
      max: 10000
rows: 100

2. Adding custom columns with specific parameters:
yaml
Copy code
  - name: users
    dataType: string
    generator: dictionary
    params:
      dictionary_type: customers
  - name: new_users
    dataType: int
    generator: range
    params:
      min: 1
      max: 10000
  - name: interest_affinity_category
    dataType: string
    generator: random
    params:
      length: 10
rows: 100

3. Generating dummy data with a specified date format:
yaml
Copy code
  - name: users
    dataType: string
    generator: dictionary
    params:
      dictionary_type: customers
  - name: date_registered
    dataType: date
    generator: date
    params:
      format: YYYY-MM-DD
rows: 100

Feel free to experiment with different column configurations and generators to suit your specific requirements.
`
