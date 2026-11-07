# Pacote de reprodutibilidade científica da IC

Este diretório prepara o pacote científico separado da fonte LaTeX, montada
pela tarefa H. O empacotador copia uma seleção explícita de código e artefatos,
confere SHA-256 e tamanhos, conserva ambientes por revisão e permite verificar
o bundle offline com Python 3.12, sem Codex. Não executa modelos, gates,
liberação, análise, renderização ou exportação. Nenhum resultado real foi lido
ou empacotado nesta entrega.

A fonte confirmatória já foi congelada. A liberação segue a
[emenda de liberação](../../research/questions/exploration/2026-09-24-parallel/detection-boundary-v4-release-amendment.md):
o primeiro entre inventário completo de 414 unidades sem worker vivo e
`2026-10-19T02:59:00Z` (18/10/2026, 23:59 em São Paulo). O horário efetivo vem
de `release-record.json`; `inventory.closed_utc` conserva o fechamento nominal.
A existência isolada do recibo não comprova liberação.

## Revisões e fontes distintas

Cada função tem sua árvore em `sources/<role>/studies/ic-2026-2027/`. Não usar
a revisão final do relatório como revisão da simulação ou da âncora.

| Papel no plano     | Revisão ou fonte exigida                                                                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `confirmatory`     | `375138418f7f9e4528f0c2466f4600a76fee1bad`; freeze v4, 80 fontes Python, `pyproject.toml` e lock originais                                                                |
| `release-wrapper`  | Commit que contém os bytes **efetivamente executados** de `release_on_completion.py`; verificar contra `release-record.script_sha256`, sem inferir pelo HEAD mais recente |
| `x3-x7`            | `3334ac0f96268a76d62c3b68a9705cb7fe05587e`; produtor/agregador sucessor X3–X7                                                                                             |
| `legacy-x5-x7`     | `c8e4861fdba24700d3ca802e337f81f103d65c57`; execução legada X5/X7, separada da agregação sucessora e da compatibilidade declarada                                         |
| `shp-code`         | `17a0dbedc06fbcabd2ebfe907b3c96c13a743f6b`; código da âncora e da ponte                                                                                                   |
| `shp-freeze`       | `703c51142b56421313fd6ed076f6ac121bc7293e`; registro de freeze do sucessor SHP, distinto do commit de código                                                              |
| `v44-successor`    | `7a1b8132f0dba9b365f678d2a5dd881cea39a9b7`; freeze da emenda v4.4, com o executor sucessor `v44_run_curve.py`, seus testes e o texto da emenda                            |
| `bridge`           | `2ace861d9c68859595abcb358a3e29d83439e27b`; único commit que gravou o registro sintético `crosswalk.json`, cujos bytes a revisão de reporting ainda lê                    |
| `reporting-export` | Commit final integrado de reporting e exportadores de A/G; fornecer o hash completo depois do lote, sem alterar seus arquivos nesta tarefa                                |

O build confere o freeze da v4.4 contra o próprio pacote: hashes do texto, do
executor sucessor e dos testes, o SHA-256 de `freeze-v4.json` e o do
`run_curve.py` congelado no papel `confirmatory`.

A emenda de liberação registra `428ca7cd6158244b494dcb520b9a69738b5bfae6`.
Esse commit identifica a regra, não necessariamente o wrapper executado.
O freeze confirmatório tem SHA-256
`99c4277235d4f2303b6f009d6ead8287a5d71372744dd6781e1e2d1847710837`.
O pré-registro v1 continua identificado pelo freeze próprio; o empacotador
conserva esses arquivos sem substituir seus bytes.

Leia os roteiros versionados no clone canônico:
[liberação e reporting](../../experiments/exploratory/detection-boundary-v4/report/RELEASE-RUNBOOK.md),
[contrato de reporting](../../experiments/exploratory/detection-boundary-v4/report/README.md),
[leituras e exportação exploratória](../../experiments/exploratory/detection-boundary-v4-exploratory/POST-RELEASE.md)
e [guia SHP](../../research/questions/exploration/2026-09-24-parallel/shp-reliability-guide.md).
Esses roteiros citam raízes privadas; a citação não autoriza copiá-las.
`POST-RELEASE.md` saiu da allowlist, porque registra endereços privados. Os
outros três continuam selecionáveis, mas um plano público os retém quando seus
bytes históricos trazem caminhos de coordenação, de home ou nomes de host, e
pode publicar no lugar deles cópias redigidas.

## Conteúdo e seleção

`build_ic_release.py` usa apenas a biblioteca padrão. A allowlist literal cobre
código próprio do estudo, arquivos exigidos pelo freeze, protocolos públicos,
locks e documentação operacional. Não há wildcard de entrada, cópia recursiva
de dados, exportação da árvore Git completa ou descoberta de `~/.local/state`.
Cada arquivo selecionado exige origem, papel, caminho relativo, tamanho,
SHA-256 e estado de licença. Seleção por nome não certifica direitos nem
privacidade: o coordenador fornece somente a projeção de release aprovada.

