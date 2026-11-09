# Africa Today: evidência conferida e proposta mínima de fonte

Em 24/09/2026, a projeção textual do [sumário primário JSTOR de Africa Today
65(1)](https://www.jstor.org/stable/10.2979/africatoday.65.issue-1) voltou a
associar `[Untitled]` ao DOI `10.2979/africatoday.65.1.08`, à resenhista Andra
le Roux-Kemp e às páginas 107–110, nas linhas 116–124. O achado sustenta propor
`explicitly_untitled`, com título nulo. Não constitui resolução de metadados,
decisão de elegibilidade, aprovação da v5 ou decisão C2 do Research Owner.

## Evidência e limites

A [transcrição retida em 23/09](../2026-09-23/africa-today-issue-toc-evidence.md)
foi reaberta localmente. O bloco UTF-8, sem cercas Markdown e com LF final,
tem 348 bytes e SHA-256
`beffc81b6992f4d799ff60e72002b39fc5db8fb8785b02e8c3664be12e9e45bb`,
igual ao hash publicado. O arquivo da nota tem SHA-256
`95b579e8075626561b998e15b9b8324263409f28dcd5977fe4cef5c616c2b76b`.
Esses hashes identificam, respectivamente, um extrato anotado e sua nota;
nenhum identifica um corpo HTTP do JSTOR.

A conferência atual usou `open` na URL pública, sem login ou texto integral.
A ferramenta informa rastreamento na semana anterior; sua projeção pode
refletir cache. Não foram observados status HTTP, headers ou corpo original.
Não foi criado um novo snapshot privado nem publicado qualquer trecho privado.
O resultado atual concorda com a transcrição histórica, mas não aumenta sua
classe de captura. [Fonte: sumário JSTOR](https://www.jstor.org/stable/10.2979/africatoday.65.issue-1).

Uma checagem direta adicional em 24/09 obteve `HTTP/2 200` e
`content-type: text/html` no `HEAD`, mas o `GET` devolveu uma página intitulada
`Client Challenge`, sem a entrada bibliográfica. Portanto, o status 200 não é
uma captura da evidência, e esse corpo não pode receber os offsets acima.

## Rota primária alternativa

O [depósito institucional da autora na University of Lincoln](https://repository.lincoln.ac.uk/articles/journal_contribution/Memory_and_Justice_in_Post-Genocide_Rwanda_Timothy_Longman_2017_/24377542)
oferece o [registro público de API](https://api.figshare.com/v2/articles/24377542)
e um PDF identificado como `file_id=42789661`, com licença CC BY 4.0. O PDF
baixado de [seu endereço oficial](https://ndownloader.figshare.com/files/42789661)
tem 495.002 bytes e SHA-256
`e97e829e1ee9bd55c0425cadfdc799bbf181c417b38f2f1e0eae163ddb9fdecc`.
A folha de rosto de Project MUSE o identifica como resenha de *Memory and
Justice in Post-Genocide Rwanda* por Timothy Longman, em *Africa Today* 65(1),
pp. 107–110, e aponta para `https://muse.jhu.edu/article/715788`. A página
seguinte traz o DOI `10.2979/africatoday.65.1.08` no rodapé editorial. A
própria resenha começa com a referência do **livro**, sem um título autoral
separado; a p. 110 a assina como Andra le Roux-Kemp. As páginas relevantes
foram inspecionadas no PDF, inclusive visualmente. O registro de API vincula
autora, periódico, volume e páginas, mas deixa o campo de DOI vazio.

Essa fonte primária corrobora a identidade da resenha e mostra por que a
descrição catalográfica do livro não deve ser automaticamente promovida a
título autoral. Ela não contém o marcador literal `[Untitled]` exigido pela
disposição `explicitly_untitled`; portanto, não substitui sozinha o sumário
JSTOR no contrato C2 v2. O arquivo desta conferência está apenas em
`/private/tmp`, que é efêmero, e ainda não há `ArtifactRef` nativo. A página
oficial Project MUSE redirecionou para `/verify`, sem metadados examináveis;
não se tentou contornar essa proteção.

A [nota de acompanhamento](../2026-09-23/africa-today-title-follow-up.md),
de SHA-256 reconferido
`5b2d2b42c323e9d30cc2fce14cbf30168d3e90fa0035ec60992f6c54ee7776b5`,
separa o título do livro do título da resenha e registra a divergência entre
Fall 2018 no fascículo e janeiro de 2019 na fonte institucional. A divergência
continua aberta; a fonte institucional não foi recapturada nesta passagem.

O lote privado em
`/Users/davi/.local/state/research-workbench/autonomous-review-20260915/metadata-source-bound-proposals-20260916/choices.json`
foi reaberto somente em leitura. Seu SHA-256 continua
`eeff79017bbf1bd25a7f886128e87916713a3e383eca249422d151ef48264553`;
Africa Today permanece `defer`, com `evidence=null`. O [índice do lote](../../../../../../docs/research/systematic-review-metadata-proposals.md)
descreve sua proveniência. A interpretação posterior não reescreve essa escolha.

## Emenda proposta

A [política editorial v5 aprovada](../../protocol/opinion-dynamics-systematic-map-v5-editorial-refresh-proposal.json)
tem SHA-256 reconferido
`4c4eda364e780acd86ce367b1d7b7bd5854f4c3352f6f15a01b735a649a568e5`.
Suas oito fontes não contêm uma identificação específica para este sumário.
Recomendo acrescentar apenas o objeto abaixo à lista ordenada
`metadata_resolution_policy.sources`, antes de `web-jstor-jah-2003`, em um
novo sucessor proposto, preservando os bytes aprovados da v5:

```json
{
  "capture_modes": ["web_excerpt_transcription"],
  "hostnames": ["www.jstor.org"],
  "source_id": "web-jstor-africa-today-2018",
  "untitled_designations": ["[Untitled]"]
}
```

O escopo bibliográfico desta fonte é o sumário
`https://www.jstor.org/stable/10.2979/africatoday.65.issue-1`.
O contrato de policy vincula ID, host, modo e designação; a URL exata pertence
à evidência C2. Compartilhar o host não permite usar o ID de outro sumário.
A autoridade continua `bibliographic_identification`, e
`source_protocol_sha256` continua
`fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f`.
Busca, elegibilidade e as oito fontes existentes não precisam mudar.
[Contrato C2 v2](../../../../../../docs/specs/editorial-metadata-resolution.md).

A v5 exata foi [aprovada em 24/09](../../../decisions/2026-09-24-editorial-metadata-policy-v5.md)
sem esta fonte. A adição exige, portanto, outro protocolo sucessor da v5,
versão e cadeia próprias, e aprovação separada; não se pode alterar os bytes
aprovados nem trocar a policy de uma resolução existente.

## Próximo passo concreto

Preparar um novo artefato privado source-bound com a transcrição e recibo de
proveniência, sob a fonte proposta, antes de pedir qualquer decisão sobre a
escolha. Deve vincular o candidato `metadata.v1.ea8185255c7dc5d57ab30655`,
a obra `work.v2.59d8455c664a03aeb09642b5` e a manifestação
`observation.5c9272239df1810851ae74ea74c294fa27e1fe986d691b913f7e03e22e081b59`,
conforme o [registro preparatório original](../2026-09-13/metadata-proposals.json).

No extrato histórico verificado, o marcador ocupa bytes `[105,115)` e a
primeira ocorrência do DOI completo ocupa `[257,284)`. São offsets deste
extrato específico, nunca de uma página HTML ou de outra captura. Um futuro
`linkage_excerpt` deve conter ambos e o contexto da mesma entrada. A evidência
precisa ainda de `ArtifactRef` restrito, `retrieved_at` verificável, URL exata,
permissão e licença documentadas, identificador canônico e validação nativa dos
bytes. Não preencher esses campos por inferência nem usar a data de hoje como
horário da consulta histórica. [Contrato de evidência](../../../../../../workbench/src/research_workbench/workflows/systematic_review/metadata_evidence.py).

Esta passagem para na lacuna de retenção: a raiz privada durável não foi
gravada; o PDF está apenas em armazenamento temporário, e não foi localizado um
recibo privado da consulta de 23/09 com horário exato e referência nativa. O
extrato anotado verificável permite preparar a emenda, mas não substitui esses
vínculos. Se for necessária uma captura manual permitida, abrir o
[sumário exato](https://www.jstor.org/stable/10.2979/africatoday.65.issue-1),
preservar fora de Git o bloco da entrada com `[Untitled]`, resenhista, páginas
e DOI, e registrar URL, instante real da transcrição, modo de captura,
permissão/licença e hash. Importar esse arquivo create-once no CAS restrito,
recalcular offsets **nos bytes importados** e validar o vínculo no contrato
`MetadataSourceEvidenceV2`. Se o navegador também apresentar desafio, registrar
a falha; não contorná-lo nem preencher proveniência fictícia. A nova policy
precisa de aprovação Git-bound; depois, `prepare_request` pode validar a escolha
sem publicá-la. A decisão Owner sobre o request exato e a execução C2 são
transições posteriores. Até lá, o lote permanece `defer` e o corpus incompleto.
