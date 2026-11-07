# Montagem determinística após a liberação

O montador recebe os catálogos dos exportadores, a cópia do manuscrito com os
arquivos `generated/` já exportados e os fatos públicos do Owner. Ele seleciona
os 267 blocos revisados, vincula os números, preserva o texto fixo e aplica o
orçamento do resumo. Não abre registros de execução nem segue as fontes dos
fatos. A montagem não declara aceitação científica.

Nos shells, `\resultplural{ID}{singular}{plural}` vincula a concordância ao
mesmo catálogo que `\resultnum{ID}{[n]}`. O valor inteiro 1 escolhe a primeira
forma; 0 e os demais inteiros não negativos escolhem a segunda. As formas são
texto simples, sem chaves internas, e podem conter substantivos, verbos ou
pronomes. Contagens com separadores de milhar e parte decimal só de zeros
também são inteiras. Um ID ausente, uma contagem inválida ou um ID sem
`\resultnum` no mesmo bloco selecionado recusam a montagem com localizador.
O montador resolve a concordância antes de calcular o orçamento do resumo.
O preâmbulo e o `paper_check` usam somente a forma plural no manuscrito ainda
não montado; a montagem contém o texto escolhido, sem o construto.

No diretório `studies/ic-2026-2027`, a montagem ocorre em um comando:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 .venv/bin/python \
  -m ic_study.analysis.v4_manuscript_assembly \
  --confirmatory-values /caminho/publico/a-catalog.json \
  --exploratory-values /caminho/publico/exploratory-catalog.json \
  --assembly-facts /caminho/publico/assembly-facts.json \
  --manuscript /caminho/publico/manuscrito-exportado \
  --output /caminho/publico/nova-montagem \
  --values /caminho/publico/valores-da-montagem.json
```

`--exploratory-values` é dispensável quando o catálogo confirmatório já foi
mesclado. `--audit-only --report arquivo-novo.json` avalia todas as decisões sem
copiar o manuscrito. Uma informação exigida ausente produz recusa, com bloco,
arquivo e linha; o processo retorna 2 e não cria a cópia. O destino e o relatório
precisam ser novos. O relatório externo não pode sobrescrever o recibo da cópia.

`--values` é opcional e exige uma montagem efetiva, sem `--audit-only`. Grava o
mesmo formato de registro dos exportadores (`schema`, `synthetic`, `values`,
`sources`, `components`), conservando a proveniência recebida e acrescentando
os hashes da montagem. O mapa `values` contém somente os IDs citados pela
árvore final a partir de `main.tex`; números ausentes ou diferentes do catálogo
recusam a gravação e removem a cópia incompleta. O caminho precisa ser novo,
distinto do relatório e do recibo. Seu digest e a contagem de IDs entram em
`assembly-record.json`. Passe esse arquivo a `paper_check.py --result-values`,
após compilar a cópia. O checker recebe o registro restrito, nunca o catálogo
completo.

A reexportação manual sobre a montagem continua sendo uma alternativa. Use
nomes novos para ambos os registros e as mesmas entradas públicas autorizadas:

```sh
"$python" -m ic_study.analysis.v4_exploratory_export \
  --x3 "$aggregates/x3.json" --x4 "$aggregates/x4.json" \
  --x6 "$aggregates/x6.json" --x7 "$aggregates/x7.json" \
  --comparisons "$comparisons" --confirmatory-values "$confirmatory_catalog" \
  --manuscript "$assembled" --values "$new_values" --catalog "$new_catalog" --fill