A seleção explícita inclui `v4_public_aggregates.py`, `verify_short_path.py`,
os três módulos `v4_manuscript_assembly*.py`, suas regras e schema, o guia
`pipeline/ASSEMBLY.md` e os quatro shells registrados nas regras. Cada caminho
está enumerado no empacotador. O papel `reporting-export` exige esses recursos
nos modos reais; escolha a revisão integrada que os contém. O pacote conserva
as fontes selecionadas no Git, não alterações ainda sem commit no worktree.

`plan` prepara a seleção de fontes a partir das revisões locais. `build` não
aceita arquivos fora da allowlist, revisões ausentes, symlinks, caminhos que
escapem da raiz, hashes diferentes ou saída preexistente. A saída é preparada
em pasta temporária, verificada e publicada em diretório novo. Arquivos
adicionais no bundle também fazem `verify` falhar.

Um arquivo da allowlist cujos bytes históricos não podem ser publicados é
retido com `--withhold CAMINHO=MOTIVO[,MOTIVO]`, em todos os papéis em que
existe. O plano (`ic-release-plan-v3`) registra em `withheld` o papel, o
caminho, o blob Git, o SHA-256, o tamanho e a categoria do motivo, sem citar o
trecho privado. Os bytes nunca são editados. A projeção histórica conserva as
árvores até o arquivo retido, de modo que `verify` confere o blob Git contra o
commit sem publicar o conteúdo. Um arquivo exigido pelo papel ou pelo
fechamento congelado pode ser retido; os arquivos de ambiente, não. Quem tem
o clone canônico confere o SHA-256 registrado com `git show REV:CAMINHO`.

Quando a retenção faz perder conteúdo real, `--redact CAMINHO=MOTIVO[,MOTIVO]`
retém o original do mesmo modo e publica um arquivo novo em
`redacted/<papel>/<caminho>`, com cada trecho privado trocado pelo marcador
fixo da categoria: `[private-host]`, `[home]`, `[coordination-dir]`,
`[private-email]`, `[private-address]` ou `[credential]`. Os colchetes
sobrevivem à renderização de Markdown e HTML. Os padrões ficam num arquivo
privado de regras (`ic-redaction-rules-v1`, uma lista de pares categoria e
expressão regular), passado com `--redaction-rules` ao `plan` e ao `build`; ele
não entra no plano, no bundle nem no Git. O plano registra em
`redacted` o blob Git e o SHA-256 do original, o SHA-256 e o tamanho da cópia e
o número de substituições por categoria, nunca o texto substituído. Um caminho
retido por `excluded-by-decision` não pode ser redigido.

Em código Python, `[home]` fora de uma string ainda compila (é uma lista).
Por isso a cópia `.py` precisa manter a árvore sintática do original, exceto os
valores de literais de texto, e a cópia `.json` precisa continuar válida. Uma
regra de home com `"form": "code"` vale só para arquivos `.py`: troca o trecho
que vai de `Path("` até a barra depois do diretório home por
`Path.home().joinpath("`, contado na categoria de home, e assim um caminho
padrão continua resolvendo sob o home de quem roda o código.

O `plan` recusa regras que não cubram todos os motivos declarados do caminho,
substituição em categoria não declarada, original que já contenha um marcador
ou a forma `Path.home().joinpath("`, padrão que ainda case na cópia e cópia que
deixe de ser analisável ou mude o código fora dos literais; nada é executado
nessa checagem. O `build` refaz cada cópia a partir do blob original e recusa
qualquer diferença do plano. O `verify` exige a cópia no inventário com hash e
tamanho do plano, confere a contagem de cada marcador (a forma de código conta
como home) e confere o blob original contra a árvore do commit na projeção
histórica. `redacted/README.md` explica os marcadores dentro do bundle. A cópia
serve à leitura: freezes, declarações e fechamentos continuam conferidos pelo
SHA-256 original. No pacote de 02/10, `DEFAULT_DATA_DIR` de
`shp_reliability.py` usa a forma de código e vira
`Path.home().joinpath(".local/state/research-workbench/restricted/shp")`; nos
demais literais, o marcador deixa um caminho relativo que não nomeia diretório
real, e o local entra pela opção da linha de comando.

O bundle leva `LICENSE` na raiz, com o texto MIT e o titular decidido no item
161 do log; o manifesto (`ic-release-manifest-v2`) e cada arquivo do plano
registram `MIT`. Material de terceiros não entra no pacote.

O bundle contém `LICENSE`, `plan.json`, `ic-release-manifest.json`, seu SHA-256,
`ic-release-manifest.schema.json`, `REPRODUCE.md`, o verificador independente,
árvores de fontes e uma projeção de objetos históricos em `history/.git`.
Ela conserva o commit de cada papel e as árvores até os caminhos selecionados e
retidos pelos IDs originais, mas inclui somente blobs da seleção. O commit leva
nome e e-mail do autor e a mensagem; antes de um depósito, confira esses
metadados nos commits dos papéis. Não contém remotos, alternates, hooks, configurações
locais, todos os ancestrais ou os blobs do restante do repositório. Consultas
`git show REV:caminho-selecionado` funcionam offline. Checkout completo,
`git fsck` de toda a história e travessia de ancestrais não são portões dessa
projeção. Os validadores de pilotos que exigem um checkout completo continuam
requerendo o clone canônico completo nas revisões registradas; não substituir
esse acesso por um ZIP ou fingir que a projeção é o clone inteiro.

