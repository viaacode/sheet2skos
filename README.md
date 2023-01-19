# Introduction

The code in this repository generates a minimal [SKOS](https://www.w3.org/TR/2009/REC-skos-reference-20090818/) file (in [Turtle](https://www.w3.org/TR/turtle/) format) from a template in a single CSV file or one (or more) Google sheets in a Google workbook.
It is mainly based on [SPARQL Anything](https://github.com/SPARQL-Anything/sparql.anything).

The Google workbook that contains meemoo's SKOS templates is available [here](https://docs.google.com/spreadsheets/d/12I_Qmh3-uIlc4nOd142HI8lvjRfVjNoYwGmvxGIxHcM).
Note, however, that it is only accessible to meemoo employees.
More information about the template as such is available in the next section.

The script uses the [gspread](https://github.com/burnash/gspread) Python package to connect to Google Sheets.
See [this link](https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id) for more information about configuring OAuth credentials.

The repository contains the following files:

- `sheet2skos.py`: the main script of this repository.
More information about its usage is included in the section "Usage" below.
- `queries.py`: this file contains the SPARQL Anything query that is used to transform the CSV to Turtle.
It contains a placeholder `{ont_iri_placeholder}` that is matched via the `uri_dict.json` file to use the correct base URI for the different terms.
The query assumes that terms that do not have a `skos:broader` property, are also top concepts of the concept scheme.
Finally, the query assumes a number of terms are required to be filled in (cf. section below).
- `uri_dict.json`: this file contains a number of key-value pairs, in which the keys represent the name of the thesaurus and the values represent the different thesauri URIs to use as a base for the different terms.
If nothing matches, a default URI (`<https://data.hetarchief.be/id/default>`) is used as a base.
- `test/test.csv`: a CSV file that uses the SKOS template to construct a thesaurus about events.
It is meant for test usage of the CSV functionality.
- `test/test_transformatie_thesaurus.ttl`: a Turtle file that contains the output of the transformation of the `test.csv` file. It is meant for test usage as a sort of 'reference output' after transforming the `test.csv` file. 
- `blanco_template.csv`: an empty version of the SKOS template that is described in the next section.

# SKOS template

The SKOS template contains a number of columns that match various terms from the SKOS ontology.
The columns are described in the table below.

A number of terms are required by the SPARQL query; this is reflected in the cardinality column of the table.

Other terms can occur multiple times; this means that a single cell of the template can contain multiple values.
In that case, these values must be separated by a semicolon.

Column name | Description | SKOS term | Cardinality
:--|:--|:--|:--
concept_benaming|This column should contain the ID that is appended to the base URI to form the unique URI of the term in the thesaurus.|`skos:Concept`|1..1|
voorkeursbenaming_en|This column contains the preferred label of the term in English.|`skos:prefLabel@en`|1..1|
voorkeursbenaming_fr|This column contains the preferred label of the term in French.|`skos:prefLabel@fr`|1..1|
voorkeursbenaming_nl|This column contains the preferred label of the term in Dutch.|`skos:prefLabel@nl`|1..1|
definitie_en|This column contains a succinct definition of the term in English.|`skos:definition@en`|1..1|
definitie_fr|This column contains a succinct definition of the term in French.|`skos:definition@fr`|1..1|
definitie_nl|This column contains a succinct definition of the term in Dutch.|`skos:definition@nl`|1..1|
alternatieve_benaming_en|This column can contain one or more alternative labels of the term in English.|`skos:altLabel@en`|0..*|
alternatieve_benaming_fr|This column can contain one or more alternative labels of the term in French.|`skos:altLabel@fr`|0..*|
alternatieve_benaming_nl|This column can contain one or more alternative labels of the term in Dutch.|`skos:altLabel@nl`|0..*|
heeft_algemener_concept|This column indicates whether the current concept has another related concept that is broader in meaning within the same concept scheme. The value of this column should be the value from the `concept_benaming` column, since it results in a unique URI of the concept.|`skos:broader`|0..*|
heeft_specifieker_concept|This column indicates whether the current concept has another related concept that is more specific in meaning within the same concept scheme. The value of this column should be the value from the `concept_benaming` column, since it results in a unique URI of the concept.|`skos:narrower`|0..*|
heeft_gerelateerd_concept|This column indicates whether the current concept has another related concept within the same concept scheme. The value of this column should be the value from the `concept_benaming` column, since it results in a unique URI of the concept.|`skos:related`|0..*|
voorbeeld_en|This column can contain one or more examples of the term in English.|`skos:example@en`|0..*|
voorbeeld_fr|This column can contain one or more examples of the term in French.|`skos:example@fr`|0..*|
voorbeeld_nl|This column can contain one or more examples of the term in Dutch.|`skos:example@nl`|0..*|

# Usage

```bash
usage: sheet2skos.py [-h] 
                     [--saJAR Sparql Anything JAR file]
                     [--out output directory]
                     [--mode input mode]
                     [--creds Google Sheets client secret]
                     [--sheet_name Google Sheets SKOS template sheet name] 
                     [--thes_names SKOS thesauri names] [--input_file CSV input file]
                     --uri_json JSON with thesauri URIs
```

## Example usage of the CSV functionality

Example commando for usage with the `test.csv` file provided in this repository.
Since `test_transformatie` is not an actual key in the `uri_dict.json`, the default base URI will be used.

```bash
python ./sheet2skos.py --saJAR ../../Documents/sparql_anything/sparql-anything-0.8.1.jar --thes_names "test_transformatie" --uri_json ./uri_dict.json --mode "csv" --input_file ./test/test.csv
```

## Example usage of the Google Sheets functionality

Example commando for usage with Google Sheets.
In this case, the name of the workbook is "skos_thesauri_meemoo" and three tabs/sheets are given to be transformed to SKOS in Turtle format: `events`, `test_transformatie` and `events2`.
Since `events2` is not an actual existing sheet, the script will skip it and only transform the other 2 sheets.
Since `test_transformatie` is not an actual key in the `uri_dict.json`, the default base URI will be used.

```bash
python ./sheet2skos.py --saJAR ../../Documents/sparql_anything/sparql-anything-0.8.1.jar --creds ./client_secret_sheet2skos.json --sheet_name "skos_thesauri_meemoo" --thes_names "events;test_transformatie;events2" --uri_json ./uri_dict.json
```

## Arguments

|Option|Default|Description|Required?|
| :--- | :--- | :--- | :--- |
|`-h`, `--help`||show this help message and exit|False|
|`--saJAR`||Location of the Sparql Anything JAR file; if not specified, the script will download the latest version to './'.|False|
|`--out`|`./skos_thesauri`|Output directory for Turtle files, default is './skos_thesauri'.|False|
|`--mode`|`"google_sheet"`|Input mode; options include 'csv' or 'google_sheet'; default is 'google_sheet' which requires credentials via the '--creds' argument.|False|
|`--creds`||The location of the client secret needed for authentication with mode 'google_sheet'.|True, with mode 'google_sheet'|
|`--wb_name`||The name of the Google workbook that contains the SKOS template(s).|True, with mode 'google_sheet'|
|`--thes_names`||The name of the thesaurus to be transformed. This name is also used to retrieve the relevant ontology URI from the JSON file. In the case of mode 'google_sheet', this can be multiple thesauri names corresponding to tabs from the sheet. In that case the multiple names must be separated by a semicolon without the use of whitespace and surrounded by quotes.|True|
|`--input_file`||The location of the input in the case of a CSV file.|True, with mode 'csv'|
|`--uri_json`|`./uri_dict.json`|The location of a JSON that contains the ontology URI for different thesauri names.|True|
