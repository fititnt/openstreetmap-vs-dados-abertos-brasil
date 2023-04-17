#!/bin/bash
#===============================================================================
#
#          FILE:  logradouros.sh
#
#         USAGE:  ./scripts/logradouros.sh
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - unzip
#                 - curl
#                 - ogr2ogr, ogrmerge.py (gdal)
#                   - apt install gdal-bin
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication
#                 SPDX-License-Identifier: Unlicense
#       VERSION:  v1.0
#       CREATED:  2023-04-14 02:13 BRT
#      REVISION:  ---
#===============================================================================
set -e

# ROOTDIR="$(pwd)"
TEMPDIR="$(pwd)/data/tmp"
CACHEDIR="$(pwd)/data/cache"
MEMDIR="/tmp"

# https://stackoverflow.com/questions/49779281/string-similarity-with-python-sqlite-levenshtein-distance-edit-distance/49815419#49815419
# https://stackoverflow.com/questions/13909885/how-to-add-levenshtein-function-in-mysql
# TIGER geocoding https://www.e-education.psu.edu/natureofgeoinfo/c4_p8.html

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
# Baixa logradouros
#
# Globals:
#   CACHEDIR
# Arguments:
#    id
#    url
# Outputs:
#
#######################################
data_ibge_logradouros_download() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  id="${1}"
  url="${2}"

  if [ ! -f "${CACHEDIR}/${id}.zip" ]; then
    set -x
    curl --output "${CACHEDIR}/${id}.zip" \
      "${url}"
    set +x
  else
    echo "Cacheado ${CACHEDIR}/${id}.zip"
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Baixa limites administrativos do IBGE
#
# Globals:
#   CACHEDIR
#   TEMPDIR
# Arguments:
#   id
#   temporalidade
#   exemplo_arquivo_interno
#   layer_final
# Outputs:
#
#######################################
data_ibge_logradouros_unzip_e_gpkg() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  id="${1}"
  temporalidade="${2}"
  exemplo_arquivo_interno="${3}"
  layer_final="${4}"

  _zip="${CACHEDIR}/${id}.zip"
  _destino="${TEMPDIR}/logradouros/${temporalidade}"

  _merged_mem="${MEMDIR}/logradouros_${temporalidade}_${id}_merged.gpkg"
  _destino_v2="${TEMPDIR}/logradouros_${temporalidade}_${id}_merged.gpkg"

  if [ ! -f "${_destino}/${exemplo_arquivo_interno}" ]; then
    # if [ -f "${_destino}/${exemplo_arquivo_interno}" ]; then
    set -x
    unzip "${_zip}" -d "${_destino}/"

    # mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.shp" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.shp"
    # mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.cpg" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.cpg"
    # mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.prj" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.prj"
    # mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.shx" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.shx"
    # mv "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID}.dbf" "${IBGE_DIR_SHAPEFILES}/${IBGE_MUNICIPIO_ID_FIXO}.dbf"

    # @TODO remover essa parte; o proximo bloco é mais otimizado do que este
    # for file in ${_destino}/*.shp; do
    #   # echo "$file"
    #   # set -x
    #   ogr2ogr -f GPKG -append "${TEMPDIR}/logradouros_${temporalidade}_${id}.gpkg" "${file}"
    # done

    set +x
  else
    echo "Ja existia: ${_destino}/${exemplo_arquivo_interno}"
  fi

  # @see https://gis.stackexchange.com/questions/353776/merge-geopackages-keeping-layer-structure
  # @see https://gdal.org/programs/ogrmerge.html
  # ogrmerge  -f gpkg -o mergetest.gpkg -nln {LAYER_NAME} test1.gpkg
  # ogrmerge  -append -o mergetest.gpkg -nln {LAYER_NAME} test2.gpkg test3.gpkg

  if [ ! -f "${_merged_mem}" ]; then
    # echo "todo... ${_merged_mem}"

    for file in ${_destino}/*.shp; do
      set -x
      if [ ! -f "${_merged_mem}" ]; then
        ogrmerge.py -f gpkg -o "${_merged_mem}" -nln "${layer_final}" "${file}"
      else
        ogrmerge.py -append -o "${_merged_mem}" -nln "${layer_final}" "${file}"
      fi
      set +x
    done

    # mv "${_merged_mem}" "$_destino_v2"
    cp "${_merged_mem}" "$_destino_v2"
  fi

  # if [ ! -f "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.shp" ]; then
  #   set -x
  #   unzip "${CACHEDIR}/${IBGE_UF_ID_FIXO}.zip" -d "${IBGE_DIR_SHAPEFILES}/"

  #   mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.shp" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.shp"
  #   mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.cpg" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.cpg"
  #   mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.prj" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.prj"
  #   mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.shx" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.shx"
  #   mv "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID}.dbf" "${IBGE_DIR_SHAPEFILES}/${IBGE_UF_ID_FIXO}.dbf"

  #   set +x
  # fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#### main ______________________________________________________________________

# @see https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/malha_de_setores_censitarios/censo_2010/base_de_faces_de_logradouros_versao_2021/
_LOGRADOUROS_ZIP_URL="https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/malha_de_setores_censitarios/censo_2010/base_de_faces_de_logradouros_versao_2021/SC/sc_faces_de_logradouros_2021.zip"
_LOGRADOUROS_ID="IBGE_logradouros_SC"

data_ibge_logradouros_download "${_LOGRADOUROS_ID}" "${_LOGRADOUROS_ZIP_URL}"
data_ibge_logradouros_unzip_e_gpkg "${_LOGRADOUROS_ID}" "recente" "4209102_faces_de_logradouros_2021.shp" "logradouros"

# data/tmp/logradouros/recente/4200051_faces_de_logradouros_2021.shp
# data/tmp/logradouros/recente/4200101_faces_de_logradouros_2021.shp
# data/tmp/logradouros/recente/4200200_faces_de_logradouros_2021.shp

## Initialize
# ogrmerge.py -f gpkg -o data/tmp/mergetest.gpkg -nln layer_name_here data/tmp/logradouros/recente/4200051_faces_de_logradouros_2021.shp

## Then start merge all others
# ogrmerge.py -append -o data/tmp/mergetest.gpkg -nln layer_name_here data/tmp/logradouros/recente/4200101_faces_de_logradouros_2021.shp data/tmp/logradouros/recente/4200200_faces_de_logradouros_2021.shp
