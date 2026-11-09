# Dois cartões de identidade novos após C2 v2 — auditoria preparatória

O [sucessor C2 v2](c2-v2-execution-result.md) recuperou os títulos de duas
obras que agora aparecem em pares antes ausentes da fila. Esta nota examina
**somente esses dois cartões** para uma futura pergunta humana; não é decisão
C3, escolha de identificador nem autorização de fusão. A base de propostas
`proposal_basis_v2` tem SHA-256
`80f4652d855e299ea938dd2f9f8f485583ddae772cc2717f25a8a32b8e7a39d9`;
o manifesto da geração 3.2.0 tem SHA-256
`9bc03a05b79664a7a7e9cb574415f5370bc88580a24af166cac2ac3befc0555c`
e o `cards.json` privado, `f2302b6c99e84097f4e18bb5dda2e5138fee744220cfd3992ccc8f8e877104ea`.
O pacote passou de 20.964 pares/10.754 cartões para 20.966/10.756; os dois
acréscimos são `T4.contradicting_identifiers`.

| Cartão e obras | Indícios observados | Limite que mantém T4 |
| --- | --- | --- |
| `dedupe.overlay.5011fc1f9b546869d1f61425` — `work.v2.26bfa8f4d833cac14f231b10` (`10.1023/A:1011486809357`) e `work.v2.82f87bcf6e0e7f87ec26d3d1` (`10.1080/13876980108412655`) | Título normalizado *The Social Psychology of Policy Analysis*, periódico e ano 2001 coincidem. A projeção primária da [página Springer](https://link.springer.com/article/10.1023/A:1011486809357) registra vol. 3(1), pp. 85–112; SHA-256 da projeção `e63c62cc88262e3d7eb8cec09ecb19e20851055a8a36741f758b0177f29fb527`, do corpo informado nela `5097cbfdedd17760e821045782b3e8697b9eec909fe9e55db4f605ad7ecd420d`. | São dois DOIs registrados distintos, sem identificador compartilhado ou declaração primária capturada de equivalência. A fonte Springer escreve `Thorngat`; a observação do DOI `10.1080/...` escreve `Thorngate`, por isso o cartão calcula `surname_jaccard=0`. A página da editora do DOI alternativo não foi validada nesta passagem. |
| `dedupe.overlay.4677796495e6f5077983d72a` — `work.v2.865d2d66bc0f1e37fddcaaf0` (`10.1111/j.1571-9979.1998.tb00171.x`) e `work.v2.e152588b3504fa1bf0b39a4c` (`10.1023/A:1024693130590`) | Título normalizado *When Settlement and Resolution Are in Conflict: Searching for a Mideast Peace Dividend*, periódico e ano 1998 coincidem; `surname_jaccard=1` e similaridade numérica de resumos `0.983607` no cartão, sem reproduzir seu texto. A projeção primária da [página Springer](https://link.springer.com/article/10.1023/A:1024693130590) registra vol. 14(4), pp. 357–367; SHA-256 da projeção `c92ae8fb3017a78960861c62fb66a412c80f84fa23971eeec4902df2182c1fc9`, do corpo informado nela `6a9a43266151235f133d562dfad14be31ee19107edd88cabca7c30af5c3726ba`. | Também há dois DOIs registrados distintos e nenhum identificador compartilhado. A projeção Springer não declara o DOI `10.1111/...` como alias; a página da editora desse DOI alternativo não foi validada nesta passagem. Similaridade de metadados e de resumos não estabelece identidade editorial. |

As observações dos DOIs alternativos vêm das capturas OpenAlex já adquiridas,
de SHA-256 `393172e239c0ba868702d7d1c427649670daa31f6466fc78d4bf6a9c1bea6711`
(`10.1080/...`) e
`a8c2b091bf6544251799b5548459cfc37ece7c03d2e34edd3efbe35331437b0f`
(`10.1111/...`). Elas vinculam DOI, título, autoria, periódico e ano, mas
não são confirmação primária de uma relação entre os dois DOIs de cada par.
Os títulos das obras C2 foram promovidos a partir das páginas Springer;
a coincidência posterior dos títulos nos cartões não é uma segunda prova
independente de alias. Os corpos brutos indicados nas projeções não foram
reabertos nesta auditoria.

Na geração atual, cada cartão contém apenas seu par de obras, cada obra dos
quatro IDs aparece em somente um cartão, e a fila original não continha
candidato de identidade para nenhuma das quatro observações. Não há caminho
T1/T2 para ampliá-los por transitividade nesta base. Isso **não** elimina o
conflito de identificadores se uma fusão futura for proposta: a escolha de DOI
canônico e a preservação dos dois registros-fonte exigiriam exame próprio.

**Proposta à revisão humana:** manter os dois cartões pendentes em T4. A
hipótese de `merge` é plausível nos dois pares, mais forte no par de *Settlement*
pelos metadados concordantes, mas ainda não é uma escolha adotável nesta nota.
Antes de propor `merge`, conferir em fonte editorial ou depositária primária
o DOI alternativo, sua paginação e eventual relação explícita entre os DOIs;
se a evidência demonstrar itens diferentes, propor `keep_separate` com o
vínculo exato da divergência. Sem essa verificação, não registrar nenhum dos
dois valores como decisão. Nenhum C3, C4, triagem ou aceite científico decorre
desta auditoria.