```

Sem exploração, repita a exportação confirmatória com `--manuscript` apontando
para a montagem e `--values`/`--catalog` novos, antes da compilação.

Antes de emitir `ready`, inclusive em `--audit-only`, o montador expande os
`\input` dos documentos compostos. Todo arquivo incluído precisa existir na
cópia exportada; rótulos `\label` repetidos recusam a montagem com o nome e
os localizadores de ambas as ocorrências. Comentários não contam. A cópia final
é verificada novamente antes da gravação do recibo. Isso verifica a composição
sem compilar LaTeX. AV03 e Other declarations continuam pendentes do Owner;
`ready` não certifica prontidão editorial nem aceitação científica.

O exportador exploratório recusa um ponto finito, válido e sem censura que fique
fora do próprio intervalo. Para X6, a cobertura conjunta respeita os limites
da interseção das coberturas marginais na população completa; gaps-as-misses
preserva o numerador de cobertura e amplia somente o denominador declarado.
Verdades indisponíveis continuam indisponíveis, sem contagens inventadas.
Contagens de excedência ou dependência do canal que superem o número de pares
comparados também recusam a entrada; zero comparações não sustenta leitura
positiva sobre o canal.

O exportador confirmatório acrescenta 15 IDs: para cada estágio G0, G1b, G1c,
G2 e G2c, `v4.gate.<estágio>.verdict.complete`, `.approved` e `.stop`, todos com
valor `"0"` ou `"1"`. Uma linha parcial com `pass: false` não constitui falha
completa; uma linha parcial nunca aprova um estágio. A parada é o registro do
guard de economia antes de G2: somente `.G2.verdict.stop` é 1. Os demais IDs
permanecem iguais. A proveniência continua identificando o código efetivamente
usado; o hash do exportador muda quando seu código muda.

O arquivo de entrada `assembly-facts.json` usa o esquema
`ic-study.v4-manuscript-assembly-facts.v1`, publicado em
`src/ic_study/analysis/v4_manuscript_assembly_facts.schema.json` e validado pelo
módulo de mesmo nome. A raiz contém exatamente `schema`, `synthetic` e `facts`.
Cada entrada de `facts` contém exatamente `value` e `source`; a fonte contém
`record`, `locator` e `sha256`. O registro e o localizador devem ser textos não
vazios; o digest tem 64 caracteres hexadecimais minúsculos. As fontes devem
identificar registros públicos de decisão ou metadados agregados, sem conteúdo
restrito. O montador verifica a estrutura e registra a fonte; não abre o registro
para certificar a declaração do Owner.

| Fato | Valor e exigência |
| --- | --- |
| `shp.state` | `B14` |
| `shp.reason` | Motivo público da não execução, causa da falha ou divergência; exigido nas alternativas sem âncora admissível. Entra como texto escapado, nunca como código TeX. |
| `shp.divergence` | Para divergência prévia: objeto com `kind` (`item`, `scale`, `mode`), `recorded_utc` e `execution_started_utc`. Ambos os horários precisam ser UTC e o registro deve preceder a execução. |
| `shp.grid_position` | `B13` |
| `gate.at_close` | Booleano que documenta a observação no encerramento, necessário apenas para B1d. Não inferido do relógio do computador. |
| `tier2.boundaries_differ` | `B06` |
| `main.boundary_nonmonotone` | `B07` |
| `post.x5_supplied` | Com PASS e comparações pós-liberação: booleano com fonte na proveniência do agregado, combinado com todas as etiquetas `by_r.x5_state` do catálogo. Ausência de listas/contagens não estabelece fornecimento. Inconsistência recusa a montagem. |
| `gate.G0.failed_criteria` | `B1b-G0` |
| `gate.G1c.failed_criteria` | `B1b-G1c` |
| `gate.G2.failed_criteria` | `B1b-G2` |
| `gate.G2c.failed_comparisons` | `B1b-G2c` |

As listas não admitem repetições. Campos, estados e tipos desconhecidos são
recusados, assim como chaves JSON duplicadas. Fatos dispensáveis podem ser
omitidos; fatos exigidos pelas alternativas selecionadas não recebem valores
padrão. Os fatos e seu digest entram em `assembly-record.json`, junto aos hashes
dos catálogos mesclados, regras, shells e documentos produzidos.

Os arquivos sob `tests/fixtures/v4_manuscript_assembly/{release-day,g2c-failure,dress}`
são fatos artificiais explícitos dos ensaios, com `synthetic: true`. Não servem
como fatos da análise real. A auditoria compara os 12 casos originais e suas
12 montagens em dress rehearsal. Ela reproduz os catálogos pelo exportador do
commit anterior, compara todos os IDs antigos byte a byte e registra cada
divergência de composição com o localizador do shell e o lado que o segue.
As montagens manuais permanecem intactas. T41c usa sucessores explicitamente
sintéticos para corrigir as identidades X6 e o ponto X7 da origem artificial;
`pipeline/review/t41c-synthetic-successors.json` vincula originais e sucessores
por hash e registra cada campo alterado. As leituras primárias permanecem
registradas; esses sucessores não são evidência do estudo.

As condições de seleção revistas estão separadas em
`pipeline/review/t41c-selection-changes.json`, com antes, depois e linha do
shell. B11 conserva inventário e não avaliação, enquanto excedência, sensibilidade
e dependência do canal têm seus próprios guards. A.B11 exige dependência positiva;
A.B05 exige queda pontual positiva. Uma marca de banda não estabelece queda
pontual. As implicações de conclusão preservam os guards existentes; a frase
de fronteira atingida exige também uma contagem positiva. A síntese X1b atual
usa apenas o agregado fornecido e seus estados em todos os r; o texto histórico
fixo é identificado como outra fonte, sem presumir identidade ou independência
das execuções. X7 é incluído uma única vez por main.tex.

A T41d aplica a consolidação do coordenador e registra a emenda às decisões
91/101 antes da exposição: A.B04, A.B05, A.B06, A.B08 e A.B11 exigem contagens
exibidas positivas somente no resumo. A.B08 exige ambas as contagens positivas.
Os guards A.B05/A.B11 da T41c já satisfaziam essa regra. A.new-seeds passa de
order 16 para 950; os resultados, inclusive os opcionais admitidos pelo
first-fit, vêm antes da ressalva e da limitação. A prioridade dos oito
opcionais permanece igual. A tabela completa está em
`review/t41d-selection-conditions.md`.

O baseline compartilhado com main.tex tem 103 palavras. O comando
`review/check_v4_abstract_budget.py` enumera as 46 composições obrigatórias
distintas com a lista máxima de nove valores de r, incluindo diferenças apenas
de intervalo entre primeira e sustentada sob B03. Os quatro fallbacks
autorizados, na ordem da consolidação, deixam o máximo em 246 palavras. As
24 montagens de ensaio têm 175–234 palavras. O recibo verificado é
`review/t41d-shell-repin-receipt-verified.json`; as propostas aplicadas e
não aplicadas constam de `review/t41d-editorial-proposals.json` e
`review/t41d-human-decisions.md`. Os mesmos bindings, marcadores e comentários
SELECT WHEN/ACTION/INCLUDES foram preservados nos outros três shells.

A repinagem reutilizável roda a partir deste estudo com o mesmo ambiente de
threads do comando de montagem:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 .venv/bin/python \
  publications/jcss-manuscript/pipeline/review/repin_v4_manuscript_assembly.py \
  --old-shell results=REV_ANTIGA_RESULTS \
  --old-shell abstract=REV_ANTIGA_ABSTRACT \
  --old-shell discussion=REV_ANTIGA_DISCUSSION \
  --receipt /caminho/publico/novo-recibo.json
```