Ambiente: `.python-version` fixa 3.12.13. Cada papel conserva `pyproject.toml`
e `uv.lock` originais; o manifesto registra seus hashes e todas as versões
fixadas no lock. O freeze confirmatório registra macOS arm64, NumPy 2.5.3 e
BLAS em uma thread. O lock de reporting consultado fixa NumPy 2.5.3, SciPy
1.18.1, Matplotlib 3.11.2 e pyreadstat 1.3.6; os outros locks não são
substituídos por esse. `uv sync --locked` prepara cada ambiente separadamente.
Instalação offline requer cache local dos wheels; eles não entram no pacote.
Integridade offline não depende de uv nem dessas bibliotecas. A sonda numérica
e seu ambiente de referência permanecem no freeze. Outro host precisa da
verificação de equivalência prevista pelo estudo; este bundle não a executa.
A liberação usa o mesmo ambiente, uv/cache e limites de BLAS do checkout
congelado, conforme o runbook.

## Comandos prontos para o coordenador

Os comandos abaixo são preparação operacional. **Não foram executados contra
raízes reais.** Use clone local com os objetos históricos disponíveis; o
empacotador não faz fetch. Forneça os commits completos do wrapper executado e
do código final integrado:

```sh
repo=/caminho/do/clone-canonico
plan=/caminho/novo/ic-source-plan.json
wrapper_revision=HASH_COMPLETO_DO_WRAPPER_EXECUTADO
reporting_revision=HASH_COMPLETO_DO_LOTE_INTEGRADO
builder="$repo/studies/ic-2026-2027/publications/reproducibility/build_ic_release.py"
rules=/caminho/privado/fora-do-git/redaction-rules.json
python3.12 "$builder" plan --repository "$repo" --mode source-only \
  --revision "release-wrapper=$wrapper_revision" \
  --revision bridge=2ace861d9c68859595abcb358a3e29d83439e27b \
  --revision "reporting-export=$reporting_revision" \
  --withhold "studies/ic-2026-2027/CAMINHO_RETIDO=excluded-by-decision" \
  --redact "studies/ic-2026-2027/CAMINHO_REDIGIDO=private-host-name" \
  --redaction-rules "$rules" \
  --output "$plan"
python3.12 "$builder" build --repository "$repo" --plan "$plan" \
  --redaction-rules "$rules" --output /caminho/novo/ic-source-package
```

As revisões fixas, inclusive `v44-successor`, entram sem `--revision`. Os
motivos aceitos são `excluded-by-decision`, `private-address`,
`private-host-name`, `absolute-home-path`, `non-allowed-email`,
`access-credential` e `coordination-path`; `--redact` aceita todos menos o
primeiro. O arquivo de regras tem este formato (padrões ilustrativos; os reais
ficam fora do repositório):

```json
{
  "schema": "ic-redaction-rules-v1",
  "rules": [
    { "category": "private-host-name", "pattern": "(?i)NOME-DO-HOST" },
    {
      "category": "absolute-home-path",
      "pattern": "Path\\(\"/(?:Users|home)/[A-Za-z0-9._-]+/",
      "form": "code"
    },
    {
      "category": "absolute-home-path",
      "pattern": "/(?:Users|home)/[A-Za-z0-9._-]+"
    }
  ]
}
```

As regras são aplicadas numa passada só: vence o casamento que começa antes e,
no empate, a regra listada primeiro. Por isso, regras de caminho de
coordenação vêm antes das de home.

Depois da liberação, o coordenador cria um **sucessor** desse plano com
`mode: "approved-release"`. Adiciona apenas os arquivos aprovados de uma raiz
curada separada, com `root: "release"`, `role: "approved-artifact"` e hashes
calculados antes do empacotamento. Exemplo de entrada (substituir digest e
bytes pelos valores conferidos; não usar este texto como aprovação):

```json
{
  "root": "release",
  "role": "approved-artifact",
  "path": "released-curves.json",
  "sha256": "SHA256_CONFERIDO_DE_64_CARACTERES",
  "bytes": 123,
  "license_status": "pending-owner-decision"
}
```

A allowlist de release inclui o par curvas/recibo, segunda vinculação,
sucessor público G1c, agregado SHP, agregados X1–X7, legado X5/X7, comparações,
catálogos de valores e saídas nomeadas do relatório. Os novos nomes públicos
curados são `public-aggregates.json`, `expected-hashes.json`, `owner-facts.json`,
`assembly-facts.json` e `assembly-record.json`. No handoff, copie o catálogo
mesclado para o nome canônico `result-catalog.json` da raiz curada, preservando
o catálogo confirmatório separado na tentativa. A verificação de integridade
do bundle não comprova completude científica dessas etapas. Não copiar logs
privados,
microdados, texto integral, chaves, traces ou registros de tarefas seladas.
Mesmo JSONs devem ter seus campos revisados pelo coordenador antes da seleção;
o empacotador não resolve licenças nem anonimiza conteúdo científico.

