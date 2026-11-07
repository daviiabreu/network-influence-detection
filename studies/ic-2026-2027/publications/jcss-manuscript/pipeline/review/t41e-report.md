T41e concluída sobre `research/shell-assembler`, já na integração `f5743882`, que contém a T41d `1b9ddddd`. Não foi necessário avançar o ramo. Não houve commit nem push.

O montador resolve `\resultplural{ID}{singular}{plural}` junto com os `\resultnum`. O inteiro 1 escolhe o singular; 0 e os demais inteiros não negativos escolhem o plural. As formas são texto simples, sem chaves internas; também servem para verbos e pronomes. Separadores de milhar e parte decimal só de zeros são aceitos como inteiros. Valor fracionário, negativo, não finito ou malformado, ID ausente e ID sem `\resultnum` no mesmo bloco selecionado causam recusa com bloco, arquivo, faixa de linhas e linha do texto. Um binding comentado não autoriza o uso.

`main.tex` ganhou somente `\newcommand{\resultplural}[3]{#3}` no preâmbulo. O resumo de base permanece byte a byte igual. O `paper_check` conta apenas a forma plural no texto não montado; depois da montagem conta o texto escolhido. Os IDs e as alternativas ocultas não entram no orçamento. ASSEMBLY.md documenta o contrato.

| Shell | Usos | Linhas alteradas | Regras com aceite |
| --- | ---: | ---: | ---: |
| Results | 109 | 58 | 49 |
| Resumo | 16 | 13 | 13 |
| Discussion/Conclusion | 120 | 53 | 48 |
| Exploratórios | 94 | 50 | 45 |
| Total | 339 | 174 | 155 |

Os pares ordenados de ID e placeholder de todos os `\resultnum` e todos os comentários, inclusive SELECT WHEN, ACTION, INCLUDES e marcadores, permanecem byte a byte iguais nos quatro shells. Números de tier são ordinais e não governam o plural de “nine … units”. Nas enumerações X4, X6 e X7, substantivos elididos foram repetidos para cada contagem; onde o verbo se referia a uma enumeração de contagens, “The counts were” conserva um sujeito plural independente de cada valor. B04.low.2 passa a falar da fronteira por share no singular, preservando a classificação; não toma emprestado um ID vinculado apenas em B04.low.1. O registro [t41e-number-agreement.json](t41e-number-agreement.json) contém o antes e o depois de cada linha.

Os exemplos abaixo vêm exclusivamente de `release-day/invalid-main`, um ensaio sintético; os números vinculados são exibidos sem a sintaxe TeX para facilitar a leitura.

| Antes | Depois |
| --- | --- |
| 1 of the nine tier-1 units were not both complete and valid | 1 of the nine tier-1 units was not both complete and valid |
| 1 units were not both complete and valid | 1 unit was not both complete and valid |
| These included 1 zero-strength gate failures | This included 1 zero-strength gate failure |

Os testes também verificam “0 units … they” e “2 units … they”, a recusa de entradas incoerentes, o limite exato de 250 palavras e os bindings locais de todas as regras para 0, 1 e 2. A montagem sintética completa com 1 não deixa chamadas de `\resultplural` no texto final.

| Elemento de seleção | Antes | Depois |
| --- | --- | --- |
| Predicados e condições das 267 regras | T41d | Iguais |
| Ações, bindings e locadores | T41d | Iguais |
| Ordem das 267 regras e first-fit | T41d | Iguais |

Não há decisão de seleção ou ordem nova. As provas estão em [t41e-selection-changes.json](t41e-selection-changes.json) e [t41e-scope-proof.json](t41e-scope-proof.json). Exportadores, figuras, tabelas, seções fixas, claim-evidence.md e fechamento de código não foram alterados.

A repinagem usa o comando existente `repin_v4_manuscript_assembly.py`, as quatro revisões antigas `f5743882` e 155 argumentos explícitos `--accept-visible ID`. O [recibo verificado](t41e-shell-repin-receipt-verified.json) conserva as 267 regras e registra hashes, locadores, texto e aceite por ID. Ele substitui os dois recibos intermediários desta tarefa. SHA-256 final das regras: `ff0fc519976819d66840491ce67809363c6c8cbb8215913cf3c232135db331a9`.

A [auditoria](v4-manuscript-assembly-audit-2026-09-30.json) foi refeita contra as montagens manuais dos três ensaios públicos: 24/24 completas, cobertura 267/267 antes e depois, resumos de 175 a 234 palavras. O oráculo atual registra a T41e e mantém os resumos da T41d, pois nenhuma dessas 24 composições mudou de texto ou ordem. As 46 composições obrigatórias alcançáveis foram recalculadas nas variantes 0, 1, 2 e 9, conservando contagens positivas onde o guard exige: máximo obrigatório 246 em todas, abaixo de 250. [Prova do orçamento](t41e-abstract-budget.json).

