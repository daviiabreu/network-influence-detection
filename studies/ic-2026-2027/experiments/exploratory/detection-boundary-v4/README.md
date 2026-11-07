# Implementação sucessora v4.2 para revisão

Esta pasta contém código de execução, calibração artificial dos critérios,
inventário completo e medição de custo. Não contém congelamento v4, liberação
confirmatória ou resultado de gate. O protocolo v1 permanece imutável.

A especificação vinculante e as decisões de implementação estão em
[amendment-v4-decision-spec.md](../../../research/questions/exploration/2026-09-24-parallel/amendment-v4-decision-spec.md), [amendment-v4-1-revision.md](../../../research/questions/exploration/2026-09-24-parallel/amendment-v4-1-revision.md),
[v4-review-findings.md](../../../research/questions/exploration/2026-09-24-parallel/v4-review-findings.md),
[v4-review-decisions.md](../../../research/questions/exploration/2026-09-24-parallel/v4-review-decisions.md)
e [detection-boundary-amendment-v4.md](../../../research/questions/exploration/2026-09-24-parallel/detection-boundary-amendment-v4.md).

Os scripts abaixo pressupõem a raiz do repositório e
`UV_CACHE_DIR=/private/tmp/uv-cache-v42`. Cada launcher fixa
`OPENBLAS_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1` e `OMP_NUM_THREADS=1`
antes de importar NumPy, inclusive em processos criados por spawn.

## Operações permitidas nesta entrega

`measure_v42.py --output CAMINHO_NOVO` mede somente matching/validação em
quatro blocos por célula B: (0,60;0,70), (0,90;0,70), (0,03;0,50),
(0,30;0,50), (0,03;0,90), (0,30;0,90). Usa `SeedPlan(9001, bloco)`,
N=10.626 e oito workers. O antes usa a fonte isolada de `688ab26`; o depois
usa o solver otimizado e orçamento 96. Os registros `cost-fits-v42-before.json`
e `cost-fits-v42-after.json` vinculam os hashes da fonte realmente executada.
O baseline e o retry preservam orçamento próprio; não há treino ou AUC.

`project_v42.py --output CAMINHO_NOVO` recusa comparações incompletas ou
blocos não pareados. A projeção usa as avaliações do depois, preços históricos
de painel separados, e 96 avaliações para retry não observado. Os registros
v4/v4.1 abaixo permanecem históricos, sem atribuir suas avaliações ao solver novo.


`calibrate_criteria.py --output CAMINHO_NOVO` gera somente dados artificiais,
com 3.000 experimentos de desenvolvimento e 3.000 de verificação. O parâmetro
`--cells` serve para recalibrar denominadores se a regra de substituição de G0
reduzir a alocação. Isso precisa ocorrer antes de G2, nunca depois de seus
resultados. Os arquivos de calibração anteriores permanecem como predecessores.

`measure_v41.py --mode panels --output CAMINHO_NOVO` mede 64 painéis por
operação em todas as famílias/canais, incluindo mobilidade. `--mode fits`
mede oito blocos × três células B: (0,003;0,70), (0,03;0,70), (0,30;0,70).
São somente matching, validação e amplificação: nenhuma fase de treino ou AUC.
Há checkpoint JSONL de cada fit e registro final com taxas, contagens e hashes.
O namespace é de calibração; isto não executa G0. Os scripts anteriores e seus
artefatos de medição ficam como histórico; `measure_cost.py` foi apenas
adaptado à assinatura e ao tamanho de validação v4.1.

`project_v41.py --output CAMINHO_NOVO` usa `panel-cost-v41.json`,
`cost-fits-v41.json` e o inventário original. Se não houver retries na amostra,
cobra o orçamento 64 nos cenários hipotéticos de retry. Decompõe gate e tiers,
com oito workers, reserva de 25% e stencils de covariância apenas em G2.
A projeção não garante recursos nem autoriza execução.

## Execução futura