O comando final, reservado à próxima etapa, é:

```sh
make -C "$repo/studies/ic-2026-2027/publications/reproducibility" package \
  PYTHON=python3.12 REPOSITORY="$repo" PLAN=/caminho/ic-approved-release-plan.json \
  RELEASE_ROOT=/caminho/da/projecao-de-release-aprovada \
  REDACTION_RULES=/caminho/privado/fora-do-git/redaction-rules.json \
  OUTPUT_DIR=/caminho/novo/ic-scientific-release
python3.12 /caminho/novo/ic-scientific-release/verify_ic_release.py verify \
  --bundle /caminho/novo/ic-scientific-release \
  --manifest-sha256 DIGEST_EXTERNO_RETIDO_PELO_COORDENADOR
```

Retenha o digest impresso pelo build fora do bundle. O arquivo de digest dentro
do pacote detecta corrupção; a comparação externa vincula o pacote recebido
à versão que o coordenador conferiu. SHA-256 não constitui assinatura ou
aceite científico.

Para ensaios, use `mode: "synthetic"` e forneça explicitamente as oito revisões.
Esse modo aceita os nomes `_synthetic` enumerados a partir das saídas fixas do
relatório, sem wildcard nem aceitação genérica de sufixos. O recibo artificial
deve ter `script_sha256` igual ao gerador `v4_report_synthetic.py` selecionado
em `reporting-export`; o build recusa um gerador ausente ou diferente. Nos
modos reais, a conferência continua vinculada a `release_on_completion.py`
de `release-wrapper`, e os nomes sintéticos continuam recusados.

O empacotador `experiments/package_jcss_submission.py --synthetic` prepara
somente staging local fora de Git, preserva os nomes e marca
`source-manifest.json` com `synthetic: true`; reconhece também
`T1s_a_star_all_units_synthetic.csv`. Sem a opção, recusa os ativos sintéticos.
O T51 usou adaptadores locais; as opções corrigidas permitem repetir o
encadeamento com os empacotadores originais. Não apagar sufixos nem substituir
o digest do recibo por um hash do wrapper real.

## Reprodução científica e limites de acesso

Os targets `g0` a `g2c` e `tier` exigem `FROZEN_STUDY` em `37513841`, freeze,
segunda vinculação e critérios aplicáveis. `SHARDS` é oito e deve coincidir
com o freeze; cada shard usa `SHARD=0` a `7`. A revisão de reporting não pode
executar os gates congelados. Esses targets são instruções históricas de
regeneração, não parte do build ou da verificação do bundle.

O target de liberação é `release-on-completion`, com `WRAPPER_STUDY` separado,
`WRAPPER_SHA256` conferido e `RELEASE_RECORD` explícito, executando no ambiente
do checkout congelado. `release-at-close` recusa a chamada antiga. O recibo
precisa acompanhar `released-curves.json`; o empacotador confere o hash das
curvas e o hash do wrapper selecionado. Não redirecionar stdout para o arquivo
de curvas: o wrapper publica esse arquivo e stdout informa o recibo.

A renderização usa a CLI real, na revisão `reporting-export`, com entradas
liberadas e autorizadas, saída nova e os mesmos inputs na exportação:

```sh
cd "$reporting_study"
uv run --frozen python -m ic_study.analysis.detection_v4_report \
  --curves "$approved_release/released-curves.json" \
  --release-record "$approved_release/release-record.json" \
  --gate-root "$authorized_gate_root" --criteria "$criteria" \
  --allocation "$approved_release/v4-allocation.json" \
  --stage-successor "$approved_release/G1c-aggregate-successor.json" \
  --shp "$approved_release/shp-aggregate-successor-1.json" --crosswalk "$crosswalk" \
  --out "$new_report"
uv run --frozen python -m ic_study.analysis.v4_report_export \
  --curves "$approved_release/released-curves.json" \
  --release-record "$approved_release/release-record.json" \
  --gate-root "$authorized_gate_root" --criteria "$criteria" \
  --allocation "$approved_release/v4-allocation.json" \
  --stage-successor "$approved_release/G1c-aggregate-successor.json" \
  --shp "$approved_release/shp-aggregate-successor-1.json" --crosswalk "$crosswalk" \
  --report "$new_report" --manuscript "$separate_manuscript_copy" \
  --values "$new_values" --catalog "$new_catalog" --fill
```

Retire opcionais ausentes conforme o runbook, sem inventar agregados: sem
curvas o relatório produz somente T3/F4; SHP e ponte são entradas separadas.
O leitor atual de gate consulta registros selados e vinculações privadas.
Eles não entram no pacote público. Esse comando continua exigindo acesso
autorizado do coordenador. O caminho curto público descrito abaixo renderiza
a projeção dos agregados; a regeneração cara permanece no ambiente congelado,
e a verificação de proveniência continua exigindo acesso autorizado.

## Caminho curto público: agregados para tabelas e figuras

`ic_study.analysis.v4_public_aggregates project` chama o mesmo `load_inputs`
do caminho autorizado. Só depois dessa validação escreve um arquivo novo;
uma projeção existente nunca é sobrescrita. É uma projeção derivada, não um
novo registro científico, uma autorização ou uma cópia do selo. Na liberação,
o coordenador projeta as entradas aprovadas, revisa os campos e conserva
separadamente a prova autorizada de proveniência. Não projetar resultados
reais antes dessa autorização.

