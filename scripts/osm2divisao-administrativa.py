#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  osm2divisao-administrativa.py
#
#         USAGE:  ./scripts/osm2divisao-administrativa.py
#                 ./scripts/osm2divisao-administrativa.py --help
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
#       CREATED:  2023-04-02 21:11 UTC
#      REVISION:  ---
# ==============================================================================

# ./scripts/osm2divisao-administrativa.py data/tmp/brasil-uf.osm.pbf > data/tmp/brasil-uf.osm.geojson
# ./scripts/osm2divisao-administrativa.py data/tmp/brasil-municipios.osm.pbf > data/tmp/brasil-municipios.osm.geojson

import sys
import json

import osmium as o

geojsonfab = o.geom.GeoJSONFactory()


class GeoJsonWriter(o.SimpleHandler):
    def __init__(self):
        super().__init__()
        # write the Geojson header
        print('{"type": "FeatureCollection", "features": [')
        self.first = True

    def finish(self):
        print("]}")

    # def node(self, o):
    #     if o.tags:
    #         self.print_object(geojsonfab.create_point(o), o.tags)

    # def way(self, o):
    #     if o.tags and not o.is_closed():
    #         self.print_object(geojsonfab.create_linestring(o), o.tags)

    def area(self, o):
        if o.tags:
            self.print_object(geojsonfab.create_multipolygon(o), o.tags)

    def print_object(self, geojson, tags):
        geom = json.loads(geojson)
        if geom and tags.get('boundary') == 'administrative':
            props = dict(tags)

            if tags.get('admin_level') == '4':
                if 'IBGE:GEOCODIGO' in props:
                    props['CD_UF'] = props['IBGE:GEOCODIGO']
                if 'name' in props:
                    props['NM_UF'] = props['name']

            if tags.get('admin_level') == '8':
                if 'IBGE:GEOCODIGO' in props:
                    props['CD_MUN'] = props['IBGE:GEOCODIGO']
                if 'name' in props:
                    props['NM_UF'] = props['name']


            # if '' in props:
            #     props['SIGLA_UF']
            # if 'IBGE:GEOCODIGO' in props:
            #     props['SIGLA_UF']

            # feature = {"type": "Feature", "geometry": geom, "properties": dict(tags)}
            feature = {"type": "Feature", "geometry": geom, "properties": props}
            if self.first:
                self.first = False
            else:
                print(",")

            print(json.dumps(feature, ensure_ascii=False))


def main(osmfile):
    handler = GeoJsonWriter()

    handler.apply_file(osmfile)
    handler.finish()

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)
    sys.exit(main(sys.argv[1]))
