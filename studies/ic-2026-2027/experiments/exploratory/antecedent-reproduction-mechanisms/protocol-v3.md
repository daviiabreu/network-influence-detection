# Correção da implementação do par projetado

24/09/2026. Sucessor de `protocol-v2.md`. O teste linear do microcaso já
passava, mas o ramo projetado computava a mesma soma algébrica da regra de
trio em vez de percorrer as três arestas por incidência. A implementação agora
acumula separadamente cada contribuição de par. Matemática, parâmetros,
sementes e critério de análise não mudam. Preservam-se as saídas v1 e v2;
`controls-results-v3.json` é a primeira execução do lote com a projeção
pareada implementada independentemente. A mudança foi feita antes de usar
o resultado para recomendar continuação ou descarte.