Cada revisão precisa reproduzir o digest que as regras ainda fixam. O comando
remapeia regras, fragmentos, cláusulas e localizadores de escopo por diff, e
recusa alterações visíveis sem `--accept-visible ID` por regra. Para limitar
um hunk que também incluiu uma nota externa, use `--locator ID=INICIO:FIM`
junto ao aceite; o limite precisa ficar dentro do candidato calculado pelo diff.
Remoção de um trecho exigido continua recusada mesmo com aceite. Em recusas,
regras e recibo permanecem ausentes ou intactos. Comentários também precisam de
revisão semântica: SELECT, ACTION e INCLUDES podem mudar o comportamento.

A T41b partiu de `c1371ebe` nos três shells. Foram aceitos `A.design`,
`D-X5-POST`, `C-B14`, `C-G2C` e `C-CLOSE`, com `A.design=13:13` para excluir a
nota editorial. O recibo `review/t41b-shell-repin-receipt.json` registra cada
ID, classificação, linhas, hashes e decisão; também vincula o registro final
após as adaptações semânticas T36/T38b. Reexecutar essa transição exige o arquivo
antigo de regras, não o registro já repinado.

T36 acrescenta os blocos `C-EVALUATION-PASS` e `D-X5-POST-UNAVAILABLE`.
`C-EVALUATION-REQUIRED` aplica às demais conclusões sem PASS a exigência geral
da linha 28, usando a sentença literal 692 sem duplicá-la em G2c ou no fechamento.
As 264 identidades anteriores permanecem. As seções fixas usadas como entrada
devem ser as versões integradas corrigidas de DS01/DS02/DS10/CN01; o montador
preserva seu conteúdo. A montagem com PASS mantém P1-P10, mas inclui F1/F2B/T1,
T4/F5, T3/F4 e F6 nessa ordem de exibição. Os arquivos gerados conservam as
legendas dos exportadores integrados.

