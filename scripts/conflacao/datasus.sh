#!/bin/bash
# shellcheck disable=SC2317,SC2034
#===============================================================================
#
#          FILE:  datasus.sh
#
#         USAGE:  ./scripts/conflacao/datasus.sh
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
#       VERSION:  v1.1
#       CREATED:  2023-04-11 18:13 BRT
#      REVISION:  ---
#===============================================================================
set -e

ROOTDIR="$(pwd)"
TEMPDIR="$(pwd)/data/tmp"
CACHEDIR="$(pwd)/data/cache"

# pip install osm_conflate
# cd scripts/temp
# conflate <profile.py> -o result.osm
# conflate velobike.py -o result.osm
# conflate velobike.py -o result.osm --changes changes.geojson

# ftp://ftp.datasus.gov.br/cnes/BASE_DE_DADOS_CNES_202302.ZIP
#    999999/0/0/ftp.datasus.gov.br/cnes/BASE_DE_DADOS_CNES_202302.ZIP
#    -> tbEstabelecimento202302.csv
#        999999/0/0/ftp.datasus.gov.br/cnes/tbEstabelecimento202302.csv
#
# /workspace/git/EticaAI/lexicographi-sine-finibus/officina/999999/0/0/ftp.datasus.gov.br/cnes/tbEstabelecimento202302.csv
# data/tmp/DATASUS-tbEstabelecimento.csv

exit

head data/tmp/DATASUS-tbEstabelecimento.csv

./scripts/csv2geojson.py --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' data/tmp/DATASUS-tbEstabelecimento.csv

head data/tmp/DATASUS-tbEstabelecimento.csv | ./scripts/csv2geojson.py --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1'
# https://github.com/mapbox/csv2geojson
# https://pypi.org/project/csv2geojson/
# pip install csv2geojson

./scripts/csv2geojson.py --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' --output-type=GeoJSON --ignore-warnings data/tmp/DATASUS-tbEstabelecimento.csv >data/tmp/DATASUS-tbEstabelecimento.geojson
ogr2ogr -nlt POINT -skipfailures points.shp geojsonfile.json OGRGeoJSON

# ogr2ogr -nlt POINT -skipfailures points.shp geojsonfile.json OGRGeoJSON
ogr2ogr -f GPKG data/tmp/DATASUS-tbEstabelecimento.gpkg data/tmp/DATASUS-tbEstabelecimento.geojson

### Santa catarina ____________________________________________________________
./scripts/csv2geojson.py --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' --output-type=GeoJSONSeq --ignore-warnings --contain-and=CO_ESTADO_GESTOR=42 data/tmp/DATASUS-tbEstabelecimento.csv >data/tmp/DATASUS-tbEstabelecimento_SC.geojsonl

ogr2ogr -f GPKG data/tmp/DATASUS-tbEstabelecimento_SC.gpkg data/tmp/DATASUS-tbEstabelecimento_SC.geojsonl

### Santa Catarina, v2 ________________________________________________________
./scripts/csv2geojson.py \
  --contain-and=CO_ESTADO_GESTOR=42 \
  --lat=NU_LATITUDE \
  --lon=NU_LONGITUDE \
  --delimiter=';' \
  --encoding='latin-1' \
  --output-type=GeoJSON \
  --cast-integer='CO_CNES|CO_UNIDADE' \
  --column-copy-to='NU_CNPJ|ref:vatin' \
  --column-copy-to='NU_CNPJ_MANTENEDORA|operator:ref:vatin' \
  --column-copy-to='CO_CNES|ref:CNES' \
  --column-copy-to='CO_CEP|addr:postcode' \
  --column-copy-to='NU_ENDERECO|addr:housenumber' \
  --column-copy-to='NO_LOGRADOURO|addr:street' \
  --column-copy-to='NO_EMAIL|contact:email' \
  --column-copy-to='NU_TELEFONE|contact:phone' \
  --column-copy-to='NU_FAX|contact:fax' \
  --value-prepend='ref:vatin|BR' \
  --value-prepend='operator:ref:vatin|BR' \
  --value-postcode-br='addr:postcode' \
  --value-phone-br='contact:phone|contact:fax' \
  --value-fixed='source|BR:DATASUS' \
  --ignore-warnings \
  data/tmp/DATASUS-tbEstabelecimento.csv \
  >data/tmp/DATASUS-tbEstabelecimento_SC_v2-2023-04-12.geojson

