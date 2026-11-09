# Proposta v5: identificação editorial sem título inventado

Recomendo adotar a [proposta v5](opinion-dynamics-systematic-map-v5-proposal.json)
como reparo metodológico do fluxo já autorizado. Ela sucede a v4, conserva a
política de referências e acrescenta somente identificação bibliográfica. Não
muda buscas, critérios de elegibilidade, população, calibração, contagem de obras
ou regras de exclusão. Seu hash canônico é
`b8e6d160a270201e3cb7fb7116d3bfcfb626db4cf8ba2278494b4af80469ba4d`.
O arquivo é uma proposta validável; este commit não contém aprovação nem decisões
Owner sobre os nove registros.

O protocolo de origem dos dados continua sendo v3
(`fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f`),
e o predecessor direto é v4
(`ff8a14178e725983945c049e75181e8eeb1f3cee56a831e714cc78b09245d413`).
O replay deve reabrir as duas transições, sem reescrever o protocolo da aquisição.
As fontes abaixo são apenas fontes de identificação; não são buscas novas nem
comprovam busca suplementar executada.

| Fonte da policy | Host exato | Captura permitida | Uso proposto |
| --- | --- | --- | --- |
| springer-learning | link.springer.com | metadata_projection | Título literal de 10.1023/a:1009902810926 |
| springer-policy | link.springer.com | metadata_projection | Título literal de 10.1023/a:1011486809357 |
| springer-settlement | link.springer.com | metadata_projection | Título literal de 10.1023/a:1024693130590 |
| web-jstor-penn | www.jstor.org | web_excerpt_transcription | Designação [Untitled] de 10.5215/pennmaghistbio.141.1.0092 |
| web-jstor-seer-2013 | www.jstor.org | web_excerpt_transcription | Designação [Untitled] de 10.5699/slaveasteurorev2.91.4.0934 |
| web-jstor-seer-2015 | www.jstor.org | web_excerpt_transcription | Designação [Untitled] de 10.5699/slaveasteurorev2.93.3.0552 |

Os IDs preservam os rótulos dos snapshots já registrados. A proposta não chama
Springer de Crossref, não amplia os hosts por wildcard e não declara um corpo
HTTP disponível quando apenas sua projeção foi preservada. O
[levantamento de 13/09](../preparation/2026-09-13/metadata-sources.md) documenta
método, limitações e hashes; as [propostas originais](../preparation/2026-09-13/metadata-proposals.json)
continuam separadas dos recibos nativos.

Os snapshots Springer retêm citation_title/citation_doi de resposta HTTP200,
mas não o corpo HTML. Seus hashes, respectivamente learning/policy/settlement,
são `4d9baf63a2ad4d4af07767c328cbc9b36ea0370dc0f49485199f16a99e0ae55a`,
`e63c62cc88262e3d7eb8cec09ecb19e20851055a8a36741f758b0177f29fb527` e
`c92ae8fb3017a78960861c62fb66a412c80f84fa23971eeec4902df2182c1fc9`.

Recomendo aceitar as transcrições dos três sumários primários JSTOR somente para
registrar a designação editorial literal, com DOI e páginas vinculados, nunca
para afirmar acesso ao texto integral ou elegibilidade. Os hashes
penn/seer-2013/seer-2015 são
`03796061dad79814382fd5b3b2d72ed80d1f251b4d77afd73a3c9795290dd36f`,
`c44d05516d215eb1b6ef1e18024edb29491e0a02ea6fb6bb70a68fd6dbae2dc3` e
`159a1748d8d3b7d921b1b553f82651ba545a05e22f81e0ebcb26df848aadb733`.
A data de crawl é desconhecida e o HTTP direto local devolveu challenge. A
reprodução garante o que ficou retido, não uma recaptura independente da página.
Título do livro e cabeçalho de resenha continuam campos distintos do título da
obra. A obra explicitamente sem título deve chegar à triagem com título nulo e
essa evidência, sem exclusão antecipada.

JOIA, OUP e Africa Today permanecem pendentes. A projeção JOIA não traz a mesma
confirmação editorial direta dos três Springer; OUP apresenta um cabeçalho de
resenha e mistura autoria do livro com autoria da resenha; a ausência atual de
Africa Today não foi reproduzida. Esta policy não preenche esses três casos por
analogia e não remove nenhuma das nove obras do histórico ou da contagem.

A instrução vigente de continuar o trabalho autoriza implementar e preparar
esse reparo reversível. Não é necessário inventar uma nova hipótese científica
ou pedir uma fórmula de aprovação. A adoção operacional pode citar essa
instrução com seu escopo real, sem afirmar que Davi leu manualmente cada fonte.
O contrato ainda exige decisões exatas e rastreáveis para cada disposição;
esta proposta não as produz. Exclusão de resenhas pelo rótulo, uso do título do
livro como título autoral ou aceitação de evidência para uma conclusão científica
seriam mudanças materiais diferentes e não são recomendadas aqui.

A capacidade completa ainda depende dos sucessores C3/C4 e TaskV4, com nova
validação de tarefas/calibração. O overlay C2 v2, sozinho, não libera triagem.
