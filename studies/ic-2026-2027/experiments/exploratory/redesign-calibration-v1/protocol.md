# Protocolo exploratório de calibração v1

24/09/2026. Sucessor dos desenhos em `decision-memo.md`; preserva as críticas
em `claude-memo-critique.md`. Autorização: pedido de Davi nesta sessão para
redesenhar P1+P2 e P4, implementar com TDD e executar somente pilotos de até
1.200 segundos somados. Este protocolo precede toda execução científica nova.
Não é registro confirmatório nem seleção canônica de questão.

## Regra anterior ao contraste

P1+P2: painel de 11 ondas, 10.626 pessoas sintéticas (7.084 entram em t=0,
3.542 em t=5), perda permanente por domicílio de duas pessoas de 0,11/ano.
Todos continuam no processo latente; entrada e perda afetam apenas observação.
A geometria é aproximada, não uma máscara SHP extraída. Marginais normais
padronizadas iguais por transformação de postos em cada onda. Núcleo social:
AR de coeficiente 0,85 mais deriva de confiança limitada em rede aleatória
fixa, limiar 1 desvio-padrão, inovação normal de DP sqrt(1-0,85²). O controle
é AR sem influência, com rho ajustado ao lag 1 latente do social, exclusivamente
em 16 painéis de calibração por mecanismo. Repulsão não entra no primário.

A grade ordenada de força social é 0,025; 0,05; 0,1; 0,2; 0,4; 0,8.
Para cada ponto, 48 painéis/classe treinam um discriminante linear de
covariância comum com shrinkage 0,2, sobre correlações ordinais de lags 2–5.
Outros 48/classe avaliam SOMENTE o braço baseline de confiabilidade 0,8.
Escolher o primeiro ponto cuja acurácia balanceada baseline esteja em
[0,68;0,82], com diferença de lag 1 latente <=0,01. Se nenhum servir, v1
falha; não escolher o máximo nem consultar o primário para desempatar.
Confiabilidade é Var(latente)/Var(latente+erro) antes da discretização:
normal independente de DP sqrt((1-r)/r), 11 categorias equiprováveis sob a
marginal normal, limiares fixos para cada r. 0,5–0,8 é faixa PROVISÓRIA
fornecida no pedido, pendente de fonte e transportabilidade. Primário r=0,65.

Só depois da seleção: treinar 96/classe em sementes novas para r=0,65 e
verificar 96/classe em outras sementes. Exportar apenas o booleano
0,55 < BA < 0,95, nunca BA, acertos, escores ou diferença entre mecanismos.
Também registrar adequação marginal e lag 1, que são critérios de matching.
Não recalibrar força, features, r ou tamanho pelo booleano primário.

P4: N=198, duas partições aleatórias em trios (grau 2), rejeitar grupos
repetidos e redes desconectadas. Atualizações síncronas de ganho 0,1, 100
passos; esta unidade substitui as tentativas focais do memo. 70% inicialmente
perto de 0,2, 30% perto de 0,8, DP 0,05. Fonte verdadeira 1 em 20 destinatários
fixos sorteados, depois de cada passo, ganho/dose d. Lock-in finito: >=50%
abaixo de 0,5 em TODOS os últimos 20 passos; resolvido: >=90% acima de 0,75
nessa janela; restante não resolvido, sempre incluído no denominador.

Calibrar somente projeção não linear, lambda=-1, 48 realizações pareadas
(rede e semente), grade d=0;0,01;0,02;0,04;0,08;0,16;0,32;0,64;1.
Exigir Pr(lock)>=0,9 no início e <=0,1 no final e monotonicidade dentro de
0,10. Refinar por cinco bisseções ao redor do cruzamento 0,5. Conservar toda
a grade e bisseções. O estimador usa regressão isotônica decrescente e
interpolação linear no cruzamento 0,5; sem cruzamento, limiar censurado.
Depois, em 48 sementes novas e na grade escolhida, verificar apenas se cada
braço não linear tem pelo menos um ponto com 0,1<Pr(lock)<0,9 e se ambos
cruzam 0,5. Não exportar taxas, limiares ou diferenças dos braços avaliados.
A grade final é compartilhada. Linear e disjunto são identidades testadas por
TDD, não contrastes procurados em piloto. A diferença dos limiares HN-PN é
primária; o 2x2 e os horizontes 50/200 serão controles confirmatórios futuros.

## Separação, limites e evidência

Sementes derivadas de SHA256 de `ic-redesign-v1|fase|papel|índice`, primeiros
8 bytes big-endian. Fases de piloto: match, operating-train, operating-check,
primary-train, primary-check, dose-calibration, dose-check. Rede, estado,
eventos, erro e máscara têm papéis distintos. Nenhuma dessas sementes pertence
aos namespaces reservados confirm-train, confirm-validation, confirm-test,
confirm-robustness. Redes de treino e avaliação também são disjuntas.

O runner deve registrar SHA de código/lock/protocolo/configuração, HEAD,
Python/NumPy/plataforma, sementes deriváveis, número de simulações e tempos;
recusar sobrescrever uma saída. Publicar diagnósticos de calibração completos,
mas apenas gates grosseiros para células primárias. Arrays de avaliação não
são persistidos; reprodução regenera os booleanos. Uma falha não autoriza
procurar outro contraste. Prazo máximo acumulado dos pilotos: 1.200 segundos;
interromper entre réplicas e registrar saída incompleta se ultrapassar.

NumPy foi acrescentado somente ao estudo (antes `dependencies = []`) para
operações vetorizadas dos painéis de dez mil pessoas, covariância de quatro
features, solução linear e operadores síncronos dos trios. O lock independente
registra a versão resolvida; não há SciPy, sklearn nem dependência no workbench.
