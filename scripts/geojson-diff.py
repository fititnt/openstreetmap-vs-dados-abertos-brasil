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
#                   - haversine (pip install haversine)
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
import logging

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

MATCH_EXACT = 1
MATCH_NEAR = 3


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

        parser.add_argument("geodataset_a", help="GeoJSON dataset 'A'")
        parser.add_argument("geodataset_b", help="GeoJSON dataset 'B'")

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
            default=None,
            required=False,
            nargs="?",
        )

        return parser.parse_args()

    def execute_cli(self, pyargs, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        if pyargs.outlog:
            fh = logging.FileHandler(pyargs.outlog)
            logger.addHandler(fh)
        else:
            ch = logging.StreamHandler()
            logger.addHandler(ch)

        # input_file = STDIN if pyargs.input == "-" else pyargs.input

        # outlog = pyargs.outlog then

        # print("@TODO")
        print(pyargs)
        logger.info("@TODO")
        logger.critical("@TODO 2")
        geodiff = GeojsonCompare(pyargs.geodataset_a, pyargs.geodataset_b, logger)
        geodiff.debug()
        return self.EXIT_OK


class DatasetInMemory:
    def __init__(self, alias: str) -> None:
        self.alias = alias
        self.index = -1
        self.items = []
        pass

    def add_item(self, item: dict):
        self.index += 1
        self.items.append(None)

        if (
            not item
            or "geometry" not in item
            or "coordinates" not in item["geometry"]
            or "type" not in item
        ):
            # Really bad input item
            self.items.append(False)
        elif item["geometry"]["type"] != "Point":
            # For now ignoring non Point features
            self.items.append(None)
        else:
            coords = (
                item["geometry"]["coordinates"][1],
                item["geometry"]["coordinates"][0],
            )
            props = None
            if (
                "properties" in item
                and item["properties"]
                and len(item["properties"].keys())
            ):
                props = item["properties"]
            self.items.append((coords, props))


class GeojsonCompare:
    """GeojsonCompare

    @TODO optimize for very large files
    """

    def __init__(self, geodataset_a: str, geodataset_b: str, logger) -> None:
        self.a = self._load_geojson(geodataset_a, "A")
        self.b = self._load_geojson(geodataset_b, "B")
        self.matrix = []

        self.compute()
        # pass

    def _load_geojson(self, path, alias) -> DatasetInMemory:
        data = DatasetInMemory(alias)

        with open(path, "r") as file:
            # TODO optimize geojsonl
            jdict = json.load(file)
            for feat in jdict["features"]:
                print(feat)
                data.add_item(feat)

        return data

    def compute(self):
        # for item in self.a.items:
        for index_a in range(0, len(self.a.items) - 1):
            if not self.a.items[index_a]:
                self.matrix.append(self.a.items[index_a])
            else:
                for index_b in range(0, len(self.b.items) - 1):
                    pass
                pass

    def debug(self):
        print(self.a)
        print(self.a.items)
        print(self.b)
        print(self.b.items)
        print(self.matrix)


if __name__ == "__main__":
    cli_2600 = Cli()
    args = cli_2600.make_args()
    # pyargs.print_help()

    # args.execute_cli(args)
    cli_2600.execute_cli(args)