# --contain-and=CO_MUNICIPIO_GESTOR=4217006 \
./scripts/csv2geojson.py \
  --contain-and=CO_CEP=88730000 \
  --lat=NU_LATITUDE \
  --lon=NU_LONGITUDE \
  --delimiter=';' \
  --encoding='latin-1' \
  --output-type=GeoJSON \
  --cast-integer='CO_CNES|CO_UNIDADE' \
  --column-copy-to='NU_CNPJ|ref:vatin' \
  --column-copy-to='NU_CNPJ_MANTENEDORA|operator:ref:vatin' \
  --column-copy-to='CO_CNES|ref:CNES' \
  --column-copy-to='CO_CEP|addr:postcode' \
  --column-copy-to='NU_ENDERECO|addr:housenumber' \
  --column-copy-to='NO_LOGRADOURO|addr:street' \
  --column-copy-to='NO_EMAIL|contact:email' \
  --column-copy-to='NU_TELEFONE|contact:phone' \
  --column-copy-to='NU_FAX|contact:fax' \
  --value-prepend='ref:vatin|BR' \
  --value-prepend='operator:ref:vatin|BR' \
  --value-postcode-br='addr:postcode' \
  --value-phone-br='contact:phone|contact:fax' \
  --value-fixed='source|BR:DATASUS' \
  --ignore-warnings \
  data/tmp/DATASUS-tbEstabelecimento.csv \
  >data/tmp/DATASUS-tbEstabelecimento_SC-SaoLudgero_v2-2023-04-12.geojson

# 88730000

## Para o iD
# ./scripts/csv2geojson.py --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' --output-type=GeoJSON --ignore-warnings --contain-and=CO_ESTADO_GESTOR=42 data/tmp/DATASUS-tbEstabelecimento.csv > data/tmp/DATASUS-tbEstabelecimento_SC.geojson

exit 0
## Teste 1
# head data/tmp/DATASUS-tbEstabelecimento.csv | /workspace/git/fititnt/openstreetmap-vs-dados-abertos-brasil/./scripts/csv2geojson.py --lat=NU_LATITUDE --lon=NU_LONGITUDE --delimiter=';' --encoding='latin-1' --output-type=GeoJSONSeq --cast-integer='CO_CNES|CO_UNIDADE' --ignore-warnings
head data/tmp/DATASUS-tbEstabelecimento.csv | ./scripts/csv2geojson.py \
  --lat=NU_LATITUDE \
  --lon=NU_LONGITUDE \
  --delimiter=';' \
  --encoding='latin-1' \
  --output-type=GeoJSONSeq \
  --cast-integer='CO_CNES|CO_UNIDADE' \
  --column-copy-to='NU_CNPJ|ref:vatin' \
  --column-copy-to='NU_CNPJ_MANTENEDORA|operator:ref:vatin' \
  --column-copy-to='CO_CNES|ref:CNES' \
  --column-copy-to='CO_CEP|addr:postcode' \
  --column-copy-to='NU_ENDERECO|addr:housenumber' \
  --column-copy-to='NO_LOGRADOURO|addr:street' \
  --column-copy-to='NO_EMAIL|contact:email' \
  --column-copy-to='NU_TELEFONE|contact:phone' \
  --column-copy-to='NU_FAX|contact:fax' \
  --value-prepend='operator:ref:vatin|BR' \
  --value-postcode-br='addr:postcode' \
  --value-phone-br='contact:phone|contact:fax' \
  --value-fixed='source|BR:DATASUS' \
  --ignore-warnings - |
  jq