```sh
cd "$reporting_study"
python -m ic_study.analysis.v4_public_aggregates project \
  --curves "$approved_release/released-curves.json" \
  --release-record "$approved_release/release-record.json" \
  --gate-root "$authorized_gate_root" --criteria "$criteria" \
  --allocation "$approved_release/v4-allocation.json" \
  --stage-successor "$approved_release/G1c-aggregate-successor.json" \
  --shp "$approved_release/shp-aggregate-successor-1.json" --crosswalk "$crosswalk" \
  --out "$new_public_aggregates"
python -m ic_study.analysis.detection_v4_report \
  --public-aggregates "$new_public_aggregates" --out "$new_report"
python -m ic_study.analysis.v4_report_export \
  --public-aggregates "$new_public_aggregates" --report "$new_report" \
  --manuscript "$separate_manuscript_copy" --values "$new_values" \
  --catalog "$new_catalog" --fill
```

Retire opcionais ausentes como no caminho autorizado. `--public-aggregates`
exclui todas as entradas autorizadas nas duas CLIs. Uma projeção sintética
conserva automaticamente a marca sintética nas saídas. O target `make project`
usa `REPORTING_STUDY`, `GATE_ROOT`, `PUBLIC_AGGREGATES` e os mesmos opcionais
do target `report`; `PYTHON` deve apontar para o ambiente de reporting.

Campos do contrato `ic-study.v4-public-aggregates.v1`:

