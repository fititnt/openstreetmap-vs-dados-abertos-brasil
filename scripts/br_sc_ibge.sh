#!/bin/bash
#===============================================================================
#
#          FILE:  br_sc_ibge.sh
#
#         USAGE:  ./scripts/br_sc_ibge.sh
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication
#                 SPDX-License-Identifier: Unlicense
#       VERSION:  v1.0
#       CREATED:  2023-04-16 20:57 BRT
#      REVISION:  ---
#===============================================================================
set -e

# @see https://dados.gov.br/dados/conjuntos-dados/base-cartografica-continua-do-estado-de-santa-catarina-escala-1-25-000-sc25-versao-2020
# @see https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/bc25/sc/versao2020/

# ROOTDIR="$(pwd)"
TEMPDIR="$(pwd)/data/tmp"
CACHEDIR="$(pwd)/data/cache"
# MEMDIR="/tmp"

IBGE_SC_GPKG_ZIP_URL="https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/bc25/sc/versao2020/geopackage/bc25_sc_2020-10-01.zip"
IBGE_SC_LISTA_NOMES_CSV_URL="https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/bc25/sc/versao2020/lista_de_nomes_geograficos/bc25_sc_listanomesgeograficos.csv"

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
# Baixa geometrias
#
# Globals:
#   CACHEDIR
# Arguments:
#    id
#    url
# Outputs:
#
#######################################
download_and_cache() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  local_file="${1}"
  url="${2}"

  if [ ! -f "${CACHEDIR}/${local_file}" ]; then
    set -x
    curl --output "${CACHEDIR}/${local_file}" \
      "${url}"
    set +x
  else
    echo "Cacheado [${CACHEDIR}/${local_file}]"
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Extrai uma camada de arquivo geopackage em arquivo geojson
#
# Globals:
#   TEMPDIR
# Arguments:
#    geopackage_file
#    geopackage_layer
#    geojson_file
# Outputs:
#
#######################################
gpkg_layer_to_geojson_on_tmp() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  in_geopackage_file="${1}"
  in_geopackage_layer="${2}"
  out_geojson_file="${3}"

  if [ ! -f "${TEMPDIR}/${out_geojson_file}" ]; then
    set -x
    # curl --output "${CACHEDIR}/${local_file}" \
    #   "${url}"
    # ogr2ogr -f GeoJSON data/tmp/bc25_sc_2020-10-01__cbge_cemiterio_p.geojson data/tmp/bc25_sc_2020-10-01.gpkg cbge_cemiterio_p
    ogr2ogr \
      -f GeoJSON "${TEMPDIR}/${out_geojson_file}" \
      "${TEMPDIR}/${in_geopackage_file}" \
      "${in_geopackage_layer}"
    set +x
  else
    echo "Cacheado [${TEMPDIR}/${out_geojson_file}]"
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Umzip
#
# Globals:
#   CACHEDIR
#   TEMPDIR
# Arguments:
#    cached_zip
#    tmp_subdir
#    example_internal_file
# Outputs:
#
#######################################
unzip_cached_on_tmp() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  cached_zip="${1}"
  tmp_subdir="${2}"
  example_internal_file="${3}"

  if [ ! -f "${TEMPDIR}/${tmp_subdir}${example_internal_file}" ]; then
    set -x
    unzip "${CACHEDIR}/${cached_zip}" -d "${TEMPDIR}/${tmp_subdir}/"
    set +x
  else
    echo "Ja existia: [${TEMPDIR}/${tmp_subdir}${example_internal_file}]"
  fi

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#### main ______________________________________________________________________

# _id_com_data="bc25_sc_2020-10-01"

download_and_cache "bc25_sc_2020-10-01.zip" "${IBGE_SC_GPKG_ZIP_URL}"
download_and_cache "bc25_sc_listanomesgeograficos.csv" "${IBGE_SC_LISTA_NOMES_CSV_URL}"

unzip_cached_on_tmp "bc25_sc_2020-10-01.zip" "" "bc25_sc_2020-10-01.gpkg"