# @see https://wiki.openstreetmap.org/wiki/Addresses
# @see https://wiki.openstreetmap.org/wiki/Key:source
# @see https://wiki.openstreetmap.org/wiki/Key:addr:place
# @see https://wiki.openstreetmap.org/wiki/Key:phone

### RS, v2 ____________________________________________________________________
./scripts/csv2geojson.py \
  --contain-and=CO_ESTADO_GESTOR=43 \
  --lat=NU_LATITUDE \
  --lon=NU_LONGITUDE \
  --delimiter=';' \
  --encoding='latin-1' \
  --output-type=GeoJSON \
  --cast-integer='CO_CNES|CO_UNIDADE' \
  --column-copy-to='NU_CNPJ|ref:vatin' \
  --column-copy-to='NU_CNPJ_MANTENEDORA|operator:ref:vatin' \
  --column-copy-to='CO_CNES|ref:CNES' \
  --column-copy-to='CO_CEP|addr:postcode' \
  --column-copy-to='NU_ENDERECO|addr:housenumber' \
  --column-copy-to='NO_LOGRADOURO|addr:street' \
  --column-copy-to='NO_EMAIL|contact:email' \
  --column-copy-to='NU_TELEFONE|contact:phone' \
  --column-copy-to='NU_FAX|contact:fax' \
  --value-prepend='ref:vatin|BR' \
  --value-prepend='operator:ref:vatin|BR' \
  --value-postcode-br='addr:postcode' \
  --value-phone-br='contact:phone|contact:fax' \
  --value-fixed='source|BR:DATASUS' \
  --ignore-warnings \
  data/tmp/DATASUS-tbEstabelecimento.csv \
  >data/tmp/DATASUS-tbEstabelecimento_RS_v2-2023-04-12.geojson

./scripts/csv2geojson.py \
  --contain-and=CO_ESTADO_GESTOR=43 \
  --contain-and=TP_ESTAB_SEMPRE_ABERTO=S \
  --lat=NU_LATITUDE \
  --lon=NU_LONGITUDE \
  --delimiter=';' \
  --encoding='latin-1' \
  --output-type=GeoJSON \
  --cast-integer='CO_CNES|CO_UNIDADE' \
  --column-copy-to='NO_FANTASIA|name' \
  --column-copy-to='NO_RAZAO_SOCIAL|official_name' \
  --column-copy-to='NU_CNPJ|ref:vatin' \
  --column-copy-to='NU_CNPJ_MANTENEDORA|operator:ref:vatin' \
  --column-copy-to='CO_CNES|ref:CNES' \
  --column-copy-to='CO_CEP|addr:postcode' \
  --column-copy-to='NU_ENDERECO|addr:housenumber' \
  --column-copy-to='NO_LOGRADOURO|addr:street' \
  --column-copy-to='NO_EMAIL|contact:email' \
  --column-copy-to='NU_TELEFONE|contact:phone' \
  --column-copy-to='NU_FAX|contact:fax' \
  --value-prepend='ref:vatin|BR' \
  --value-prepend='operator:ref:vatin|BR' \
  --value-postcode-br='addr:postcode' \
  --value-phone-br='contact:phone|contact:fax' \
  --value-fixed='source|BR:DATASUS' \
  --ignore-warnings \
  data/tmp/DATASUS-tbEstabelecimento.csv \
  >data/tmp/DATASUS-tbEstabelecimento_RS_v4_sempreaberto-2023-04-12.geojson

