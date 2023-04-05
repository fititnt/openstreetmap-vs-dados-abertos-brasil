#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  compare-tabelas.py
#
#         USAGE:  ./scripts/compare-tabelas.py
#                 ./scripts/compare-tabelas.py --help
#                 USE_PYGEOS=0 ./scripts/compare-tabelas.py --help
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
#       CREATED:  2023-04-04 20:58 BRT
#      REVISION:  ---
# ==============================================================================


import datetime
import json
import os
import sys
import argparse
import csv

PROGRAM = "compare-tabelas"
DESCRIPTION = """
------------------------------------------------------------------------------
Compara duas tabelas

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
            '--input-osm-arquivo',
            help='Caminho do CSV com dados da OpenStreetMap',
            dest='in_osm',
            nargs='?'
        )

        parser.add_argument(
            '--input-externa-arquivo',
            help='Caminho do CSV de fonte externa à OpenStreetMap',
            dest='in_externa',
            nargs='?'
        )

        parser.add_argument(
            '--input-osm-id',
            help='Coluna de referencia no arquivo da OpenStreetMap',
            dest='in_osm_id',
            nargs='?'
        )

        parser.add_argument(
            '--input-externa-id',
            help='Coluna de referencia no arquivo da fonte externa à OpenStreetMap',
            dest='in_externa_id',
            nargs='?'
        )

        parser.add_argument(
            '--relatorio-titulo',
            help='Titulo para fonte externa à OpenStreetMap que está sendo comparada',
            dest='relatorio_titulo',
            default=None,
            nargs='?'
        )

        parser.add_argument(
            '--input-externa-titulo',
            help='Titulo para fonte externa à OpenStreetMap que está sendo comparada',
            dest='in_externa_titulo',
            default='Fonte Externa Sem Nome',
            nargs='?'
        )

        parser.add_argument(
            '--filtro-tag-contem',
            help='Filtro de tags. Exemplo: boundary=administrative',
            dest='filtro_tag_contem',
            nargs='?',
            action='append'
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

        comp = CompareTabelas(
            pyargs.in_osm,
            pyargs.in_externa,
            pyargs.in_osm_id,
            pyargs.in_externa_id,
            pyargs.in_externa_titulo,
            pyargs.relatorio_titulo,
        )
        print(comp.debug())
        # print('todo')
        return self.EXIT_OK


class CompareTabelas:

    def __init__(
            self,
            in_osm: str,
            in_externa: str,
            in_osm_id: str,
            in_externa_id: str,
            in_externa_titulo: str,
            relatorio_titulo: str = None,
    ) -> None:

        self.osm, self.erros_graves_osm = self._load(in_osm, in_osm_id)
        self.externa, self.erros_graves_externa = self._load(
            in_externa, in_externa_id)

        self.osm_sobrando = self._nem_mencionado(self.osm, self.externa)
        self.externa_sobrando = self._nem_mencionado(self.externa, self.osm)

        self.in_externa_titulo = in_externa_titulo
        self.relatorio_titulo = relatorio_titulo

    def _load(self, in_osm, in_osm_id):

        data = {

        }
        erros = []

        with open(in_osm) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # print(row)
                # print(row[in_osm_id])

                if not row[in_osm_id] or len(row[in_osm_id]) == 0:
                    erros.append(f'SEM CHAVE REFERENCIA {row}')
                    continue

                if row[in_osm_id] in data:
                    erros.append(f'REPETIDO {row[in_osm_id]}')
                    continue

                data[row[in_osm_id]] = row

        return data, erros

    def _nem_mencionado(self, fonte_a: dict, fonte_b: dict):
        resultado = []
        for key in fonte_a.keys():
            if key not in fonte_b:
                resultado.append(key)
        return resultado

    def debug(self):

        print(f'# {self.relatorio_titulo}')

        print(f'')
        print(f'> {datetime.datetime.now()}')
        print(f'')

        print('## Avisos graves')

        if self.erros_graves_osm:
            print('')
            print('<details>')
            print('<summary>Fonte: OpenStreetMap</summary>')
            print(self.erros_graves_osm)
            print('</details>')

        # print(f'## Avisos graves ({self.in_externa_titulo})')

        if self.erros_graves_externa:
            print('')
            print('<details>')
            print(f'<summary>Fonte: {self.in_externa_titulo}</summary>')
            print(self.erros_graves_osm)
            print('</details>')

        print('')
        print('## Conteúdo adicional (OpenStreetMap)')
        print(self.osm_sobrando)

        print(f'')
        print(f'## Conteúdo adicional ({self.in_externa_titulo})')
        print(self.externa_sobrando)

        # print('osm_sobrando', self.osm_sobrando)
        # print('externa_sobrando', self.externa_sobrando)
        return ""


if __name__ == "__main__":

    cli_2600 = Cli()
    args = cli_2600.make_args()
    cli_2600.execute_cli(args)