`run_gate.py --freeze REGISTRO_REVISADO --gate G0` exige um registro externo já
existente. Não cria congelamento e não aceita flag para ignorá-lo. O registro
precisa ter `schema=2`, `status=frozen`, `workers=8`, `blas_threads=1`,
`code` exatamente igual a `source_hashes(study)`, hashes de
`criteria-v43.json` e `inventory.json` em `artifacts`,
`amendment_sha256`, `revision_sha256`, `review_findings_sha256`,
`review_decisions_sha256`, `delta_review_decisions_sha256`, `code_sha256`,
`environment_sha256`, `environment`, `numerical_probe` e
`allocation_binding="post-G0-pre-G2-statuses-sha256"`. Código inclui o plano
de sementes e a regra de alocação. A lista concreta não pertence a esse
primeiro registro. O registro congelado é `freeze-v4.json`.

A ordem é G0 → G1b → G1c → G2 → G2c. G1a é a bateria de identidades unitárias.
Cada estágio requer os anteriores completos e aprovados. `--shard I --shards K`
particiona índices deterministicamente; execute um shard de cada vez com oito
processos locais e a mesma
revisão. O preflight compara a sonda numérica com tolerância absoluta 1e-12,
além de hashes de código e ambiente. `--aggregate-only` lê apenas checkpoints
selados pelo caminho auditado e emite critérios.

A raiz é `~/.local/state/research-workbench/sealed-v4-gate/<hash-do-código>/`.
Há diretórios 0700, arquivos 0600, JSONL de estimativas e acessos, checksums e
checkpoints de 32 painéis. Cada tarefa tem lock exclusivo. A retomada reproduz
somente blocos ainda não concluídos; falhas concluídas permanecem falhas. A
primeira execução de cada estágio vincula seu hash de congelamento. Trocar
critérios e tentar novamente o mesmo estágio é recusado.

G0 informa quais substituições a regra determinística exige. Antes de G2,
`--allocation SEGUNDO_REGISTRO` é obrigatório, mesmo sem substituições.
O segundo registro contém `schema=1`, `stage="post-G0-pre-G2"`,
`freeze_sha256`, `g0_statuses_sha256`, `g2_cells`, `criteria_sha256` e
`g0_gap_binding`, com a contagem observada em 54 ajustes, os parâmetros
posteriores e a probabilidade preditiva conjunta das cotas G2/G2c. O segundo
registro documenta a parada antes de G2 se ela ficar abaixo de 0,80.
`g0_statuses(root)` projeta somente estados; `status_digest` usa JSON ordenado,
separadores compactos e SHA-256. Campos de ajuste ou AUC não entram no vínculo.
O código valida a lista pela regra de substituição, o denominador dos critérios,
os hashes da calibração e a meta conjunta. Em redução, `--criteria ARQUIVO`
seleciona a recalibração artificial vinculada no segundo registro. Os estágios
anteriores continuam vinculados ao primeiro registro imutável.

G2c, retomadas e `--aggregate-only` exigem o mesmo segundo vínculo usado
em G2. Cada tarefa também guarda o vínculo e sua alocação dentro do selo;
a agregação verifica esse registro para recusar shards de outra alocação. Nenhuma substituição
é escolhida por AUC. O segundo registro só pode ser criado após G0.

`run_curve.py --freeze REGISTRO --allocation SEGUNDO_REGISTRO --shard I
--shards K` é o executor dos tiers, condicionado a todos os gates aprovados.
O namespace confirmatório é separado, com CRN entre forças da mesma unidade/r.
O scheduler tem ordem fixa, barreiras entre tiers, manifests imutáveis e
retomada por célula. `--release-at-close` recusa liberação anterior a
2026-10-19T02:59:00Z e publica somente unidades completas com o inventário
D9 inteiro. O fechamento interrompe também bootstrap incompleto. Nenhum
desses comandos foi executado com dados científicos nesta entrega.

