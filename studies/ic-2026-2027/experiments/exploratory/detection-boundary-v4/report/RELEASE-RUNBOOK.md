# Roteiro do dia da liberação da v4

Este roteiro leva as curvas confirmatórias seladas até um PDF do manuscrito JCSS com os números vinculados. Após a liberação pelo sucessor `release_on_completion.py`, que chama a função congelada `released_curves` (seção 2), a sequência é: relatório autorizado, exportação confirmatória e exploratória para uma cópia nova, projeção pública candidata e sua conferência, derivação dos fatos, conferência de `missing_facts`, montagem determinística, nova exportação de `--values` sobre a montagem, compilação, `paper_check` e empacotamento. A projeção candidata depende da revisão pública do Owner. A seleção dos blocos segue [pipeline/ASSEMBLY.md](../../../../publications/jcss-manuscript/pipeline/ASSEMBLY.md); a montagem técnica não autoriza submissão. O fechamento é 2026-10-19T02:59:00Z, que corresponde a 18/10/2026 às 23:59 em São Paulo, e pela emenda de liberação a liberação acontece antes dele se o inventário completar antes. Nenhum comando deste roteiro roda contra as raízes reais antes da liberação, a não ser o script de espera da seção 2, e nada do que sai da liberação entra no Git antes da revisão.

Com a cadeia automática instalada, o trabalho manual do dia começa no status `awaiting-authorized-handoff` e segue a seção 12, ensaiada em 02/10/2026.

A cadeia foi ensaiada ponta a ponta com dados sintéticos em 28/09/2026, nos dois caminhos: gate aprovado e gate reprovado em G0 (seção 11). Nos dois, o `paper_check --submission` só acusou os três placeholders editoriais que os autores ainda precisam escrever. Com a máquina ocupada pelo gate, a renderização, a exportação, a compilação e a verificação somaram menos de dois minutos.

Os comandos usam estas variáveis, definidas uma vez no terminal:

```sh
coord=$HOME/.local/state/research-workbench/coord-20260925
out=$coord/v4-release
frozen=$HOME/.local/state/research-workbench/ic-boundary-v4
springer=$HOME/.local/state/research-workbench/springer-template
report_checkout=CAMINHO_DO_CHECKOUT_DO_RELATORIO
```

`report_checkout` é um checkout limpo de um commit que contém `src/ic_study/analysis/v4_report_export.py` e o script sucessor `experiments/exploratory/detection-boundary-v4/release_on_completion.py`, normalmente o ramo de integração. `springer` guarda o `sn-jnl.cls` e o `sn-mathphys-num.bst` oficiais, fora do Git.

## 1. Pré-condições

O checkout congelado precisa estar limpo no commit do congelamento, e o registro de congelamento precisa ter o hash que o driver do gate conferiu:

```sh
git -C "$frozen" rev-parse HEAD
git -C "$frozen" status --porcelain
shasum -a 256 "$frozen/studies/ic-2026-2027/experiments/exploratory/detection-boundary-v4/freeze-v4.json"
```

O primeiro comando deve imprimir `375138418f7f9e4528f0c2466f4600a76fee1bad`, o segundo nada, e o terceiro `99c4277235d4f2303b6f009d6ead8287a5d71372744dd6781e1e2d1847710837`.

A raiz selada do gate é a linha que o preflight do driver imprimiu no log. O comando abaixo lê só essa linha e confere o identificador, que é o SHA-256 do mapa `code` do registro de congelamento:

```sh
gate=$(grep -m1 '^sealed root: ' "$coord/v4-gate-driver.log" | sed 's/^sealed root: //')
test "$(basename "$gate")" = 6d6f9f4d5d04fbc1cd79f20d3beff499ccdc318584f3f348bdb956c71a344c90 && echo "$gate"
```

Os registros privados de coordenação ficam onde estão: a segunda vinculação em `$coord/v4-allocation.json`, o sucessor de G1c em `$coord/v4-gate-logs/G1c-aggregate-successor.json` e, se o Owner fornecer, o agregado SHP em `$coord/shp-aggregate-successor-1.json`. O crosswalk sintético é versionado em `experiments/exploratory/shp-anchor-crosswalk-v1/crosswalk.json` e já passa pelo leitor do relatório.

Antes da cadeia, registre num inventário de entradas o produtor, a revisão completa, o caminho autorizado e o SHA-256 de cada arquivo: segunda vinculação, sucessor G1c, agregado SHP, ponte, agregado aberto da execução registrada de X1b e execuções únicas X5/X7 identificadas pelo coordenador. A existência do caminho não identifica a execução escolhida. O agregado SHP é produzido pelo Owner no ambiente autorizado; estas ferramentas apenas o consomem. Registre também o arquivo público `owner-facts.json` e sua origem. Esses caminhos não autorizam acesso antecipado aos dados privados.

No checkout do relatório, o ambiente precisa estar sincronizado antes do dia, e o `git status` precisa estar limpo para que o manifesto registre `reporting_code_dirty: false`:

```sh
cd "$report_checkout/studies/ic-2026-2027" && nice -n 10 uv sync --frozen && git status --porcelain
ls "$springer"
```

A compilação precisa de um executável Tectonic já disponível, cache preparado e de `pdfinfo` e `pdftotext` (poppler); o `ls` deve mostrar os dois arquivos da Springer. Prepare o ambiente e copie o cache antes de um ensaio offline. Não invoque `nix shell` ou `uv sync` durante uma execução em que downloads são proibidos. Falta de recurso no cache é uma recusa explícita. As decisões ainda abertas do Owner (seção 10) precisam estar tomadas antes do fechamento.

## 2. Agendar a liberação

