import argparse
from clint.textui import progress
import gspread
import json
import os
import pandas as pd
import requests
import subprocess
import tempfile
import skosify

MAPPING = open("mapping.rq", "r")

def google_config(creds_file, wb_name):
    gc = gspread.oauth(
        credentials_filename=creds_file,
    )
    wb = gc.open(wb_name)
    worksheet_list = wb.worksheets()
    worksheet_names = []
    for worksheet in worksheet_list:
        worksheet_names.append(worksheet.title)
    worksheet_names = [
        worksheet_name
        for worksheet_name in worksheet_names
        if worksheet_name
        not in ["uitleg_template_termen", "template_mapping", "blanco_template"]
    ]
    return wb, worksheet_names


def update_mapping(uri_json, thes_name, pref_label):
    with open(uri_json, "r") as json_uri_file:
        uri_dict = json.load(json_uri_file)
        if thes_name in uri_dict:
            sa_mapping = MAPPING.replace(
                "{ont_iri_placeholder}", f'"{uri_dict[thes_name]}"'
            )
            sa_mapping = sa_mapping.replace(
                "{pref_label_placeholder}", f'"{pref_label}"'
            )
        else:
            print(
                f"Key '{thes_name}' was not found in '{uri_json}'; using default URI 'https://data.hetarchief.be/id/default'"
            )
            sa_mapping = MAPPING.replace(
                "{ont_iri_placeholder}", '"https://data.hetarchief.be/id/default"'
            )
            sa_mapping = sa_mapping.replace(
                "{pref_label_placeholder}", f'"{pref_label}"'
            )
        return sa_mapping


def transform(sa_jar, sa_mapping, filename):
    output = subprocess.run(
        [
            "java",
            "-jar",
            sa_jar,
            "-q",
            sa_mapping,
            "-v",
            f"file={filename}",
            "-v",
            f"scheme=",
            

        ],
        capture_output=True,
        check=True,
        universal_newlines=True,
    )
    return output


def write_temp(df):
    tmpfile = tempfile.NamedTemporaryFile()
    with open(tmpfile.name, "w") as f:
        f.write(df.to_csv(header=True, index=False))
    return tmpfile


def write_output(args, output, output_fname):
    try:
        os.makedirs(args.out)
    except FileExistsError:
        pass
    with open(f"{args.out}/{output_fname}_thesaurus.ttl", "w") as output_f:
        output_f.write(output.stdout)
        return output_f.name


def csv_func(args):
    print(f"Now transforming '{args.thes_names}'-sheet to SKOS in ttl-format")
    sa_mapping = update_mapping(
        uri_json=args.uri_json, thes_name=args.thes_names, pref_label=args.pref_label
    )
    output = transform(
        sa_jar=args.saJAR, sa_mapping=sa_mapping, filename=args.input_file
    )
    output_fname = write_output(args=args, output=output, output_fname=args.thes_names)
    print(
        f"Finished transforming '{args.thes_names}'; output was written to '{output_fname}'"
    )

    voc = skosify.skosify(output_fname, default_language="nl")
    voc.serialize(destination=output_fname, format='turtle')
    print(
        f"Applied skosify '{args.thes_names}'; output was written to '{output_fname}'"
    )


def sheet_func(args):
    sheet, thes_list = google_config(creds_file=args.creds, wb_name=args.wb_name)
    thes_names = args.thes_names.split(";")
    for i in range(len(thes_names)):
        if " " in thes_names[i]:
            thes_names[i] = thes_names[i].strip()
    for thes in thes_names:
        print(f"Now transforming '{thes}'-sheet to SKOS in ttl-format")
        if thes not in thes_list:
            print(
                f"Sheet '{thes}' was not found in the workbook '{args.wb_name}'. Check for a spelling mistake and rerun the script to generate this thesaurus."
            )
            continue
        sheet_pref_label = str(
            input(
                f"Please enter a `skos:prefLabel` for the {thes}-sheet concept scheme: "
            )
        )
        dataframe = pd.DataFrame(sheet.worksheet(thes).get_all_records())
        tmpfile = write_temp(df=dataframe)
        sa_mapping = update_mapping(
            uri_json=args.uri_json, thes_name=thes, pref_label=sheet_pref_label
        )
        output = transform(
            sa_jar=args.saJAR, sa_mapping=sa_mapping, filename=tmpfile.name
        )
        output_fname = write_output(args=args, output=output, output_fname=thes)
        print(f"Finished transforming '{thes}'; output was written to '{output_fname}'")