O log registra acessos feitos pela API. Permissões 0700 não impedem Davi ou
outro processo sob o mesmo UID de ler os arquivos diretamente: o sistema não
oferece isolamento de confiança entre agentes do mesmo usuário. O runner só permite
liberar curvas confirmatórias após o fechamento; os registros privados de gate
continuam separados. Isso não é isolamento criptográfico de outro processo do mesmo UID.

## Verificação histórica de cda3a92

Na implementação v4 em `cda3a92`: 274 testes do estudo passaram (17,58 s); Ruff check e
format passaram nos 80 arquivos do estudo; mypy passou nos 56 arquivos de
src/tests; check_repository.py passou nos sete checks. Os dois wheels foram
construídos e passaram nos smoke tests de instalação independente.

`just quality` foi também iniciado. Estrutura, lint e tipos de ambos os projetos
passaram, mas a execução completa do workbench foi interrompida após 826,57 s,
com 1.209 testes passados, ainda em
`tests/recovery/test_focused_attempts_backup.py`. Isso não é aprovação da suíte
completa do workbench. O teste não foi removido, alterado ou marcado xfail.
O estudo completo e seus checks foram executados separadamente após os últimos
ajustes. Logs locais: `/private/tmp/ic-boundary-v4-quality.log` e
`/private/tmp/ic-boundary-v4-build.log`.

Os testes novos cobrem lei/identidades em N completo, canais, 24 etapas,
faces/cantos e domínio variável do perfil, limite de avaliações, NaN, secantes
problemáticas, regressões numéricas E6/bloco 7, validação com retry, projeção e
herança dos controles, centralização de variância, alinhamento de índices,
bootstrap com EPs heterogêneos, gaps, namespaces, inventário, retomada, selamento,
integridade e captura privada de stdout/stderr. Os ciclos de desenvolvimento
começaram com testes falhando nos novos contratos; não se alteraram os testes
congelados. O contraponto de linearização preserva explicitamente a falha da
interpretação forte de D11, em vez de escondê-la atrás do teste de vetores.

Na entrega histórica v4.1, a calibração permaneceu `criteria-v4.json`: script e módulo mantêm
os mesmos SHA-256, sem mudança de modelo, critérios ou denominadores. O teste
do deslocamento médio em v4.1 substitui a exigência por realização de D11.
G2c isolado não satisfaz a potência; a redação vigente esclarece que G2 sozinho
atende à meta e G2c complementa a verificação de V_nuis.
A projeção histórica v4.1 é `compute-projection-v41.json`; as anteriores permanecem
artefatos históricos, não alocações. Os testes de engenharia v4.1 e as medições
estão registrados abaixo.

Há um freeze v4. Não há execução científica de G0/G1b/G1c/G2/G2c ou seeds
confirmatórios nesta pasta. Testes unitários sintéticos não são resultados do
gate. Nenhum classificador foi treinado nas medições reais em a>0.

Para shards em hosts diferentes, transportar diretórios de tarefas concluídas
inteiros, preservando modos, hashes, `task-binding` e as autorizações de
estágio da raiz, para a mesma raiz de agregação. O runner
não sincroniza hosts nem transfere automaticamente dados selados. A retomada
usa os mesmos identificadores e recusa mudança do congelamento de um estágio
já iniciado.


## Revisão v4.1 — evidência de desenvolvimento

R1 começou com três falhas (assinatura e tamanho de validação); R2 falhou na
tolerância antiga 0,1 EP. R3 começou sem a entrada de Jacobiana média e sem os
contratos do diagnóstico, e o teste de agregação falhou por ausência da flag.
R6 começou sem o segundo vínculo; as regressões adicionais rejeitam critérios
sem hash de calibração, alteração de vínculo em G2c e revisão literal não
vinculada. R7 começou sem a extração seletiva; 35 combinações válidas de
família/canal/resumo preservam os bytes do extrator congelado em N completo.
R5 já estava implementado: ampliou-se a regressão para matching/validação e
para treino/teste/referência, sem alterar sementes para fabricar um teste red.
R4 e R8 mudam a declaração e o planejamento, sem novos critérios científicos.

