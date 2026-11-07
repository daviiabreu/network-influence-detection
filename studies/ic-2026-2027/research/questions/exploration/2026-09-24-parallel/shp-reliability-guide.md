# SHP: execução local da âncora de confiabilidade

**Não execute a análise do SHP antes de existir `shp-reliability-successor-1-freeze.json` neste diretório.** O [sucessor 1](shp-reliability-successor-1.md) acrescentou à análise uma sensibilidade de traço (STARTS) e uma descrição da onda de 2004. Esse registro de congelamento, escrito pelo coordenador depois da revisão do código, vincula por SHA-256 o sucessor, o seu JSON e o commit de código, e registra o estado do diretório restrito. Sem ele, a execução não tem especificação congelada e o resultado não pode ser usado.

1. Em [FORS → dados SHP](https://forscenter.ch/projects/swiss-household-panel/data/), siga para SWISSUbase, **Living in Switzerland**, edição publicada que contenha 1999–2009. Entre com sua conta pessoal, leia e aceite o contrato SHP. Guarde a versão, a data e o identificador do conjunto. O contrato limita o uso às pessoas que o assinaram; não envie os arquivos a colegas, agentes, chats ou repositórios.
2. Baixe o pacote **STATA** com os arquivos individuais anuais `SHP99_P_USER.dta`, `SHP00_P_USER.dta`, …, `SHP09_P_USER.dta` e a documentação/questionários dessas ondas. Não é necessário fornecer arquivos domiciliares, a versão long ou os mestres para a execução inicial. Confira se `P99P04` … `P09P04` mantêm a pergunta e a escala; se houver divergência, pare antes da análise. Os nomes podem variar na versão baixada: nesse caso, confirme no guia SHP antes de renomear uma cópia local.
3. Crie `/Users/davi/.local/state/research-workbench/restricted/shp/` com permissão **0700** (`mkdir -p ...` e `chmod 700 ...`). Extraia ali somente os onze `.dta` anuais. Não coloque os dados na worktree. O programa lê apenas `idpers` e a variável `PyyP04` de cada arquivo; também aceita CSV com esses nomes de coluna se sua edição só permitir exportação local.
4. Confirme que `shp-reliability-successor-1-freeze.json` existe e que `git rev-parse HEAD` mostra o commit de código que ele registra. Então, na raiz desta worktree, execute:

   ```sh
   cd studies/ic-2026-2027
   UV_CACHE_DIR=/private/tmp/uv-cache-shp /Users/davi/.local/bin/uv run --locked python -m ic_study.analysis.shp_reliability --output /Users/davi/.local/state/research-workbench/restricted/shp-aggregate-successor-1.json
   ```

O programa recusa diretório vazio, arquivo anual ausente, valor fora da escala e saída já existente. A saída JSON (0600) contém apenas estimativas, erros-padrão modelares, ajuste e contagens agregadas. Verifique o relatório localmente; compartilhe somente agregados aprovados, nunca linhas ou identificadores. Se o diagnóstico apontar falha, não escolha outra trinca ou ponto de `r` sem registrar um sucessor do pré-registro.

## O que a saída contém

As seções do pré-registro original não mudam: `anchor` (r de 2004 do quase-simplex em onze ondas, erro-padrão e IC de Wald de 95%), `multiwave`, `triplets`, `sensitivity_envelope`, `sensitivity` (Heise policórico, casos completos e proxy anterior a 2004) e as contagens por onda.

A seção `successor_1` traz as adições do sucessor. Em `starts_sensitivity` está o ajuste traço–estado–erro, com a mesma amostra, escala e FIML do ajuste principal e valores iniciais fixados no código. Quando é admissível (`"status": "admissible"`), traz `anchor` com o r de 2004, o erro-padrão pelo método delta e o IC de Wald de 95%, cada `r_t` com seu erro-padrão, as variâncias de traço, de estado inicial, de inovação e de erro, a persistência φ, a fração de traço na variância latente de 2004, log-verossimilhança, AIC, BIC e o resíduo máximo de correlação contra os casos completos. Se alguma regra de falha declarada for atingida (não convergência, informação observada não positiva definida, variância abaixo de 10⁻⁴ vezes a variância observada média, |φ| acima de 0,99 ou `r_t` fora de (0, 1)), o status é `"failed"`, `reasons` lista as regras atingidas e `solution_at_termination` guarda os valores sem truncamento, só como diagnóstico. Nesse caso não existe estimativa STARTS: a falha é o resultado, e não se tenta outro valor inicial, priori ou restrição. Um erro numérico inesperado também vira registro de falha, com o motivo `numerical error before a solution was reached`, sem interromper o restante da análise.

Em `wave_2004_description` estão `r_2003`, `r_2004` e `r_2005` do ajuste principal lado a lado e o quase-simplex de 2004 a 2009 entre respondentes cuja primeira resposta válida é de 2004, uma proxy da entrada pelo refrescamento. O r de 2004 desse grupo é uma estimativa de borda. As duas saídas são descritivas e não substituem a âncora. A diferença entre o r de 2004 do quase-simplex e o do STARTS indica quanto a âncora depende de um traço estável; não escolha entre os dois por AIC, BIC ou proximidade da grade.

## Figura F6

Com o agregado aprovado, a F6 do relatório v4 (`python -m ic_study.analysis.detection_v4_report`, ver `experiments/exploratory/detection-boundary-v4/report/README.md`) recebe `--shp` e, se houver, `--crosswalk`. O quase-simplex continua como ponto principal. O STARTS aparece como sensibilidade rotulada quando é admissível; quando falha, a legenda registra a falha e nada é desenhado.

## Ponte sintética (sem dados SHP)

A Adição 2 não lê microdados do SHP e pode rodar em outro host. Ela gera painéis com o gerador congelado da v4 na geometria SHP, aplica todos os estimadores da âncora e grava média, desvio-padrão, mínimo, máximo e contagens de falha por célula, família e estimador. Rode a partir do mesmo commit registrado no congelamento, para que a saída registre o código revisado. Cada processo cuida de um fragmento (`--shard K --shards N`, com K de 0 a N−1) e grava cada célula terminada em `DIR/cells/`; se for interrompido, basta repetir o mesmo comando. Para juntar fragmentos de hosts diferentes, copie os arquivos de `cells/` para um só diretório e rode o comando uma vez com `--shards 1`: ele pula as células prontas e escreve `DIR/crosswalk.json`.

```sh
cd studies/ic-2026-2027
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --locked python -m ic_study.analysis.shp_crosswalk --out DIR --shard 0 --shards 4
```

O plano declarado tem 99 células com 10 réplicas, ou 990 painéis. No teste de 28/09/2026, com duas células e duas réplicas no Mac do gate sob carga e BLAS com uma thread, cada painel custou de 3 a 4,5 s de CPU, o que projeta cerca de 1 a 1,5 CPU-hora no total, ou uns 20 minutos com quatro fragmentos em paralelo.

`--cells N --replicates R` faz um teste rápido nas N primeiras células (ou nas células cujas chaves forem listadas, separadas por vírgula); use outro diretório, porque o programa recusa misturar células de planos diferentes, e esse agregado sai marcado com `"declared_plan": false`.
