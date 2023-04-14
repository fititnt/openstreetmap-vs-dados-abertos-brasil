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
# Download CNPJs de empresas via site da Receita Federal do Brasil
#
# Globals:
#   CACHEDIR
# Arguments:
#
# Outputs:
#
#######################################
data_cnpj_empresas_download() {
  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  # https://dadosabertos.rfb.gov.br/CNPJ/Empresas0.zip

  for i in {0..9}; do
    if [ ! -f "${CACHEDIR}/CNPJ_Empresas${i}.zip" ]; then
      set -x
      curl --output "${CACHEDIR}/CNPJ_Empresas${i}.zip" \
        "https://dadosabertos.rfb.gov.br/CNPJ/Empresas${i}.zip"
      set +x
    else
      echo "Cacheado CNPJ_Empresas${i}.zip"
    fi
  done

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

#######################################
# Faz um grep linha por linha em todos dentro ddos zips das empresas
#
# Example:
#  data_cnpj_estabelecimentos_grep 'DEFESA CIVIL' "${TEMPDIR}/outfile.csv"
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
data_cnpj_empresas_grep() {
  grep_args="${1}"
  outfile="${2}"

  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "${outfile}" ]; then

    echo '"CNPJ_BASICO";"RAZAO_SOCIAL";"NATUREZA_JURIDICA";"QUALIFICACAO_DO_RESPONSAVEL";"CAPITAL_SOCIAL_DA_EMPRESA";"PORTE_DA_EMPRESA";"ENTE_FEDERATIVO_RESPONSAVEL"' \
      >"${outfile}"

    for i in {0..9}; do
      set -x
      zipgrep "${grep_args}" "${CACHEDIR}/CNPJ_Empresas${i}.zip" | cut -d: -f2- >>"${outfile}"
      set +x
    done
  else
    echo "Cacheado ${outfile}. Delete se quiser re-gerar"
  fi

  _count=$(wc -l ${outfile})

  printf "\t%40s\n" "${tty_green} ${_count} ${tty_normal}"

  printf "\t%40s\n" "${tty_green}${FUNCNAME[0]} FINISHED OKAY ${tty_normal}"
}

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
#    outfile
#    grep_args_extra
#
# Outputs:
#
#######################################
data_cnpj_estabelecimentos_grep() {
  grep_args="${1}"
  outfile="${2}"
  grep_args_extra="${3-''}"

  printf "\n\t%40s\n" "${tty_blue}${FUNCNAME[0]} STARTED ${tty_normal}"

  if [ ! -f "${outfile}" ]; then

    echo '"CNPJ_BASICO";"CNPJ_ORDEM";"CNPJ_DV";"IDENTIFICADOR_MATRIZ_FILIAL";"NOME_FANTASIA";"SITUACAO_CADASTRAL";"DATA_SITUACAO_CADASTRAL";"MOTIVO_SITUACAO_CADASTRAL";"NOME_DA_CIDADE_NO_EXTERIOR";"PAIS";"DATA_DE_INICIO_ATIVIDADE";"CNAE_FISCAL_PRINCIPAL";"CNAE_FISCAL_SECUNDARIA";"TIPO_DE_LOGRADOURO";"LOGRADOURO";"NUMERO";"COMPLEMENTO";"BAIRRO";"CEP";"UF";"MUNICIPIO";"DDD_1";"TELEFONE_1";"DDD_2";"TELEFONE_2";"DDD_DO_FAX";"FAX";"CORREIO_ELETRONICO";"SITUACAO_ESPECIAL";"DATA_DA_SITUACAO_ESPECIAL"' \
      >"${outfile}"

    for i in {0..9}; do

      if [ -z "${grep_args_extra}" ]; then
        set -x
        zipgrep "${grep_args}" "${CACHEDIR}/CNPJ_Estabelecimentos${i}.zip" | cut -d: -f2- >>"${outfile}"
        set +x
      else
        set -x
        zipgrep "${grep_args}" "${CACHEDIR}/CNPJ_Estabelecimentos${i}.zip" | cut -d: -f2- | grep --extended-regexp "${grep_args_extra}" >>"${outfile}"
        set +x
      fi
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
data_cnpj_empresas_download
data_cnpj_estabelecimentos_download
data_cnpj_estabelecimentos_grep ';"SC";' "${TEMPDIR}/ReceitaFederal_CNPJ_Estabelecimentos__SC_2023-04-12.csv"
data_cnpj_estabelecimentos_grep ';"SC";' "${TEMPDIR}/ReceitaFederal_CNPJ_Estabelecimentos__SC-defesa-civil-et-al_2023-04-12.csv" 'DEFESA CIVIL|HOSPITAL |PRONTO SOCORRO|BOMBEIROS|DELEGACIA'

data_cnpj_empresas_grep 'DEFESA CIVIL' "${TEMPDIR}/ReceitaFederal_CNPJ_Empresas__BR-defesacivil_2023-04-12.csv"

# Nao aceita regex extendido
# data_cnpj_empresas_grep 'DEFESA CIVIL|HOSPITAL |PRONTO SOCORRO|BOMBEIROS|DELEGACIA' "${TEMPDIR}/ReceitaFederal_CNPJ_Empresas__defesacivil_v2_2023-04-12.csv"

# @TODO data_cnpj_empresas_grep
# "CNPJ_BASICO";"RAZAO_SOCIAL";"NATUREZA_JURIDICA";"QUALIFICACAO_DO_RESPONSAVEL";"CAPITAL_SOCIAL_DA_EMPRESA";"PORTE_DA_EMPRESA";"ENTE_FEDERATIVO_RESPONSAVEL"
# zipgrep 'SAMU' data/cache/CNPJ_Empresas0.zip

# data_cnpj_empresas_grep ';"SC";' "${TEMPDIR}/ReceitaFederal_CNPJ_Estabelecimentos__SC_2023-04-12.csv"
# data_osm_extract_boundaries
# data_ibge_convert_geopackage

# head data/tmp/ReceitaFederal_CNPJ_Estabelecimentos__SC_2023-04-12.csv
# tail data/tmp/ReceitaFederal_CNPJ_Estabelecimentos__SC_2023-04-12__old.csv
# tail data/tmp/ReceitaFederal_CNPJ_Estabelecimentos__SC_2023-04-12__old.csv | sed -i 's/^*://g' input.txt

# Exemplo CNPJ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
# (https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf)
# CNPJ_BASICO;CNPJ_ORDEM;CNPJ_DV;IDENTIFICADOR;MATRIZ_FILIAL;SITUACAO_CADASTRAL;DATA_SITUACAO_CADASTRAL;MOTIVO_SITUACAO_CADASTRAL;NOME_DA_CIDADE_NO_EXTERIOR;PAIS;DATA_DE_INICIO_ATIVIDADE;CNAE_FISCAL_PRINCIPAL;CNAE_FISCAL_SECUNDÁRIA;TIPO_DE_LOGRADOURO;LOGRADOURO;NUMERO;COMPLEMENTO;BAIRRO;CEP;UF;MUNICIPIO;DDD_1;TELEFONE_1;DDD_2;TELEFONE_2;DDD_DO_FAX;FAX;CORREIO_ELETRONICO;SITUACAO_ESPECIAL;DATA_DA_SITUACAO_ESPECIAL

# https://github.com/thampiman/reverse-geocoder