O total de divergências literais passou de 1.375 para 1.472: 97 novas, 132 com texto atualizado e nenhuma desaparecida. As 97 novas estão em B1b-G0 (1), nas três referências de calibração X4 (16 cada), X7 inválido e censurado (16 cada), X6 sem subcobertura detectada (10), X6 com precisão inconclusiva (2), X7 inconclusivo (2) e X7 incompleto (2). Decorrem de concordância singular e da explicitação de substantivos antes elididos. O montador segue os shells revisados; as montagens históricas permanecem intactas. Cada divergência nova ou atualizada tem antes, depois, caso, localizador e decisão no JSON; o [relatório por bloco](t41e-divergences.md) explica todas. A comparação foi corrigida para não contar novamente como mudança da T41e o resumo fixo já consolidado na T41d. As 24 provas de igualdade dos IDs antigos dos catálogos continuam passando.

| Portão final | Resultado |
| --- | --- |
| Ruff check | PASS, 5 arquivos Python tocados |
| Ruff format --check | PASS, 5 arquivos |
| Mypy | PASS, 5 arquivos |
| test_v4_manuscript_assembly.py | 177 passed, 15,37 s |
| test_v4_manuscript_assembly_derive.py | 84 passed, 14,38 s |
| test_frozen_files_are_untouched | 1 passed, 2,07 s |
| Tectonic --only-cached | Uma compilação, exit 0, sem download |
| paper_check com assembled-values.json | PASS, rascunho; 5.101 IDs, resumo 196 palavras |

A única compilação usou `release-day/invalid-main` e um wrapper sem texto visível adicional: ele executa a sonda da macro não montada e depois inclui o `main.tex` intacto. O log confirma `RESULTPLURAL-DEFAULT: units were`. Foram usadas a classe e a bibliografia já existentes do T51 e uma cópia do cache do T41d. O PDF sintético tem 88 páginas e 50.110 palavras extraídas. A [prova de compilação](t41e-compilation.json) registra hashes, dependências e valores. AV03 e Other declarations permanecem como os dois placeholders do Owner; o PASS é técnico e não declara aceitação científica ou prontidão de submissão.

Todos os portões foram sequenciais, com um pytest por arquivo/processo e OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS e VECLIB_MAXIMUM_THREADS em 1. `nice -n 15` foi tentado; o macOS recusou setpriority, mas executou os comandos. A primeira execução de Ruff apontou dois ajustes de estilo nos testes; a primeira execução de pytest teve 173 passed e uma falha no padrão da mensagem esperada de um teste novo. Ambos foram corrigidos antes dos portões finais. A revisão adicional de concordância incluiu G0 fits e complete but invalid units; a auditoria e a repinagem finais já os incorporam.

A árvore final dos 24 ensaios está em `/private/tmp/v4-shell-assembly-audit-7re6ekcq`. Todos os fatos e agregados usados são artificiais, explícitos e provenientes apenas dos ensaios públicos nomeados; nenhum resultado sob selo foi aberto e nenhum microdado do SHP foi usado.

`git diff --stat` ao fim da tarefa, incluindo somente arquivos rastreados:

```text
 .../publications/jcss-manuscript/main.tex          |     1 +
 .../jcss-manuscript/pipeline/ASSEMBLY.md           |    11 +
 .../drafts/2026-09-28/results-shells-abstract.md   |    26 +-
 .../pipeline/drafts/2026-09-28/results-shells.tex  |   116 +-
 .../2026-09-30/discussion-conclusion-shells.tex    |   106 +-
 .../2026-09-30/exploratory-results-shells.tex      |   100 +-
 .../jcss-manuscript/pipeline/paper_check.py        |    10 +-
 .../review/audit_v4_manuscript_assembly.py         |    48 +-
 .../pipeline/review/check_v4_abstract_budget.py    |    31 +-
 .../v4-manuscript-assembly-audit-2026-09-30.json   | 46304 ++++---------------
 .../ic_study/analysis/v4_manuscript_assembly.py    |    38 +-
 .../analysis/v4_manuscript_assembly_rules.json     |     8 +-
 .../current_shell_oracles.json                     |     4 +-
 .../tests/unit/test_v4_manuscript_assembly.py      |   139 +
 14 files changed, 8817 insertions(+), 38125 deletions(-)
```

Os recibos e relatórios novos aparecem como não rastreados; o coordenador revisa e commita. `git status --short`:

```text
 M studies/ic-2026-2027/publications/jcss-manuscript/main.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/ASSEMBLY.md
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells-abstract.md
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/drafts/2026-09-30/exploratory-results-shells.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/paper_check.py
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/audit_v4_manuscript_assembly.py
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/check_v4_abstract_budget.py
 M studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/v4-manuscript-assembly-audit-2026-09-30.json
 M studies/ic-2026-2027/src/ic_study/analysis/v4_manuscript_assembly.py
 M studies/ic-2026-2027/src/ic_study/analysis/v4_manuscript_assembly_rules.json
 M studies/ic-2026-2027/tests/fixtures/v4_manuscript_assembly/current_shell_oracles.json
 M studies/ic-2026-2027/tests/unit/test_v4_manuscript_assembly.py
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-abstract-budget.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-compilation.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-divergences.md
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-number-agreement.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-plural-default-probe.tex
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-report.md
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-scope-proof.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-selection-changes.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-shell-repin-receipt-final.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-shell-repin-receipt-verified.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-shell-repin-receipt.json
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/t41e-synthetic-successors.json
```
