

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
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication
#                 SPDX-License-Identifier: Unlicense
#       VERSION:  v1.0
#       CREATED:  2023-03-01 17:59 UTC
#      REVISION:  ---
#===============================================================================
set -e

ROOTDIR="$(pwd)"
TEMPDIR="$(pwd)/data/tmp"

OSM_BRASIL_URL="https://download.geofabrik.de/south-america/brazil-latest.osm.pbf"
OSM_BRASIL_PBF="${ROOTDIR}/data/osm/brasil.osm.pbf"

# Exemplo: https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_UF_2022.zip
# Exemplo: https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_Municipios_2022.zip
IBGE_BASE_URL="https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/"
IBGE_UF_ID="BR_UF_2022"
IBGE_MUNICIPIO_ID="BR_Municipios_2022"

IBGE_DIR_SHAPEFILES="${ROOTDIR}/data/ibge/"

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
# Download IBGE Brasil UF dump
#
# Globals:
#   IBGE_BASE_URL
#   IBGE_UF_ID
#   TEMPDIR
# Arguments:
#
# Outputs:
#
#######################################
data_ibge_download() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "${TEMPDIR}/${IBGE_UF_ID}.zip" ]; then
    set -x
    curl -o "${TEMPDIR}/${IBGE_UF_ID}.zip" "${IBGE_BASE_URL}${IBGE_UF_ID}.zip"
    unzip "${TEMPDIR}/${IBGE_UF_ID}.zip" -d "${IBGE_DIR_SHAPEFILES}"
    set +x
  fi

  if [ ! -f "${TEMPDIR}/${IBGE_MUNICIPIO_ID}.zip" ]; then
    set -x
    curl -o "${TEMPDIR}/${IBGE_MUNICIPIO_ID}.zip" "${IBGE_BASE_URL}${IBGE_MUNICIPIO_ID}.zip"
    unzip "${TEMPDIR}/${IBGE_MUNICIPIO_ID}.zip" -d "${IBGE_DIR_SHAPEFILES}"
    set +x
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

# @see https://gis.stackexchange.com/questions/323148/extracting-admin-boundary-data-from-openstreetmap
# @see https://www.openstreetmap.org/user/SomeoneElse/diary/47007
# @see https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative
# osmium tags-filter data/osm/brasil.osm.pbf r/admin_level=4 -o data/tmp/brasil-uf.osm.pbf
# osmium tags-filter data/osm/brasil.osm.pbf r/admin_level=8 -o data/tmp/brasil-municipios.osm.pbf

#### main ______________________________________________________________________

data_osm_download
data_ibge_download