def main(args):
    if not os.path.isfile(args.saJAR):
        print(
            "Sparql Anything JAR was not provided; preparing to download sparql-anything-v1.0.0.jar to './sparql-anything-v1.0.0.jar'"
        )
        r = requests.get(
            "https://github.com/SPARQL-Anything/sparql.anything/releases/download/v1.0.0/sparql-anything-v1.0.0.jar"
        )
        with open("./sparql-anything-v1.0.0.jar", "wb") as f:
            total_length = int(r.headers.get("content-length"))
            for chunk in progress.bar(
                r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1
            ):
                if chunk:
                    f.write(chunk)
                    f.flush()
        args.saJAR = "./sparql-anything-v1.0.0.jar"
        print("Finished downloading Sparql Anything.")

    if args.mode == "csv":
        csv_func(args=args)
    elif args.mode == "google_sheet":
        sheet_func(args=args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--saJAR",
        metavar="Sparql Anything JAR file",
        required=False,
        help="Location of the Sparql Anything JAR file; if not specified, the script will download the latest version to './'.",
    )
    parser.add_argument(
        "--out",
        metavar="output directory",
        type=str,
        default="./skos_thesauri",
        required=False,
        help="Output directory for Turtle files, default is './skos_thesauri'.",
    )
    parser.add_argument(
        "--mode",
        metavar="input mode",
        type=str,
        default="google_sheet",
        choices=["google_sheet", "csv"],
        help="Input mode; options include 'csv' or 'google_sheet'; default is 'google_sheet' which requires credentials via the '--creds' argument.",
    )
    parser.add_argument(
        "--creds",
        metavar="Google Sheets client secret",
        type=str,
        required=False,
        help="The location of the client secret needed for authentication with mode 'google_sheet'.",
    )
    parser.add_argument(
        "--wb_name",
        metavar="Google Sheets SKOS template workbook name",
        type=str,
        required=False,
        help="The name of the Google workbook that contains the SKOS template(s).",
    )
    parser.add_argument(
        "--thes_names",
        metavar="SKOS thesauri names",
        type=str,
        required=True,
        help="The name of the thesaurus to be transformed. This name is also used to retrieve the relevant ontology URI from the JSON file. In the case of mode 'google_sheet', this can be multiple thesauri names corresponding to tabs from the sheet. In that case the multiple names must be separated by a semicolon without the use of whitespace and surrounded by quotes.",
    )
    parser.add_argument(
        "--pref_label",
        metavar="Concept scheme skos:prefLabel",
        type=str,
        required=False,
        help="The `skos:prefLabel` for the concept scheme that is being transformed. This parameter is only required in the case of a CSV file.",
    )
    parser.add_argument(
        "--input_file",
        metavar="CSV input file",
        type=str,
        required=False,
        help="The location of the input in the case of a CSV file.",
    )
    parser.add_argument(
        "--uri_json",
        metavar="JSON with thesauri URIs",
        type=str,
        default="./uri_dict.json",
        required=True,
        help="The location of a JSON that contains the ontology URI for different thesauri names.",
    )

    args_dict = vars(parser.parse_args())
    if args_dict["mode"] == "google_sheet" and (
        not (args_dict["creds"])
        or args_dict["creds"] == None
        or not os.path.isfile(args_dict["creds"])
    ):
        exit(
            "Mode 'google_sheet' was used but no credentials were given. Script will exit."
        )
    if args_dict["mode"] == "google_sheet" and (
        not (args_dict["thes_names"]) or args_dict["thes_names"] == None
    ):
        exit(
            "Mode 'google_sheet' was used but no tabs were specified. Script will exit."
        )
    if args_dict["mode"] == "google_sheet" and (
        not (args_dict["wb_name"]) or args_dict["wb_name"] == None
    ):
        exit(
            "Mode 'google_sheet' was used but no sheet name was specified. Script will exit."
        )
    if args_dict["mode"] == "csv" and (
        not (args_dict["input_file"])
        or args_dict["input_file"] == None
        or not os.path.isfile(args_dict["input_file"])
    ):
        exit("Mode 'csv' was used but no input file was given. Script will exit.")
    if args_dict["mode"] == "csv" and (not (args_dict["pref_label"])):
        exit("Mode 'csv' was used but no skos:prefLabel was given. Script will exit.")

    argsv = parser.parse_args()
    main(argsv)
