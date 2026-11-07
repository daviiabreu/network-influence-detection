# Checagem da correção externa de confiabilidade

24/09/2026. Protocolo anterior à execução, autorizado pelo pedido de incorporar
a decisão 13 e verificar a mudança em no máximo dez minutos. Sucessor ligado
ao [piloto original](../redesign-calibration-v1/README.md), sem sobrescrever
qualquer entrada ou saída. A [emenda](../../../research/questions/exploration/2026-09-24-parallel/decision-13-amendment.md)
vincula os hashes do log e do dossiê. Não é confirmação de hipótese.

O seletor original consulta somente r=0,80. Esse braço, o kernel, as features,
a geometria e o matching não mudaram: não há motivo para refazer a busca do
ponto de operação. Preservar a=0,4 e rho=0,838961863215152, selecionados no
piloto original. Fixar externamente r=0,70; não ajustar r, rho ou força após
olhar o gate. A grade principal futura é {0,65;0,70;0,75;0,80}; sensibilidade
complementar {0,50;0,55;0,60;0,85;0,90}. Não rodar essa grade confirmatória aqui.

Executar 96 painéis por classe para treino do discriminante e 96 por classe
para checagem (384 trajetórias ao todo). Reusar as interfaces científicas já
testadas, sem mudar os mecanismos. Sementes conforme SHA256 original, com as
fases `primary-train` e `primary-check`, mas índices `10000+2*i+classe`,
i=0,...,95. São exclusivamente sementes de desenvolvimento/calibração, apesar
do nome histórico da fase. Papéis: state, network, events, mask, error.
Conferir interseção zero com todo o piloto original (incluindo P4) e com os
31.002 inteiros confirmatórios reservados, sem executar confirmatórios.

Exportar apenas `0,55 < BA < 0,95`, junto aos diagnósticos permitidos de
matching marginal e lag 1. Não exportar BA, acertos, escores, diferença contra
r=0,65 ou r=0,80, nem qualquer valor de contraste primário. Se o gate falhar,
registrar falha e parar; não escolher outra confiabilidade ou força.

O executor grava revisão, ambiente, hashes de entradas/código, parâmetros,
ledger dos hashes de trajetórias/respostas, auditoria de sementes e tempo.
Diretório existente é recusado. Teto de parede: 590 segundos, abaixo dos
600 segundos autorizados; timeout gera registro incompleto. Executar uma vez.
O braço secundário ancorado e P4 não serão simulados neste lote.
