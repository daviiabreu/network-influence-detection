# Piloto diagnóstico DBLP com blocos menores

O [input congelado](dblp-split-pilot-v3.json) divide somente Q03, Q04 e Q06,
mantendo exatamente os termos e sua união por família. O predecessor é o
protocolo `opinion-dynamics-query-design-dblp-v1` de `dblp-pilot-v1.json`,
arquivo SHA-256 `ba27e7df63193015ac1537a4f796b72d9bc24e5660f47ab6ddad9d9490caabb2`,
usado pelo run privado `dblp-pilot-v2`. O diagnóstico split v3 foi iniciado no
código `c6843ac`.

| Subbloco | Consulta literal |
| --- | --- |
| Q03a | DeGroot OR Friedkin-Johnsen |
| Q03b | linear opinion pool OR opinion pooling |
| Q03c | social influence and opinions |
| Q04a | voter model OR q-voter |
| Q04b | Sznajd OR majority rule |
| Q06a | adaptive network OR coevolving network |
| Q06b | co-evolving network OR coevolution of networks |

A sondagem privada `dblp-q03-timeout90-probe-20260908T022525Z` recebeu HTTP 429
no COUNT após 30,807 s, apesar de timeout de cliente de 90 s. O JSON do QLever
informa `Operation timed out` no filtro de títulos; não é uma contagem vazia.
Corpo original: 8.351 bytes, SHA-256
`47fa9869c024f36c76d4547de4c3a2e06a611618768a391fa20b9da04b3cd9c4`.
Isso motiva medir blocos menores; não comprova antecipadamente que funcionarão.

O adaptador permanece `dblp_sparql_v1` 1.0.0, timeout de 30 s, mesmo host,
intervalo de dez segundos, retries e limite de duas páginas de cem registros
por subbloco. O texto herdado da regra de parada foi alinhado ao limite de duas
páginas. Os demais campos científicos permanecem iguais. O protocolo tem ID
próprio, aponta para o predecessor e não altera aprovações existentes.

A equivalência é lógica: em um grafo fixo, a união dos predicados dos subblocos
é o predicado original. Paginação limitada, ranks locais, sobreposição e mudanças
no grafo impedem afirmar igualdade das observações efetivamente adquiridas.
Não se somam contagens dos subblocos como se fossem publicações distintas;
ausência exige esgotamento e falhas permanecem explícitas. O eventual candidato
completo terá 14 consultas DBLP cobrindo as mesmas dez famílias, não sete.

Validação anterior à execução: protocolo válido, sete IDs ordenados, um ou dois
termos por consulta, união textual exata e URLs aceitas pelo host. SHA-256 do
protocolo canônico: `5e0bb728e6c9c7a8293c2571e8074b2c06c592be198a846ffc658ab77081755d`.
SHA-256 deste input JSON: `efbbbae79b3c508a94004d320ea68c5ae57958e870f3e5c644c2385411a99c80`.
Logs, bytes, lineage e resultados ficam fora do Git no novo run
`dblp-split-pilot-v3`; sua conclusão exige comparação com replay offline.
