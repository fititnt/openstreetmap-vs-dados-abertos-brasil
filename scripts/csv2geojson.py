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

        # Near same options as https://github.com/mapbox/csv2geojson
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

        # parser.add_argument(
        #     '--excel',
        #     help='Relative path and extension to the excel file.'
        #     'Defaults to mdciii.xlsx on current directory',
        #     dest='excel',
        #     default='mdciii.xlsx',
        #     nargs='?'
        # )

        return parser.parse_args()

    def execute_cli(self, pyargs, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
        # input_file = STDIN if pyargs.input == "-" else pyargs.input

        # @TODO finish this MVP
        with open(pyargs.input, "r", encoding=pyargs.encoding) if len(
            pyargs.input
        ) > 1 else sys.stdin as csvfile:
            reader = csv.reader(csvfile, delimiter=pyargs.delimiter)
            for row in reader:
                print(row)

        return self.EXIT_OK


def geojson_item(row, lat, lon):
    result = {
        "type": "Feature",
        "geometry": "Feature",
    }
    return "@TODO"


if __name__ == "__main__":
    cli_2600 = Cli()
    args = cli_2600.make_args()
    # pyargs.print_help()

    # args.execute_cli(args)
    cli_2600.execute_cli(args)