A [emenda de liberação](../../../../research/questions/exploration/2026-09-24-parallel/detection-boundary-v4-release-amendment.md) antecipou a liberação para o primeiro de dois momentos: (a) as 414 unidades de `curve_units()` têm o registro de curva gravado e nenhum processo `run_curve.py` está em execução, o que se verifica só pela existência do `curve.json` de cada unidade, sem abrir conteúdo; (b) o fechamento declarado. Não existe liberação parcial. Quem libera é o script sucessor `release_on_completion.py`. Ele repete o pré-voo do `run_curve.py --release-at-close` congelado, com as mesmas funções congeladas e na mesma ordem, confere a condição e chama o `released_curves` congelado. Antes do fechamento, passa `now` igual ao fechamento declarado, e por isso o inventário selado continua com `closed_utc` igual a 2026-10-19T02:59:00Z. Depois do fechamento, segue o caminho original. O script publica `released-curves.json` diretamente no diretório do recibo, no formato de `released_curves` que o leitor espera. A saída padrão informa o caminho do recibo; ela não deve ser redirecionada para o arquivo de curvas. O horário real, a condição que disparou, o caminho e o commit da emenda, o SHA-256 da saída e o do próprio script ficam em `release-record.json`.

O pré-voo confere o estudo de onde vem o `ic_study` importado. Por isso o script roda com o ambiente do checkout congelado, com o mesmo `uv`, o mesmo cache e os mesmos limites de BLAS que o driver dos tiers usa, mas o arquivo fica no checkout do relatório. Um `.py` a mais na pasta do experimento do checkout congelado mudaria o mapa `code` e o pré-voo recusaria. Enquanto o script de espera roda, o checkout do relatório não deve ser atualizado; de todo modo, o registro guarda o SHA-256 do arquivo que de fato rodou.

A cada 5 minutos, o script de espera roda `--check-only`, que imprime só `{"complete": ..., "pending": ...}`. `pending` conta as unidades sem `curve.json`, e `complete` só é verdadeiro quando não falta nenhuma e nenhum `run_curve.py` está vivo. Quando `complete` fica verdadeiro, o script tenta a liberação imediatamente. Uma recusa grava `$out/release-ALERT`, com o código de saída, a data operacional e a causa na última linha do stderr, e repete a tentativa a cada 30 minutos, sem limite, até liberar. O alerta fica preservado para diagnóstico, mesmo depois de uma tentativa bem-sucedida. O fechamento continua como gatilho alternativo: espera o último `run_curve.py` terminar e libera pelo caminho original, com a mesma política de repetição se houver recusa. O pré-voo, o lock e a validação do par saída+recibo continuam no sucessor, sem alteração. Salve esta cópia nova em `$coord/v4-release-wait.next.sh`; não substitua nem reinicie a espera em uso:

```sh
#!/bin/bash
set -uo pipefail
umask 077
coord=${V4_COORD:-$HOME/.local/state/research-workbench/coord-20260925}
out=$coord/v4-release
script=${1:?report checkout}/studies/ic-2026-2027/experiments/exploratory/detection-boundary-v4/release_on_completion.py
test -f "$script" || exit 1
mkdir -p "$out" && chmod 700 "$out"
cd "${V4_FROZEN:-$HOME/.local/state/research-workbench/ic-boundary-v4}/studies/ic-2026-2027" || exit 1
export UV_CACHE_DIR=/private/tmp/uv-cache-v44
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
run() {
  "${V4_UV:-$HOME/.local/bin/uv}" run --frozen python "$script" \
    --freeze experiments/exploratory/detection-boundary-v4/freeze-v4.json \
    --allocation "$coord/v4-allocation.json" "$@"
}
release() {
  run --record "$out/release-record.json" >>"$out/release.stdout" 2>>"$out/release.stderr"
  status=$?
  echo "exit=$status $(date -u +%FT%TZ)" >>"$out/release.exit"
  if [ "$status" -ne 0 ]; then
    { echo "release refused: exit=$status $(date -u +%FT%TZ)"; tail -n 1 "$out/release.stderr"; } >"$out/release-ALERT.tmp"
    mv "$out/release-ALERT.tmp" "$out/release-ALERT"
  fi
  return "$status"
}
if test -e "$out/release-record.json"; then release; exit "$?"; fi
closed() { [ "$(date -u +%Y%m%d%H%M)" -ge 202610190300 ]; }
while :; do
  if closed; then
    while pgrep -f run_curve.py >/dev/null; do sleep 30; done
    release && exit 0
    sleep 1800
  elif run --check-only | grep -q '"complete": true'; then
    release && exit 0
    sleep 1800
  else
    sleep 300
  fi
done
```

O script recebe o caminho do checkout do relatório. Ele é iniciado depois das conferências da seção 1, com o checkout do relatório num commit que contém `release_on_completion.py`, e pode ficar esperando desde antes do primeiro tier, porque até o inventário completar só testa a existência dos arquivos de curva. Para que o Mac não durma, o script roda sob `caffeinate`, com o computador na tomada e a tampa aberta:

```sh
nohup caffeinate -ims /bin/bash "$coord/v4-release-wait.next.sh" "$report_checkout" >"$coord/v4-release-wait.next.log" 2>&1 &
```

A saída da liberação (`released-curves.json`), o registro (`release-record.json`), o stderr e o código de saída de cada tentativa (`release.exit`) ficam em `$out`, dentro da pasta privada de coordenação (modo 700, arquivos 600), fora do Git. O stderr das checagens vai para `$coord/v4-release-wait.next.log`. Se o script for iniciado depois do fechamento, ele libera assim que não houver `run_curve.py` vivo. O script usa um único lock de arquivo (`.release.lock`) por diretório para proteger a tentativa inteira, inclusive o pré-voo. Uma tentativa concorrente é recusada sem escrever curvas ou recibo. Saída e recibo são gravados em temporários no mesmo diretório, com `fsync`; a saída é publicada por rename atômico e sincronização do diretório antes do recibo. O recibo contém o SHA-256 dos bytes publicados. Sucesso exige esse par íntegro. Ao reiniciar, um par válido é idempotente, sem repetir o pré-voo nem regravar bytes; recibo sem saída ou com digest diferente é erro explícito. Saída sem recibo indica tentativa interrompida e pode ser refeita. Uma falha de escrita não publica o recibo. O lock permanece no diretório e não deve ser removido enquanto houver uma tentativa viva.

## 3. Conferir a saída da liberação

