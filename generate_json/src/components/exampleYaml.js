export const exampleYaml = `
// Copy this example as the indentation and naming conventions are crucial. Then clear input to re-generate table params. If no datasource and report type specified, add 'columns:' above the custom YML.

  - name: users_example
    dataType: string
    generator: dictionary
    params:
      dictionary_type: customers

  - name: new_users_example
    dataType: int
    generator: range
    params:
      min: 1
      max: 10000

  - name: interest_affinity_category_example
    dataType: string
    generator: random
    params:
      length: 10

  - name: page_views_example
    dataType: int
    generator: range
    params:
      min: 1
      max: 10000

  - name: sessions_example
    dataType: string
    generator: random
    params:
      length: 10

  - name: bounce_example
    dataType: string
    generator: random
    params:
      length: 10

  - name: date_example
    dataType: date
    generator: date

  - name: datetime_example
    dataType: datetime
    generator: datetime

  - name: users_example_email
    dataType: string
    generator: email

  - name: country
    dataType: string
    generator: fixed
    params:
      value: USA
rows: 100`;
