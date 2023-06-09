# openstreetmap-vs-dados-abertos-brasil
**[RASCUNHO] Comparativo de dados no OpenStreetMap com dados de fontes abertas no Brasil**

# Motivação
- https://t.me/OSMBrasil_Comunidade/67244

## Divisões político-administrativas

> **Nota: entre abril e junho de 2023 as pequenas difefenças de limites administrativos do Brasil na OpenStreetMap com do IBGE (que é fornecido pelo estados) foi revisada e diferenças (em 2 de julho de 2023) pequenas (abaixo de 1% para área). Vide histórico em <https://t.me/OSMBrasil_Comunidade> para detalhes (TL;DR obrigado [Fidelis Assis](https://www.openstreetmap.org/user/Fidelis%20Assis)!)**

- https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Leia_me.pdf
- (por verificar, aqui tem a nível intramunicipal)
  - https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/26565-malhas-de-setores-censitarios-divisoes-intramunicipais.html
    - https://ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/15774-malhas.html?=&t=downloads


- **(acessível apenas se estiver acessando da página web em https://fititnt.github.io/openstreetmap-vs-dados-abertos-brasil/)**
  - [relatorio/temp_divisao-administrativa-municipio_ibge.csv](relatorio/temp_divisao-administrativa-municipio_ibge.csv)
  - [relatorio/temp_divisao-administrativa-uf_ibge.csv](relatorio/temp_divisao-administrativa-uf_ibge.csv)
  - [relatorio/temp_divisao-administrativa-municipios.f-osm.csv](relatorio/temp_divisao-administrativa-municipios.f-osm.csv)
  - [relatorio/temp_divisao-administrativa-uf.f-osm.csv](relatorio/temp_divisao-administrativa-uf.f-osm.csv)
  - [relatorio/temp_divisao-administrativa-uf.osm-vs-ibge](relatorio/temp_divisao-administrativa-uf.osm-vs-ibge)
  - [relatorio/temp_divisao-administrativa-municipios.osm-vs-ibge](relatorio/temp_divisao-administrativa-municipios.osm-vs-ibge)

<!--

## Estradas
- https://servicos.dnit.gov.br/

### Nomes de estradas
- https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/28971-base-de-faces-de-logradouros-do-brasil.html?=&t=downloads
-->

## População de divisões político-administrativas

> TODO: por fazer

## Mapeamento de campos entre fontes governamentais e OpenStreetMap
### Identificadores _unicos_

- ref:CNES
  - https://taginfo.openstreetmap.org/keys/ref%3ACNES#overview
  - https://wiki.openstreetmap.org/wiki/Key:ref:CNES
- ref:vatin ("CNPJ" no Brasil)
  - https://taginfo.openstreetmap.org/keys/ref%3Avatin
  - https://wiki.openstreetmap.org/wiki/Key:ref:vatin
  - Veja também:
    - [operator:ref:vatin (?)](https://taginfo.openstreetmap.org/keys/operator%3Aref%3Avatin#values)
    - [not:ref:vatin](https://taginfo.openstreetmap.org/keys/not%3Aref%3Avatin#values)
- ref:INEP
  - https://wiki.openstreetmap.org/wiki/Key:ref:INEP

# Veja também

### Projeto de [Fidelis Assis](https://www.openstreetmap.org/user/Fidelis%20Assis)
- http://gpsutil.com/DifLimitesMunicipaisOSMxIBGE.html

# Licença

## Código
Domínio publico

## Dados
### OpenStreetMap
- https://www.openstreetmap.org/copyright

> OpenStreetMap® is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).

## IBGE
> TODO: explicar aqui