./scripts/csv2geojson.py \
  --contain-and=CO_ESTADO_GESTOR=43 \
  --lat=NU_LATITUDE \
  --lon=NU_LONGITUDE \
  --delimiter=';' \
  --encoding='latin-1' \
  --output-type=GeoJSON \
  --cast-integer='CO_CNES|CO_UNIDADE' \
  --column-copy-to='NO_FANTASIA|name' \
  --column-copy-to='NO_RAZAO_SOCIAL|official_name' \
  --column-copy-to='NU_CNPJ|ref:vatin' \
  --column-copy-to='NU_CNPJ_MANTENEDORA|operator:ref:vatin' \
  --column-copy-to='CO_CNES|ref:CNES' \
  --column-copy-to='CO_CEP|addr:postcode' \
  --column-copy-to='NO_BAIRRO|addr:suburb' \
  --column-copy-to='NU_ENDERECO|addr:housenumber' \
  --column-copy-to='NO_LOGRADOURO|addr:street' \
  --column-copy-to='NO_EMAIL|contact:email' \
  --column-copy-to='NU_TELEFONE|contact:phone' \
  --column-copy-to='NU_FAX|contact:fax' \
  --value-prepend='ref:vatin|BR' \
  --value-prepend='operator:ref:vatin|BR' \
  --value-postcode-br='addr:postcode' \
  --value-phone-br='contact:phone|contact:fax' \
  --value-name-place-br='name|official_name|addr:suburb' \
  --value-name-street-br='addr:street' \
  --value-fixed='source|BR:DATASUS' \
  --ignore-warnings \
  data/tmp/DATASUS-tbEstabelecimento.csv \
  >data/tmp/DATASUS-tbEstabelecimento_RS_v5_2023-04-12.geojson

# addr:city=Florianópolis
# addr:suburb=Centro

# ./scripts/csv2geojson.py \
#     --contain-and=CO_ESTADO_GESTOR=43 \
#     --contain-and=TP_ESTAB_SEMPRE_ABERTO=S \
#     --contain-and=CO_REGIAO_SAUDE='0008' \
#     --lat=NU_LATITUDE \
#     --lon=NU_LONGITUDE \
#     --delimiter=';' \
#     --encoding='latin-1' \
#     --output-type=GeoJSON \
#     --cast-integer='CO_CNES|CO_UNIDADE' \
#     --column-copy-to='NU_CNPJ|ref:vatin' \
#     --column-copy-to='NU_CNPJ_MANTENEDORA|operator:ref:vatin' \
#     --column-copy-to='CO_CNES|ref:CNES' \
#     --column-copy-to='CO_CEP|addr:postcode' \
#     --column-copy-to='NU_ENDERECO|addr:housenumber' \
#     --column-copy-to='NO_LOGRADOURO|addr:street' \
#     --column-copy-to='NO_EMAIL|contact:email' \
#     --column-copy-to='NU_TELEFONE|contact:phone' \
#     --column-copy-to='NU_FAX|contact:fax' \
#     --value-prepend='ref:vatin|BR' \
#     --value-prepend='operator:ref:vatin|BR' \
#     --value-postcode-br='addr:postcode' \
#     --value-phone-br='contact:phone|contact:fax' \
#     --value-fixed='source|BR:DATASUS' \
#     --ignore-warnings \
#     data/tmp/DATASUS-tbEstabelecimento.csv \
#     >data/tmp/DATASUS-tbEstabelecimento_RS_v3+S+reg008_2023-04-12.geojson

# Regioes de saude
# http://189.28.128.100/dab/docs/portaldab/documentos/regioes_saude_cuida_mais_brasil.pdf
# https://www.cosemsrs.org.br/regioes-de-saude
# RS 43008 Região 08 - Vale do Caí e Metropolitana
# CO_REGIAO_SAUDE=008

## Alguem ja fez import parcial?
# https://wiki.openstreetmap.org/wiki/Import_of_the_Brazilian_National_Register_of_Health_Facilities

## URL
# https://cnes2.datasus.gov.br/cabecalho_reduzido.asp?VCod_Unidade=

##### RS ______________________________________________________________________

