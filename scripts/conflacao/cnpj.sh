#!/bin/bash
#===============================================================================
#
#          FILE:  cnpj.sh
#
#         USAGE:  ./scripts/conflacao/cnpj.sh
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - zipgrep
#                   - sudo apt install unzip
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication
#                 SPDX-License-Identifier: Unlicense
#       VERSION:  v1.0
#       CREATED:  2023-04-12 20:21 BRT
#      REVISION:  ---
#===============================================================================
set -e

ROOTDIR="$(pwd)"
TEMPDIR="$(pwd)/data/tmp"
CACHEDIR="$(pwd)/data/cache"

# - https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj
#   - https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf
#   - https://dadosabertos.rfb.gov.br/CNPJ/Estabelecimentos0.zip

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
# Download CNPJs de estabelecimentos via site da Receita Federal do Brasil
#
# Globals:
#   CACHEDIR
# Arguments:
#
# Outputs:
#
#######################################
data_cnpj_estabelecimentos_download() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  # https://dadosabertos.rfb.gov.br/CNPJ/Estabelecimentos0.zip

  for i in {0..9}; do
    if [ ! -f "${CACHEDIR}/CNPJ_Estabelecimentos${i}.zip" ]; then
      set -x
      curl --output "${CACHEDIR}/CNPJ_Estabelecimentos${i}.zip" \
        "https://dadosabertos.rfb.gov.br/CNPJ/Estabelecimentos${i}.zip"
      set +x
    else
      echo "Cacheado CNPJ_Estabelecimentos${i}.zip"
    fi
  done

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Faz um grep linha por linha em todos dentro ddos zips dos estabelecimentos
#
# Example:
#  data_cnpj_estabelecimentos_grep ';"SC";' "${TEMPDIR}/outfile.csv"
#
# Globals:
#   CACHEDIR
#   TEMPDIR
# Arguments:
#    grep_args
#
# Outputs:
#
#######################################
data_cnpj_estabelecimentos_grep() {
  grep_args="${1}"
  outfile="${2}"

  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "${outfile}" ]; then
    for i in {0..9}; do
      set -x
      # echo zipgrep "${grep_args}" "${CACHEDIR}/CNPJ_Estabelecimentos${i}.zip" ">> ${outfile}"
      zipgrep "${grep_args}" "${CACHEDIR}/CNPJ_Estabelecimentos${i}.zip" >>"${outfile}"
      set +x
    done
  else
    echo "Cacheado ${outfile}. Delete se quiser re-gerar"
  fi

  _count=$(wc -l ${outfile})

  printf "\t%40s\n" "${tty_green} ${_count} ${tty_normal}"

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#### main ______________________________________________________________________

# init_cache_dirs
data_cnpj_estabelecimentos_download
data_cnpj_estabelecimentos_grep ';"SC";' "${TEMPDIR}/ReceitaFederal_CNPJ_Estabelecimentos__SC_2023-04-12.csv"
# data_osm_extract_boundaries
# data_ibge_convert_geopackage