```sh
cat "$out/release.exit"
python3 -c 'import json, sys; d = json.load(open(sys.argv[1])); print(sorted(d), d["inventory"]["closed_utc"], len(d["curves"]))' "$out/released-curves.json"
python3 -c 'import json, sys; r = json.load(open(sys.argv[1])); print(r["condition"], r["released_utc"], r["released_curves_sha256"])' "$out/release-record.json"
python3 - "$out" <<'PYPAIR'
import hashlib, json, sys
from pathlib import Path
out = Path(sys.argv[1])
record = json.loads((out / "release-record.json").read_bytes())
assert hashlib.sha256((out / "released-curves.json").read_bytes()).hexdigest() == record["released_curves_sha256"]
print("release pair verified")
PYPAIR
```

A última linha de `release.exit` deve ser `exit=0`, e nos dois caminhos aparecem as chaves `['curves', 'inventory']` e `2026-10-19T02:59:00Z`. O registro diz se a liberação veio do inventário completo (`inventory-complete`) ou do fechamento (`declared-close`) e quando ela aconteceu de fato, e a conferência automática precisa imprimir `release pair verified`. A existência isolada do recibo não declara sucesso. O horário real vem do registro, não do inventário, e é ele que a emenda manda citar ao lado do `closed_utc`.

Se a saída for `{"preflight_or_execution_failure_count": 1}` com `exit=2`, o script sucessor escreve a causa numa linha de `$out/release.stderr`. As causas possíveis, na ordem em que ele verifica, são: ambiente diferente do congelado (checkout sujo ou `uv` diferente); a segunda vinculação ou um estágio do gate que não passou; algum `run_curve.py` ainda vivo (`pgrep -fl run_curve.py`); inventário incompleto antes do fechamento; ou falha de integridade do par publicado. Um par já válido retorna sucesso sem alterações. Para o gate, basta procurar o marcador que o driver dos tiers também usa, sem abrir nada selado: `grep -c '^GATE_SEQUENCE_DONE' "$coord/v4-gate-driver.log"`. Sem esse marcador não existe liberação, e o artigo segue um dos ramos de falha do gate. Nesse caso as seções 4 e 5 rodam sem `--curves`, sem `--shp` e sem `--crosswalk`, e o relatório contém só T3 e F4. Se o gate ainda estiver rodando no fechamento (ramo B1d), a decisão Q3 do Owner diz se o driver continua; o relatório só do gate deve ser gerado com o driver parado, porque a exportação confere os hashes do gate contra o manifesto e recusa entradas que mudaram.

## 4. Renderizar o relatório

As entradas são montadas uma vez e reutilizadas na exportação. Os arquivos opcionais entram só se existirem:

```sh
cd "$report_checkout/studies/ic-2026-2027"
inputs=(--gate-root "$gate" --criteria experiments/exploratory/detection-boundary-v4/criteria-v43.json)
test -f "$coord/v4-allocation.json" && inputs+=(--allocation "$coord/v4-allocation.json")
successor=$coord/v4-gate-logs/G1c-aggregate-successor.json
test -f "$successor" && inputs+=(--stage-successor "$successor")
if grep -q '"inventory"' "$out/released-curves.json" 2>/dev/null; then
  inputs+=(--curves "$out/released-curves.json" --release-record "$out/release-record.json")
  shp=$coord/shp-aggregate-successor-1.json
  crosswalk=experiments/exploratory/shp-anchor-crosswalk-v1/crosswalk.json
  test -f "$shp" && inputs+=(--shp "$shp" --crosswalk "$crosswalk")
fi
printf '%s\n' "${inputs[@]}"
nice -n 10 uv run --frozen python -m ic_study.analysis.detection_v4_report "${inputs[@]}" --out "$out/report"
```

O relatório valida todas as entradas antes de escrever. Ele recusa `--criteria` se o SHA-256 não for o `criteria_sha256` da segunda vinculação, e recusa o sucessor de G1c se ele não bater com a autorização do estágio e com os registros selados, com o predicado congelado aplicado aos campos do resumo e com o digest independente aprovado na decisão 46 do Owner (`a945e8484791f886289d51b083886854b4f540f6b26dcf1463d8d4c9dcd9a4d6`). Havendo curvas, exige o recibo, verifica o hash dos bytes, condição e horário real; antes do fechamento, exige as 414 curvas concluídas. O manifesto vincula o recibo e a liberação efetiva. `$out/report/manifest.json` registra os hashes de entradas e saídas, o commit e `"synthetic": false`.

## 5. Exportar para uma cópia temporária do manuscrito

Exporte primeiro `generated/` e os catálogos completos sobre uma cópia nova das seções integradas. Depois execute a derivação e o montador de `pipeline/ASSEMBLY.md`. Quando o catálogo exploratório já inclui o confirmatório, passe apenas o catálogo mesclado a `--confirmatory-values`; não o forneça novamente como `--exploratory-values`. Não acrescente `sections/event-exploratory.tex`: o montador inclui `sections/supplement-exploratory-x3-x7.tex`.

```sh
exported=$out/manuscript-exported
test ! -e "$exported" || exit 1
cp -R publications/jcss-manuscript "$exported"
cp "$springer"/sn-jnl.cls "$springer"/sn-mathphys-num.bst "$exported"/
nice -n 10 uv run --frozen python -m ic_study.analysis.v4_report_export "${inputs[@]}" \
  --report "$out/report" --manuscript "$exported" \
  --values "$out/result-values-preliminary.json" --catalog "$out/result-catalog.json" --fill
```

A exportação recusa um relatório renderizado de outras entradas, uma tabela alterada depois da renderização e uma figura com hash diferente do manifesto. Ela preenche os marcadores do texto, grava em `result-values.json` exatamente os IDs usados pelo manuscrito e em `result-catalog.json` todos os IDs, para consulta. Código de saída 1 significa ID citado sem valor, e os IDs aparecem no stderr.

