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
# TEMPDIR="$(pwd)/data/tmp"
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

# #######################################
# # Baixa geometrias
# #
# # Globals:
# #   CACHEDIR
# # Arguments:
# #    id
# #    url
# # Outputs:
# #
# #######################################
# data_ibge_sc_gpkg_download() {
#   printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

#   id="${1}"
#   url="${2}"

#   if [ ! -f "${CACHEDIR}/${id}.zip" ]; then
#     set -x
#     curl --output "${CACHEDIR}/${id}.zip" \
#       "${url}"
#     set +x
#   else
#     echo "Cacheado ${CACHEDIR}/${id}.zip"
#   fi

#   printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
# }

#### main ______________________________________________________________________

# _id_com_data="bc25_sc_2020-10-01"

download_and_cache "bc25_sc_2020-10-01.zip" "${IBGE_SC_GPKG_ZIP_URL}"
download_and_cache "bc25_sc_listanomesgeograficos.csv" "${IBGE_SC_LISTA_NOMES_CSV_URL}"
# data_ibge_sc_gpkg_download "bc25_sc_2020-10-01" "${IBGE_SC_GPKG_ZIP_URL}"
