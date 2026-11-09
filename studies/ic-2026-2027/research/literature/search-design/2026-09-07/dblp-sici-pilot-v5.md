# Diagnóstico final DBLP: Q04b com DOI SICI

O [input congelado](dblp-sici-pilot-v5.json), criado em 2026-09-08, contém
somente `search.dblp.q04b`, com a consulta literal `Sznajd OR majority rule`.
Preserva o objeto de busca, os limites de duas páginas de 100 registros e o
corte científico de 2026-09-07. Seu predecessor é
`opinion-dynamics-query-design-dblp-multidoi-v4`.

A execução ocorreu no código `0a6379601980ac3f6c8e58ff20a26cad63cf0bc8`, que
integra a correção da validação de identificadores DOI. Foram mantidos o
adaptador `dblp_sparql_v1` versão `1.0.0`, o timeout de 30 segundos e o intervalo
de 10 segundos. Nenhum outro bloco foi repetido e não houve consultas após
esse diagnóstico.

| Página | Registros | Total informado | Exaustão | SHA-256 do corpo combinado |
| --- | ---: | ---: | --- | --- |
| 0 | 100 | 129 | Não | `d6f5ae1af111ebd76bdcddfa6da18162d0c62a1618d27dab5f08ab17333570be` |
| 1 | 29 | 129 | Sim | `06e8e16341a26e3a83a1837f58f9ec2da049d0b83edc373fec2cb7a777a1ac53` |

Q04b terminou `complete`, com 129 IDs de registro distintos, sem duplicatas
ou sobreposição entre páginas. Os IDs da primeira página coincidem com a
página preservada no v4; as publicações da segunda coincidem com o corpo
diagnóstico final daquele predecessor. Isso não estabelece isolamento de
snapshot entre consultas.

O registro `dblp.dabd8969d181a05fbc0128b3`, correspondente a
`journals/rsa/FangV98`, foi retido na posição 110 com seu DOI SICI. A correção
preserva a representação codificada do identificador, convertida para
minúsculas como antes; não autoriza nova navegação pelo DOI.

Os 16 pares semente/consulta ficaram `not_found_in_page_budget`: zero
encontrados e zero incompletos, sem bloqueadores. A flag
`recall_is_assertable=true` pertence apenas a este diagnóstico esgotado.
Ela não resolve a incompletude de Q06a no v4 nem estabelece recall científico
da revisão inteira.

O replay reproduziu os resultados online byte a byte. Os 12 arquivos do run
mantiveram bytes e mtimes, e os runs predecessores não foram alterados. Os
corpos, journals, lista completa de IDs, lineage e prova de replay permanecem
fora do Git na raiz privada `claude-handoff-20260907/dblp-sici-pilot-v5` e nos
arquivos derivados de auditoria no diretório pai.

| Evidência | SHA-256 |
| --- | --- |
| Protocolo canônico | `0c9e992bf0dc5bdc5873e0c343116d71963e4022b0dfa4c1a2a4845ef3fcc4a8` |
| Bytes do input | `b0e290d1ddc0acd1b9b946b769f5e0849fe7ade6d2175e419c40ca41e8b5d64d` |
| Resultado canônico | `8bcea4e3ee39f7e950a174603b0533416edf5204378d3f94778bb43c88add540` |
| Bytes dos resultados online/offline | `60e5001cc153c0476c797625603a1fb50697e8bf0da94c671e2ea2423135a988` |
