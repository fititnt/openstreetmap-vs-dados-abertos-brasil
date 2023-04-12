#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  csv2geojson.py
#
#         USAGE:  ./scripts/csv2geojson.py
#                 ./scripts/csv2geojson.py --help
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#                   - pip install osmium
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v1.0.0
#       CREATED:  2023-04-11 18:13 BRT
#      REVISION:  ---
# ==============================================================================


# import geopandas
# import os
import argparse
import csv
import json
import sys


PROGRAM = "csv2geojson"
DESCRIPTION = """
------------------------------------------------------------------------------
CSV to GeoJSOM

------------------------------------------------------------------------------
""".format(
    __file__
)

# https://www.rfc-editor.org/rfc/rfc7946
# The GeoJSON Format
# https://www.rfc-editor.org/rfc/rfc8142
# GeoJSON Text Sequences

# __EPILOGUM__ = ""
__EPILOGUM__ = """
------------------------------------------------------------------------------
                            EXEMPLŌRUM GRATIĀ
------------------------------------------------------------------------------
File on disk . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

    {0} --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' \
--encoding='latin-1' data/tmp/DATASUS-tbEstabelecimento.csv

STDIN . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
(Note the "-" at the end)
    head data/tmp/DATASUS-tbEstabelecimento.csv | \
{0} --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' -


(With jq to format output)
    head data/tmp/DATASUS-tbEstabelecimento.csv | \
{0} --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' \
--ignore-warnings - | jq

GeoJSONSeq . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    head data/tmp/DATASUS-tbEstabelecimento.csv | \
{0} --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' \
--output-type=GeoJSONSeq --ignore-warnings -

    head data/tmp/DATASUS-tbEstabelecimento.csv | \
{0} --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' \
--output-type=GeoJSONSeq --ignore-warnings - \
> data/tmp/DATASUS-tbEstabelecimento-head.geojsonl

GeoJSONSec -> Geopackage . . . . . . . . . . . . . . . . . . . . . . . . . . .
    {0} --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' \
--output-type=GeoJSONSeq --ignore-warnings \
data/tmp/DATASUS-tbEstabelecimento.csv \
> data/tmp/DATASUS-tbEstabelecimento.geojsonl

    ogr2ogr -f GPKG data/tmp/DATASUS-tbEstabelecimento.gpkg \
data/tmp/DATASUS-tbEstabelecimento.geojsonl
------------------------------------------------------------------------------
                            EXEMPLŌRUM GRATIĀ
------------------------------------------------------------------------------
""".format(
    __file__
)

STDIN = sys.stdin.buffer


class Cli:
    """Main CLI parser"""

    def __init__(self):
        """
        Constructs all the necessary attributes for the Cli object.
        """
        self.pyargs = None
        self.EXIT_OK = 0
        self.EXIT_ERROR = 1
        self.EXIT_SYNTAX = 2

    def make_args(self):
        """make_args

        Args:
            hxl_output (bool, optional): _description_. Defaults to True.
        """
        parser = argparse.ArgumentParser(
            prog=PROGRAM,
            description=DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__EPILOGUM__,
        )

        parser.add_argument("input", help="path to CSV file on disk. Use - for stdin")

        parser.add_argument(
            "--lat",
            help="the name of the latitude column",
            dest="lat",
            required=True,
            nargs="?",
        )

        parser.add_argument(
            "--lon",
            help="the name of the longitude column",
            dest="lon",
            required=True,
            nargs="?",
        )

        parser.add_argument(
            "--delimiter",
            help="the type of delimiter",
            dest="delimiter",
            default=",",
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--encoding",
            help="the type of delimiter",
            dest="encoding",
            default="utf-8",
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--output-type",
            help="Change the default output type",
            dest="outfmt",
            default="GeoJSON",
            # geojsom
            # geojsonl
            choices=[
                "GeoJSON",
                "GeoJSONSeq",
            ],
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--ignore-warnings",
            help="Ignore some errors (such as empty latitude/longitude values)",
            dest="ignore_warnings",
            action="store_true",
        )

        return parser.parse_args()

    def execute_cli(self, pyargs, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
        # input_file = STDIN if pyargs.input == "-" else pyargs.input

        # @TODO finish this MVP
        with open(pyargs.input, "r", encoding=pyargs.encoding) if len(
            pyargs.input
        ) > 1 else sys.stdin as csvfile:
            reader = csv.DictReader(csvfile, delimiter=pyargs.delimiter)

            if pyargs.outfmt == "GeoJSON":
                print('{"type": "FeatureCollection", "features": [')

            prepend = ""

            for row in reader:
                item = geojson_item(
                    row, pyargs.lat, pyargs.lon, ignore_warnings=pyargs.ignore_warnings
                )
                if not item:
                    continue

                jsonstr = json.dumps(item, ensure_ascii=False)

                # https://www.rfc-editor.org/rfc/rfc8142
                if pyargs.outfmt == "GeoJSONSeq":
                    print(f"\x1e{jsonstr}\n", sep="", end="")
                    continue

                print(f"{prepend} {jsonstr}")
                if prepend == "":
                    prepend = ","

            if pyargs.outfmt == "GeoJSON":
                print("]}")

        return self.EXIT_OK


def geojson_item(row, lat, lon, ignore_warnings: bool = False):
    _lat = row[lat] if lat in row and len(row[lat].strip()) else False
    _lon = row[lon] if lon in row and len(row[lon].strip()) else False

    if not _lat or not _lon:
        if not ignore_warnings:
            print(f"WARNING LAT/LON NOT FOUND [{row}]", file=sys.stderr)

        return False

    if _lat.find(",") > -1:
        _lat = _lat.replace(",", ".")

    if _lon.find(",") > -1:
        _lon = _lon.replace(",", ".")

    _lat = float(_lat)
    _lon = float(_lon)

    result = {
        "geometry": {"coordinates": [_lon, _lat], "type": "Point"},
        "properties": {},
        "type": "Feature",
    }

    _ignore = [lat, lon]

    result["properties"] = geojsom_item_properties(row, _ignore)

    return result


def geojsom_item_properties(row: dict, ignore: list):
    result = {}

    for key, value in row.items():
        if key in ignore:
            continue

        if not value or len(value.strip()) == 0:
            continue

        result[key] = value

    return result


if __name__ == "__main__":
    cli_2600 = Cli()
    args = cli_2600.make_args()
    # pyargs.print_help()

    # args.execute_cli(args)
    cli_2600.execute_cli(args)
