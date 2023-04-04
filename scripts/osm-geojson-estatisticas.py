#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  osm-geojson-estatisticas.py
#
#         USAGE:  ./scripts/osm-geojson-estatisticas.py
#                 ./scripts/osm-geojson-estatisticas.py --help
#                 USE_PYGEOS=0 ./scripts/osm-geojson-estatisticas.py --help
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
#       CREATED:  2023-04-04 12:57 BRT
#      REVISION:  ---
# ==============================================================================


# USE_PYGEOS=0 ./scripts/osm-geojson-estatisticas.py --input-ibge-shapefile='data/ibge/BR_Municipios_2022.shp' --input-ibge-nivel='municipio' > relatorio/_divisao-administrativa-municipio_ibge.csv
# USE_PYGEOS=0 ./scripts/osm-geojson-estatisticas.py --input-ibge-shapefile='data/ibge/BR_UF_2022.shp' --input-ibge-nivel='uf' > relatorio/_divisao-administrativa-uf_ibge.hxl.csv

import geopandas
import os
import sys
import argparse
import csv

# Fix "UserWarning: The Shapely GEOS version ... needs come before geopandas
# os.environ['USE_PYGEOS'] = '0'


PROGRAM = "osm-geojson-estatisticas"
DESCRIPTION = """
------------------------------------------------------------------------------
Gera estatisticas de GeoJSON Text Sequence (RFC8142) tipicos da OpenStreetMap.
Otimizado para arquivos enormes.

Requer arquivo de entrada já estar salvo em disco, pois le o arquivo duas
vezes.

------------------------------------------------------------------------------
""".format(__file__)

__EPILOGUM__ = """
------------------------------------------------------------------------------
                            EXEMPLŌRUM GRATIĀ
------------------------------------------------------------------------------
Crie GeoJSONSeq  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
(Exempmplo com osmium)
    osmium export \
      --output-format=geojsonseq \
      --geometry-types=polygon \
      --attributes=type,id,version,timestamp \
      --overwrite \
      --output=data/tmp/brasil-uf.osm.geojsonseq \
      data/tmp/brasil-uf.osm.pbf

Gere o relatorio . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    {0} --input-osm-geojsonseq data/tmp/brasil-uf.osm.geojsonseq

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
            '--input-osm-geojsonseq',
            help='Caminho do GeoJSON seq tipico da OSM',
            dest='in_geojsonseq',
            nargs='?'
        )

        # parser.add_argument(
        #     '--input-ibge-nivel',
        #     help='Caminho para o shapefile do IBGE',
        #     dest='ibge_nivel',
        #     default='municipio',
        #     choices=['municipio', 'uf'],
        #     nargs='?'
        # )

        return parser.parse_args()

    def execute_cli(
            self, pyargs, stdin=STDIN, stdout=sys.stdout,
            stderr=sys.stderr
    ):
        # frictionless_to_excel(pyargs.datapackage, pyargs.excel)

        if pyargs.ibge_nivel == 'municipio':
            ibge_estatisticas_municipio(pyargs.ibge_shp)
        elif pyargs.ibge_nivel == 'uf':
            ibge_estatisticas_uf(pyargs.ibge_shp)
        else:
            raise SyntaxError

        # print('unknow option.')
        return self.EXIT_OK


def ibge_estatisticas_uf(path_shapefile: str):
    gdf_ibge = geopandas.read_file(path_shapefile)

    # print(">> resumo IBGE")
    # print(gdf_ibge)

    # https://gis.stackexchange.com/questions/48949/epsg-3857-or-4326-for-googlemaps-openstreetmap-and-leaflet
    gdf_ibge = gdf_ibge.to_crs(epsg=32723)
    gdf_ibge_centroid = gdf_ibge.centroid.to_crs(epsg=4326)

    # @see https://cursos.alura.com.br/forum/topico-calculo-do-centroid-nao-funciona-129758
    # print(gdf_ibge.area)

    csvw = csv.writer(sys.stdout)
    csvw.writerow(['CD_UF', 'NM_UF', 'SIGLA_UF', 'NM_REGIAO',
                  'AREA_KM2', '_inferencia-area-m2_errada', '_centroid'])
    for index, row in gdf_ibge.iterrows():

        _x = gdf_ibge_centroid[index].x
        _y = gdf_ibge_centroid[index].y
        csvw.writerow([row['CD_UF'], row['NM_UF'], row['SIGLA_UF'], row['NM_REGIAO'],
                       row['AREA_KM2'], row['geometry'].area, f"POINT({_x} {_y})"])


def ibge_estatisticas_municipio(path_shapefile: str):
    gdf_ibge = geopandas.read_file(path_shapefile)

    # print(">> resumo IBGE")
    # print(gdf_ibge)

    # https://gis.stackexchange.com/questions/48949/epsg-3857-or-4326-for-googlemaps-openstreetmap-and-leaflet
    gdf_ibge = gdf_ibge.to_crs(epsg=32723)

    # @see https://cursos.alura.com.br/forum/topico-calculo-do-centroid-nao-funciona-129758
    gdf_ibge_centroid = gdf_ibge.centroid.to_crs(epsg=4326)

    # print(gdf_ibge.area)

    csvw = csv.writer(sys.stdout)
    csvw.writerow(['CD_MUN', 'NM_MUN', 'SIGLA_UF',
                  'AREA_KM2', '_inferencia-area-m2_errada', '_centroid'])
    for index, row in gdf_ibge.iterrows():

        _x = gdf_ibge_centroid[index].x
        _y = gdf_ibge_centroid[index].y
        csvw.writerow([row['CD_MUN'], row['NM_MUN'], row['SIGLA_UF'],
                       row['AREA_KM2'], row['geometry'].area, f"POINT({_x} {_y})"])


if __name__ == "__main__":

    cli_2600 = Cli()
    args = cli_2600.make_args()
    cli_2600.execute_cli(args)
