# Reconferência das fontes editoriais

Em 16/09/2026, a continuação da auditoria de
[13/09](../2026-09-13/metadata-sources.md) encontrou evidência adicional para
dois dos nove casos sem título. As observações originais e a proposta v5
permanecem preservadas. Esta nota registra identificação bibliográfica; não
registra inclusão, exclusão ou leitura integral dos trabalhos.

## JOIA

A [página da revista](https://ejournal-binainsani.ac.id/index.php/JOIA/article/view/1513)
contém `citation_title` e `citation_doi` no mesmo bloco HTML. O título é
“Levers of Control, Organizational Life Cycle, dan Strategi: Sebuah Pendekatan
Kualitatif”, ligado ao DOI `10.51211/joia.v6i2.1513`. O candidato original é
`metadata.v1.8a79703d6ac027039213a5f9`.

A ferramenta web apresentou timeout, mas uma requisição HTTP local limitada a
30 segundos e dois megabytes concluiu. Foram retidos 21.011 bytes do corpo HTML,
SHA-256 `c7b080bed4995201d015fbe73f4f41b83f252eacf1b20dc03eb2978372db43e2`.
O código HTTP e a cadeia de redirecionamentos não foram registrados
separadamente; não são inferidos nesta nota. A evidência suporta a proposta
`title_resolved`, com fonte `joia-publisher`, host
`ejournal-binainsani.ac.id` e captura `raw_response`.

Uma segunda captura, preservada separadamente, reteve cabeçalhos e dados da
transferência: HTTP 302 para a rota `/JOIA/en/article/view/1513`, no mesmo host,
seguido de HTTP 200. Seus campos `citation_title` e `citation_doi` coincidem
com a primeira captura. O corpo também tem 21.011 bytes, com SHA-256
`3a904ab901efb6b9e442e9035f6e2b03a47a4089353e746e45669db56399e73f`.
O recibo privado `joia-http-recapture-receipt.json`, na mesma pasta dos demais
recibos desta nota, tem SHA-256
`3d42ec41449b8d3b47a5bb131d75930ca9e1be140fe267453e78ef73711b1db5`.
A primeira captura permanece inalterada.

## Resenha em Journal of American History

O [sumário da edição 89(4)](https://www.jstor.org/stable/i355587)
designa explicitamente a resenha como “[Untitled]” e liga essa entrada ao DOI
`10.2307/3092578`, às páginas 1516–1517 e ao resenhista James O. Farmer.
O título do livro aparece em outro campo. A entrada suporta a proposta
`explicitly_untitled`, mantendo título nulo, para
`metadata.v1.b1a486199ea6c6fee2c9a177`.

A evidência disponível é a projeção textual da ferramenta web, linhas
464–474, sem corpo HTTP original. O snapshot completo tem SHA-256
`bd72067421863f95848baa6bbd0cebe37d47d94e72ecfd380eaa74fee56720e3`.
A fonte proposta é `web-jstor-jah-2003`, host `www.jstor.org`, captura
`web_excerpt_transcription`. A designação permite representar a ausência
editorial; não permite inferir a elegibilidade da resenha.

## Africa Today continua pendente

O [sumário primário da edição 65(1)](https://www.jstor.org/stable/10.2979/africatoday.65.issue-1)
mostra o livro resenhado e seu autor, mas não apresenta uma designação explícita
de obra sem título. O acesso ao registro e à opção XML retornou uma página
sem metadados examináveis. O
[registro institucional](https://scholars.cityu.edu.hk/en/publications/book-review-longman-timothy-2017-memory-and-justice-in-post-genoc/)
identifica a resenha, seu DOI e as páginas, mas data a publicação em janeiro
de 2019; o sumário editorial identifica a edição como Fall 2018. A proposta
permanece `defer`. Nem o título do livro nem a falha de acesso serão tratados
como título ou ausência editorial confirmada da resenha.

## Verificação e limite

O recibo privado `audits/editorial-refresh-20260916/capture-validation-receipt.json`,
sob a raiz de continuação `autonomous-review-20260915`, tem SHA-256
`0cd40e723df2451bb78ae0974f1f04b33d026d59551bd056aec65ceb8df306a1`.
Ele reabre as propostas de 13/09 pelo hash, verifica os candidatos e valida
offsets UTF-8, trechos literais e tokens completos de DOI nos bytes retidos.
O horário de modificação local identifica a retenção do arquivo; não é data
HTTP nem data de publicação. Fontes e recibo estão fora de Git, com acesso
restrito.

A política sucessora precisa declarar as duas fontes antes do uso nativo.
Nenhuma decisão Owner ou resolução canônica foi produzida por esta captura.
O conjunto conhecido passa a oferecer propostas fundamentadas para quatro
títulos e quatro designações sem título; o caso Africa Today continua
pendente. A triagem depende dos consumidores versionados e da calibração
correspondente.