`manual_oracles.json` continua sendo a evidência histórica. O oráculo separado
`current_shell_oracles.json` troca a abertura T38a nas mesmas escolhas manuais
e repõe, com fonte e hash, as etiquetas X5 que o catálogo público já trazia e
o recorte compacto histórico omitia. A auditoria registra novas divergências,
as desaparecidas e aquelas
cujo texto mudou. A prova dos três digests exploratórios fica em
`review/t41b-verdict-catalog-proof.json`: após retirar exatamente os 15 IDs
novos, a serialização integral coincide com os catálogos do worktree limpo
`6fce4b50`; apenas os três digests que continham gate foram atualizados.

## Derivação antes da montagem

Antes da montagem, `v4_manuscript_assembly_derive` recebe as mesmas entradas
públicas de `detection_v4_report` e um arquivo parcial do Owner. Usa
`load_inputs`, incluindo a validação do recibo de liberação, dos sucessores de
estágio e da alocação vinculada aos critérios. Os catálogos entram somente na
auditoria posterior; nenhum valor formatado participa da derivação.

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 .venv/bin/python \
  -m ic_study.analysis.v4_manuscript_assembly_derive \
  --curves /caminho/publico/released-curves.json \
  --release-record /caminho/publico/release-record.json \
  --gate-root /caminho/publico/gate \
  --allocation /caminho/publico/v4-allocation.json \
  --stage-successor /caminho/publico/G1c-aggregate-successor.json \
  --shp /caminho/publico/shp-aggregate-successor-1.json \
  --crosswalk /caminho/publico/crosswalk.json \
  --criteria experiments/exploratory/detection-boundary-v4/criteria-v43.json \
  --owner-facts /caminho/publico/owner-facts.json \
  --out /caminho/publico/assembly-facts-novo.json \
  --confirmatory-values /caminho/publico/a-catalog.json \
  --exploratory-values /caminho/publico/exploratory-catalog.json \
  --manuscript /caminho/publico/manuscrito-exportado
