# Evidência das decisões 16 e 17

Entrega em 25/09/2026, exclusivamente exploratória. Código científico final:
`9fe4264ce0dbf9774ada0eed306b9f95f89d8fb8`; implementação inicial da correção:
`2bb2e91`. Nenhum experimento confirmatório nem nova AUC científica foi calculado
nesta validação. O [pré-registro congelado](../../../research/questions/exploration/2026-09-24-parallel/detection-boundary-preregistration-frozen.md)
define o plano futuro e suas condições de execução.

## RED → GREEN e escopo

Os arquivos em `red/` preservam saídas reais anteriores à implementação.
Falhas de importação por API inexistente e falhas de asserção constam sem edição.

| Comportamento | Evidência RED |
| --- | --- |
| Persistência dependente de estado | `state-null.txt` |
| Matching conjunto observado L1/L2 | `observed-matching.txt` |
| Logit, piso de EP e endpoints degenerados | `logit-band.txt`, `nested-null-and-endpoints.txt` |
| Fronteira sustentada e gate nulo | `boundary-gate.txt` |
| Bootstrap por rede + quadratura sem dividir variância por K | `quadrature.txt` |
| Runner com alvos observados, controles por canal e nulo C | `runner-channels.txt` |
| Mover–stayer, estilos de resposta e deriva por tenure | `decision17-channels.txt` |
| Limite de viabilidade | `feasibility.txt` |
| Discriminador exclui os dois lags pareados | `runner-scores.txt` |

A atualização manual com ρ≠0 e ruído já passou na implementação existente;
é regressão adicional, não reivindicação de RED. Os testes preservam também
|g|=1, sinal da repulsão, momentos dos nulos e corr²(w,z)=r antes da ordenação.
O controle rank observado e a função morta log_dose_ratio foram removidos.

Validação do código final: **166 testes passaram em 7,55 s**; ruff check e
format --check passaram; mypy src tests passou; build isolado e smoke do wheel
do estudo passaram. Comandos a partir da raiz:

```sh
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --directory studies/ic-2026-2027 pytest -q
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --directory studies/ic-2026-2027 ruff check .
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --directory studies/ic-2026-2027 ruff format --check .
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --directory studies/ic-2026-2027 mypy src tests
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 ./scripts/build_and_smoke.sh studies/ic-2026-2027 ic_study /Users/davi/.local/bin/uv
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --project studies/ic-2026-2027 python scripts/check_repository.py
```

O check_repository passou antes de cada commit de implementação. A matriz
integrada `just quality` foi iniciada uma vez; seu estado final é registrado
na entrega, sem converter o verde do estudo em aprovação de toda a plataforma.
Não houve edição de workbench nem mudança de dependências nesta emenda; NumPy
já está declarado e travado no estudo para álgebra e simulação vetorizadas.

## Checagem cega, sem discriminador

[matching-run-01/summary.json](matching-run-01/summary.json): somente a=0,
r=0,70, N=10.626, onze ondas, 256 realizações. O matching conjunto observado
atingiu as duas tolerâncias; 2.048 painéis gerados, 105,50 segundos. Não houve
treino, teste de discriminação, AUC ou fronteira calculada. Isso verifica a
operação do matching nesse ponto, não a cobertura, a grade completa nem a
interioridade da fronteira do mecanismo corrigido.

[manifest.json](matching-run-01/manifest.json) registra código, ambiente,
parâmetros e 25 hashes; [seed-ledger.json](matching-run-01/seed-ledger.json)
registra as sementes realmente usadas. [audit.py](audit.py) verificou os bytes
contra os blobs da revisão do código e 1.280 sementes únicas contra 7.136
sementes dos ledgers históricos de painéis: interseção zero. O
[audit.json](matching-run-01/audit.json) delimita o universo auditado; não é
prova sobre scripts externos sem ledger nem enumera reservas confirmatórias.

O bit de interioridade divulgado em cb457af pertence ao desenho anterior.
Não reaproveitá-lo como prova de não-teto/não-piso do principal agora com
repulsão, matching conjunto e L3–L5. A exposição anterior está no pré-registro.

## Precisão sob hipóteses explícitas

[precision_planning.py](precision_planning.py) e
[precision-planning.json](precision-planning.json) usam verdades artificiais
conhecidas, namespace próprio e 100.000 sorteios por cenário. Com 2.000 redes
por classe e banda de nove células por r, crítico normal 2,7729, a probabilidade
de IC válido cobrindo a fronteira e com largura ≤um passo é 99,0%/84,3% para
AUCs adjacentes 0,62/0,78 e DP nuisance 0,01/0,02. Para 0,66/0,74 é 43,9%/19,2%;
para 0,58/0,82 é 99,5%/99,4%. Hipóteses: erros normais independentes entre
células, curva declarada e EP conservador; não são resultados científicos
observados nem garantia da banda bootstrap efetiva.

## Validação paralela e bloqueio de execução

A branch `research/boundary-bootstrap-validation`, consultada no commit
`e1b458590d3e82239e7e68ef3a3df1169d5722a3`, acrescentou código de validação,
sem resultados commitados nessa revisão. Seu gerador de quatro características
gaussianas e bootstrap aninhado não validam o novo procedimento com matching
observado em dois momentos, L3–L5, clusters de escores fixos e 40 refits.
Nenhum resultado não commitado foi promovido a evidência de cobertura aqui.
A frente paralela recebeu a especificação corrente por nota de coordenação;
não duplicamos a rodada dela nem integramos código incompatível.

O congelamento é autorizado pelo pedido explícito de Davi, com cobertura em
a=0 obrigatória antes da execução confirmatória. Cobertura corrente está
**pendente**, não aprovada. Seu plano, critérios e necessidade de nova emenda
se falhar estão no pré-registro. Congelamento não é ratificação nem licença
para iniciar sementes confirmatórias.