O comparador reproduzível `verify_v41.py --output CAMINHO_NOVO` verifica o
snapshot `cost-fit-source-v41.json` contra os hashes da medição. O custo dos
24 fits começou após R1/R2 e a primeira extração seletiva; enquanto corria,
foram implementados D5, G2 e o desvio de cálculo de canais não usados. A
árvore sintática de solver, validação, amplificação, stencils, sementes,
`fit_cell` e checkpoints permaneceu idêntica. Setenta lotes de dois painéis
em N completo comparam o extrator daquele snapshot e o final byte a byte.
A medição por painel usa o extrator final. O stdout do launcher inicial de
fits tinha um resumo herdado de painéis (64×24=1.536); os contadores por fase
do JSON registram corretamente 1.114.112 painéis. O launcher atual imprime
o número de medições, e a projeção usa somente os contadores/arquivos, nunca
aquele resumo de stdout. Não se apresenta hash do arquivo
inteiro anterior como se fosse o hash do arquivo final.

Na revisão final v4.1: 326 testes do estudo passaram (28,87 s); Ruff check
passou e format conferiu 87 arquivos; mypy estrito passou nos 60 arquivos de
src/tests; `check_repository.py` passou nos sete checks. Todas as verificações
usaram `UV_CACHE_DIR=/private/tmp/uv-cache-v41`. A cópia R1–R8 foi comparada
byte a byte com o arquivo fornecido. A especificação D1–D11, a calibração e os
módulos v1 permaneceram inalterados. Logs locais: `/private/tmp/v41-pytest-final.log`,
`/private/tmp/v41-fits.log`, `/private/tmp/v41-panels.log` e
`/private/tmp/v41-verification.log`.

As 24 medições de fit foram válidas, sem retries; avaliações médias
23,625 / 30,625 / 57,750 nas três forças. O maior consumo foi 63/64 avaliações.
As 76 operações de painel cobrem 4.864 painéis. O cenário de retry medido
projeta gate=93,98 h, tiers 1–5=185,36 h e tier 6=42,81 h, oito workers e
reserva de 25%; total com bootstrap=322,44 h. A auditoria de custo corrigiu
G2c para cobrar a regeneração efetiva da referência social em cada tarefa,
sem supor cache entre diretórios; o predecessor da projeção foi preservado.
São projeções condicionais, com cenários de retry 25% e 100%, não execução
nem alocação de recursos. Todos os tiers permanecem.

O erro do deslocamento médio foi 2,0371%. A regressão sintética R1 observou
411/3.000 falsas falhas pela regra antiga e 0/3.000 pela nova. O diagnóstico
G2 de covariância usa uma aproximação de AUC gaussiana por momentos; essa
interpretação e seu limite estão explícitos na emenda. Os hashes do script
e módulo de critérios são os mesmos de `criteria-v4.json`; não houve
recalibração sem mudança dos critérios. Nenhum freeze, gate científico,
treinamento/AUC real em a>0, semente confirmatória ou push nesta revisão.


## Revisão v4.2 — decisões e evidência

As duas revisões fornecidas foram copiadas byte a byte. A emenda PT-BR foi
atualizada por seção, inclusive a edição histórica de `detection_panel.py`
posterior ao freeze v1 e sua evidência de identidade. O solver conserva a
tolerância e validação v4.1, usa predição pela Jacobiana na âncora, solução
interna inexata apertada antes da aceitação, Illinois externo e 96 avaliações
por tentativa. Regressões cobrem endpoints sem passo, residual de fronteira
não centralizado e dependência observada ausente/falha.

