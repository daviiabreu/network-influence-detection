# Evidência primária dos DOIs alternativos — preparação

Sucessor da [auditoria dos dois cartões C2 v2](c2-v2-new-identity-cards-audit.md),
limitado aos dois DOIs alternativos. Consultas independentes em 24/09/2026,
por leitura pública da ferramenta web e uma checagem comum no navegador
integrado; tentativas de terminal não alcançaram Crossref por falha de DNS.
Esta nota registra somente metadados bibliográficos públicos e limites de
acesso, sem texto integral, resumo transcrito, decisão de identidade ou
execução C3/C4.

## Par *Policy*

| Fonte e URL exata | Método em 24/09/2026 | Evidência observada e limite |
| --- | --- | --- |
| [Springer Nature, `10.1023/A:1011486809357`](https://link.springer.com/article/10.1023/A:1011486809357) | Leitura pública da página editorial pela ferramenta web. | *The Social Psychology of Policy Analysis*, Warren `Thorngat` (grafia da fonte), *Journal of Comparative Policy Analysis*, junho de 2001, volume 3, páginas 85–112 e DOI `10.1023/A:1011486809357`. A página consultada não declara `10.1080/13876980108412655` como segundo DOI ou alias. A [auditoria anterior](c2-v2-new-identity-cards-audit.md) vincula a projeção Springer ao SHA-256 `e63c62cc88262e3d7eb8cec09ecb19e20851055a8a36741f758b0177f29fb527`. |
| [Taylor & Francis, `10.1080/13876980108412655`](https://www.tandfonline.com/doi/abs/10.1080/13876980108412655) | Abertura direta pela ferramenta web; inacessível neste ambiente. O [resolvedor DOI](https://doi.org/10.1080/13876980108412655) também não abriu. | Título, autoria, volume, páginas e eventual relação com o DOI Springer não puderam ser confirmados na editora. A falha de acesso não demonstra inexistência do registro. |
| [Crossref REST, DOI alternativo](https://api.crossref.org/works/10.1080/13876980108412655) | Abertura pública pela ferramenta web inacessível; uma checagem comum no navegador integrado retornou `ERR_BLOCKED_BY_CLIENT`, e o terminal não resolveu o host. | Os metadados depositados pelo registrante, inclusive `author`, `volume`, `issue`, `page`, `relation` e `update`, não foram lidos. Não se verificou vínculo explícito entre os DOIs. |

A observação do DOI `10.1080/...` no pacote adquirido é do OpenAlex; sua
grafia `Thorngate` difere de `Thorngat` na página Springer. A semelhança de
título, periódico e ano registrada no cartão é hipótese bibliográfica, não
confirmação primária da paginação ou de alias para o DOI alternativo. O par
`dedupe.overlay.5011fc1f9b546869d1f61425` permanece pendente em
`T4.contradicting_identifiers`.

## Par *Settlement*

| Fonte e URL exata | Método em 24/09/2026 | Evidência observada e limite |
| --- | --- | --- |
| [Springer Nature, `10.1023/A:1024693130590`](https://link.springer.com/article/10.1023/A:1024693130590) | Leitura pública da página editorial pela ferramenta web; conteúdo bibliográfico acessível. | *When Settlement and Resolution Are in Conflict: Searching for a Mideast Peace Dividend*, Abdelmagid M. Mazen, *Negotiation Journal*, volume 14, páginas 357–367, outubro de 1998. A citação editorial e o campo DOI apontam explicitamente para `10.1023/A:1024693130590`. A página consultada não declara `10.1111/j.1571-9979.1998.tb00171.x` como segundo DOI, alias ou outra manifestação. A página marca o conteúdo do artigo como sujeito a assinatura. |
| [Wiley Online Library, `10.1111/j.1571-9979.1998.tb00171.x`](https://onlinelibrary.wiley.com/doi/10.1111/j.1571-9979.1998.tb00171.x) | Abertura direta pela ferramenta web; URL inacessível neste ambiente. A variante pública `/doi/abs/` também não abriu. | Nenhum título, autor, volume, número, paginação ou vínculo entre DOIs foi validado diretamente na página editorial da Wiley nesta passagem. A falha de acesso não demonstra inexistência do registro. Não houve tentativa de contornar a restrição. |
| [Crossref REST, DOI alternativo](https://api.crossref.org/works/10.1111%2Fj.1571-9979.1998.tb00171.x) | Consulta pública `GET /works/{doi}` pela ferramenta web; URL inacessível. Uma chamada de terminal não alcançou o host por falha de DNS. | O depósito do registrante para o DOI alternativo não pôde ser inspecionado. Portanto, seus campos `author`, `volume`, `issue`, `page`, `relation`, `update` e eventual redirecionamento de alias permanecem não verificados aqui. |
| [Crossref REST, DOI Springer](https://api.crossref.org/works/10.1023%2FA%3A1024693130590) | Consulta pública `GET /works/{doi}` pela ferramenta web; URL inacessível. | Os campos de relação e atualização do depósito deste DOI também não foram verificados nesta passagem. |
| [Documentação Crossref de conflitos e aliases](https://www.crossref.org/documentation/reports/conflict-report/) | Leitura pública da documentação pela ferramenta web. | A Crossref descreve três possibilidades para metadados coincidentes: registros duplicados do mesmo item, itens distintos com metadados escassos, ou metadados incorretos. Alias formal requer designação de DOI primário e redirecionamento do outro identificador. Essa regra não constitui evidência de que este par específico já tenha tal relação. |

A [auditoria anterior](c2-v2-new-identity-cards-audit.md) registra título normalizado, periódico e ano coincidentes nos dois cartões, `surname_jaccard=1` e similaridade numérica de resumos `0.983607`. Para o DOI `10.1111/...`, a observação ali era uma captura OpenAlex, não confirmação editorial ou depositária primária. A confirmação atual da Springer sustenta a bibliografia do DOI `10.1023/...`; a ausência de leitura primária da Wiley e dos depósitos Crossref impede confirmar a paginação e a autoria do DOI alternativo por fonte primária ou estabelecer uma relação explícita entre os dois identificadores.

**Estado preparatório conjunto:** manter também o par
`dedupe.overlay.4677796495e6f5077983d72a` pendente em
`T4.contradicting_identifiers`. Não escolher DOI canônico nem registrar `merge`
ou `keep_separate` em nenhum dos dois pares com base nesta consulta. Para
propor uma dessas escolhas, verificar por acesso normal uma página editorial
ou um depósito primário dos DOIs alternativos, com autoria, volume, páginas e
eventual relação explícita entre identificadores. Se o acesso continuar
indisponível, registrar a lacuna; não contornar o bloqueio, inferir alias pela
coincidência de metadados ou alterar as observações de origem.
