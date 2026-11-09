# Propostas de identidade T4, revisão v3 — 24/09/2026

Esta é uma proposta para os 2.130 cartões T4, sem decisão do Research Owner, fusão aplicada, escolha de DOI canônico ou pedido C3. O pacote privado novo está em `/Users/davi/.local/state/research-workbench/identity-t4-audit-20260924-v3/`; v1 e v2 foram preservados. A entrada v2 é o manifesto SHA-256 `0b1a1d8a184840f68902f04104cf539b2cac7c2b5bc139e5f9bab152ff7c7014`. A base C2 v2 continua com SHA-256 `80f4652d855e299ea938dd2f9f8f485583ddae772cc2717f25a8a32b8e7a39d9`.

## Resultado

| Proposta | v2 | v3 |
| --- | ---: | ---: |
| `merge` | 453 | 519 |
| `distinct` | 227 | 227 |
| `defer` | 1.450 | 1.384 |

As 66 mudanças de `defer` para `merge` vieram da categoria `two_dois_without_allowed_proof`: 15 por relação Crossref, 27 por relação DataCite e 24 por DOI conceitual comum no Zenodo. A contagem exata dessa categoria na v2 era **901**, embora o resumo anterior dissesse 902; **835** continuam pendentes. As outras categorias mantiveram a escolha `defer`:

| Categoria da v2 | Antes | `merge` v3 | Ainda `defer` |
| --- | ---: | ---: | ---: |
| Dois DOIs sem prova admitida | 901 | 66 | 835 |
| Evidência além do título insuficiente | 166 | 0 | 166 |
| Conferência/periódico, julgamento necessário | 108 | 0 | 108 |
| Identidade de versões não provada | 72 | 0 | 72 |
| Intervalo de anos entre versões | 69 | 0 | 69 |
| Conferência/periódico com resumos visíveis | 51 | 0 | 51 |
| Intervalo de anos sem resolução | 47 | 0 | 47 |
| DOI com conflito de título | 34 | 0 | 34 |
| DOI com conflito de resumo | 2 | 0 | 2 |

## Prova externa e regra

Consultamos os **1.770 DOIs distintos** dos 1.450 cartões adiados na v2: 71 lotes OpenAlex (todos HTTP 200), 1.770 consultas DOI Crossref (1.309 HTTP 200 e 461 HTTP 404), 221 DataCite (194/27) e 142 Zenodo (132 HTTP 200 e 10 HTTP 410). Um DOI terminado em `.xml` devolveu XML no endpoint Crossref; uma consulta adicional por filtro DOI obteve o JSON correspondente. HTTP 404/410 indica indisponibilidade naquele serviço, sem invalidar o DOI. Os corpos brutos, códigos HTTP, URLs e SHA-256 estão no manifesto e no índice privados. Cada cartão tem uma ficha com IDs e localizações OpenAlex, versões, relações diretas, DOI conceitual, metadados comparados, regra e referências às respostas brutas.

| Força máxima observada nos 1.450 `defer` da v2 | Cartões | Nova proposta `merge` |
| --- | ---: | ---: |
| Forte: relação direta declarada no Crossref/DataCite ou mesmo conceito Zenodo | 128 | 66 |
| Média: mesmo ID de obra no OpenAlex, sem relação direta | 47 | 0 |
| Fraca: concordância de metadados apenas | 849 | 0 |
| Nenhuma concordância suficiente ou prova externa disponível | 426 | 0 |

Os 62 cartões com prova forte ainda adiados têm conflito nos metadados ou exigem julgamento de conferência/periódico. Em 55 cartões, uma localização do OpenAlex lista os dois DOIs sob a mesma obra; o agrupamento é evidência de terceiro e pode errar. Nenhum dos 47 cartões cuja melhor prova era apenas esse agrupamento satisfez simultaneamente título, autoria, ano e resumos. `IsSupplementTo` foi registrado quando apareceu, mas indica material suplementar, não identidade. A interpretação das relações segue a documentação do [Crossref](https://www.crossref.org/documentation/schema-library/markup-guide-metadata-segments/relationships), do [DataCite](https://support.datacite.org/docs/connecting-versions-with-related-identifiers) e dos [campos de localização do OpenAlex](https://help.openalex.org/data/locations/).

A política do Owner, item 7 do registro privado, permite por regra preprint↔versão publicada do mesmo artigo, com autoria compatível e até dois anos, e depósito em repositório da mesma obra. Conferência↔versão estendida em periódico continua exclusivamente por julgamento, com contribuição central e resumo visível. Relação externa não supera conflito de título, autoria, resumo ou tipo de material. Nenhuma cadeia nova de `merge` proposta atravessa um `distinct` no componente.

## Auditoria e carga do Owner

`audit-sample-v3.json` sorteia os cartões por SHA-256 com semente `identity-t4-v3:20260924`. Para cada regra nova, usa a menor amostra de população finita cuja chance de observar zero erro, caso a taxa real seja superior a 2%, seja no máximo 5%. O Owner precisa observar **zero erros** antes de considerar a adoção do respectivo lote.

| Nova regra | Propostas | Amostra |
| --- | ---: | ---: |
| Relação Crossref declarada | 15 | 15 |
| Relação DataCite declarada | 27 | 26 |
| Mesmo DOI conceitual Zenodo | 24 | 23 |
| **Total** | **66** | **64** |

Com pelo menos **60 segundos por cartão não trivial**, a fila operacional contém 1.384 `defer`, 227 `distinct`, os 50 cartões da amostra v2 já prevista e os 64 da nova amostra: **1.725 cartões, pelo menos 28 h 45 min**, antes de pesquisa adicional ou correções. Pela mesma conta, a v2 exigia 1.727 cartões e 28 h 47 min: a amostragem rigorosa desta v3 poupa apenas dois cartões. Se o Owner quiser analisar todos os 2.130 individualmente, o piso permanece **35 h 30 min**. A amostra v2 de 10% não oferece, por si, a garantia estatística de 2% usada aqui.

Permanecem para julgamento os 159 cartões de conferência/periódico, os conflitos de título/resumo e as identidades sem prova suficiente. As duas propostas de split anterior e a correção de ano 1970→1986 registradas na v2 permanecem pendentes, sem alteração da base. Todo o material de revisão e as respostas externas ficam fora do Git; este arquivo público relata apenas contagens, método e limites da proposta.