Havendo exploração, siga a exportação do [POST-RELEASE](../../detection-boundary-v4-exploratory/POST-RELEASE.md) sobre `$exported`, preservando o catálogo confirmatório e escrevendo um catálogo mesclado novo. Projete as mesmas entradas autorizadas e prepare `expected-hashes.json` pelo subcomando `prepare` de `verify_short_path.py`, conforme o [README de reprodução](../../../../publications/reproducibility/README.md#caminho-curto-público-agregados-para-tabelas-e-figuras). Confira o replay antes da curadoria pública; a referência vem do relatório autorizado, nunca do replay.

Comece o arquivo público do Owner com `facts: {}` e a marca `synthetic` correspondente à execução. Derive sobre as mesmas entradas autorizadas, com o catálogo completo selecionado, e leia a auditoria. Neste ramo com PASS e comparações, `post.x5_supplied` exige uma declaração pública do Owner mesmo quando X5 não foi fornecido, vinculando a proveniência das comparações e as etiquetas `by_r.x5_state`. Não inferir fatos pelo relógio ou pela ausência de arquivos; não copiar fixtures que incluem fatos calculáveis. Uma recusa preserva os fatos derivados, mas impede a montagem. Após completar as fontes exigidas, derive novamente para um arquivo novo, sem sobrescrever a primeira tentativa.

```sh
assembly_catalog=$out/result-catalog.json # usar o catálogo mesclado se houver exploração
owner_facts=/caminho/publico/owner-facts.json
assembly_facts=$out/assembly-facts.json
nice -n 15 .venv/bin/python -m ic_study.analysis.v4_manuscript_assembly_derive \
  "${inputs[@]}" --owner-facts "$owner_facts" --out "$assembly_facts" \
  --confirmatory-values "$assembly_catalog" --manuscript "$exported" \
  >"$out/assembly-audit.json" || exit 1
ms=$out/manuscript-assembled
nice -n 15 .venv/bin/python -m ic_study.analysis.v4_manuscript_assembly \
  --confirmatory-values "$assembly_catalog" --assembly-facts "$assembly_facts" \
  --manuscript "$exported" --output "$ms" || exit 1
```

Exija `missing_facts=[]` e `refusal=null` na auditoria antes da montagem. O montador grava `assembly-record.json`, mas não regenera o JSON restrito aos IDs citados. Antes da compilação e de `paper_check`, repita o exportador sobre `$ms`, com destinos novos para `--values` e `--catalog`. Com exploração:

```sh
nice -n 15 .venv/bin/python -m ic_study.analysis.v4_exploratory_export \
  --x3 "$aggregates_dir/x3.json" --x4 "$aggregates_dir/x4.json" \
  --x6 "$aggregates_dir/x6.json" --x7 "$aggregates_dir/x7.json" \
  --comparisons "$comparison_json" --confirmatory-values "$out/result-catalog.json" \
  --manuscript "$ms" --values "$out/result-values-final.json" \
  --catalog "$out/result-catalog-final.json" --fill
```

Sem exploração, repita `v4_report_export` com `"${inputs[@]}"`, `--report "$out/report"`, `--manuscript "$ms"` e os mesmos destinos finais novos. O checker recebe `result-values-final.json`, nunca o catálogo completo. A automação atual entrega uma exportação preliminar: para o handoff, prepare outra cópia integrada e copie apenas `generated/` e as dependências Springer da tentativa, preservando os catálogos; não passe sua árvore com `event-exploratory` diretamente ao montador.

Cada arquivo gerado tem nome fixo. No texto principal entram `gate-outcomes.tex` (T3 e F4), `unit-status.tex` (T4 e F5), `primary-boundary-figure.tex` (F1), `auc-profiles.tex` (F2 de B), `boundary-table.tex` (fronteiras de T1) e `shp-anchor.tex` (F6). O `main.tex` já inclui os do suplemento: `supplement-auc-profiles.tex` (F2 de A, C, D e E), `supplement-family-offsets.tex` (F3, exploratória), `supplement-secondary-targets.tex` (alvos secundários), `supplement-low-strength-cells.tex` (células das duas primeiras forças positivas, ramo B04) e `supplement-gap-domain.tex` (domínio elegível e lacunas de B). Quando um resultado não existe, o arquivo sai só com um comentário que diz por quê: sem liberação, sem agregado SHP ou sem fronteira nas duas primeiras forças positivas. A T1s sai como `T1s_a_star_all_units.csv` em `generated/`, que é o material suplementar eletrônico citado como Online Resource 1.

A data efetiva e a condição da liberação saem como `v4.release.effective_local`, `v4.release.effective_utc` e `v4.release.condition`; o fechamento nominal continua em `v4.protocol.close_local`. Os shells distinguem esses dois horários. As constantes de protocolo que o texto cita (0,70, 2,7729, 935, 414, a data do fechamento e as demais) também são valores exportados, com IDs `v4.protocol.*`. O módulo `v4_report_protocol.py` lê cada uma das fontes congeladas: do código congelado, só depois de conferir o SHA-256 do módulo contra `freeze-v4.json`, do `criteria-v43.json` congelado e dos pré-registros v1 e SHP congelados. O corte de região e os alvos secundários vêm do texto v1 verificado pelo hash; os critérios da T3 reutilizam o mesmo leitor do catálogo. A seção 6 das notas dos shells lista a fonte de cada ID.

## 6. Compilar

```sh
tectonic=/caminho/do/executavel/tectonic
export TECTONIC_CACHE_DIR=/caminho/do/cache-preparado
cd "$ms" && nice -n 15 "$tectonic" --only-cached --keep-logs main.tex >"$out/tectonic.log" 2>&1
```

## 7. Verificações

```sh
cd "$ms"
python3 pipeline/paper_check.py --venue jcss --pdf main.pdf --submission --result-values "$out/result-values-final.json"
python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["synthetic"], json.load(open(sys.argv[2]))["code"])' "$out/result-values-final.json" "$out/report/manifest.json"
grep -n 'generated/.*Overfull\|Float too large' "$out/tectonic.log"
pdftotext main.pdf - | grep -n '\(Table\|Tables\|Fig\.\|Figs\.\|Section\|Appendix\) ??'
```

O `paper_check` precisa terminar em `PASS`, o que exige que os placeholders editoriais da seção 10 já tenham sido escritos. O segundo comando precisa mostrar `False` e, no dicionário `code`, `'reporting_code_dirty': False`. Os dois `grep` não devem encontrar nada: o primeiro procura tabelas e figuras geradas fora da área útil, o segundo referências sem rótulo, que o tectonic não lista na saída. Para a JASSS, repita o primeiro comando com `--venue jasss`.

## 8. Revisão manual

Antes de qualquer commit, alguém lê o PDF inteiro contra o relatório e o `assembly-record.json`. No pacote real, as figuras não podem ter a marca SYNTHETIC; no ensaio, preserve essa marca. Cada número de T1, T3 e T4 no PDF deve bater com os CSVs de `$out/report`, e cada bloco selecionado precisa corresponder ao estado real: gate, curva principal válida ou não, lacunas, censuras e âncora. Confira as decisões, exclusões e fontes de fatos da montagem na ordem das regras. As legendas geradas descrevem o que é fixo; a marca de curva principal inválida entra sozinha na legenda de T1 quando se aplica. Os eixos das figuras ainda dizem "Influence strength a" e "Reliability r", enquanto o texto usa "partner drift" e "signal share" (nota N3 dos shells). O resumo precisa ficar em até 250 palavras depois da montagem, lembrando que o `paper_check` conta os tokens do ID de cada `\resultnum` do resumo (nota N2).

## 9. Levar ao repositório

Depois da revisão, o coordenador integra as seções montadas e os ativos conferidos no checkout de trabalho e repete a exportação dos valores finais e o `paper_check` sobre o PDF desse estado. Entram no commit os `generated/*.tex`, os PDFs e o CSV copiados para `generated/` e as seções com os valores preenchidos. `released-curves.json`, o relatório completo e o JSON de valores ficam na pasta privada até o Owner decidir o que vai para o pacote de reprodutibilidade. A classe Springer nunca entra no Git.

## 10. Estado do manuscrito e o que ainda depende do Owner

O manuscrito já tem o que a exportação precisa. O preâmbulo define `\resultnum` e `\allunitsresource`, e carrega `graphicx`. Os arquivos gerados têm nomes que dizem o que contêm, cada um com um placeholder até o dia. O suplemento inclui os arquivos gerados dele, com um `\clearpage` antes do apêndice. As quatro entradas da bibliografia que imprimiam "???" ganharam o local da editora. Nos shells, as 121 constantes de protocolo estão vinculadas, a definição de REGION segue a coluna `region` de T1 e as seis referências à T1s citam o Online Resource 1. As notas dos shells (seção 6) registram as decisões do coordenador: os IDs `v4.low.*` e as tabelas `tab:v4-slow` e `tab:v4-sgaps` saem dos registros liberados; o deslocamento médio selado do G2 e a falha do SHP não têm fonte que o relatório leia, e as frases que os citavam foram removidas ou reescritas; a `tab:v4-sdiag` deixou de ser citada, porque o resumo dela nunca foi definido.

A decisão 91, registrada na seção 8 das notas dos shells com a base `44b722dd`, resolve Q6, Q8 a Q16, Q19 e Q22. A permissão global, os denominadores comuns, os três controles e as sensibilidades seguem essas decisões; os alvos derivados permanecem no suplemento em todo ramo com curvas. Após a montagem atual, no ramo ensaiado em T51, restam a localização pública, revisão e manifests do pacote (`main.tex:89`) e as declarações verificadas de financiamento, conflitos, ética e contribuições (`main.tex:94`). A conclusão já é composta pelo montador. O Owner ainda decide a revisão pública, direitos/licenças e destino do depósito. PASS no modo rascunho não substitui `--submission`; os pendentes históricos da seção 11.1 descrevem aquele ensaio, não a montagem atual.

## 11. Ensaio sintético de 28/09/2026

O ensaio usou só dados sintéticos gerados pelas fixtures do módulo do relatório: o cenário de `render_samples.py`, com duas unidades B a mais cuja fronteira cai em 0,001 e 0,003, para exercitar B04, e ainda a raiz de gate com todos os estágios, a segunda vinculação, o sucessor de G1c, o SHP com o sucessor 1 e o crosswalk. A renderização rodou com `--synthetic`. A exportação, a compilação com a classe Springer oficial e o `paper_check --submission` rodaram sobre cópias temporárias do manuscrito.

No caminho do gate aprovado, o texto de resultados foi montado com todos os ramos B1a, B02 a B17 e B00, para exercitar todos os IDs de uma vez. A exportação vinculou os 1.422 IDs citados, entre números de tabelas, contagens e constantes de protocolo. A compilação não deixou tabela nem figura gerada fora da página nem referência sem rótulo, e o `paper_check` só acusou os três placeholders editoriais. No caminho do gate reprovado em G0, sem liberação, o relatório trouxe só T3 e F4, o texto foi o ramo B1b-G0 seguido de B1-END, os 30 IDs foram vinculados, os demais arquivos gerados saíram só com comentário e o `paper_check` acusou os mesmos três placeholders.

O primeiro ensaio encontrou dois problemas no código do relatório, fora do congelamento, e os dois foram corrigidos: o relatório exigia `--curves`, então os ramos de falha do gate não tinham como renderizar T3 e F4, e a legenda de F5 ficava cortada. As amostras em `samples/` foram regeneradas depois da correção de F5.

Para repetir o ensaio, gere as entradas sintéticas em uma pasta temporária, fora do checkout:

```sh
cd "$report_checkout/studies/ic-2026-2027"
nice -n 10 uv run --frozen python - /caminho/temporario <<'PY'
import importlib.util, json, sys
from pathlib import Path
from ic_study.analysis.v4_report_synthetic import (
    UnitPlan, build_gate, build_release, crosswalk_fixture, logistic_profile,
    shp_successor_fixture, stage_successor, unit_keys, write_release)
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location(
    "samples", "experiments/exploratory/detection-boundary-v4/report/render_samples.py")
samples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(samples)
plans = samples.sample_plans()
b = unit_keys(tier=1, family="B")
plans[b[0.8]] = UnitPlan(logistic_profile(0.002))
plans[b[0.85]] = UnitPlan(logistic_profile(0.001))
# write_release também grava o release-record.json sintético, vinculado aos bytes.
write_release(out / "released-curves.json",
              build_release(out / "confirmatory", plans, draws=200))
gate = build_gate(out / "gate", allocation=out / "v4-allocation.json")
(out / "G1c-aggregate-successor.json").write_text(json.dumps(stage_successor(gate)))
(out / "shp-aggregate-successor-1.json").write_text(json.dumps(shp_successor_fixture()))
(out / "crosswalk.json").write_text(json.dumps(crosswalk_fixture()))
PY
```

Para o caminho de falha, um gate que reprova em G0 sai de `build_gate(pasta, GatePlan(stages=("G0",), g0_failures={**G0_FAILURES, ("B", 0.3, 0.7): ("budget", 1)}))`. Depois, as seções 4 a 7 rodam com esses caminhos no lugar dos reais e com `--synthetic` na renderização; o exportador herda essa marca do manifesto. Passe também `--release-record` para o recibo sintético gerado por `write_release`. O ramo G0 reprovado não tem curvas nem recibo de liberação. As legendas e os arquivos gerados saem marcados como SYNTHETIC, e o JSON de valores traz `"synthetic": true`.

Use também `--synthetic` em `v4_public_aggregates project`, `verify_short_path.py prepare`, na derivação e no empacotador JCSS. O pacote científico usa um plano `mode: "synthetic"` e aceita apenas os nomes de relatório `_synthetic` enumerados; vincula o recibo ao `v4_report_synthetic.py` selecionado em `reporting-export`. Os modos reais continuam exigindo o wrapper executado e recusando esses nomes. O JCSS marca o manifesto e reconhece `T1s_a_star_all_units_synthetic.csv` apenas com a opção explícita, para staging local fora de Git. Não remova sufixos nem troque `script_sha256` para simular o wrapper real. O T51 precisou de adaptadores locais; os comandos corrigidos dispensam esses adaptadores.


### 11.1. Reensaio da decisão 91, base `44b722dd`

O reensaio usa a branch `research/shell-decisions-91`, sem commit, e apenas fixtures sintéticas de `v4_report_synthetic`: `UnitPlan`, `build_release`, `write_release`, `build_gate`, o sucessor de G1c, o agregado SHP e o crosswalk sintéticos. Nenhum dado selado foi aberto. As curvas, os recibos e os registros do gate ficam fora do Git. Nos três caminhos com curvas, o recibo sintético de fechamento declarado vincula os bytes por SHA-256 e é verificado pelo leitor. G0 reprovado não tem liberação nem recibo.

A composição aplica o mesmo `v4.mechanisms.allowed` a todas as frases entre famílias, nos Results e no resumo. O primeiro caso tem todas as 36 unidades do tier 2 completas válidas e as nove unidades B válidas, com lacunas em B a r = 0,55 e 0,65 e em D a r = 0,75. B e D continuam lado a lado nos nove r; as leituras e contagens pareadas usam os seis r comuns sem lacuna: 0,50; 0,60; 0,70; 0,80; 0,85; 0,90. O segundo caso retira D em r = 0,90; o terceiro mantém tier 2 completo válido e invalida B em r = 0,90. Nos dois, a permissão é zero, nenhum texto local ou de manchete compara famílias, e as tabelas e figuras mantêm as unidades válidas. O quarto caso reprova G0 por um status `budget`, sem executar os estágios seguintes.

| Caminho sintético | Permissão | IDs ligados / citados | Placeholders editoriais | Palavras no resumo | `paper_check` | `paper_check --submission` |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Gate aprovado; tier 2 completo válido; curva principal válida | 1 | 1.505 / 1.505 | 2 | 231 | PASS, exit 0 | FAIL, exit 1: somente os 2 placeholders |
| Gate aprovado; tier 2 incompleto | 0 | 1.475 / 1.475 | 2 | 177 | PASS, exit 0 | FAIL, exit 1: somente os 2 placeholders |
| Gate aprovado; tier 2 completo válido; curva principal inválida | 0 | 1.473 / 1.473 | 2 | 183 | PASS, exit 0 | FAIL, exit 1: somente os 2 placeholders |
| Gate reprovado em G0 | 0 | 28 / 28 | 2 | 151 | PASS, exit 0 | FAIL, exit 1: somente os 2 placeholders |

As quatro compilações com Tectonic e a classe Springer terminaram com exit 0. O JSON de valores contém exatamente os IDs citados pela árvore de `main.tex`; não sobrou marcador numérico após `--fill`. Os dois placeholders editoriais são a declaração de financiamento, conflitos, ética e contribuições em `main.tex`, e a conclusão. O marcador `X6-PRIMARY-D1-ID-PENDING` permanece nos shells, fora da árvore compilada: ele aguarda o ID exato do exportador exploratório, conforme a decisão 91, e não é preenchido por um valor sintético inventado.

O ensaio encontrou e corrigiu o resumo G0 inicialmente abaixo do mínimo, a ausência da marca de invalidação na tabela dos alvos derivados e a localização da frase dos secundários no texto principal. Os secundários agora entram pelo bloco `SECONDARY-SUPPLEMENT`, destinado a `sections/supplement.tex`, em todo ramo com curvas; as nove linhas B e a legenda retêm a marca de invalidação quando ela se aplica. As regressões foram escritas antes de cada correção e mostraram o vermelho. A asserção da marca foi ajustada para verificar as nove linhas e a legenda separadamente, porque as duas usam formas LaTeX diferentes.

Os portões finais, a partir do estudo e com um processo, sem xdist, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1`, passaram: ruff check e format --check nos quatro arquivos Python tocados; `uv run --locked mypy src tests` (104 fontes); e pytest de `test_v4_report_export.py`, `test_detection_v4_report.py` e `test_v4_exploratory_comparisons.py` (188 testes). Os 80 fontes Python congelados conferem com o freeze, e os seis módulos X3–X7 mantêm os hashes da base. `pyproject.toml` e `uv.lock` também permanecem iguais à base.

Os insumos, as primeiras cópias e as cópias finais foram preservados em `/private/tmp/shell-decisions-91-evidence/rehearsal/`. A reprodução local usa `/private/tmp/shell-decisions-91-evidence/rehearse.py`, que monta as quatro variantes, verifica os recibos, aplica as condições dos shells, acrescenta os secundários ao suplemento, exporta os IDs, compila e executa o checker nos dois modos. Para repetir enquanto esse diretório existir:

```sh
cd "$report_checkout/studies/ic-2026-2027"
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
MPLCONFIGDIR=/private/tmp/shell-decisions-91-evidence/mpl-cache \
UV_CACHE_DIR=/private/tmp/uv-cache-shell91 \
uv run --locked python /private/tmp/shell-decisions-91-evidence/rehearse.py
```

`summary.json` conserva os resultados da primeira execução, incluindo o vermelho do resumo G0; `summary-final.json` registra a rodada final. Os logs `01-*-red.log` a `12-*-red.log`, os logs dos portões e `protected-before.json` / `protected-after.json` ficam em `/private/tmp/shell-decisions-91-evidence/`. Nenhum arquivo deste ensaio é um resultado científico ou uma autorização para abrir os selos.

## 12. Dia da liberação: do status awaiting-authorized-handoff ao PDF

A cadeia instalada (`$coord/v4-post-release-chain.sh`, que delega a `$coord/v4_event_automation.py`) faz as seções 4 e 5 até a exportação exploratória. Sem `V4_HANDOFF_SPEC`, ela termina com exit 3, grava `awaiting-authorized-handoff` em `$coord/v4-release/chain-status.json` com a lista dos insumos selecionados e deixa ao lado os checkpoints confirmatório e exploratório. A cadeia só chega a esse status depois de receber os recibos verificados das três exportações X3–X7; enquanto faltar um, ela fica em `waiting-exports`. O handoff recusa ler `v4-release`, `v4-gate-logs`, `v4-tier-logs`, as raízes `sealed-v4-*` e `restricted`; por isso precisa de cópias autorizadas fora delas. Os três comandos de [release_handoff.py](release_handoff.py) fazem essa passagem. `copy` e `owner-facts` terminam com exit 2 e uma linha `refused: ...` quando a evidência falta ou diverge; `run` faz o mesmo nas conferências que antecedem a automação. Nenhum deles preenche um valor por suposição.

```sh
coord=$HOME/.local/state/research-workbench/coord-20260925
handoff_checkout=CAMINHO_DO_CHECKOUT_INTEGRADO_LIMPO
study=$handoff_checkout/studies/ic-2026-2027
tool=$study/experiments/exploratory/detection-boundary-v4/report/release_handoff.py
day=$HOME/.local/state/research-workbench/release-handoff-AAAAMMDD
cd "$study"
python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["status"])' "$coord/v4-release/chain-status.json"
git -C "$handoff_checkout" status --porcelain
```

`handoff_checkout` é um checkout integrado, limpo e com `.venv` sincronizado que contém `release_handoff.py`; dele vêm as seções fixas e os shells da montagem. Ele não é o checkout que a cadeia recebeu nem o `report_checkout` da espera: a cadeia confere revisão e limpeza do seu checkout depois da espera das exportações, e por isso esse checkout não deve ser atualizado. A primeira conferência deve imprimir `awaiting-authorized-handoff`, e a segunda, nada. `day` é uma pasta nova, fora das raízes protegidas.

Primeiro, as cópias autorizadas:

```sh
nice -n 15 .venv/bin/python "$tool" copy \
  --status "$coord/v4-release/chain-status.json" \
  --out "$day/authorized"