```

As entradas opcionais seguem o relatório: omitir curvas e recibo quando não há
liberação, SHP quando não há agregado e sucessor/alocação quando não se aplicam.
`--stage-successor` aceita repetição. `--synthetic` marca somente os ensaios
artificiais e precisa coincidir com o arquivo do Owner. Esse arquivo conserva o
mesmo esquema de fatos, podendo conter `facts: {}`. Deve trazer exclusivamente
as declarações aplicáveis: `shp.reason`, `shp.divergence`, `gate.at_close`,
`post.x5_supplied` e `shp.state` em `not-run`, `failed` ou `pre-run-divergence`.
A derivação exige as entradas liberadas autorizadas e recusa `--public-aggregates`.

Comece com `facts: {}` e leia `missing_facts`. Neste ramo com PASS e comparações,
`post.x5_supplied` exige uma declaração pública do Owner mesmo quando X5 não foi
fornecido; a fonte vincula a proveniência do agregado e as etiquetas `by_r.x5_state`.
Omitir `--crosswalk` quando a ponte não foi usada no relatório. Não reutilize
fixtures manuais como arquivo do Owner: elas também contêm fatos calculáveis,
recusados pela derivação. Use nomes novos para a segunda saída de fatos.

| Fato derivado | Definição sobre os agregados | Bloco de `results-shells.tex` |
| --- | --- | --- |
| `tier2.boundaries_differ` | Alguma unidade válida de tier 2 tem tuplas `(point, interval, censoring, interval_censoring)` diferentes entre primeira e sustentada. Inclui diferenças apenas de intervalo ou censura; ignora unidades inválidas. | `B06` |
| `main.boundary_nonmonotone` | Nas unidades válidas de tier 1, em ordem de `r`, usa `idx(first)` quando atingida e 9 quando `first` é nulo sem censura; omite os demais casos. É verdadeiro somente se a sequência definida não for crescente nem decrescente, admitindo empates. | `B07` |
| `shp.state` | Em agregado emitido com ajuste primário convergente, `multiwave.at_parameter_bound` booleano verdadeiro dá `parameter-bound`; falso dá `admissible`. Sem agregado, os três estados restantes não são distinguíveis e continuam declaração do Owner. | `B14` |
| `shp.grid_position` | Com âncora admissível e liberação, compara primeiro a estimativa com `[0.50, 0.90]`: `below` ou `above`; se estiver dentro, extremos do Wald estritamente fora dão `interval-outside`, senão `inside`. Os limites pertencem à grade; a âncora não é arredondada. | `B13` |
| `gate.G0.failed_criteria` | Com estágio completo falho e `fits`, seleciona contagem de falhas de âncora > 0, de budget > 0 e proporção de implementação > 0.01. | `B1b-G0` |
| `gate.G1c.failed_criteria` | Com estágio completo falho e critérios, seleciona `anchor_count < 150`, `pointwise_failures > 3` e `mean_z > 3`. | `B1b-G1c` |
| `gate.G2.failed_criteria` | Com estágio completo falho e critérios, seleciona allowance falsa; algum limite inferior de célula ou pooled estritamente acima do limiar superior (`above`); algum limite superior estritamente abaixo do limiar inferior (`below`); FD estável falso; e razões de células vazias (`insufficient`). Com razões presentes, exige `--criteria` para decidir a lista inteira. | `B1b-G2` |
| `gate.G2c.failed_comparisons` | Com estágio completo falho e as duas razões presentes, usa a ordem `a010`, `a003`. Falha se `failure_count` exceder 3/100 ou 2/40, `upper < 0.8` ou `lower > 2.0`; verifica a concordância com o `pass` de cada comparação. | `B1b-G2c` |

Cada fato traz o nome público do arquivo, a regra ou ponteiro e seu SHA-256.
Para um estágio suprido por sucessor, a fonte é o sucessor com `/summary`;
caso contrário, é a linha selecionada de `criteria.jsonl`. A regra de G2
também registra no localizador o nome e digest dos critérios que fornecem os
limiares. Fronteiras usam o digest das curvas validado pelo recibo.

O comando recusa um fato calculável no arquivo do Owner, inclusive quando o
valor coincide com o derivado. Valores diferentes produzem conflito explícito.
`merge_facts` valida ambos os registros e a união com `validate_facts`. Não
preenche estados, motivos nem observações no encerramento. Falha técnica antes
de avaliar critérios ou estágio incompleto não produz uma lista de critérios.

Depois de gravar os fatos em um arquivo novo, o comando chama o montador com
`--audit-only`. A saída JSON contém `missing_facts`, a mensagem de recusa com
blocos e linhas e o relatório completo em `assembly_audit`. Retorna 2 se a
montagem recusar; o arquivo de fatos continua disponível para inspeção. Não
copia o manuscrito. A montagem efetiva continua sendo o comando inicial.

A comparação dos 24 ensaios com suas fixtures manuais é reproduzível por
`pipeline/review/audit_v4_manuscript_assembly_derive.py --report arquivo-novo.json`.
Esse script lê somente os três ensaios públicos sintéticos nomeados e escreve
um recibo novo com hashes, comparações e divergências. A opção
`--write-synthetic-inputs arquivo-novo.json` produz a cópia reduzida de agregados
usada em `tests/fixtures/v4_manuscript_assembly/synthetic_inputs.json`; os testes
reconstroem entradas válidas com esses números e não dependem de `/private/tmp`.
As fixtures manuais permanecem intactas. O ensaio `dress/ii-comparison-no-ratio`
declara `admissible`, embora seu agregado tenha `at_parameter_bound: true`:
B14, linhas 567–569, determina `parameter-bound`. O teste registra essa
divergência conhecida e exige igualdade nos demais fatos calculáveis.

## Ordem e numeração do suplemento (T59)

A cópia final conserva a ordem texto principal, declarações, Apêndice A
(ODD+D), referências e Supplementary Material. O `\clearpage` após a
bibliografia esvazia os floats anteriores antes de zerar os contadores de
tabelas e figuras. O Apêndice A não tem floats; se ganhar algum, a classe
sn-jnl o numera como A1, A2, …. Os floats do suplemento usam S1, S2, …, com destinos hyperref separados (`supp.`).
As chamadas no texto principal identificam as tabelas e figuras suplementares.

O slot `\input{sections/supplement-exploratory-x1-x2}` continua único e
recebe imediatamente depois o suplemento X3–X7. A montagem ainda transfere
`generated/exploratory-x7-boundaries` para depois de `generated/exploratory-x7`
nesse suplemento, antes das tabelas pós-liberação. As sondagens de conteúdo,
o título condicional e todos os includes suplementares ficam após as referências.
