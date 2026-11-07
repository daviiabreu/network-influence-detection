# Crítica independente do memo de decisão (Claude, 24/09/2026)

Revisão independente de `decision-memo.md` (commit `aead1d6`), feita por um
agente Claude em contexto separado. Os scripts e saídas das reproduções estão
em `~/.local/state/research-workbench/memo-critique-20260924/`; cópias das
saídas ficam em `review-memo-evidence/`. Hashes no `MANIFEST.sha256` daquele
diretório. As reproduções são leituras do texto do memo, não implementações
aprovadas.

## Defeitos demonstrados

1. P1 está no teto na célula principal. Com os parâmetros das linhas 44–46 do
   memo, a repulsão leva 76% dos agentes às fronteiras até a onda 4, contra
   menos de 1% no modelo DW; a acurácia balanceada é 1,000 para L1 e L2 com
   canal conhecido ou ignorado (`p1_primary.out`). O contraste principal é
   zero porque o memo não iguala as marginais dos dois mecanismos.
2. O contraste "conhecido − ignorado" da P1 compara treino correto com treino
   mal especificado: a direção é garantida assintoticamente e o tamanho depende
   só do σ escolhido (lacuna em L2 de 0/7/10/37 pontos para σ = 0,1/0,2/0,3/0,5,
   `p1_diag.out`).
3. P4 está no teto: Pr(travamento) = 1,00 nos quatro braços, interação zero
   (`p4_ceiling.out`).
4. A margem da P3 é inalcançável: o efeito total do acoplamento é −0,0087,
   menor que a margem de +0,01; a diferença adaptativo × uniforme é ≤ 1e-4
   (`p3_bound.out`).
5. A tabela de custos contradiz as medições do próprio memo: uma execução da
   P4 leva cerca de 25–29 ms, e uma trajetória da P1 cerca de 2,2 ms. Computação
   não é o caminho crítico.

## Riscos não demonstrados

O capítulo de Carpentras e Quayle (2026) e o texto integral de Dong et al.
não foram lidos. A P4 pode depender da normalização. A busca de novidade durou
um dia e foi feita só em inglês.

## Consequências para a escolha

Uma versão refutável da P1 precisa de parâmetros que o pesquisador não escolhe:
par de mecanismos igualado nas marginais, geometria real de painel e faixa de
confiabilidade publicada. O plano de 48 horas precisa de uma regra de ponto de
operação declarada antes dos dados e cega ao contraste principal. A ordem
recomendada é: estudo sintético ancorado P1+P2; P4 com estimando de dose
crítica, condicionada à leitura do texto de Dong; P2 empírica bloqueada por
acesso; P3 encerrada. Condição de parada em 48 horas: sem âncora de
confiabilidade, ou se Carpentras–Quayle 2026, Alwin ou Hill já contiverem o
contraste, mudar para a P4.

## Governança

A carta exige síntese aceita antes da pergunta final, e o mapa amplo não
termina até 31/10. A opção recomendada, adotada por Davi em 24/09, é desacoplar:
selecionar a pergunta do artigo a partir da evidência exploratória e de uma
revisão focada de trabalhos relacionados, protocolada e declarada, mantendo o
mapa amplo como entrega separada.
