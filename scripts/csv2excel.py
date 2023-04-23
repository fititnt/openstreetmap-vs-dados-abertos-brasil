#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  csv2excel.py
#
#         USAGE:  ./scripts/csv2excel.py
#                 ./scripts/csv2excel.py --help
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#                   - pip install pandas (https://pandas.pydata.org/)
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.2.0
#       CREATED:  2023-04-23 01:04 BRT
#      REVISION:  ---
# ==============================================================================

import sys
import argparse
import pandas as pd

__VERSION__="0.2.0"
PROGRAM = "csv2excel"
DESCRIPTION = """
------------------------------------------------------------------------------
{1} v{2} Convert CSV to Excel file with autofilters

------------------------------------------------------------------------------
""".format(
    __file__, PROGRAM, __VERSION__
)

__EPILOGUM__ = """
------------------------------------------------------------------------------
                            EXEMPLŌRUM GRATIĀ
------------------------------------------------------------------------------
    {0} input.csv output.xlsx
------------------------------------------------------------------------------
                            EXEMPLŌRUM GRATIĀ
------------------------------------------------------------------------------
""".format(
    __file__
)

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
        """make_args"""
        parser = argparse.ArgumentParser(
            prog=PROGRAM,
            description=DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__EPILOGUM__,
        )

        parser.add_argument("input_csv", help="Input CSV file")
        parser.add_argument("output_xlsx", help="Output XLSX")

        # # @see https://stackoverflow.com/questions/41669690/how-to-overcome-the-limit-of-hyperlinks-in-excel
        # parser.add_argument(
        #     "--hiperlink",
        #     help="Add hiperlink to column names if they have non-empty value. "
        #     "alredy are mached with each other. "
        #     "Use '||' to deparate colum name from the URL. "
        #     "Add {value} as part of the URL for placeholder of external link. "
        #     "Accept multiple values. "
        #     "Example: "
        #     "--pivot-key-main='colum_name||http://example.com/page/{value}'",
        #     dest="hiperlink",
        #     nargs="?",
        #     action="append",
        # )

        return parser.parse_args()

    def execute_cli(self, pyargs, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
        csv2excel(pyargs.input_csv, pyargs.output_xlsx)
        return self.EXIT_OK


def csv2excel(input_csv: str, output_xlsx: str, delimiter: str = ","):
    """csv2excel
    @see https://xlsxwriter.readthedocs.io/example_pandas_autofilter.html

    Args:
        input_csv (str): Input CSV file
        output_xlsx (str): Output XLSX
    """
    # print("TODO")
    df = pd.read_csv(input_csv, sep=delimiter)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(output_xlsx, engine="xlsxwriter")

    # Convert the dataframe to an XlsxWriter Excel object. We also turn off the
    # index column at the left of the output dataframe.
    df.to_excel(writer, sheet_name="Sheet1", index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    # worksheet.write_url("A2", "ftp://www.python.org/")

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 12)

    # Set the autofilter.
    worksheet.autofilter(0, 0, max_row, max_col - 1)

    # Add an optional filter criteria. The placeholder "Region" in the filter
    # is ignored and can be any string that adds clarity to the expression.
    # worksheet.filter_column(0, "Region == East")

    # # It isn't enough to just apply the criteria. The rows that don't match
    # # must also be hidden. We use Pandas to figure our which rows to hide.
    # for row_num in df.index[(df["Region"] != "East")].tolist():
    #     worksheet.set_row(row_num + 1, options={"hidden": True})

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()


def parse_argument_values(arguments: list, delimiter: str = "||") -> dict:
    if not arguments or len(arguments) == 0 or not arguments[0]:
        return None

    result = {}
    for item in arguments:
        if item.find(delimiter) > -1:
            _key, _val = item.split(delimiter)
            result[_key] = _val
        else:
            result[_key] = True
    return result


if __name__ == "__main__":
    cli_main = Cli()
    args = cli_main.make_args()
    cli_main.execute_cli(args)
