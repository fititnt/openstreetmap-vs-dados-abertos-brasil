#!/bin/bash
#===============================================================================
#
#          FILE:  setup.sh
#
#         USAGE:  ./scripts/setup.sh
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - curl
#                 - unzip
#                 - osmium (https://osmcode.org/osmium-tool/)
#                   - apt install osmium-tool
#                 - crudini (https://github.com/pixelb/crudini)
#                   - pip install crudini
#                 - gdal
#                   - apt install gdal-bin
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication
#                 SPDX-License-Identifier: Unlicense
#       VERSION:  v1.1
#       CREATED:  2023-04-01 17:59 UTC
#      REVISION:  2023-04-01 20:02 BRT logica movido para relatorio-admin.sh 
#===============================================================================
set -e

#ROOTDIR="$(pwd)"
#TEMPDIR="$(pwd)/data/tmp"
CACHEDIR="$(pwd)/data/cache"

OSM_BRASIL_URL=$(crudini --get configuracao.ini DEFAULT OSM_BRASIL_URL | tr -d '"')
OSM_BRASIL_PBF=$(crudini --get configuracao.ini DEFAULT OSM_BRASIL_PBF | tr -d '"')

IBGE_UF_URL=$(crudini --get configuracao.ini DEFAULT IBGE_UF_URL | tr -d '"')
IBGE_MUNICIPIO_URL=$(crudini --get configuracao.ini DEFAULT IBGE_MUNICIPIO_URL | tr -d '"')

IBGE_BASE_URL=$(crudini --get configuracao.ini DEFAULT IBGE_BASE_URL | tr -d '"')
IBGE_UF_ID=$(crudini --get configuracao.ini DEFAULT IBGE_UF_ID | tr -d '"')
IBGE_UF_ID_FIXO=$(crudini --get configuracao.ini DEFAULT IBGE_UF_ID_FIXO | tr -d '"')
IBGE_MUNICIPIO_ID=$(crudini --get configuracao.ini DEFAULT IBGE_MUNICIPIO_ID | tr -d '"')
IBGE_MUNICIPIO_ID_FIXO=$(crudini --get configuracao.ini DEFAULT IBGE_MUNICIPIO_ID_FIXO | tr -d '"')

# IBGE_DIR_SHAPEFILES="${ROOTDIR}/data/cache/"
IBGE_DIR_SHAPEFILES="data/tmp"

#_OSM_BRASIL_URL=$(awk -F "=" '/OSM_BRASIL_URL/ {print $2}' configuracao.ini | tr -d ' ' | tr -d '"')

#echo "_OSM_BRASIL_URL $_OSM_BRASIL_URL"

# Test data, < 1MB
# OSM_PBF_TEST_DOWNLOAD="https://download.geofabrik.de/africa/sao-tome-and-principe-latest.osm.pbf"
# OSM_PBF_TEST_FILE="$ROOTDIR/data/cache/osm-data-test.osm.pbf"

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

#######################################
# Download OpenStreetMap dump
#
# Globals:
#   OSM_BRASIL_PBF
#   OSM_BRASIL_URL
# Arguments:
#
# Outputs:
#
#######################################
data_osm_download() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "$OSM_BRASIL_PBF" ]; then
    set -x
    curl -o "${OSM_BRASIL_PBF}" "${OSM_BRASIL_URL}"
    set +x
  fi
  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Baixa limites administrativos do IBGE
#
# Globals:
#   CACHEDIR
#   IBGE_UF_ID_FIXO
#   IBGE_UF_URL
#   IBGE_DIR_SHAPEFILES
#   IBGE_MUNICIPIO_URL
#   IBGE_MUNICIPIO_ID_FIXO
# Arguments:
#
# Outputs:
#
#######################################
data_ibge_download() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "${CACHEDIR}/${IBGE_UF_ID_FIXO}.zip" ]; then
    echo "IBGE_BASE_URL [$IBGE_BASE_URL]"
    echo "IBGE_UF_ID [$IBGE_UF_ID]"
    set -x
    curl -o "${CACHEDIR}/${IBGE_UF_ID_FIXO}.zip" "${IBGE_UF_URL}"
    # unzip "${CACHEDIR}/${IBGE_UF_ID_FIXO}.zip" -d "${IBGE_DIR_SHAPEFILES}/"
    set +x
  fi

  if [ ! -f "${CACHEDIR}/${IBGE_MUNICIPIO_ID_FIXO}.zip" ]; then
    set -x
    curl -o "${CACHEDIR}/${IBGE_MUNICIPIO_ID_FIXO}.zip" "${IBGE_MUNICIPIO_URL}"
    # unzip "${CACHEDIR}/${IBGE_MUNICIPIO_ID_FIXO}.zip" -d "${IBGE_DIR_SHAPEFILES}/"
    set +x
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Baixa limites administrativos do IBGE
#
# Globals:
#   CACHEDIR
#   IBGE_UF_ID_FIXO
#   IBGE_UF_URL
#   IBGE_DIR_SHAPEFILES
#   IBGE_MUNICIPIO_URL
#   IBGE_MUNICIPIO_ID_FIXO
# Arguments:
#
# Outputs:
#
#######################################
data_ibge_unzip() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.shp" ]; then
    set -x
    unzip "${CACHEDIR}/${IBGE_MUNICIPIO_ID_FIXO}.zip" -d "${IBGE_DIR_SHAPEFILES}/"

    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.shp" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.shp"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.cpg" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.cpg"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.prj" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.prj"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.shx" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.shx"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.dbf" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.dbf"

    set +x
  fi

  if [ ! -f "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.shp" ]; then
    set -x
    unzip "${CACHEDIR}/${IBGE_UF_ID_FIXO}.zip" -d "${IBGE_DIR_SHAPEFILES}/"

    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.shp" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.shp"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.cpg" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.cpg"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.prj" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.prj"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.shx" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.shx"
    mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.dbf" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.dbf"

    set +x
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#### main ______________________________________________________________________

# init_cache_dirs
data_osm_download
data_ibge_download
data_ibge_unzip
# data_osm_extract_boundaries
# data_ibge_convert_geopackage

