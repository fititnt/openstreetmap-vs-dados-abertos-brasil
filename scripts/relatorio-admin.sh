

#!/bin/bash
#===============================================================================
#
#          FILE:  relatorio-admin.sh
#
#         USAGE:  ./scripts/relatorio-admin.sh
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - curl
#                 - unzip
#                 - osmium (https://osmcode.org/osmium-tool/)
#                   - apt install osmium-tool
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication
#                 SPDX-License-Identifier: Unlicense
#       VERSION:  v1.1
#       CREATED:  2023-04-01 17:59 UTC
#      REVISION:  2023-04-01 20:02 BRT extraido de setup.sh
#===============================================================================
set -e

ROOTDIR="$(pwd)"
TEMPDIR="$(pwd)/data/tmp"
CACHEDIR="$(pwd)/data/cache"

# OSM_BRASIL_URL=$(crudini --get configuracao.ini DEFAULT OSM_BRASIL_URL | tr -d '"')
OSM_BRASIL_PBF=$(crudini --get configuracao.ini DEFAULT OSM_BRASIL_PBF | tr -d '"')

# IBGE_UF_ID=$(crudini --get configuracao.ini DEFAULT IBGE_UF_ID | tr -d '"')
IBGE_UF_ID_FIXO=$(crudini --get configuracao.ini DEFAULT IBGE_UF_ID_FIXO | tr -d '"')
# IBGE_MUNICIPIO_ID=$(crudini --get configuracao.ini DEFAULT IBGE_MUNICIPIO_ID | tr -d '"')
IBGE_MUNICIPIO_ID_FIXO=$(crudini --get configuracao.ini DEFAULT IBGE_MUNICIPIO_ID_FIXO | tr -d '"')

IBGE_DIR_SHAPEFILES="data/tmp"

#### Fancy colors constants - - - - - - - - - - - - - - - - - - - - - - - - - -
tty_blue=$(tput setaf 4)
tty_green=$(tput setaf 2)
# tty_red=$(tput setaf 1)
tty_normal=$(tput sgr0)

## Example
# printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"
# printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
# printf "\t%40s\n" "${tty_blue} INFO: [] ${tty_normal}"
# printf "\t%40s\n" "${tty_red} ERROR: [] ${tty_normal}"
#### Fancy colors constants - - - - - - - - - - - - - - - - - - - - - - - - - -

#### functions _________________________________________________________________

# @see https://gis.stackexchange.com/questions/323148/extracting-admin-boundary-data-from-openstreetmap
# @see https://www.openstreetmap.org/user/SomeoneElse/diary/47007
# @see https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative
# osmium tags-filter data/osm/brasil.osm.pbf r/admin_level=4 -o data/tmp/brasil-uf.osm.pbf
# osmium tags-filter data/osm/brasil.osm.pbf r/admin_level=8 -o data/tmp/brasil-municipios.osm.pbf


#######################################
# Extrai divisões administrativas do arquivo da OpenStreetMap
#
# Globals:
#
# Arguments:
#
# Outputs:
#
#######################################
data_osm_extract_boundaries() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "data/tmp/brasil-uf.osm.pbf" ]; then
    set -x
    osmium tags-filter data/cache/brasil.osm.pbf r/admin_level=4 -o data/tmp/brasil-uf.osm.pbf
    ogr2ogr -f GPKG data/tmp/brasil-uf.gpkg data/tmp/brasil-uf.osm.pbf

    # https://docs.osmcode.org/osmium/latest/osmium-export.html
    # osmium export --output-format=geojson --geometry-types=polygon --output=data/tmp/brasil-uf.osm.geojson data/tmp/brasil-uf.osm.pbf
    osmium export \
      --output-format=geojsonseq \
      --geometry-types=polygon \
      --attributes=type,id,version,timestamp \
      --overwrite \
      --output=data/tmp/brasil-uf.osm.geojsonseq \
      data/tmp/brasil-uf.osm.pbf
    # osmium export --output-format=txt --geometry-types=polygon --output=data/tmp/brasil-uf.osm.geojson --overwrite data/tmp/brasil-uf.osm.txt

    osmium tags-filter data/cache/brasil.osm.pbf r/admin_level=8 -o data/tmp/brasil-municipios.osm.pbf
    ogr2ogr -f GPKG data/tmp/brasil-municipios.gpkg data/tmp/brasil-municipios.osm.pbf

    osmium export \
      --output-format=geojsonseq \
      --geometry-types=polygon \
      --attributes=type,id,version,timestamp \
      --overwrite \
      --output=data/tmp/brasil-municipios.osm.geojsonseq \
      data/tmp/brasil-municipios.osm.pbf
    # ogr2ogr -f GPKG data/tmp/brasil-municipios.gpkg data/tmp/brasil-municipios.osm.pbf
    set +x
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}


