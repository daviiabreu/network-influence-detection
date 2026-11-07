# Correção de calibração antes da interpretação da candidata 1

24/09/2026. Sucessor de `protocol.md`, sem apagar `controls-results.json`.
O controle estático inicial usou a média de probabilidades apenas no instante
inicial de 32 réplicas independentes. Isso não estima a exposição esperada
durante a trajetória adaptativa como exigido pelo memo. A comparação inicial
fica como diagnóstico de desenho, não resultado para decidir a candidata 1.

Mantêm-se sementes, grafo, estados iniciais, regra, fonte, 120 oportunidades,
desfechos e os três braços de `protocol.md`. Para o controle estático esperado,
as 32 sementes de calibração 9001–9032 percorrem 120 oportunidades adaptativas
com o mesmo calendário de fonte. Antes de cada evento, registra-se o vetor de
probabilidades de exposição. A média dos 3.840 vetores é congelada para cada
braço estático das oito réplicas de avaliação 101–108. Nenhum estado, matriz
realizada ou desfecho da avaliação entra na calibração. Não haverá ajuste após
ler o sucessor. A correção é necessária para o estimando, não uma busca de
sinal favorável.

Na reprodução de Dong, `antecedents-results.json` também foi preservado:
herdou `K=0,3` do construtor, enquanto o limiar calculado pressupunha `K=1`.
`antecedents-results-v2.json` executa a mesma configuração com `K=1`, como
nos scripts numéricos do arquivo dos autores.
