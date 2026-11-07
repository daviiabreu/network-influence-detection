# Emenda anterior ao congelamento — decisão 13

24/09/2026. Base do rascunho: `418be2d`. O pedido de Davi nesta sessão manda
incorporar a decisão 13 do coordenador, sob a delegação explícita registrada
na decisão 10. Isso atualiza o rascunho; não transforma a decisão do agente em
ratificação pessoal de Davi nem autoriza experimentos confirmatórios.

O log conferido é
`/Users/davi/.local/state/research-workbench/owner-decisions-20260924-session-log.md`,
SHA-256 `da05b2baf86d3359e5561ac9033f490f690d2d772f016856fa9319a27fb70ed1`.
O [dossiê copiado sem alteração](reliability-and-prior-art.md) tem SHA-256
`1c51a797520f6e168d1743195d1fb6a69c0fd6d45e238c57e2e0df4c52f5c08a`,
idêntico ao original indicado na decisão. As leituras e lacunas bibliográficas
são as declaradas pelo autor do dossiê, não uma nova revisão integral feita
nesta emenda.

A decisão mantém P1+P2 como principal após avaliar a condição de parada de 48 h,
com três exigências: nenhuma ancoragem à opinião inicial no braço principal;
confiabilidade fixada externamente em 0,65–0,80, centro 0,70, e sensibilidade
0,50–0,90; interpretação como distinção de padrões dinâmicos, sem detecção de
influência social. Registra sobreposições parciais fortes com Kiley–Vaisey,
Lersch e Moor-Smith–Carpentras e a lacuna de leitura de Carpentras–Quayle 2026.
O veredito de continuidade do coordenador não é prova de novidade.

O rascunho anterior fixou provisoriamente r=0,65 ANTES do piloto; o piloto não
estimou nem escolheu r. A mudança para 0,70 é uma correção externa anterior ao
congelamento, motivada pela decisão 13 e pelas fontes, não pelo valor ou sinal
do contraste primário (que continua oculto). O registro executado a r=0,65
permanece imutável. A faixa nova é transportada de outros itens/desenhos;
não é uma estimativa direta da confiabilidade de `P$$P04`.

O código `latent_panel` de `0e2d8ee` usa `rho*values` da onda anterior, sem
consulta à opinião inicial na atualização. A normalização R_N iguala marginais,
mas não devolve pessoas a seus postos iniciais. Logo, não é preciso trocar o
kernel principal. A variante com retorno à opinião inicial é especificada como
braço secundário no [rascunho](redesign-and-preregistration-draft.md), com
implementação e pilotos ainda não executados.

O critério de seleção do ponto de operação consulta apenas o baseline r=0,80,
que não mudou. Mantêm-se a=0,4 e rho=0,838961863215152. Não repetir a busca
nem recalibrar rho ou r pelo resultado novo. A
[checagem sucessora](../../../../experiments/exploratory/reliability-correction-v1/protocol.md)
usa sementes exploratórias novas para verificar só o gate de não teto/piso
em r=0,70, em até 600 segundos. P4 e as sementes confirmatórias permanecem
intocados.