```

O comando copia, para a pasta nova, cada insumo que a cadeia selecionou: curvas, recibo, raiz do gate com o mesmo nome da raiz selada, critérios, a segunda vinculação, o sucessor de G1c, o agregado SHP com o crosswalk quando o checkpoint os registra, o relatório, `generated/` com as duas dependências Springer, os dois catálogos, X3, X4, X6, X7 e as comparações. Cada arquivo é conferido por SHA-256 contra a origem. Conforme o papel, também é conferido contra os checkpoints da cadeia, que fixam ainda os diretórios das árvores, contra o recibo de liberação (curvas) ou contra o manifesto do relatório (critérios e crosswalk). O manifesto também fixa nomes, identificador do gate, marca sintética e DPI. O resultado é `handoff.json` no contrato da entrega T56, com `synthetic: false`, e `copy-receipt.json`, que registra origem, cópia e SHA-256 de cada arquivo, o SHA-256 do `handoff.json` e o dos dois checkpoints. Qualquer divergência apaga a pasta parcial. `--synthetic` existe só para ensaio e precisa coincidir com o relatório.

Depois, os fatos do Owner:

```sh
nice -n 15 .venv/bin/python "$tool" owner-facts \
  --handoff "$day/authorized/handoff.json" \
  --out "$day/owner-facts.json"
