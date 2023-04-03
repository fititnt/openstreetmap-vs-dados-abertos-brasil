#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  govbrasil-ibge_estatisticas.py
#
#         USAGE:  ./scripts/govbrasil-ibge_estatisticas.py
#                 ./scripts/govbrasil-ibge_estatisticas.py --help
#                 USE_PYGEOS=0 ./scripts/govbrasil-ibge_estatisticas.py --help
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
#       CREATED:  2023-04-03 16:27 BRT
#      REVISION:  ---
# ==============================================================================

# ./scripts/govbrasil-ibge_estatisticas.py data/tmp/brasil-uf.osm.pbf > data/tmp/brasil-uf.osm.geojson
# ./scripts/govbrasil-ibge_estatisticas.py data/tmp/brasil-municipios.osm.pbf > data/tmp/brasil-municipios.osm.geojson

import geopandas
import os
import sys
import argparse

# Fix "UserWarning: The Shapely GEOS version ... needs come before geopandas
os.environ['USE_PYGEOS'] = '0'


# from frictionless import Package
# from openpyxl import Workbook


PROGRAM = "govbrasil-ibge_estatisticas"
DESCRIPTION = """
------------------------------------------------------------------------------
The {0} is a simpler wrapper to export frictionless mapped data to Excel.
After 1,048,576 rows it get even faster!

------------------------------------------------------------------------------
""".format(__file__)

__EPILOGUM__ = """
------------------------------------------------------------------------------
                            EXEMPLŌRUM GRATIĀ
------------------------------------------------------------------------------
Quickstart . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    {0} --input-ibge-shapefile='data/ibge/BR_Municipios_2022.shp'
    USE_PYGEOS=0 {0} --input-ibge-shapefile='data/ibge/BR_Municipios_2022.shp'

Validate file with cli . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
(Use this if export does not work for some reason)
    frictionless validate datapackage.json

Create the datapackage.json (requires other tool) . . . . . . . . . . . . . . .
(This command may be outdated eventually)
    ./999999999/0/1603_1.py --methodus='data-apothecae' \
--data-apothecae-ad-stdout --data-apothecae-formato='datapackage' \
--data-apothecae-ex-suffixis='no1.tm.hxl.csv' \
--data-apothecae-ex-praefixis='1603_16,!1603_1_1,!1603_1_51' \
> ./datapackage.json

(same, but now all tables under 1603. Migth run out of memory) . . . . . . . . .
    ./999999999/0/1603_1.py --methodus='data-apothecae' \
--data-apothecae-ad-stdout --data-apothecae-formato='datapackage' \
--data-apothecae-ex-suffixis='no1.tm.hxl.csv' \
--data-apothecae-ex-praefixis='1603' \
> ./datapackage.json

(Use jq to print resources)
    jq .resources[].name < datapackage.json

------------------------------------------------------------------------------
                            EXEMPLŌRUM GRATIĀ
------------------------------------------------------------------------------
""".format(__file__)

STDIN = sys.stdin.buffer


class Cli:
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
            epilog=__EPILOGUM__
        )

        parser.add_argument(
            '--input-ibge-shapefile',
            help='Caminho para o shapefile do IBGE',
            dest='ibge_shp',
            # default='datapackage.json',
            nargs='?'
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

    def execute_cli(
            self, pyargs, stdin=STDIN, stdout=sys.stdout,
            stderr=sys.stderr
    ):
        # frictionless_to_excel(pyargs.datapackage, pyargs.excel)

        ibge_estatisticas(pyargs.ibge_shp)

        # print('unknow option.')
        return self.EXIT_OK


def ibge_estatisticas(path_shapefile: str):
    # gdf_ibge = geopandas.read_file("data/tmp/BR_UF_2022.gpkg")
    gdf_ibge = geopandas.read_file(path_shapefile)

    print(">> resumo IBGE")
    print(gdf_ibge)

    gdf_ibge.to_crs(crs=3857)

    print(gdf_ibge.area)

    for index, row in gdf_ibge.iterrows():
        # print(index, row, row['geometry'].to_crs().area)
        print(index, row, row['geometry'].area)


if __name__ == "__main__":

    cli_2600 = Cli()
    args = cli_2600.make_args()
    cli_2600.execute_cli(args)
