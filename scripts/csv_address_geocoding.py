#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  csv_address_geocoding.py
#
#         USAGE:  ./scripts/csv_address_geocoding.py
#                 ./scripts/csv_address_geocoding.py --help
#
#   DESCRIPTION:  (RASCUNHO, não finalizado)
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#                   - pip install geopy
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.12.0
#       CREATED:  2023-04-13 22:14 BRT
#      REVISION:  ---
# ==============================================================================


import argparse
import csv
import json
import os
import sys
from typing import Union

from geopy.geocoders import Nominatim

__VERSION__ = "0.2.0"

USER_AGENT = os.getenv("USER_AGENT", "csv_address_geocoding.py/" + __VERSION__)
USER_AGENT_LANG = os.getenv("USER_AGENT_LANG", "pt")


PROGRAM = "csv_address_geocoding"
DESCRIPTION = """
------------------------------------------------------------------------------
CSV 2 CSV online address geocoding

(RASCUNHO, não finalizado)

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
    {0} --mode='inline2debug' --v-postalcode=88015600 -

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
            # required=True,
            nargs="?",
        )

        parser.add_argument(
            "--lon",
            help="the name of the longitude column",
            dest="lon",
            # required=True,
            nargs="?",
        )

        parser.add_argument(
            "--contain-or",
            help="If defined, only results that match at least one clause"
            " will appear on output. Accept multiple values."
            "--contain-or=tag1=value1 --contain-or=tag2=value2",
            dest="contain_or",
            nargs="?",
            action="append",
        )

        parser.add_argument(
            "--contain-and",
            help="If defined, only results that match all clauses"
            " will appear on output. Accept multiple values."
            "--contain-and=tag1=value1 --contain-and=tag2=value2",
            dest="contain_and",
            nargs="?",
            action="append",
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
            "--q",
            help="(inline mode only) raw query",
            dest="q",
            default=None,
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--v-postalcode",
            help="postalcode value",
            dest="v_postalcode",
            default=None,
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--v-country",
            help="country value",
            dest="v_country",
            default=None,
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--v-state",
            help="state value",
            dest="v_state",
            default=None,
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--v-street",
            help="street value (equivalent: <housenumber> <streetname>)",
            dest="v_street",
            default=None,
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--v-housenumber",
            help="housenumber value",
            dest="v_housenumber",
            default=None,
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--v-streetname",
            help="streetname value",
            dest="v_streetname",
            default=None,
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--mode",
            help="Change the operation mode",
            dest="mode",
            default="csv2csv",
            # geojsom
            # geojsonl
            choices=[
                "csv2csv",
                "inline2debug",
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

        _contain_or = {}
        _contain_and = {}
        if pyargs.contain_or:
            for item in pyargs.contain_or:
                if item:
                    if item.find("="):
                        _key, _val = item.split("=")
                        _contain_or[_key] = _val
                    else:
                        _contain_or[_key] = True

        if pyargs.contain_and:
            for item in pyargs.contain_and:
                if item:
                    if item.find("="):
                        _key, _val = item.split("=")
                        _contain_and[_key] = _val
                    else:
                        _contain_and[_key] = True

        if pyargs.mode == "inline2debug":
            if pyargs.q and len(pyargs.q):
                query_params = pyargs.q
            else:
                query_params = {}
                if pyargs.v_postalcode:
                    query_params["postalcode"] = pyargs.v_postalcode
                if pyargs.v_country:
                    query_params["country"] = pyargs.v_country
                if pyargs.v_state:
                    query_params["state"] = pyargs.v_state

                if pyargs.v_street:
                    query_params["street"] = pyargs.v_state

                if pyargs.v_housenumber:
                    query_params["housenumber"] = pyargs.v_housenumber

                if pyargs.v_streetname:
                    query_params["streetname"] = pyargs.v_streetname

                # if pyargs.v_county:
                #     query_params["county"] = pyargs.v_county

            # query_params = "175 5th Avenue NYC"
            query_params = {"postalcode": "88015600"}
            result = geocoding_item(query_params)
            print(json.dumps(result, ensure_ascii=False))
            # TODO: continue
            return self.EXIT_OK
        else:
            raise NotImplemented

        with open(pyargs.input, "r", encoding=pyargs.encoding) if len(
            pyargs.input
        ) > 1 else sys.stdin as csvfile:
            reader = csv.DictReader(csvfile, delimiter=pyargs.delimiter)

            if pyargs.outfmt == "GeoJSON":
                print('{"type": "FeatureCollection", "features": [')

            prepend = ""

            for row in reader:
                item = geojson_item(
                    row,
                    pyargs.lat,
                    pyargs.lon,
                    contain_or=_contain_or,
                    contain_and=_contain_and,
                    ignore_warnings=pyargs.ignore_warnings,
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


def geocoding_item(query_params: Union[dict, str]):
    # geolocator = Nominatim(user_agent="specify_your_app_name_here")
    geolocator = Nominatim(user_agent=USER_AGENT)

    # query_params = "175 5th Avenue NYC"

    location = geolocator.geocode(query_params)

    return location.raw

    # print(location.address)

    # sys.exit()
    pass


def geojson_item(
    row,
    lat,
    lon,
    contain_or: list = None,
    contain_and: list = None,
    ignore_warnings: bool = False,
):
    _lat = row[lat] if lat in row and len(row[lat].strip()) else False
    _lon = row[lon] if lon in row and len(row[lon].strip()) else False

    if not geojson_item_contain(row, contain_or=contain_or, contain_and=contain_and):
        return False

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


def geojson_item_contain(
    item, contain_or: list = None, contain_and: list = None
) -> bool:
    if not item:
        return False

    if not contain_or and not contain_and:
        return True

    if contain_and:
        _count = len(contain_and.keys())

        for _key, _val in contain_and.items():
            if _key not in item:
                raise SyntaxError(f"key {_key} not in {item}")
                # return False

            if _val is not True and _val != item[_key]:
                return False
            _count -= 1

        if _count > 0:
            return False

    for _key, _val in contain_or.items():
        if _key not in item:
            raise SyntaxError(f"key {_key} not in {item}")
            # return False

        if _val is not True and _val != item[_key]:
            return False

    return True


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
