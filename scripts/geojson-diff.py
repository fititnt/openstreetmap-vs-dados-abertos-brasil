#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  geojson-diff.py
#
#         USAGE:  ./scripts/geojson-diff.py
#                 ./scripts/geojson-diff.py --help
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.2.0
#       CREATED:  2023-04-16 22:36 BRT
#      REVISION:  ---
# ==============================================================================


# import geopandas
# import os
import argparse
import csv
import json
import re
import sys


PROGRAM = "geojson-diff"
DESCRIPTION = """
------------------------------------------------------------------------------
GeoJSON diff

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
    {0} --output-diff=data/tmp/diff-points-ab.geojson \
--output-log=data/tmp/diff-points-ab.log.txt \
tests/data/data-points_a.geojson \
tests/data/data-points_b.geojson

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

        parser.add_argument("data-a", help="GeoJSON dataset 'A'")
        parser.add_argument("data-b", help="GeoJSON dataset 'B'")

        parser.add_argument(
            "--output-diff",
            help="Path to output file",
            dest="outdiff",
            required=True,
            nargs="?",
        )

        parser.add_argument(
            "--output-log",
            help="Path to output file",
            dest="outlog",
            required=False,
            nargs="?",
        )

        # parser.add_argument(
        #     "--lat",
        #     help="the name of the latitude column",
        #     dest="lat",
        #     required=True,
        #     nargs="?",
        # )

        # parser.add_argument(
        #     "--lon",
        #     help="the name of the longitude column",
        #     dest="lon",
        #     required=True,
        #     nargs="?",
        # )

        # parser.add_argument(
        #     "--contain-or",
        #     help="If defined, only results that match at least one clause"
        #     " will appear on output. Accept multiple values."
        #     "--contain-or=tag1=value1 --contain-or=tag2=value2",
        #     dest="contain_or",
        #     nargs="?",
        #     action="append",
        # )

        # parser.add_argument(
        #     "--contain-and",
        #     help="If defined, only results that match all clauses"
        #     " will appear on output. Accept multiple values."
        #     "--contain-and=tag1=value1 --contain-and=tag2=value2",
        #     dest="contain_and",
        #     nargs="?",
        #     action="append",
        # )

        # parser.add_argument(
        #     "--delimiter",
        #     help="the type of delimiter",
        #     dest="delimiter",
        #     default=",",
        #     required=False,
        #     nargs="?",
        # )

        # parser.add_argument(
        #     "--encoding",
        #     help="the type of delimiter",
        #     dest="encoding",
        #     default="utf-8",
        #     required=False,
        #     nargs="?",
        # )

        # parser.add_argument(
        #     "--output-type",
        #     help="Change the default output type",
        #     dest="outfmt",
        #     default="GeoJSON",
        #     # geojsom
        #     # geojsonl
        #     choices=[
        #         "GeoJSON",
        #         "GeoJSONSeq",
        #     ],
        #     required=False,
        #     nargs="?",
        # )

        # parser.add_argument(
        #     "--ignore-warnings",
        #     help="Ignore some errors (such as empty latitude/longitude values)",
        #     dest="ignore_warnings",
        #     action="store_true",
        # )

        # cast_group = parser.add_argument_group(
        #     "Convert/preprocess data from input, including generate new fields"
        # )

        # cast_group.add_argument(
        #     "--cast-integer",
        #     help="Name of input fields to cast to integer. "
        #     "Use | for multiple. "
        #     "Example: <[ --cast-integer='field_a|field_b|field_c' ]>",
        #     dest="cast_integer",
        #     nargs="?",
        #     type=lambda x: x.split("|"),
        #     default=None,
        # )

        # cast_group.add_argument(
        #     "--cast-float",
        #     help="Name of input fields to cast to float. "
        #     "Use | for multiple. "
        #     "Example: <[ --cast-float='latitude|longitude|field_c' ]>",
        #     dest="cast_float",
        #     nargs="?",
        #     type=lambda x: x.split("|"),
        #     default=None,
        # )

        # cast_group.add_argument(
        #     "--column-copy-to",
        #     help="Add extra comluns. "
        #     "For multiple, use multiple times this parameter. "
        #     "Source vs destiny column must be divided by |. "
        #     "Example: <[ --column-copy-to='ORIGINAL_FIELD_PT|name:pt' "
        #     "--column-copy-to='CNPJ|ref:vatin' ]>",
        #     dest="column_copy",
        #     nargs="?",
        #     # type=lambda x: x.split("||"),
        #     action="append",
        #     default=None,
        # )

        # cast_group.add_argument(
        #     "--value-fixed",
        #     help="Define a fixed string for every value of a column, "
        #     "For multiple, use multiple times this parameter. "
        #     "Source vs destiny column must be divided by |. "
        #     "Example: <[ --value-fixed='source|BR:DATASUS' ]>",
        #     dest="value_fixed",
        #     nargs="?",
        #     # type=lambda x: x.split("||"),
        #     action="append",
        #     default=None,
        # )

        # cast_group.add_argument(
        #     "--value-prepend",
        #     help="Prepend a custom string to all values in a column. "
        #     "For multiple, use multiple times this parameter. "
        #     "Source vs destiny column must be divided by |. "
        #     "Example: <[ --value-prepend='ref:vatin|BR' ]>",
        #     dest="value_prepend",
        #     nargs="?",
        #     # type=lambda x: x.split("||"),
        #     action="append",
        #     default=None,
        # )

        # cast_group.add_argument(
        #     "--value-postcode-br",
        #     help="One or more column names to format as if was Brazilan postcodes, CEP",
        #     dest="value_postcode_br",
        #     nargs="?",
        #     type=lambda x: x.split("|"),
        #     default=None,
        # )

        # cast_group.add_argument(
        #     "--value-phone-br",
        #     help="One or more column names to format as Brazilian "
        #     "phone/fax/WhatsApp number",
        #     dest="value_phone_br",
        #     nargs="?",
        #     type=lambda x: x.split("|"),
        #     default=None,
        # )

        return parser.parse_args()

    def execute_cli(self, pyargs, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
        # input_file = STDIN if pyargs.input == "-" else pyargs.input

        # outlog = pyargs.outlog then 


        print("@TODO")
        return self.EXIT_OK


if __name__ == "__main__":
    cli_2600 = Cli()
    args = cli_2600.make_args()
    # pyargs.print_help()

    # args.execute_cli(args)
    cli_2600.execute_cli(args)