```

Antes de ler qualquer evidência, o comando reconfere o recibo: as cópias, o `handoff.json` e os checkpoints da cadeia precisam ter os mesmos SHA-256 da cópia, sem arquivo ou diretório a mais ou a menos, e todo caminho do `handoff.json` precisa apontar para dentro de `authorized/`. Não abra essa pasta no Finder: o `.DS_Store` que ele cria fica fora do recibo e faz `owner-facts` e `run` recusarem; se aparecer, apague-o. O arquivo novo traz apenas `gate.at_close` e `post.x5_supplied`, cada um com o caminho da cópia relativo a `authorized/`, seu SHA-256 e o localizador. `gate.at_close` sai de `release-record.json`: `declared-close`, no fechamento ou depois, dá `true`; `inventory-complete`, antes do fechamento, dá `false`. `post.x5_supplied` sai de `provenance.inputs.x5` em `comparisons.json` e do `x5_state` das nove confiabilidades. Recibo de liberação inconsistente, comparações ligadas a outras curvas e vínculo de X5 ausente ou contradito pelas etiquetas são recusados. Fatos calculáveis nunca entram. Se `pending_owner` listar `shp.state` e `shp.reason`, falta o agregado SHP; o Owner acrescenta essas declarações, e `shp.divergence` quando o estado for `pre-run-divergence`, num arquivo novo antes do passo seguinte. O Owner lê e aprova o arquivo, porque ele continua sendo uma declaração pública sob sua responsabilidade.

Por fim, a montagem e o PDF:

```sh
nice -n 15 .venv/bin/python "$tool" run \
  --checkout "$handoff_checkout" \
  --handoff "$day/authorized/handoff.json" \
  --owner-facts "$day/owner-facts.json" \
  --out "$day/handoff-attempts"
