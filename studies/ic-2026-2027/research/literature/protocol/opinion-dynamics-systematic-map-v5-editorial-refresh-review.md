# Proposta v5: revisão das fontes editoriais

Esta [revisão da proposta v5](opinion-dynamics-systematic-map-v5-editorial-refresh-proposal.json)
substitui, para avaliação, a [proposta inicial](opinion-dynamics-systematic-map-v5-proposal.json),
cujos bytes e hash `b8e6d160a270201e3cb7fb7116d3bfcfb626db4cf8ba2278494b4af80469ba4d`
permanecem preservados. A revisão tem hash canônico
`4c4eda364e780acd86ce367b1d7b7bd5854f4c3352f6f15a01b735a649a568e5`.
Ambas são rascunhos da mesma emenda v5, sucessora da v4; nenhuma delas
constitui uma aprovação ou decisão Owner. A aquisição continua vinculada à v3.

A única diferença para a proposta inicial é a inclusão de duas fontes de
identificação, verificadas em capturas primárias retidas em 16/09. As seis
fontes anteriores, seus modos de captura, buscas, critérios de elegibilidade e
política de referências ficam iguais. Recomendo esta revisão como reparo
representacional dentro da instrução vigente de continuar o trabalho. Essa
base operacional não afirma que Davi inspecionou as fontes manualmente.

| Fonte acrescentada | Host exato | Captura permitida | Evidência disponível |
| --- | --- | --- | --- |
| joia-publisher | ejournal-binainsani.ac.id | raw_response | citation_title e citation_doi literais de 10.51211/joia.v6i2.1513 |
| web-jstor-jah-2003 | www.jstor.org | web_excerpt_transcription | Designação [Untitled], DOI 10.2307/3092578, páginas e autoria da resenha no sumário primário |

A captura JOIA conserva o título “Levers of Control, Organizational Life Cycle,
dan Strategi: Sebuah Pendekatan Kualitatif”. A primeira resposta tem hash
`c7b080bed4995201d015fbe73f4f41b83f252eacf1b20dc03eb2978372db43e2`;
a recaptura com headers/status/redirects tem corpo de hash
`3a904ab901efb6b9e442e9035f6e2b03a47a4089353e746e45669db56399e73f`.
O recibo da recaptura, de hash
`3d42ec41449b8d3b47a5bb131d75930ca9e1be140fe267453e78ef73711b1db5`,
registra HTTP200 após redirecionamento no mesmo host. As duas capturas concordam
nos campos bibliográficos; a futura escolha nativa deve apontar os bytes exatos
que usa, com seus próprios offsets, sem reaproveitar offsets entre capturas.

Para o caso OUP/JAH, o [sumário primário JSTOR](https://www.jstor.org/stable/i355587)
identifica a resenha como [Untitled], por James O. Farmer, páginas 1516–1517,
e liga o DOI completo. O título do livro resenhado não é promovido a título da
resenha. A transcrição retida tem hash
`bd72067421863f95848baa6bbd0cebe37d47d94e72ecfd380eaa74fee56720e3`.
Esse modo preserva a projeção textual da ferramenta, sem afirmar que seu corpo
HTTP original foi capturado. A designação permite propor `explicitly_untitled`
com título nulo, e não excluir a obra antes da triagem.

O recibo de conferência dos candidatos, DOI completos e offsets UTF-8 tem hash
`0cd40e723df2451bb78ae0974f1f04b33d026d59551bd056aec65ceb8df306a1`.
As capturas e os recibos continuam privados; esta revisão publica apenas
metadados e hashes. Identificação bibliográfica não comprova busca suplementar,
texto integral disponível, qualidade ou elegibilidade.

Africa Today permanece `defer`: o sumário consultado nomeia o livro e seu autor,
mas não designa a resenha como sem título. A divergência entre a data de um
registro institucional e o fascículo também permanece registrada. Nenhuma obra
é apagada, nenhum título é inventado e nenhuma decisão Owner é produzida aqui.
O caminho operacional ainda requer replay C2/C3/C4 versionado e validação
explícita de TaskV4 antes da produção; esta proposta não declara calibração nem
aceitação científica.

## Atualização de 24/09

O estado acima registra a revisão da proposta na data em que foi escrita. Davi
depois [aprovou os bytes exatos desta emenda](../../decisions/2026-09-24-editorial-metadata-policy-v5.md),
sem aprovar escolhas individuais ou resultados. Uma
[conferência posterior de Africa Today](../preparation/2026-09-24/africa-today-source-policy-proposal.md)
encontrou o marcador no sumário JSTOR, mas a fonte específica não integra os
bytes aprovados; sua escolha continua `defer` e exige sucessor próprio.