## data/tmp/osm-healtcare_RS_2023-04-20.geojson
# [out:json][timeout:25];
# {{geocodeArea:Rio Grande do Sul}}->.searchArea;
# (
#   nwr["ref:CNES"](area.searchArea);
#   nwr["healthcare"](area.searchArea);
#   nwr["amenity"="hospital"](area.searchArea);
#   nwr["amenity"="clinic"](area.searchArea);
#   nwr["amenity"="social_facility"](area.searchArea);
#   nwr["amenity"="pharmacy"](area.searchArea);
#   nwr["amenity"="doctors"](area.searchArea);
# );
# out body;
# >;
# out skel qt;

./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/datasus_RS__sus-x-osm.diff.geojson \
  --output-diff-csv=data/tmp/datasus_RS__sus-x-osm.diff.csv \
  --pivot-key-main='CO_CNES||ref:CNES' --pivot-key-main='ref:vatin' \
  --tolerate-distance=1000 \
  data/tmp/DATASUS-tbEstabelecimento_RS_v4_sempreaberto-2023-04-12.geojson \
  data/tmp/osm-healtcare_RS_2023-04-20.geojson

## data/tmp/osm-healtcare-hospital_RS_2023-04-23.geojson
# [out:json][timeout:25];
# {{geocodeArea:Rio Grande do Sul}}->.searchArea;
# (
#   nwr["ref:CNES"](area.searchArea);
#   nwr["healthcare"="hospital"](area.searchArea);
#   nwr["amenity"="hospital"](area.searchArea);
#   //nwr["amenity"="clinic"](area.searchArea);
#   //nwr["amenity"="social_facility"](area.searchArea);
#   //nwr["amenity"="pharmacy"](area.searchArea);
#   //nwr["amenity"="doctors"](area.searchArea);
# );
# out body;
# >;
# out skel qt;

./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/datasus_RS__sus-x-osm.diff.geojson \
  --output-diff-csv=data/tmp/datasus_RS__sus-x-osm.diff.csv \
  --pivot-key-main='CO_CNES||ref:CNES' --pivot-key-main='ref:vatin' \
  --tolerate-distance=1000 \
  --filter-ab-dist-min=0 \
  data/tmp/DATASUS-tbEstabelecimento_RS_v4_sempreaberto-2023-04-12.geojson \
  data/tmp/osm-healtcare-hospital_RS_2023-04-23.geojson

./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/datasus_RS__sus-x-osm.diff.geojson \
  --output-diff-csv=data/tmp/datasus_RS__sus-x-osm.diff.csv \
  --pivot-key-main='CO_CNES||ref:CNES' --pivot-key-main='ref:vatin' \
  --tolerate-distance=1000 \
  --filter-ab-dist-min=0 \
  --prefilter-a-contain='NO_RAZAO_SOCIAL||hospital' \
  --prefilter-b-contain='name||hospital' \
  data/tmp/DATASUS-tbEstabelecimento_RS_v4_sempreaberto-2023-04-12.geojson \
  data/tmp/osm-healtcare-hospital_RS_2023-04-23.geojson

./scripts/geojson-diff.py \
  --output-diff-geojson=data/tmp/datasus_RS__sus-x-osm.diff.geojson \
  --output-diff-csv=data/tmp/datasus_RS__sus-x-osm.diff.csv \
  --pivot-key-main='CO_CNES||ref:CNES' --pivot-key-main='ref:vatin' \
  --tolerate-distance=1000 \
  --filter-ab-dist-min=0 \
  --prefilter-a-contain='NO_RAZAO_SOCIAL||hospital' \
  --prefilter-b-contain='name||hospital' \
  --prefilter-b-contain='amenity||hospital' \
  data/tmp/DATASUS-tbEstabelecimento_RS_v5_2023-04-12.geojson \
  data/tmp/osm-healtcare-hospital_RS_2023-04-23.geojson

./scripts/csv2excel.py \
  data/tmp/datasus_RS__sus-x-osm.diff.csv \
  data/tmp/datasus_RS__sus-x-osm.diff.xlsx

# @TODO extrair bairros, ex: addr:suburb=Centro
# @TODO extrair cidade, ex: addr:city=Cândido Godói