#######################################
# Gera relatório do IBGE, para UFs
#
# Globals:
#    IBGE_DIR_SHAPEFILES
#    IBGE_MUNICIPIO_ID_FIXO
#    IBGE_UF_ID_FIXO
# Arguments:
#
# Outputs:
#
#######################################
relatorio_ibge_uf() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  set -x

  USE_PYGEOS=0 "${ROOTDIR}/scripts/govbrasil-ibge_estatisticas.py" \
    --input-ibge-shapefile="${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.shp" \
    --input-ibge-nivel='uf' \
    > relatorio/temp_divisao-administrativa-uf_ibge.csv

  set +x

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Gera relatório do IBGE, para municipios
#
# Globals:
#    IBGE_DIR_SHAPEFILES
#    IBGE_MUNICIPIO_ID_FIXO
#    IBGE_UF_ID_FIXO
# Arguments:
#
# Outputs:
#
#######################################
relatorio_ibge_municipio() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  set -x

  USE_PYGEOS=0 "${ROOTDIR}/scripts/govbrasil-ibge_estatisticas.py" \
    --input-ibge-shapefile="${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.shp" \
    --input-ibge-nivel='municipio' \
    > relatorio/temp_divisao-administrativa-municipio_ibge.csv

  set +x

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

# #######################################
# # Extrai divisões administrativas do arquivo da OpenStreetMap
# #
# # Globals:
# #
# # Arguments:
# #
# # Outputs:
# #
# #######################################
# data_ibge_convert_geopackage() {
#   printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

#   if [ ! -f "data/tmp/${IBGE_UF_ID}.gpkg" ]; then
#     set -x
#     ogr2ogr -f GPKG "data/tmp/${IBGE_UF_ID}.gpkg" "${IBGE_DIR_SHAPEFILES}${IBGE_UF_ID}.shp" -nln "${IBGE_UF_ID}"
#     set +x
#   fi

#   if [ ! -f "data/tmp/${IBGE_MUNICIPIO_ID}.gpkg" ]; then
#     set -x
#     ogr2ogr -f GPKG "data/tmp/${IBGE_MUNICIPIO_ID}.gpkg" "${IBGE_DIR_SHAPEFILES}${IBGE_MUNICIPIO_ID}.shp" -nln "${IBGE_MUNICIPIO_ID}"
#     set +x
#   fi

#   # if [ ! -f "${TEMPDIR}/${IBGE_MUNICIPIO_ID}.zip" ]; then
#   #   set -x
#   #   curl -o "${TEMPDIR}/${IBGE_MUNICIPIO_ID}.zip" "${IBGE_BASE_URL}${IBGE_MUNICIPIO_ID}.zip"
#   #   unzip "${TEMPDIR}/${IBGE_MUNICIPIO_ID}.zip" -d "${IBGE_DIR_SHAPEFILES}"
#   #   set +x
#   # fi

#   printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
# }


# ogr2ogr -f GPKG data/tmp/brasil-uf.gpkg data/tmp/brasil-uf.osm.pbf


#### main ______________________________________________________________________

data_osm_extract_boundaries
# data_ibge_convert_geopackage
relatorio_ibge_uf
relatorio_ibge_municipio

# set -x

# USE_PYGEOS=0 "${ROOTDIR}/scripts/govbrasil-ibge_estatisticas.py" \
#   --input-ibge-shapefile='data/tmp/BR_Municipios_2022.shp' \
#   --input-ibge-nivel='municipio' \
#   > relatorio/temp_divisao-administrativa-municipio_ibge.csv

# USE_PYGEOS=0 "${ROOTDIR}/scripts/govbrasil-ibge_estatisticas.py" \
#   --input-ibge-shapefile='data/tmp/BR_UF_2022.shp' \
#   --input-ibge-nivel='uf' \
#   > relatorio/temp_divisao-administrativa-uf_ibge.hxl.csv

# set +x