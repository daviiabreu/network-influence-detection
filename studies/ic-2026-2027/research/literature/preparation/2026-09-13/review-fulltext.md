# Revisão independente da preparação de texto completo

Data local: 13/09/2026, America/Sao_Paulo. Candidato: [fulltext-preparation.md](fulltext-preparation.md), 2988 bytes, SHA-256 `4ff44df4927f9edf5e9e8126cb4160ee478c7c53212409a7988b681f4431691f`. Nenhum achado acionável dentro do escopo de identidade bibliográfica, licença declarada, recibos e reprodução estrutural. Não foi revisado o conteúdo científico do PDF nem a qualidade de uma futura extração.

## Vínculo bibliográfico e versão

O arquivo privado `broad-research-20260911/calibration-preparation-v3-20260913/case-bindings.json`, SHA-256 `31421b39e86e7f41e54a222f513fdafb4107075a1897c85f319d86170a2f1ef0`, vincula V3-29 à obra proposta `work.v2.e618414ee47714dd46aca671` e à observação `observation.e65db6d02136166dc2ac9f1cc1c09f40ac650c9a4867aeef7246bf4b3830d492`. O `FullTextRecord` preserva exatamente esses identificadores.

A deduplicação CAS `41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53` inclui essa observação nas duas manifestações propostas da obra, com identificador `arxiv:2508.17711`, tipo preprint e ano 2025. Na projeção bibliográfica CAS `772afb69e868ef3fc6cf94e79d3c1b422f11f8fba453621c0092fc65028fa5a1`, a observação aponta para a página Atom `1a386c3b65757a0bddec89d93a2120aa2ae99203edd51b11c72628a280c99a2e` (95582 bytes). Os três hashes foram conferidos antes da consulta de metadados.

A página Atom contém uma única entrada `http://arxiv.org/abs/2508.17711v3`, com atualização em `2025-09-16T07:17:30Z`, título *Enhancing LLM-Based Social Bot via an Adversarial Learning Framework* e os seis autores citados no candidato. A versão e a atualização coincidem com a alegação; a data é anterior ao corte de 07/09/2026 do protocolo. Na [página versionada arXiv](https://arxiv.org/abs/2508.17711v3) retida, os metadados bibliográficos concordam e o link de download é `/pdf/2508.17711v3`. A correspondência foi verificada contra os bytes preservados, sem adquirir outra versão.

## Licença, recibos e integridade

A página versionada contém uma âncora `class="has_license"`, com título `Rights to this article`, apontando para `http://creativecommons.org/licenses/by/4.0/`. A página HTTPS de [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) retida se identifica como *Deed - Attribution 4.0 International*. A atribuição, o identificador versionado, o URL da licença e a nota de transformação estão em `FullTextRecord.acquisition.license_note`; o registro vincula essa nota ao PDF e à projeção por seus hashes. A projeção textual isolada contém páginas e proveniência do parser; a atribuição é carregada pelo registro associado.

Todos os hashes e tamanhos abaixo foram recalculados sobre os arquivos preservados. Para PDF, projeção e registro, os bytes CAS também foram conferidos; o PDF CAS é idêntico ao arquivo privado.

| Artefato | SHA-256 | Bytes |
| --- | --- | ---: |
| Página arXiv v3 | `2a8a21d7b1452fde03e00d0a102fd4c36ba62d0685112bb5b7b05086dcd51cf9` | 43055 |
| Página CC BY 4.0 | `231a5dac65bbf135ba27145969a63cd289faadc172f1512c4810a6c60ba91036` | 32178 |
| PDF | `a7eea3ee9fbdaf40403b2a0fc5de2c2fd780021aa853fef0aecff01c2c986f0c` | 11640818 |
| Projeção | `bb25c8ac262e16494419451688283308cd23baba82226de7dbac44b45d878713` | 105413 |
| `fulltext-record.json` | `ac9adff69ca7c58bee0882a38b2b9df1aa54a014ca707dc9baac2e57e4c07396` | 2047 |
| `source-receipts.json` | `de8ad476f10e47d5c9034a1395f26a38dcd724b07bf6d44aa393ad4460716339` | 1687 |
| `ingestion-summary.json` | `7ae580c4040028b7be613e214bcece5631c160a8065b99fa49c222aec1fa698c` | 1082 |
| `acquire_and_ingest.py` | `20af779032682dfe89d8fa099ba859eaf22756f2e2f40eb5c3db5e9618fdfce3` | 6006 |

As fontes e os recibos estão em `/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/fulltext-v3/`. O recibo registra HTTP 200 para as três aquisições e URLs finais iguais às solicitadas. Os horários UTC em 14/09/2026 correspondem a 13/09/2026, 21:33:01–21:33:18 em America/Sao_Paulo, coerentes com o candidato. Esta revisão conferiu o registro e os corpos preservados; não repetiu as requisições nem observou a sessão HTTP original.

## Ingestão e limites da conclusão

`FullTextRecord` e `FullTextProjection` passaram pela validação dos contratos atuais. A reprodução independente com `resolve_full_text_evidence` releu o PDF CAS, executou o parser nativo existente e exigiu igualdade de todas as páginas com a projeção armazenada. O resultado foi `available`, parser `pypdf-6.17.0-plain-strict-v1`, 26 páginas não vazias e título concordante na primeira página. O locator estrutural reproduzido aponta à página 1, linha 1, da projeção `bb25c8ac262e16494419451688283308cd23baba82226de7dbac44b45d878713`; nenhum trecho foi escolhido como referência de uma resposta científica.

O hash semântico do protocolo, calculado por `review_protocol_sha256`, é `fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f`. O hash da política de texto completo é `dd35968dac9deea3d16449dd924a444cacecdc06da0a5e2d22b4898a3b804e17`, igual ao registro. Os limites correspondem aos valores nativos do contrato. O script retido usa `ingest_full_text` e a revisão de código informada, `b1f8bea6574137ce176ddfd5aecab5d158e93c1f`, coincide com o HEAD observado. A revisão não reexecutou a aquisição ou a ingestão que escreve no CAS.

As duas seleções privadas consultadas contêm 50 entradas e 50 obras propostas distintas. Na seleção inicial, V3-29 tem `full_text: null` e `include_extraction: false`; na seleção sucessora `calibration-preparation-v3-extraction-20260913/corpus-selection.json`, SHA-256 `316b118739cb6e6eebd3b7cebe748d805124bda4523a7fb9e404a7c5278b62e7`, seu registro de texto completo é idêntico ao revisado e `include_extraction` é verdadeiro. Isso sustenta a preparação de um caso entre os 50, não a disponibilidade de 50 textos completos. O sumário de ingestão mantém `reference_extraction: null`, `human_references_authored: false` e `locator_check_is_human_reference: false`.

O candidato não atribui elegibilidade, positivo de referência, fidelidade de extração ou calibração concluída. A ressalva sobre fórmulas, tabelas e figuras é coerente com o [processo de ingestão](../../../../../../docs/process/systematic-review-full-text.md). Esta revisão somente verificou metadados e propriedades estruturais da projeção pública; não avaliou o conteúdo científico, não executou modelos ou suíte completa e não alterou o candidato, protocolo, corpus ou decisões humanas. O hash do candidato foi reconferido ao encerrar.
