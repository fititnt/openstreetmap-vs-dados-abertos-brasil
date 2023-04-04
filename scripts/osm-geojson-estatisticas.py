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

# import geopandas
import datetime
import json
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

        osm_estatisticas(pyargs.in_geojsonseq)
        return self.EXIT_OK


def osm_estatisticas(path):

    attrs = {

    }

    # primeira leitura: frequencia em que termos aparecem
    with open(path, "r") as fileobject:
        for linha in fileobject:
            # print("")
            # print(line)
            if linha:
                # 1e = record separator
                item = json.loads(linha.lstrip("\x1e"))

                if 'properties' not in item:
                    # Likeky error?
                    continue

                for key, _val in item['properties'].items():
                    if key not in attrs:
                        attrs[key] = 0
                    attrs[key] += 1

                # print(json.dumps(item, indent=2))
                # do_something_with(linha)

    attrs_sorted = sorted(attrs.items(), key=lambda x: x[1], reverse=True)

    # print(attrs)
    # print(attrs_sorted)
    cabecalho = []
    for _key, _count in attrs_sorted:
        cabecalho.append(_key)

    csvw = csv.writer(sys.stdout)

    csvw.writerow(cabecalho)

    # segunda leitura, agora imprime os valores de fato
    with open(path, "r") as fileobject:
        for linha in fileobject:
            # print("")
            # print(line)
            if linha:
                # 1e = record separator
                item = json.loads(linha.lstrip("\x1e"))

                if 'properties' not in item:
                    # Likeky error?
                    continue

                linha_padrao = []
                for key in cabecalho:
                    if key in item['properties']:
                        _val = item['properties'][key]

                        if key == '@timestamp':
                            _val = datetime.datetime.fromtimestamp(_val)

                        linha_padrao.append(_val)
                    else:
                        linha_padrao.append('')

                csvw.writerow(linha_padrao)


if __name__ == "__main__":

    cli_2600 = Cli()
    args = cli_2600.make_args()
    cli_2600.execute_cli(args)
