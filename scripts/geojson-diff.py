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
#                   - shapely (pip install shapely)
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.6.0
#       CREATED:  2023-04-16 22:36 BRT
#      REVISION:  2023-04-17 02:32 BRT v0.4.0 accept Overpas GeoJSON flavor
#                 2023-04-18 00:25 BRT v0.5.0 supports Polygon (not just Point)
#                 2023-04-19 21:52 BRT v0.6.0 draft of diff GeoJSON and JOSM
# ==============================================================================

import argparse
import csv
import json
import sys
import logging
from typing import List, Type
from haversine import haversine, Unit

# from shapely.geometry import Polygon, Point
from shapely.geometry import Polygon
from xml.sax.saxutils import escape


__VERSION__ = "0.6.0"

PROGRAM = "geojson-diff"
DESCRIPTION = """
------------------------------------------------------------------------------
GeoJSON++ diff

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
    {0} --output-diff-geojson=data/tmp/diff-points-ab.geojson \
--output-diff-tsv=data/tmp/diff-points-ab.tsv \
--output-diff-csv=data/tmp/diff-points-ab.csv \
--output-log=data/tmp/diff-points-ab.log.txt \
--tolerate-distance=1000 \
tests/data/data-points_a.geojson \
tests/data/data-points_b.geojson

GeoJSON (center point) example with overpass . . . . . . . . . . . . . . . . .
    [out:json][timeout:25];
    {{geocodeArea:Santa Catarina}}->.searchArea;
    (
    nwr["plant:source"="hydro"](area.searchArea);
    );
    convert item ::=::,::geom=geom(),_osm_type=type();
    out center;

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
            "--output-diff-geojson",
            help="(Experimental) Path to output GeoJSON diff file",
            dest="outdiffgeo",
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--output-diff-csv",
            help="Path to output CSV diff file",
            dest="outdiffcsv",
            required=False,
            nargs="?",
        )

        parser.add_argument(
            "--output-diff-tsv",
            help="Path to output TSV (Tab-separated values) diff file",
            dest="outdifftsv",
            required=False,
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

        pivot = parser.add_argument_group(
            "Parameters used to know how to conflate A and B "
        )

        pivot.add_argument(
            "--tolerate-distance",
            help="Typical maximum distance for features match if not "
            "exact same point. In meters. Default to 100",
            dest="tdist",
            default="100",
            required=False,
            nargs="?",
        )

        pivot.add_argument(
            "--pivot-key-main",
            help="If defined, its an strong hint that item from A and B "
            "alredy are mached with each other. "
            "Use '||' if attribute on A is not the same on the B. "
            "Accept multiple values. "
            "Example: "
            "--pivot-key-main='CO_CNES||ref:CNES' --pivot-key-main='ref:vatin'",
            dest="pivot_key_main",
            nargs="?",
            action="append",
        )

        pivot.add_argument(
            "--pivot-attr-2",
            help="A non primary attribute on A and B (like phone or website) "
            "which while imperfect, is additional hint about being about same. "
            "Use '||' if attribute on A is not the same on the B. "
            "Accept multiple values. "
            "Example: "
            "--pivot-attr-2='contact:email'",
            dest="pivot_attr_2",
            nargs="?",
            action="append",
        )

        advanced = parser.add_argument_group(
            "ADVANCED. Do not upload to OpenStreetMap unless you review the output. "
            "Requires A be an external dataset, and B be OpenStreetMap data. "
        )

        advanced.add_argument(
            "--output-josm-file",
            help="Output OpenStreetMap change proposal in JOSM file format",
            dest="outosc",
            # default="100",s
            required=False,
            nargs="?",
        )

        # parser.add_argument(
        #     "--tolerate-distance-extra",
        #     help="Path to output file",
        #     dest="tdist",
        #     default="500",
        #     required=False,
        #     nargs="?",
        # )

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

        # distance_okay = 50
        distance_okay = int(pyargs.tdist)
        # distance_permissive = 250

        crules = ConflationRules(
            distance_okay=int(pyargs.tdist),
            pivot_key_main=parse_argument_values(pyargs.pivot_key_main),
            pivot_attr_2=parse_argument_values(pyargs.pivot_attr_2),
        )

        geodiff = GeojsonCompare(
            pyargs.geodataset_a, pyargs.geodataset_b, crules, logger
        )

        if pyargs.outosc:
            with open(pyargs.outosc, "w") as file:
                file.write(geodiff.osmchange())

        if pyargs.outdiffcsv:
            with open(pyargs.outdiffcsv, "w") as file:
                tabular_writer(file, geodiff.summary_tabular(), delimiter=",")

        if pyargs.outdifftsv:
            with open(pyargs.outdifftsv, "w") as file:
                tabular_writer(file, geodiff.summary_tabular(), delimiter="\t")

        if pyargs.outdiffgeo:
            with open(pyargs.outdiffgeo, "w") as file:
                geojson_diff = geodiff.diff_geojson_full()
                file.write(json.dumps(geojson_diff, ensure_ascii=False, indent=2))
                # tabular_writer(file, geodiff.summary_tabular(), delimiter="\t")

        # geodiff.debug()
        return self.EXIT_OK


class ConflationRules:
    def __init__(
        self,
        distance_okay: int = None,
        pivot_key_main: list = None,
        pivot_attr_2: list = None,
    ) -> None:
        self.distance_okay = distance_okay
        self.pivot_key_main = pivot_key_main
        self.pivot_attr_2 = pivot_attr_2


class DatasetInMemory:
    def __init__(self, alias: str) -> None:
        self.alias = alias
        self.index = -1

        # Tuple
        # (coords, props, geometry?)
        # geometry? = only if not already point
        self.items = []

    def add_item(self, item: dict):
        self.index += 1
        # self.items.append(None)

        if (
            not item
            or "geometry" not in item
            or "coordinates" not in item["geometry"]
            or "type" not in item
        ):
            # Really bad input item
            self.items.append(False)
        elif item["geometry"]["type"] != "Point":
            if item["geometry"]["type"] == "Polygon":
                poly = Polygon(item["geometry"]["coordinates"][0])

                coords = (poly.centroid.y, poly.centroid.x)
                props = None
                geometry_original = item["geometry"]
                if (
                    "properties" in item
                    and item["properties"]
                    and len(item["properties"].keys())
                ):
                    props = item["properties"]
                # self.items.append(None)
                # self.items.append((coords, props))
                self.items.append((coords, props, geometry_original))
            else:
                # For now ignoring non Point features
                self.items.append(None)
        else:
            # Exact point
            coords = (
                item["geometry"]["coordinates"][1],
                item["geometry"]["coordinates"][0],
            )
            props = None

            # Overpass geojson store in "tags" instead of "properties"
            _properties = "tags" if "tags" in item else "properties"

            # if (
            #     "properties" in item
            #     and item["properties"]
            #     and len(item["properties"].keys())
            # ):
            if (
                _properties in item
                and item[_properties]
                and len(item[_properties].keys())
            ):
                props = item[_properties]
            # self.items.append((coords, props))
            self.items.append((coords, props, None))


class GeojsonCompare:
    """GeojsonCompare

    @TODO optimize for very large files
    """

    def __init__(
        self,
        geodataset_a: str,
        geodataset_b: str,
        crules: Type["ConflationRules"],
        logger,
    ) -> None:
        self.distance_okay = crules.distance_okay
        self.a = self._load_geojson(geodataset_a, "A")
        self.b = self._load_geojson(geodataset_b, "B")
        self.a_is_osm = None
        self.b_is_osm = None
        self.matrix = []

        self.compute()

        # logger.info(self.summary())
        # pass

    def _load_geojson(self, path: str, alias: str) -> DatasetInMemory:
        """Load optimized version of GeoJSON++ into memory

        Args:
            path (str): _description_
            alias (str): _description_

        Returns:
            DatasetInMemory
        """
        data = DatasetInMemory(alias)

        with open(path, "r") as file:
            # TODO optimize geojsonl
            jdict = json.load(file)

            # Overpass geojson store in "elements" instead of "features"
            container = "elements" if "elements" in jdict else "features"

            # for feat in jdict["features"]:
            for feat in jdict[container]:
                # print(feat)
                data.add_item(feat)

        return data

    def _short_title(self, properties: dict) -> str:
        if not properties or len(properties.keys()) == 0:
            return ""

        result = ""
        if "nome" in properties:
            result = properties["nome"]
        if "name" in properties:
            result = properties["name"]

        if "ref" in properties:
            result = result + f" ({properties['ref']})"

        return result.strip()

    def compute(self):
        """compute difference of B against A"""
        # for item in self.a.items:

        if len(self.a.items) > 0:
            for index in range(0, len(self.a.items)):
                if not self.a.items[index] or not self.a.items[index][1]:
                    continue

                if "id" in self.a.items[index][1] and self.a.items[index][1][
                    "id"
                ].startswith(("node/", "way/", "relation/")):
                    self.a_is_osm = True
                    break

        if len(self.b.items) > 0:
            for index in range(0, len(self.a.items)):
                # print(self.b.items[index])
                if not self.b.items[index] or not self.b.items[index][1]:
                    continue

                if "id" in self.b.items[index][1] and self.b.items[index][1][
                    "id"
                ].startswith(("node/", "way/", "relation/")):
                    self.b_is_osm = True
                    break

        # if len(self.b.items) > 0:
        #     if "id" in self.b.items[0][1] and self.b.items[0][1]["id"].startswith(
        #         ("node/", "way/", "relation/")
        #     ):
        #         self.b_is_osm = True

        # print(self.a_is_osm, self.b_is_osm)

        for index_a in range(0, len(self.a.items)):
            # print(f"    > teste A i{index_a}", self.a.items[index_a])
            found = False
            # if not self.a.items[index_a]:
            #     self.matrix.append(None)
            # else:
            if self.a.items[index_a]:
                candidates = []
                for index_b in range(0, len(self.b.items)):
                    # print("oibb", len(self.b.items))
                    # print('a', self.a.items[index_a])
                    # print('b', self.b.items[index_b][0])

                    # Try perfect match (including tags)
                    if (
                        self.b.items[index_b]
                        and self.a.items[index_a] == self.b.items[index_b]
                    ):
                        self.matrix.append((index_b, MATCH_EXACT, 0, None))
                        found = True
                        # print("  <<<<< dist zero a")

                    elif (
                        self.b.items[index_b]
                        and self.a.items[index_a][0] == self.b.items[index_b][0]
                    ):
                        # perfect match, except tags (TODO improve this check)
                        self.matrix.append((index_b, MATCH_EXACT, 0, None))
                        found = True
                        # print("  <<<< dist zero b")

                    # else:
                    elif self.b.items[index_b]:
                        dist = haversine(
                            self.a.items[index_a][0],
                            self.b.items[index_b][0],
                            unit=Unit.METERS,
                        )
                        # print(f"        >> teste A i{index_a} vs B i{index_b}", dist)
                        if dist <= self.distance_okay:
                            # TODO sort by near
                            candidates.append((dist, index_b))
                            # self.matrix.append((index_b, MATCH_NEAR, round(dist, 2)))
                            found = True
                        # break

            if found == True and len(candidates) > 0:
                # pass
                candidates_sorted = sorted(candidates, key=lambda tup: tup[0])

                dist = candidates_sorted[0][0]
                index_b = candidates_sorted[0][1]
                skiped = None
                if len(candidates) > 1:
                    skiped = []
                    # for i in range(1, len(candidates)):
                    for i in range(0, len(candidates)):
                        skiped.append(f"B{candidates[i][1]}")

                # self.matrix.append((index_b, MATCH_NEAR, round(dist, 2)))
                self.matrix.append((index_b, MATCH_NEAR, dist, skiped))

            if not found:
                self.matrix.append(None)

    def debug(self):
        print(self.a)
        # print("dataset a", self.a.items)
        print(self.b)
        # print("dataset b", self.b.items)
        print("matrix", self.matrix)

    def diff_geojson_full(self):
        dataobj = {"type": "FeatureCollection", "features": []}
        for index_a in range(0, len(self.a.items)):
            _item_a = self.a.items[index_a]

            _matrix = self.matrix[index_a]

            final_properties = {}

            # print("_item_a", _item_a)
            if _item_a[2] is not None:
                final_geometry = _item_a[2]
            else:
                # We assume will be a point
                final_geometry = {
                    "type": "Point",
                    "coordinates": [_item_a[0][1], _item_a[0][0]],
                }

            if _item_a[1] is not None:
                for key, value in _item_a[1].items():
                    final_properties[f"a.{key}"] = value
            # else:
            #     pass

            if _matrix and self.b.items[_matrix[0]][1]:
                # print('_matrix', _matrix)
                for key, value in self.b.items[_matrix[0]][1].items():
                    final_properties[f"b.{key}"] = value
            # else:
            #     pass

            if _matrix:
                # print("_matrix", _matrix)
                final_properties[f"a->b.distance"] = round(_matrix[2], 2)
                if _matrix[3]:
                    final_properties[f"a->b.near"] = " ".join(_matrix[3])
            else:
                final_properties[f"a->b.distance"] = -1

            # Colors inspired by
            # https://wiki.openstreetmap.org/wiki/OSM_Conflator

            if final_properties[f"a->b.distance"] == -1:
                # 'create': '#11dd11',  # creating a new node
                final_properties["action"] = "create"
                final_properties["marker-color"] = "#11dd11"
            elif final_properties[f"a->b.distance"] == 0:
                # 'retag':  '#660000',  # cannot delete unmatched feature, changing tags
                final_properties["action"] = "retag"
                final_properties["marker-color"] = "#660000"
            else:
                # 'move':   '#110055',  # moving an existing node
                final_properties["action"] = "move"
                final_properties["marker-color"] = "#110055"

            res = {
                "geometry": final_geometry,
                "properties": final_properties,
                "type": "Feature",
                # "_debug": f"_item_a {_item_a}",
                # "_original": _item_a,
            }

            dataobj["features"].append(res)
            # dataobj["features"].append(
            #     f"_item_a {_item_a}",
            # )

        return dataobj

    def osmchange(self):
        # @see https://wiki.openstreetmap.org/wiki/OsmChange
        # @see https://wiki.openstreetmap.org/wiki/JOSM_file_format
        if not self.b_is_osm:
            raise SyntaxError(
                "--output-josm-file=file.osm requires Dataset B be an "
                "OpenStreetMap-like geojson. "
                "(id starting with node/N, way/N or relation/N)"
            )

        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            "<!-- TEST ONLY, DO NOT UPLOAD! -->",
            f'<osm version="0.6" generator="{PROGRAM} {__VERSION__}" upload="never">',
            f"  <changeset>",
            f'    <tag k="created_by" v="{PROGRAM} {__VERSION__}"/>',
            f"  </changeset>",
        ]

        count = 0

        for index_a in range(0, len(self.a.items)):
            count -= 1
            _item_a = self.a.items[index_a]

            _matrix = self.matrix[index_a]

            n_lat = None
            n_lon = None

            if _item_a[2] is None:
                n_lat = round(_item_a[0][0], 7)
                n_lon = round(_item_a[0][1], 7)
            else:
                lines.append(
                    f"  <!-- {count} ignoring non Point feature suggestion -->"
                )
                continue

            final_properties = {}
            if _item_a[1] is not None:
                for key, value in _item_a[1].items():
                    if value is not False and value is not None and value:
                        final_properties[f"_{key}"] = escape(str(value))

            # @see https://github.com/openstreetmap/osmdbt/issues/29
            #      (topic about order of tags)
            if len(final_properties.keys()) > 0:
                # _kv = sorted(final_properties, key=lambda key: final_properties[key])

                lines.append(
                    f'  <node id="{count}" version="1" lat="{n_lat}" lon="{n_lon}">'
                )
                for key, value in sorted(final_properties.items()):
                    lines.append(f'    <tag k="{key}" v="{value}"/>')
                lines.append(f"  </node>")
            else:
                raise SyntaxError(f"No tags for item {count}. Aborting.")

        # <changeset>
        #     <tag k="source" v="velobike.ru"/>
        #     <tag k="created_by" v="OSM Conflator 1.4.1"/>
        #     <tag k="type" v="import"/>
        # </changeset>

        lines.append("</osm>")
        return "\n".join(lines)

    def summary(self):
        lines = []
        # lines.append("@TODO summary")

        found = 0
        for item in self.matrix:
            if item:
                found += 1

        lines.append(f"A {len(self.a.items)} | {found}")
        lines.append(f"B {len(self.b.items)} | _")

        tabular_out = self.summary_tabular()
        spamwriter = csv.writer(sys.stdout, delimiter="\t")
        for line in tabular_out:
            spamwriter.writerow(line)
        return "\n".join(lines)

    def summary_tabular(self) -> List[list]:
        header = [
            "uid_a",
            "uid_b",
            "id_a",
            "id_b",
            "match_stage",
            "distance_ab",
            "latitude_a",
            "longitude_a",
            "latitude_b",
            "longitude_b",
            "desc_a",
            "desc_b",
            "near_a",
        ]
        data = []

        for index_a in range(0, len(self.a.items)):
            _item_a = self.a.items[index_a]

            _matrix = self.matrix[index_a]

            # print(_item_a, _matrix)
            # print(_item_a[1], _matrix)
            # # print(_item_a[1])
            # print('aa', _matrix)

            uid_a = f"A{index_a}"
            uid_b = "" if not _matrix else f"B{_matrix[0]}"
            # id_a = "" if not "id" in _item_a else _item_a["id"]
            id_a = "" if not _item_a[1] or not "id" in _item_a[1] else _item_a[1]["id"]
            id_b = ""
            # if _matrix and self.b.items[_matrix[0]]:
            if (
                _matrix
                and self.b.items[_matrix[0]][1]
                and "id" in self.b.items[_matrix[0]][1]
            ):
                # print(self.b.items[_matrix[0]][1])
                id_b = self.b.items[_matrix[0]][1]["id"]
                # pass

            match_stage = ""

            # if not _matrix or not "id" in _matrix[1] else _item_a[1]["id"]
            distance_ab = -1 if not _matrix else _matrix[2]
            latitude_a = "" if not _item_a else _item_a[0][1]
            longitude_a = "" if not _item_a else _item_a[0][0]
            latitude_b = "" if not _matrix else self.b.items[_matrix[0]][0][1]
            longitude_b = "" if not _matrix else self.b.items[_matrix[0]][0][0]

            # print(self.a.items[index_a])
            desc_a = "" if not _item_a else self._short_title(self.a.items[index_a][1])
            desc_b = (
                "" if not _matrix else self._short_title(self.b.items[_matrix[0]][1])
            )
            # if _matrix:
            #     print(_matrix[3])
            near_a = "" if not _matrix or not _matrix[3] else " ".join(_matrix[3])

            # @TODO implement stages
            if distance_ab > -1:
                match_stage = 5

            # print("index_a", index_a)
            # pass
            data.append(
                [
                    uid_a,
                    uid_b,
                    id_a,
                    id_b,
                    match_stage,
                    distance_ab,
                    latitude_a,
                    longitude_a,
                    latitude_b,
                    longitude_b,
                    desc_a,
                    desc_b,
                    near_a,
                ]
            )

        data.insert(0, header)

        # return data.insert(0, header)
        return data


class ItemMatcher:
    def __init__(self, item, candidates: list, crules: Type[ConflationRules]) -> None:
        self.item = item
        self.candidates = candidates
        self.crules = crules


def parse_argument_values(arguments: list, delimiter: str = "||") -> dict:
    if not arguments or len(arguments) == 0 or not arguments[0]:
        return None

    result = {}
    for item in arguments:
        if item.find(delimiter):
            _key, _val = item.split(delimiter)
            result[_key] = _val
        else:
            result[_key] = True
    return result


def tabular_writer(file_or_stdout: str, data: List[list], delimiter: str = ",") -> None:
    """Write a tabular file

    Args:
        file_or_stdout (str): file or stdout
        data (List[list]): List of lists with data to be outputed
        delimiter (str, optional): Delimiter. Defaults to ",".
    """
    cwriter = csv.writer(file_or_stdout, delimiter=delimiter)
    for line in data:
        cwriter.writerow(line)


if __name__ == "__main__":
    main = Cli()
    args = main.make_args()
    # pyargs.print_help()

    # args.execute_cli(args)
    main.execute_cli(args)
