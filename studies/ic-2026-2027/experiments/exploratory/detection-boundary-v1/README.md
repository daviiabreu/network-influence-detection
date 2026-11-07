# Piloto de estimabilidade da fronteira — decisão 14

Concluído em 25/09/2026; especificação científica commitada em `c081cee` antes de
qualquer execução. [Rascunho sucessor](../../../research/questions/exploration/2026-09-24-parallel/detection-boundary-preregistration-draft.md).

**Única divulgação do desfecho primário piloto: a*(0,70) está no interior da
grade pré-fixada.** Não se publica seu valor, curvas de AUC, escores ou gates
adicionais. Isso demonstra estimabilidade pontual no piloto; não demonstra
precisão do IC, cobertura, separação de todos os braços nem resultado nos
outros valores de r. O pré-registro permanece rascunho.

[Resumo imutável](run-02/summary.json): execução completa; nove células de força
pareadas, 256 realizações por célula, pelo critério
`|Δmedia lag-1 observado| <= min(0,0003; 0,1 DP de cada braço)`.
As marginais observadas são iguais por construção na máscara compartilhada.
64 treinos/classe e 64 checks/classe, redes distintas no piloto, r=0,70.
13.824 gerações de painel, incluindo avaliações reutilizando sementes para
resolver o matching. São gerações, não réplicas independentes adicionais.

A [primeira tentativa](run-01/failure.json), revisão `c081cee`, chegou à gravação
final em 152,883 s mas falhou no JSON de um `numpy.bool_`. O teste de regressão
foi escrito e falhou antes da correção. A [repetição](run-02/manifest.json),
revisão `5e2a32f`, mudou apenas a conversão para bool nativo, destino e teto
restante (440 s), preservando parâmetros científicos. Terminou em 151,299 s.
Tempo conjunto aproximado: **304,182 s (5,07 min)**; contabilizando 160 s
conservadores para a primeira tentativa, 311,299 s, abaixo dos 600 s fixados.
Não foi repetição motivada pelo desfecho: a falha de serialização impediu a
publicação do bit, e nenhum valor de AUC foi mostrado.

[Auditoria](run-02/audit.json): 27 hashes de entradas conferidos contra a revisão
Git de cada manifesto; 2.176 sementes únicas desta calibração, sem interseção
com 5.248 sementes de pilotos anteriores nem com 31.002 reservas confirmatórias
anteriores. Os ledgers das duas tentativas são idênticos byte a byte. Nenhuma
semente da nova reserva confirmatória foi gerada e nenhum confirmatório rodou.
Os scripts da revisão independente usam outros namespaces; sem ledger de
execução deles não se afirma uma auditoria numérica exaustiva dessas sementes.

Reprodução autorizada nesta entrega foi somente a repetição acima:

```sh
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --project studies/ic-2026-2027 \
  python studies/ic-2026-2027/experiments/exploratory/detection-boundary-v1/run.py \
  --output run-02 --seconds 440
```

O comando recusa sobrescrever o diretório existente. O manifesto inclui
parâmetros efetivos, Python/NumPy/plataforma, lock, módulos e protocolo. Usar a
revisão indicada para reprodução histórica; não alterar resultados completos.
Auditorias posteriores só leem as entradas commitadas e os ledgers.

[Poder reproduzível](power-planning.json), calculado por [planning.py](planning.py),
sem simulação: 2.000 redes independentes/classe, dois eventos por rede e pior
ICC=1; aproximação normal e DP adicional de nuisance de 0,01 resultam em
SE=0,01871, referência simultânea de meia largura 0,0641, poder 97,3% sob AUC
verdadeira 0,80 e 22,6% sob 0,75 para superar o alvo 0,70. Com nuisance DP=0,02,
o primeiro poder cai para 69,1%. São hipóteses de planejamento, não estimativas
obtidas do piloto; não medem precisão em unidades de a.

[Validação de engenharia](validation.md): 153 testes do estudo, ruff, mypy e
wheel/smoke passaram; gate estrutural antes de cada commit. Matriz global
iniciada anteriormente ainda pendente nos testes do workbench. Sem edição do
workbench, push, merge, congelamento ou alegação de novidade.

O núcleo científico inclui os nulos, canais, decomposição, matching estrito,
AUC e motor bootstrap-t. O callback do bootstrap que une resampling, novo
matching e retreino do estudo completo ainda precisa ser integrado e validado
para cobertura/custo antes do congelamento. Um bit favorável não remove essa
pendência. P4 permanece no-go conforme item 15 do coordenador; definição em
log-razão e margem de equivalência foram preservadas no rascunho.
