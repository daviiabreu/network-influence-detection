# *Africa Today* 65(1): transcrição preparatória do sumário

Em 23/09/2026, consultei o [sumário público da edição no JSTOR](https://www.jstor.org/stable/10.2979/africatoday.65.issue-1) pela projeção textual da ferramenta web (`open`, `response_length=long`), sem login, contorno de acesso ou consulta ao texto integral. A projeção informa que foi rastreada “last week”; não fornece status HTTP, headers nem bytes do corpo editorial. Pode refletir indexação ou cache. Não tentei capturar esse corpo e não criei arquivo de conteúdo restrito.

No bloco abaixo, `Source` identifica a URL consultada; as linhas `L...` transcrevem uma seleção da projeção exibida, com a numeração e a ordem originais. Linhas intermediárias foram omitidas. O bloco, sem as cercas Markdown e com LF final, é o extrato UTF-8 retido nesta nota. Seu SHA-256 é `beffc81b6992f4d799ff60e72002b39fc5db8fb8785b02e8c3664be12e9e45bb`. Esse hash identifica **este extrato anotado**, não uma resposta HTTP do JSTOR.

```text
Source: https://www.jstor.org/stable/10.2979/africatoday.65.issue-1
L104:   8. BOOK REVIEWS
L116:      * [Untitled]
L118: Memory and Justice in Post-Genocide Rwanda by Longman, Timothy (pp. 107-110)
L120: Review by: Andra le Roux-Kemp
L122: https://doi.org/10.2979/africatoday.65.1.08
L124: https://www.jstor.org/stable/10.2979/africatoday.65.1.08
```

No sumário, o marcador `[Untitled]` pertence à entrada da resenha de Andra le Roux-Kemp, páginas 107–110, ligada ao DOI `10.2979/africatoday.65.1.08`. *Memory and Justice in Post-Genocide Rwanda* é o livro resenhado, não um título autoral demonstrado da resenha. A [nota de acompanhamento anterior](africa-today-title-follow-up.md), SHA-256 `5b2d2b42c323e9d30cc2fce14cbf30168d3e90fa0035ec60992f6c54ee7776b5`, já separou essa interpretação da promoção bibliográfica. Esta passagem não resolve a divergência de datas entre fontes nem avalia elegibilidade.

O candidato `metadata.v1.ea8185255c7dc5d57ab30655` (`work.v2.59d8455c664a03aeb09642b5`) continua `proposal_only`, com `finding=no_authorial_title_verified`, no [lote de propostas](../2026-09-13/metadata-proposals.json). A [proposta editorial v5](../../protocol/opinion-dynamics-systematic-map-v5-editorial-refresh-proposal.json), de hash canônico `4c4eda364e780acd86ce367b1d7b7bd5854f4c3352f6f15a01b735a649a568e5`, é `review_candidate`: permite `web_excerpt_transcription` para quatro IDs JSTOR, mas nenhum deles identifica *Africa Today*. O protocolo aprovado em operação não foi alterado; não se pode reutilizar o ID de outro sumário.

Para uso operacional ainda faltam uma emenda de policy **específica desta fonte** e a decisão Research Owner sobre o novo sujeito. Só então uma transição nativa sucessora poderá reter a evidência sob o `source_id` aprovado, com `capture_mode=web_excerpt_transcription`, referência restrita ao artefato, host e permissão/licença, `retrieved_at`, `record_id` da manifestação, token DOI completo, marcador literal e offsets UTF-8 verificáveis de um trecho que vincule DOI e `[Untitled]` à mesma entrada. Essa validação e o recibo de resolução do candidato não ocorreram aqui. Não houve adoção de v5, alteração do corpus/CAS real, de referências canônicas ou de decisão Owner.