`criteria-v42.json` é o sucessor recalibrado: falhas Bernoulli independentes a
1% em G2/refits G2c, cotas 5/100 e 14/700, 3/100 e 2/40, medianas FD por
célula. Limiares G2 por célula 0,497601373848/1,287913779846; agregados
0,818380973934/1,054506540701. Em 3.000 experimentos de verificação, G2
aprovou 2.959 com EP correto e 130 com EP×0,8; G2+G2c aprovou 2.855 e 97.
A aprovação conjunta correta é 95,1667%, MCSE 0,3916 pp, próxima da meta;
é condicionada à disponibilidade dos baselines G2c e ao modelo declarado.
Não se confunde essa estimativa com garantia de aprovação do gate real.

`seed-role-audit-v42.json` auditou 13.129.728 materiais, sem colisões, incluindo
G1b/G1c/G2c e oito fases/namespaces. Os testes de identidade acrescentam
128 casos em N completo, nas duas tentativas e fases acopladas, verificando
máscara, valores medidos/observados e atributos selecionados byte a byte.
Os testes do runner usam fixtures e relógio controlado: nenhum gate ou
curva confirmatória foi executado.


As medições finais têm 24 fits por versão, quatro blocos em cada uma das seis
células, sem treino ou AUC. O baseline validou 19/24 (quatro budgets e uma
lacuna de perfil); o otimizado validou 22/24 (uma lacuna de perfil e uma
ill-conditioned). Nos 18 pares validados em ambas as versões, a média caiu
39,3333 → 23,1667 avaliações. Os seis pares restantes continuam contabilizados.
O solver novo usou no máximo 42/96 avaliações, sem retry observado.

[compute-projection-v42.json](compute-projection-v42.json) usa 23,1818
avaliações iniciais, o maior valor entre a média de todos os fits e a dos
validados, mais orçamento 96 para retry não observado. Com oito workers e
25% de reserva, projeta 256,04 h no cenário amostral, 725,61 h com 25% de
retry e 2.134,34 h com 100%. São hipóteses condicionais, com todos os tiers;
as contagens por célula e a decomposição estão na emenda e no JSON.

[revision-verification-v42.json](revision-verification-v42.json) preserva as
fontes efetivamente medidas e verifica seus hashes, as rotinas de matching
contra o código final, critérios dos fits aceitos e validação, a linhagem da
auditoria de sementes e os bytes dos dois documentos fornecidos. Executar
`verify_v42.py --replay-evidence revision-verification-v42.json --output CAMINHO_NOVO`
reproduz a verificação sem depender dos snapshots temporários. Mudanças de
orquestração durante a medição não são atribuídas à fonte medida: as rotinas
de matching e seus geradores são verificadas separadamente. As duas execuções
se sobrepuseram no host; a comparação de eficiência usa avaliações, não parede.

Depois das 48 medições, a recalibração artificial foi reproduzida em
`/private/tmp/v42-criteria-post-measurement.json` e comparada byte a byte com
`criteria-v42.json`, sem reescrever o artefato concluído. Os limiares e as
características operacionais coincidiram integralmente.

Verificação final v4.2: 508 testes passaram em 45,38 s; Ruff check passou e
format conferiu 99 arquivos; mypy estrito passou nos 67 arquivos de src/tests;
`check_repository.py` passou nos sete checks. Todos usaram
`UV_CACHE_DIR=/private/tmp/uv-cache-v42`. O replay da evidência preservada
passou sem ler os snapshots temporários. Logs locais:
`/private/tmp/v42-pytest-final.log`, `/private/tmp/v42-repository-final.log`,
`/private/tmp/v42-calibration-final.log`, `/private/tmp/v42-verification-final.log`
e `/private/tmp/v42-verification-replayed.log`.
A regressão de concorrência reproduziu a descoberta de shards antes do lock
da raiz; o fechamento agora adquire esse lock antes de listar shards e não
pode perder uma execução registrada simultaneamente. Nenhum freeze, gate,
curva confirmatória, treino/AUC real ou push foi executado nesta revisão.