gpkg_layer_to_geojson_on_tmp "bc25_sc_2020-10-01.gpkg" "cbge_cemiterio_p" "bc25_sc_2020-10-01__cbge_cemiterio_p.geojson"
gpkg_layer_to_geojson_on_tmp "bc25_sc_2020-10-01.gpkg" "enc_torre_energia_p" "bc25_sc_2020-10-01__enc_torre_energia_p.geojson"

# plant:source=hydro
# https://overpass-turbo.eu/s/1tS7
#  [out:json][timeout:25];area(id:3600296584)->.searchArea;(nwr["plant:source"="hydro"](area.searchArea););out body;>;out skel qt;
gpkg_layer_to_geojson_on_tmp "bc25_sc_2020-10-01.gpkg" "enc_hidreletrica_p" "bc25_sc_2020-10-01__enc_hidreletrica_p.geojson"

# ogr2ogr -f GeoJSON data/tmp/bc25_sc_2020-10-01__cbge_cemiterio_p.geojson data/tmp/bc25_sc_2020-10-01.gpkg cbge_cemiterio_p

# data_ibge_sc_gpkg_download "bc25_sc_2020-10-01" "${IBGE_SC_GPKG_ZIP_URL}"

# ogrinfo data/tmp/bc25_sc_2020-10-01.gpkg
# ogrinfo data/cache/bc25_sc_2020-10-01.zip
# ogr2ogr data/cache/bc25_sc_2020-10-01.zip

# ogr2ogr -f GeoJSON data/tmp/bc25_sc_2020-10-01.gpkg -nln cbge_cemiterio_p data/tmp/bc25_sc_2020-10-01__cbge_cemiterio_p.geojson
# ogr2ogr -f GeoJSON data/tmp/bc25_sc_2020-10-01.gpkg data/tmp/bc25_sc_2020-10-01__cbge_cemiterio_p.geojson
# ogr2ogr -f GeoJSON data/tmp/bc25_sc_2020-10-01__cbge_cemiterio_p.geojson -nln cbge_cemiterio_p data/tmp/bc25_sc_2020-10-01.gpkg

exit 1
# shellcheck disable=SC2317,SC2034
./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/diff-points-ab.geojson \
  --output-log=data/tmp/diff-points-ab.log.txt \
  tests/data/data-points_a.geojson \
  tests/data/data-points_b.geojson

# shellcheck disable=SC2317,SC2034
./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/diff-points-ab.geojson \
  --output-log=data/tmp/diff-points-ab.log.txt \
  --tolerate-distance=1000 \
  data/tmp/bc25_sc_2020-10-01__enc_hidreletrica_p.geojson \
  data/tmp/overpass-hidro-sc.geojson

# shellcheck disable=SC2317,SC2034
./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/diff-points-ab.geojson \
  --output-diff-tsv=data/tmp/diff-points-ab.tsv \
  --output-diff-csv=data/tmp/diff-points-ab.csv \
  --output-log=data/tmp/diff-points-ab.log.txt \
  --tolerate-distance=1000 \
  data/tmp/overpass-hidro-sc.geojson \
  data/tmp/bc25_sc_2020-10-01__enc_hidreletrica_p.geojson


# https://github.com/tyrasd/osmtogeojson
# npm install -g osmtogeojson
# osmtogeojson overpass-hidro-sc.json > overpass-hidro-sc.geojson
# shellcheck disable=SC2317,SC2034
./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/diff-points-ab__osm-x-sc.geojson \
  --output-diff-csv=data/tmp/diff-points-ab__osm-x-sc.csv \
  --tolerate-distance=1000 \
  data/tmp/overpass-hidro-sc.geojson \
  data/tmp/bc25_sc_2020-10-01__enc_hidreletrica_p.geojson


# shellcheck disable=SC2317,SC2034
./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp//diff-points-ab__sc-x-osm.geojson \
  --output-diff-csv=data/tmp/diff-points-ab__sc-x-osm.csv \
  --tolerate-distance=1000 \
  data/tmp/bc25_sc_2020-10-01__enc_hidreletrica_p.geojson \
  data/tmp/overpass-hidro-sc.geojson