| Objeto e campos                                                                                                                                                                                                                                                | Razão para a projeção pública                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema`, `notice`, `synthetic`                                                                                                                                                                                                                                | Versão, limite explícito de proveniência e distinção entre ensaio e resultado.                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `code.commit`, `code.reporting_code_dirty`, `code.modules_sha256`                                                                                                                                                                                              | Revisão e hashes do projetor, leitor autorizado e entrada de reporting; identificam código sem caminhos ou hosts. A marca de árvore alterada impede apresentar HEAD como os bytes finais.                                                                                                                                                                                                                                                                                                             |
| `source_hashes`                                                                                                                                                                                                                                                | SHA-256 por papel (`curves`, `release_record`, `shp`, `crosswalk`, `criteria`, `allocation`, `stage_successors`, `gate_criteria` e `gate_G*_results/seals/authorization`), em listas ordenadas de digests. Nenhum nome, chave de tarefa ou vinculação privada acompanha esses hashes. Incluem os arquivos lidos pelo leitor e resultados cuja existência determina os totais do gate.                                                                                                                 |
| `objects_sha256`, `sha256`                                                                                                                                                                                                                                     | Hash de cada objeto e do documento, por JSON canônico UTF-8 com chaves ordenadas, sem espaços e sem números não finitos. Detectam corrupção, não autenticidade.                                                                                                                                                                                                                                                                                                                                       |
| `objects.release.closed_utc`, `main_curve_valid`, `statuses`, `curves`                                                                                                                                                                                         | Fechamento nominal, validade principal e inventário público de estados usados em T1/T1s/T4, F1/F2/F3/F5/F6 e contagens do exportador.                                                                                                                                                                                                                                                                                                                                                                 |
| Cada curva: `meta.key/tier/family/channel/sensitivity/r`, `status`, `valid_null_gate`, `gap_count`, `band_complete`, `available`, `auc`, `lower`, `upper`, `critical`, `empirical_exceeds_floor`, `nonmonotone_band`                                           | Configuração registrada e estimativas/diagnósticos já consumidos pelas tabelas, figuras e valores. Não contêm painéis, parâmetros ajustados, scores ou sementes. A validade principal vem do objeto release; estados finais individuais não consumidos são descartados.                                                                                                                                                                                                                               |
| Cada curva: `first`, `sustained`, `secondary` com `point`, `interval`, `censoring`, `interval_censoring`, `sustained`                                                                                                                                          | Fronteiras, intervalos e censuras usados pelo reporting, sem interpolação.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Cada curva: `cell_success`, `cell_gap`, `diagnostics`                                                                                                                                                                                                          | Estados e categorias de lacuna usados nas contagens e tabelas. `diagnostics` é null fora das duas forças positivas iniciais de B válida cuja primeira fronteira esteja nessas forças. Só essas células publicadas contêm `retry`, `residual_se_units`, `amplification`, `nuisance_variance`, `nuisance_mcse`, `mean_shift`, `projected_fraction`. `retry` conserva sim/não, descartando os tamanhos de todas as tentativas. Não copia tentativas brutas nem diagnósticos que o relatório não imprime. |
| `objects.gate.summaries` — base `gate/planned/completed/failures/pass`; G0 `statuses/fits/anchor_failures/implementation_statuses/budget_statuses`; G1b `coverage_counts/empirical_exceeds_floor_count`; G1c `pointwise_failures/anchor_count/mean_z/tie_rate` | Somente critérios e contagens mostrados em T3/F4 e no catálogo. A máscara de matching e as vinculações são descartadas.                                                                                                                                                                                                                                                                                                                                                                               |
| Resumo G2: `cell_failure_counts`, `successful_pair_counts`, `cell_ratios`, `cell_lower`, `cell_upper`, `pooled_ratio`, `pooled_lower`, `pooled_upper`, `loo_tail_counts`, `fd_ratio_median_by_cell`, `covariance_flag_counts`                                  | Dispersão, intervalos, falhas e diagnósticos impressos em T3/F4. Os campos internos que os consumidores não usam são descartados.                                                                                                                                                                                                                                                                                                                                                                     |
| Resumo G2c: `comparisons` com `failure_count/denominator/ratio/lower/upper/tails`                                                                                                                                                                              | Comparações agregadas de propagação local versus refits já mostradas em T3/F4. Não inclui draws nem verdades seladas.                                                                                                                                                                                                                                                                                                                                                                                 |
| `objects.gate.summary_counts`, `sealed`, `planned`, `started`, `g2_cells`                                                                                                                                                                                      | Notas de linhas agregadas, progresso por estágio e coordenadas públicas (a, r) que rotulam T3/F4. `started` conserva apenas a presença do estágio, nunca a autorização privada.                                                                                                                                                                                                                                                                                                                       |
| `objects.gate.g0_fits` com `status/gap/count`; `g0_evaluations` e `g1b_critical` com `value/count`                                                                                                                                                             | Contagens por categoria ou valor, necessárias a F4. Eliminam a ordem das tarefas e os identificadores; nenhuma linha bruta de registro é copiada.                                                                                                                                                                                                                                                                                                                                                     |
| `objects.gate.stop` com `pass_probability/minimum/gaps/denominator`                                                                                                                                                                                            | Apenas os valores da regra de economia impressos em T3/F4 e no catálogo.                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `objects.gate.successors` com `stage/name/sha256`                                                                                                                                                                                                              | Apenas os sucessores usados: nome e prefixo de hash já constam das notas públicas de T3. Não inclui selo, razão privada, host ou vinculações.                                                                                                                                                                                                                                                                                                                                                         |
| `objects.shp.year/estimate/standard_error/wald_95_interval/sensitivity_envelope`; `starts.year/estimate/standard_error/wald_95_interval/failure_reasons`                                                                                                       | Estimativas e limites agregados da âncora e sensibilidade que F6 e o catálogo publicam. Nenhum microdado acompanha a projeção.                                                                                                                                                                                                                                                                                                                                                                        |
| `objects.crosswalk.declared_plan/replicates/ranges`; cada faixa `reference/r/low/high/values/failures`                                                                                                                                                         | Apenas faixas e contagens das referências da ponte usadas em F6. Não inclui replicações individuais, parâmetros ou sementes.                                                                                                                                                                                                                                                                                                                                                                          |
| `objects.thresholds.cell_lower/cell_upper/pooled_lower/pooled_upper`                                                                                                                                                                                           | Critérios públicos para rotular T3/F4 e contar os resultados do gate.                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `objects.release_event.condition/released_utc`                                                                                                                                                                                                                 | Condição e hora efetiva da liberação usadas no catálogo; não copia o recibo integral.                                                                                                                                                                                                                                                                                                                                                                                                                 |

O leitor público recusa campos desconhecidos em todos os níveis, chaves JSON
duplicadas, números não finitos e hashes internos divergentes. Verifica tipos,
domínios e os invariantes necessários à renderização. Declarar hashes de
entrada não demonstra que o projetor recebeu aqueles bytes: um autor pode
recalcular todos os hashes de uma projeção alterada. A verificação dos selos,
autorizações, segunda vinculação e aprovação de sucessores pertence ao leitor
autorizado. A projeção não certifica proveniência, execução nem aceite científico.

A comparação científica usa bytes idênticos para CSVs, tabelas LaTeX, figuras
PDF/PNG, conteúdo de `generated/` e pares ID/valor do catálogo. Há uma exceção
explícita para metadados: o manifesto autorizado contém identificador privado
do gate e hashes de código; o público contém o hash da projeção e a declaração
de limite. Os hashes de módulos editados também mudam por definição. Isso
propaga diferenças ao `report_manifest_sha256` dos valores/catálogos e ao
comentário de SHA do manifesto em `generated/*.tex`. Portanto a entrega não
afirma igualdade literal desses documentos completos. O verificador remove
somente `code` e `inputs` de `report/manifest.json`, `code` e
`report_manifest_sha256` de `values.json`/`catalog.json`, e substitui somente o
digest naquele comentário de cada `.tex` gerado. Os demais campos e bytes
permanecem na comparação. Não arredonda números nem normaliza figuras.

Antes do replay, `verify_short_path.py prepare` produz um arquivo novo
`expected-hashes.json` a partir das mesmas entradas autorizadas e da
renderização autorizada já existente. Valida a vinculação das entradas e os
hashes de todas as saídas do relatório, copia apenas essas saídas e exporta
uma árvore mínima de `main.tex`: todos os `PLACEHOLDERS` e todos os IDs de
`result_values`, ordenados, como no replay. Não renderiza novamente nem usa
o manuscrito completo como referência. Recusa `--public-aggregates` e um
relatório produzido pelo replay público; a projeção é usada apenas como
referência hash-bound no manifesto, não como origem dos valores esperados.

O manifesto tem `schema: ic-study.v4-short-path-hashes.v1`,
`projection: {file, sha256}`, `dpi` herdado da renderização e `files` calculado
por `hashes()` com as normalizações descritas acima. A referência e o replay
usam diretórios novos distintos. O manifesto fica ao lado da projeção e
nunca é sobrescrito. Para um ensaio artificial, acrescente `--synthetic` ao
`prepare`; essa marca deve coincidir com relatório e projeção.

```sh
python publications/reproducibility/verify_short_path.py prepare \
  --curves "$approved_release/released-curves.json" \
  --release-record "$approved_release/release-record.json" \
  --gate-root "$authorized_gate_root" --criteria "$criteria" \
  --allocation "$approved_release/v4-allocation.json" \
  --stage-successor "$approved_release/G1c-aggregate-successor.json" \
  --shp "$approved_release/shp-aggregate-successor-1.json" --crosswalk "$crosswalk" \
  --report "$authorized_report" --projection "$new_public_aggregates" \
  --out /caminho/novo/referencia-autorizada \
  --manifest /caminho/do/demo/expected-hashes.json
```

Retire opcionais ausentes conforme o runbook. `authorized_report` é o
relatório renderizado com as entradas autorizadas, antes do replay público.
Não substitua esse diretório pelo `$new_report` renderizado da projeção no
exemplo anterior.

`verify_short_path.py verify` recebe uma pasta com projeção e manifesto esperado,
confere o hash externo da projeção, renderiza numa pasta nova e lista `OK` ou
`FAIL` por arquivo, incluindo arquivos ausentes ou extras. Sai com 0 somente
se todas as comparações passarem; falhas de leitura, validação e saída existente
retornam 1. Usa o ambiente do estudo e a biblioteca padrão, sem dependências
novas, instalação automática ou chamadas de modelo. A cópia mínima de fonte
LaTeX criada no ensaio serve para exercitar o exportador; não monta o manuscrito.

```sh
cd /caminho/do/checkout/studies/ic-2026-2027
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 .venv/bin/python \
  publications/reproducibility/verify_short_path.py \
  verify --bundle /caminho/do/demo --out /caminho/novo/reproducao
# Alternativa: make -C publications/reproducibility short-path \
#   PYTHON="$PWD/.venv/bin/python" BUNDLE=/caminho/do/demo OUTPUT_DIR=/caminho/novo/reproducao
```

A chamada anterior sem subcomando continua equivalente a `verify`, inclusive
no target `make short-path`.

O ambiente separado usa Python 3.12 e o mesmo `uv.lock`; instalação offline
exige cache de wheels, conforme a seção de ambientes. Compatibilidade Linux
do comando não é promessa de PDFs/PNGs iguais entre sistemas: fontes, FreeType
e backends podem alterar bytes. O manifesto conserva a referência produzida
no Mac e uma divergência no Linux fica visível como falha, sem tolerância
oculta. A execução Linux da demonstração e o pacote real ficam com o coordenador.

Execução Linux da demonstração, 30/09/2026: num PC do laboratório (Linux
6.8 x86-64, glibc 2.35, Python 3.12.13, NumPy 2.5.3, Matplotlib 3.11.2, mesmo
`uv.lock`), com o estudo extraído por `git archive` de `d4b7b189`, o
verificador aprovou 43 das 54 saídas. Os 20 PDFs vetoriais, as 16 tabelas e
arquivos `generated/` em LaTeX, os 5 CSVs e os pares ID/valor de
`values.json` e `catalog.json` saíram idênticos aos do Mac. Os 10 PNGs
divergiram, porque a rasterização difere entre plataformas, e com eles o
`report/manifest.json`, que registra os hashes dos PNGs. O manuscrito usa os
PDFs, não os PNGs. Portanto tudo o que entra no artigo se reproduz byte a byte
num segundo sistema operacional; os PNGs são pré-visualizações dependentes de
plataforma. O verificador segue estrito e mostra essas 11 falhas, sem
tolerância.

As [regressões sintéticas](../../tests/unit/test_v4_public_aggregates.py) cobrem
gate-only T3/F4, liberação com SHP e ponte, falha de gate, minimização dos
diagnósticos e rejeição de corrupção, campos extras e chaves duplicadas.
Os três catálogos de pares ID/valor conservam SHA-256 registrados antes da
mudança. A rodada final conjunta com os testes de reporting e exportação
passou com 267 testes em 272,82 s, em um processo e com BLAS limitado a uma
thread. Ruff, format e mypy passaram nos quatro arquivos Python tocados.
A demonstração sintética preparada no Mac compara 54 saídas: 40 por bytes
brutos e 14 pelas regras explícitas de metadados acima. O replay passou com
as entradas autorizadas indisponíveis no caminho original; não é uma
execução Linux nem uma verificação de dados reais.

Para a exportação exploratória, o contrato final usa os agregados do sucessor
X3–X7 e as comparações públicas, preservando a fonte legada separada:

```sh
uv run --frozen python -m ic_study.analysis.v4_exploratory_export \
  --x3 "$approved_release/x3.json" --x4 "$approved_release/x4.json" \
  --x6 "$approved_release/x6.json" --x7 "$approved_release/x7.json" \
  --comparisons "$approved_release/comparisons.json" \
  --confirmatory-values "$new_catalog" --manuscript "$separate_manuscript_copy" \
  --values "$new_merged_values" --catalog "$new_merged_catalog" --fill
```

O exemplo histórico de fragmentação permanece em `regenerate_fragmentation.py`:
`make example ARTIFACT_ROOT=/caminho/autorizado OUTPUT_DIR=/caminho/novo` valida
os quatro objetos retidos e regenera apenas o caso 35. Não foi rodado nesta
entrega. Seus microartefatos externos e revisões exigidas pelo validador não
são substituídos pelas fixtures deste empacotador.

## Relatório da tarefa L — 30/09/2026

Revisões/fontes: as cinco revisões históricas fixas foram resolvidas no Git
local; arquitetura, contexto e regras do estudo, freeze, emenda, wrapper,
README/Makefile e roteiros acima foram lidos. O commit da ponte foi consultado
no histórico. Wrapper efetivamente executado e reporting/export final aguardam
vinculação do coordenador; não foram inferidos de um arquivo de resultado.
Nenhuma raiz selada, log privado ou diretório restricted foi lido.

Exemplos prontos: seleção de fontes, build de release aprovado, verificação
offline com digest externo e CLIs científicas acima. O pacote leva instruções
e verificador próprios para uso independente de Codex após 01/10.

Testes reais desta entrega: `pytest -q tests/unit/test_ic_release_package.py`
passou com **26 testes em 40,41 s**, em um processo, sem xdist. Cobriu seleção
fora da allowlist, caminhos absolutos e traversal, caminhos proibidos,
symlink no Git e na raiz/arquivo/diretório de release, hash adulterado,
revisão/papel/lock ausentes, saída existente (arquivo, diretório e symlink),
par de liberação incompleto, wrapper diferente, digest externo divergente,
conteúdo extra no bundle e blob histórico extra mesmo com inventário
recalculado. As regressões do blob extra e do wrapper foram vistas em
vermelho antes das correções. Ruff check, Ruff format --check e mypy --strict
passaram nos dois arquivos Python tocados. O esquema JSON foi parseado, seus
papéis conferidos contra o manifesto e os links relativos do README conferidos.
`git diff --check` passou; fontes científicas, LaTeX, freezes, `pyproject.toml`
e `uv.lock` permaneceram iguais ao HEAD.

Os testes usaram Python 3.12.13 e uv 0.10.9, com ambiente e cache em
`/private/tmp/ic-package-venv` e `/private/tmp/uv-cache-ic-package`. As fixtures
são novas e artificiais, em pastas temporárias, incluindo um Git mínimo local;
não usam dados do estudo. A rodada final está em
`/private/tmp/ic-package-final2-tests/`. A matriz de integração fica para o
coordenador, uma vez após o lote.

O pacote sintético foi inspecionado em
`/private/tmp/ic-package-inspection-nj9myen2/bundle/`: 84 arquivos inventariados,
oito árvores de fontes, objetos históricos selecionados, instruções e
verificador. O verificador levado pelo pacote passou com o repositório de
origem renomeado e indisponível no caminho original; `git show` recuperou o
código histórico e recusou o blob não selecionado. Todos os estados de licença
ficaram pendentes. Os targets `make package` e `make verify` também passaram
somente com esse Git artificial, em `make-bundle/`, com digest
`51b9f9bbf4091785f14978a5e465fee2b8cc2b4814faabff17aee9c96f414c28`.
Os comandos em `REPRODUCE.md` foram lidos e a liberação foi inspecionada com
`make -n`, sem executá-la. Essas pastas temporárias são evidência local do
ensaio; as instruções permanentes são os arquivos deste diretório e os
arquivos levados pelo próprio bundle.

Replay: acesso histórico e verificação de integridade do pacote são portões
técnicos. O caminho curto público renderiza os agregados projetados; a
proveniência exige o leitor de gate com acesso autorizado. Regeneração cara
continua reservada ao ambiente congelado. Regeneração nesta entrega original
do empacotador: nenhum modelo,
trajetória, gate, âncora ou figura científica foi regenerado. Teste técnico:
empacotamento e verificação sintéticos, separados de qualquer resultado real.
Aceite científico: não produzido; os três estados científicos do manifesto
permanecem `false`.

Aguardam liberação: projeção pública aprovada, hashes reais do par curvas/recibo,
agregados liberados e entradas opcionais disponíveis, fonte do wrapper que
rodou e revisão final integrada. Licenças, direitos de terceiros, seleção
pública, conta de depósito, plataforma, acesso a pareceristas e DOI ficam
reservados ao Davi. Todos os componentes entram como licença pendente ou
metadado; nenhuma licença foi atribuída nesta tarefa. Não houve publicação,
DOI, commit ou push no repositório de trabalho, nem alteração em fonte LaTeX, ledger, exportadores ou freezes.
