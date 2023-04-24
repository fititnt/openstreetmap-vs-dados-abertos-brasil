#!/bin/bash
#===============================================================================
#
#          FILE:  inep.sh
#
#         USAGE:  ./scripts/conflacao/inep.sh
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
#       CREATED:  2023-04-12 00:05 BRT
#      REVISION:  ---
#===============================================================================
set -e

#ROOTDIR="$(pwd)"
#TEMPDIR="$(pwd)/data/tmp"
#CACHEDIR="$(pwd)/data/cache"

## Escolas
# - Refcode?
#   - https://taginfo.openstreetmap.org/keys/ref%3AINEP#overview
#   - https://taginfo.openstreetmap.org/keys/IPP%3ACOD_INEP#overview
# - https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos
#   - https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/inep-data
#   - https://inepdata.inep.gov.br/analytics/saw.dll?Dashboard&NQUser=inepdata&NQPassword=Inep2014&PortalPath=%2Fshared%2FCenso%20da%20Educa%C3%A7%C3%A3o%20B%C3%A1sica%2F_portal%2FCat%C3%A1logo%20de%20Escolas&Page=Pr%C3%A9-Lista%20das%20Escolas
# - Potenciais exemplos de ref:CNES em SC
#   - https://www.openstreetmap.org/way/1098279702
#   - https://www.openstreetmap.org/search?query=CNES-2538229#map=19/-26.92522/-53.00268
#

# echo "todo"

## Dados baixados de https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/inep-data
## (https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/inep-data/catalogo-de-escolas)
## Não tem link direto, requer simuilar navegador completo

# ./scripts/csv2geojson.py --lat=Latitude --lon=Longitude --delimiter=';' data/tmp/INEP_SC_2023-04-11.csv

# ./scripts/csv2geojson.py --lat=Latitude --lon=Longitude --delimiter=';' data/tmp/INEP_SC_2023-04-11.csv > data/tmp/INEP_SC_2023-04-11.geojson
./scripts/csv2geojson.py \
    --lat='Latitude' \
    --lon='Longitude' \
    --delimiter=';' \
    --output-type=GeoJSON \
    --value-fixed='amenity|school' \
    --column-copy-to='Escola|name' \
    --column-copy-to='Código INEP|ref:INEP' \
    --column-copy-to='Telefone|contact:phone' \
    --value-phone-br='contact:phone' \
    --value-fixed='source|BR:INEP' \
    data/tmp/INEP_SC_2023-04-11.csv \
    >data/tmp/INEP_SC-v2_2023-04-11.geojson
    
# data/tmp/INEP_SC_2023-04-11.csv

# [out:json][timeout:25];
# {{geocodeArea:Santa Catarina}}->.searchArea;
# (
#   nwr["ref:INEP"](area.searchArea);
#   // nwr["amenity"="school"](area.searchArea);
#   // nwr["amenity"="university"](area.searchArea);
#   // nwr["amenity"="kindergarten"](area.searchArea);
#   // nwr["amenity"="college"](area.searchArea);
#   // nwr["amenity"="childcare"](area.searchArea);
#   // nwr["amenity"="prep_school"](area.searchArea);
#   // nwr["education"="centre"](area.searchArea);
#   // nwr["school"](area.searchArea);
# );
# out body;
# >;
# out skel qt;