```

`run` recusa antes de começar se `~/.local/state/research-workbench/tectonic-cache` não existir ou estiver vazio, se faltar o Tectonic `/nix/store/pxrhhj0zcl8ywp8ym4jw6fj7rrckfvcc-tectonic-wrapped-0.17.0/bin/tectonic`, se o recibo não conferir ou se as marcas sintéticas do `handoff.json`, do recibo e dos fatos do Owner divergirem entre si ou de `--synthetic`, que só se usa em ensaio. O cache e o Tectonic podem ser trocados por `--tectonic-cache` e `--tectonic`. O cache em `~/Library/Caches/TectonicProject.Tectonic` não serve, porque as limpezas do Owner o apagam. O comando chama `$coord/v4_event_automation.py handoff` com caminhos absolutos, `V4_SHORT_PATH=1`, `V4_TECTONIC`, `TECTONIC_CACHE_DIR`, `V4_OWNER_FACTS`, as quatro variáveis de threads em 1 e prioridade 15, sem `V4_ALLOW_UNNICE`, e no fim imprime o resumo do status novo. Se a automação não gravar um status novo, por exemplo porque outra instância detém o lock, o resumo diz isso em vez de repetir o anterior.

O resultado esperado é exit 1 com `awaiting-human-review` e `assembly_ready: true`: `tectonic`, `paper_check_draft`, `prepare_short_path` e `verify_short_path` em 0 e `paper_check_submission` em 1 apenas pelo placeholder de `main.tex:96`, a localização pública, a revisão arquivada e os manifests do pacote final, que o Owner preenche depois de decidir o depósito. Exit 2 com `awaiting-owner-facts` indica uma declaração que falta: leia `missing_facts` e o `derive-audit.json` da tentativa, escreva outro arquivo do Owner e repita o comando, que cria uma tentativa nova e preserva a anterior. `technical-checks-failed` grava checkpoint, e repetir com as mesmas entradas apenas o reconfere. `failed` não grava checkpoint: leia `error` e os logs em `outputs.attempt/logs`, corrija a causa e repita, o que cria uma tentativa nova. O arquivo `chain-ALERT` da pasta de tentativas permanece depois de uma falha; o status vigente é o de `chain-status.json`.

```sh
python3 -c 'import json, sys; s = json.load(open(sys.argv[1])); print(s["status"], s.get("pdf")); print(json.dumps(s.get("checks"), indent=1))' "$day/handoff-attempts/chain-status.json"
pdf=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1])).get("pdf") or "")' "$day/handoff-attempts/chain-status.json")
test -n "$pdf" && open "$pdf"
```

A partir desse PDF valem a revisão manual da seção 8 e a integração da seção 9. Continuam manuais a aprovação dos fatos pelo Owner, a leitura integral do PDF, o preenchimento de `main.tex:96`, a revisão pública da projeção, do manifesto e do replay candidatos, direitos e licenças, o depósito e a submissão.

Em 02/10/2026 a sequência foi ensaiada sobre a integração `5d66440a` e repetida no ramo `research/release-handoff-tooling-20261002`, que só acrescenta estas ferramentas, com uma cópia da automação instalada, sobre um estado sintético na disposição da cadeia: gate aprovado, tiers 1 e 2 completos, o agregado SHP sucessor 1 real e X5 fornecido. Com os oito shards confirmatórios em execução, na rodada do ramo a cópia levou cerca de 25 s (54.758 arquivos, 195 MB), os fatos do Owner cerca de 10 s, o handoff com `facts: {}` cerca de 40 s até `awaiting-owner-facts`, faltando só `post.x5_supplied`, e o handoff completo cerca de 70 s até `awaiting-human-review`; os fatos e o handoff incluem a reconferência do recibo, com PDF de 91 páginas, resumo de 230 palavras, 5.331 IDs vinculados e replay com 54 arquivos conferidos. A primeira compilação do ensaio falhou porque faltavam ao cache durável seis arquivos Computer Modern (`cmr6.tfm`, `cmmi6.tfm`, `cmmi6.pfb`, `cmsy6.tfm`, `cmsy6.pfb` e `cmsy9.pfb`), exigidos pelas legendas que usam `\dag`; eles foram acrescentados ao cache em 02/10. Uma compilação `--only-cached` aprovada no manuscrito com placeholders não prova o cache da montagem.

Para repetir o ensaio, por exemplo depois de refazer o cache ou de atualizar a integração, use um checkout limpo e pastas novas fora dele. A compilação de conferência da própria cadeia usa `nix shell nixpkgs#tectonic` e a rede, como a cadeia instalada, sobre uma cópia do cache; o handoff compila só a partir do cache durável.

```sh
rehearsal=/caminho/novo/ensaio-AAAAMMDD
mkdir -p "$rehearsal-tools" && cp "$coord/v4_event_automation.py" "$rehearsal-tools/"
nice -n 15 .venv/bin/python experiments/exploratory/detection-boundary-v4/report/rehearse_release_handoff.py \
  --root "$rehearsal" --automation "$rehearsal-tools/v4_event_automation.py" \
  --shp "$coord/shp-aggregate-successor-1.json"
```

O ensaio passa quando imprime `"passed": true`; `rehearsal-results.json` guarda os dois status e os tempos de cada passo. Sem `--shp`, ele usa o agregado SHP sintético. Com `--shp`, o agregado real entra na F6, nos IDs da âncora e na projeção candidata do ensaio; a pasta recebe o aviso `PRIVATE-REAL-SHP-AGGREGATE`, fica privada e nada dela vai para depósito.
