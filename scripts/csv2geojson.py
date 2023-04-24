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
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v1.1.0
#       CREATED:  2023-04-11 18:13 BRT
#      REVISION:  2023-04-20 01:20 BRT v1.1 --contain-and-in
# ==============================================================================


# import geopandas
# import os
import argparse
import csv
import json
import re
import sys
import string


__VERSION__ = "1.1.0"
PROGRAM = "csv2geojson"
DESCRIPTION = """
------------------------------------------------------------------------------
CSV to GeoJSON

------------------------------------------------------------------------------
""".format(
    PROGRAM, __VERSION__
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

Exemplo CNPJ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
(https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf)
CNPJ_BASICO;CNPJ_ORDEM;CNPJ_DV;IDENTIFICADOR;MATRIZ_FILIAL;SITUAÇÃO_CADASTRAL;DATA_SITUACAO_CADASTRAL;MOTIVO_SITUACAO_CADASTRAL;NOME_DA_CIDADE_NO_EXTERIOR;PAIS;DATA_DE_INICIO_ATIVIDADE;CNAE_FISCAL_PRINCIPAL;CNAE_FISCAL_SECUNDÁRIA;TIPO_DE_LOGRADOURO;LOGRADOURO;NUMERO;COMPLEMENTO;BAIRRO;CEP;UF;MUNICIPIO;DDD_1;TELEFONE_1;DDD_2;TELEFONE_2;DDD_DO_FAX;FAX;CORREIO_ELETRONICO;SITUACAO_ESPECIAL;DATA_DA_SITUACAO_ESPECIAL
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
            "--contain-and-in",
            help="Alternative to -contain-and where values for a "
            "single field are a list. Separe values with ||"
            "Accept multiple values."
            "--contain-and=tag_a=valuea1||valuea2||valuea3",
            dest="contain_and_in",
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
            "--ignore-warnings",
            help="Ignore some errors (such as empty latitude/longitude values)",
            dest="ignore_warnings",
            action="store_true",
        )

        cast_group = parser.add_argument_group(
            "Convert/preprocess data from input, including generate new fields"
        )

        cast_group.add_argument(
            "--cast-integer",
            help="Name of input fields to cast to integer. "
            "Use | for multiple. "
            "Example: <[ --cast-integer='field_a|field_b|field_c' ]>",
            dest="cast_integer",
            nargs="?",
            type=lambda x: x.split("|"),
            default=None,
        )

        cast_group.add_argument(
            "--cast-float",
            help="Name of input fields to cast to float. "
            "Use | for multiple. "
            "Example: <[ --cast-float='latitude|longitude|field_c' ]>",
            dest="cast_float",
            nargs="?",
            type=lambda x: x.split("|"),
            default=None,
        )

        cast_group.add_argument(
            "--column-copy-to",
            help="Add extra comluns. "
            "For multiple, use multiple times this parameter. "
            "Source vs destiny column must be divided by |. "
            "Example: <[ --column-copy-to='ORIGINAL_FIELD_PT|name:pt' "
            "--column-copy-to='CNPJ|ref:vatin' ]>",
            dest="column_copy",
            nargs="?",
            # type=lambda x: x.split("||"),
            action="append",
            default=None,
        )

        cast_group.add_argument(
            "--value-fixed",
            help="Define a fixed string for every value of a column, "
            "For multiple, use multiple times this parameter. "
            "Source vs destiny column must be divided by |. "
            "Example: <[ --value-fixed='source|BR:DATASUS' ]>",
            dest="value_fixed",
            nargs="?",
            # type=lambda x: x.split("||"),
            action="append",
            default=None,
        )

        cast_group.add_argument(
            "--value-prepend",
            help="Prepend a custom string to all values in a column. "
            "For multiple, use multiple times this parameter. "
            "Source vs destiny column must be divided by |. "
            "Example: <[ --value-prepend='ref:vatin|BR' ]>",
            dest="value_prepend",
            nargs="?",
            # type=lambda x: x.split("||"),
            action="append",
            default=None,
        )

        cast_group.add_argument(
            "--value-postcode-br",
            help="One or more column names to format as if was Brazilan postcodes, CEP",
            dest="value_postcode_br",
            nargs="?",
            type=lambda x: x.split("|"),
            default=None,
        )

        cast_group.add_argument(
            "--value-phone-br",
            help="One or more column names to format as Brazilian "
            "phone/fax/WhatsApp number",
            dest="value_phone_br",
            nargs="?",
            type=lambda x: x.split("|"),
            default=None,
        )

        cast_group.add_argument(
            "--value-name-place-br",
            help="One or more columsn to format as name of place (Locale BR)",
            dest="value_name_place_br",
            nargs="?",
            type=lambda x: x.split("|"),
            default=None,
        )

        cast_group.add_argument(
            "--value-name-street-br",
            help="One or more columsn to format as name of street "
            "(Locale BR, 'logradouro') ",
            dest="value_name_street_br",
            nargs="?",
            type=lambda x: x.split("|"),
            default=None,
        )

        return parser.parse_args()

    def execute_cli(self, pyargs, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
        # input_file = STDIN if pyargs.input == "-" else pyargs.input

        _contain_or = {}
        _contain_and = {}
        _contain_and_in = {}
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

        if pyargs.contain_and_in:
            for item in pyargs.contain_and_in:
                if item:
                    if item.find("="):
                        _key, _val = item.split("=")
                        _val = _val.strip("|").strip()
                        _val_items = _val.split("||")
                        _contain_and_in[_key] = _val_items
                    else:
                        raise SyntaxError("contain-and-in requires at least one value")

        with open(pyargs.input, "r", encoding=pyargs.encoding) if len(
            pyargs.input
        ) > 1 else sys.stdin as csvfile:
            reader = csv.DictReader(csvfile, delimiter=pyargs.delimiter)

            if pyargs.outfmt == "GeoJSON":
                print('{"type": "FeatureCollection", "features": [')

            prepend = ""

            line_num = -1

            for row in reader:
                line_num += 1

                if not geojson_item_contain(
                    row,
                    contain_or=_contain_or,
                    contain_and=_contain_and,
                    contain_and_in=_contain_and_in,
                ):
                    continue

                formated_row = row_item_cast(
                    row,
                    line_num=line_num,
                    cast_integer=pyargs.cast_integer,
                    cast_float=pyargs.cast_float,
                    ignore_warnings=pyargs.ignore_warnings,
                )

                row_v2 = row_item_column_add(
                    formated_row,
                    column_copy=pyargs.column_copy,
                    ignore_warnings=pyargs.ignore_warnings,
                )
                row_v3 = row_item_values(
                    row_v2,
                    value_fixed=pyargs.value_fixed,
                    value_prepend=pyargs.value_prepend,
                    value_postcode_br=pyargs.value_postcode_br,
                    value_phone_br=pyargs.value_phone_br,
                    value_name_place_br=pyargs.value_name_place_br,
                    value_name_street_br=pyargs.value_name_street_br,
                    ignore_warnings=pyargs.ignore_warnings,
                )

                item = geojson_item(
                    # formated_row,
                    # row_v2,
                    row_v3,
                    pyargs.lat,
                    pyargs.lon,
                    contain_or=_contain_or,
                    contain_and=_contain_and,
                    contain_and_in=_contain_and_in,
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


def geojson_item(
    row,
    lat,
    lon,
    contain_or: list = None,
    contain_and: list = None,
    contain_and_in: list = None,
    ignore_warnings: bool = False,
):
    _lat = row[lat] if lat in row and len(row[lat].strip()) else False
    _lon = row[lon] if lon in row and len(row[lon].strip()) else False

    if not geojson_item_contain(
        row,
        contain_or=contain_or,
        contain_and=contain_and,
        contain_and_in=contain_and_in,
    ):
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
    item, contain_or: list = None, contain_and: list = None, contain_and_in: list = None
) -> bool:
    if not item:
        return False

    if not contain_or and not contain_and and not contain_and_in:
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

    if contain_and_in:
        _count = len(contain_and_in.keys())

        for _key, _val in contain_and_in.items():
            if _key not in item:
                raise SyntaxError(f"key {_key} not in {item}")
                # return False

            if item[_key] not in _val:
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

        if not value or isinstance(value, str) and len(value.strip()) == 0:
            continue

        result[key] = value

    return result


def row_item_cast(
    row: dict,
    line_num: int = -1,
    cast_integer: list = None,
    cast_float: list = None,
    ignore_warnings: bool = False,
):
    result = {}

    for key, value in row.items():
        if isinstance(cast_integer, list) and key in cast_integer:
            if not value.isnumeric() and ignore_warnings:
                continue

            result[key] = int(value)

        elif isinstance(cast_float, list) and key in cast_float:
            if value.find(",") > -1:
                value = value.replace(",", ".")

            result[key] = float(value)
        else:
            result[key] = value

    return result


def row_item_column_add(
    row: dict,
    column_copy: list = None,
    cast_float: list = None,
    ignore_warnings: bool = False,
):
    _column_copy = {}
    if isinstance(column_copy, list) and len(column_copy) > 0:
        for item in column_copy:
            _key, _value = item.split("|")
            _column_copy[_key] = _value

    if len(_column_copy.keys()) == 0:
        return row

    result = {}
    result = row
    for key, value in _column_copy.items():
        if key not in row:
            if not ignore_warnings:
                # print("", file=sys.stderr)
                raise SyntaxError(f"row_item_column_add {key} not found")
        else:
            result[value] = result[key]

    #     elif isinstance(cast_float, list) and key in cast_float:
    #         if value.find(",") > -1:
    #             value = value.replace(",", ".")

    #         result[key] = float(value)
    #     else:
    #         result[key] = value

    return result


def row_item_values(
    row: dict,
    value_fixed: list = None,
    value_prepend: list = None,
    value_postcode_br: list = None,
    value_phone_br: list = None,
    value_name_place_br: list = None,
    value_name_street_br: list = None,
    ignore_warnings: bool = False,
):
    # result = row

    if isinstance(value_fixed, list) and len(value_fixed) > 0:
        for item in value_fixed:
            _key, _value = item.split("|")
            row[_key] = _value

    _value_prepend = {}
    if isinstance(value_prepend, list) and len(value_prepend) > 0:
        for item in value_prepend:
            _key, _value = item.split("|")
            _value_prepend[_key] = _value

    if len(_value_prepend.keys()) > 0:
        for key, value in _value_prepend.items():
            if key not in row:
                if not ignore_warnings:
                    # print("", file=sys.stderr)
                    raise SyntaxError(f"row_item_column_add {key} not found")
            else:
                # Sometimes the value is empty, so we don't prepend
                if row[key]:
                    row[key] = f"{value}{row[key]}"

    if isinstance(value_postcode_br, list) and len(value_postcode_br) > 0:
        for item in value_postcode_br:
            _value = _zzz_format_cep(row[item])
            if _value:
                row[item] = _value
            else:
                row[item] = ""

    if isinstance(value_phone_br, list) and len(value_phone_br) > 0:
        for item in value_phone_br:
            _value = _zzz_format_phone_br(row[item])
            if _value:
                row[item] = _value
            else:
                row[item] = ""

    if isinstance(value_name_place_br, list) and len(value_name_place_br) > 0:
        for item in value_name_place_br:
            _value = _zzz_format_name_place_br(row[item])
            if _value:
                row[item] = _value
            else:
                row[item] = ""

    if isinstance(value_name_street_br, list) and len(value_name_street_br) > 0:
        for item in value_name_street_br:
            _value = _zzz_format_name_street_br(row[item])
            if _value:
                row[item] = _value
            else:
                row[item] = ""

    return row


def _zzz_format_cep(value: str):
    if not value:
        return False
    if value.isnumeric():
        if len(value) == 8:
            return re.sub(r"(\d{5})(\d{3})", r"\1-\2", value)
    return False


def _zzz_format_name_place_br(value: str):
    if not value or not isinstance(value, str):
        return value

    term = string.capwords(value.strip())
    term2 = re.sub("\s\s+", " ", term)

    # @TODO deal with Do Da De

    return term2


def _zzz_format_name_street_br(value: str):
    if not value or not isinstance(value, str):
        return value

    term = string.capwords(value.strip())
    term2 = re.sub("\s\s+", " ", term)

    # @TODO deal with Do Da De
    # @TODO deal with abbreviations

    return term2


def _zzz_format_phone_br(value: str):
    if not value:
        return False

    if value.startswith("+"):
        return value

    # @TODO deal with more than one number

    if value.startswith("(") and value.find(")") > -1:
        _num_com_ddd = "".join(filter(str.isdigit, value))

        _regiao = _num_com_ddd[0:2]
        _num_loc = _num_com_ddd[2:]
        _num_loc_p2 = _num_loc[-4:]
        _num_loc_p1 = _num_loc.replace(_num_loc_p2, "")
        # return "+55 " + _regiao + ' ' + _num_com_ddd[2:]
        return "+55 " + _regiao + " " + _num_loc_p1 + " " + _num_loc_p2

    # if value.isnumeric():
    #     if len(value) == 8:
    #         return re.sub(r"(\d{5})(\d{3})", r"\1-\2", value)
    return False


if __name__ == "__main__":
    cli_2600 = Cli()
    args = cli_2600.make_args()
    # pyargs.print_help()

    # args.execute_cli(args)
    cli_2600.execute_cli(args)
