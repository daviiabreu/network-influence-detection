# T57 — decisões de texto delegadas pelo Owner

Data: 01/10/2026. Origem: decisão 161, em que o Owner delegou ao coordenador as escolhas pendentes de `t41d-human-decisions.md`. Base: integração `45a1dfaf`. Tudo foi aplicado antes da liberação de qualquer resultado dos tiers; nenhum dado selado, log de tier, diretório restricted ou microdado SHP foi aberto, e nenhum arquivo congelado mudou.

## O que mudou

**Texto fixo de Discussion e Conclusion.** Entraram as dez propostas T54 que estavam fora do escopo da T41d (DS01–DS07, DS09, DS10 e CN01). Quatro trechos foram ajustados para não mudar o sentido. Em DS01, a não travessia continua sendo por valor de r ("A complete valid noncrossing at a value of $r$ …"), a largura do intervalo continua "reported", e a última afirmação volta a ser "Statements about how the boundary changes across $r$ are descriptive". Em DS02 volta o motivo de parear B e D ("The pairing matters because …"), e a condição vem antes da leitura congelada. Em DS05, a mistura de primeiras entrevistas em 2004 passa a ser atribuída à amostra de reposição, e não ao fato de 2004 ser a quinta onda sintética. Em CN01 fica a primeira frase original, com a paragrafação nova; o montador continua achando exatamente os três marcadores.

**B06 (Results).** A regra ganhou seleção por frase, como B05 e B11. A frase "The two boundaries differ at …" só entra com `v4.t1.n_first_ne_sustained > 0`. A frase "At [n] of them the sustained boundary is censored at a gap" tinha um erro de contagem: `v4.t1.n_sustained_gap` conta todas as curvas válidas do tier 1 com fronteira sustentada censurada, inclusive as que não diferem. Uma curva válida cuja banda superior nunca chega a 0,70 e que tem uma única lacuna entra nessa contagem com as duas fronteiras iguais. A frase nova explica a regra sem contagem e só entra com `n_sustained_gap > 0`. A contagem continua no B08.main.4: uma fronteira censurada por lacuna exige `gap_count > 0`, então `v4.t1.gap_cells > 0` e o B08 é selecionado sempre que a frase nova entra. Quando o B06 é selecionado só porque o tier 2 difere, sobram a frase da Tabela T1 e a frase RS57.

**B07 (Results).** "no statement is made that separation holds for some value of $r$ as a whole-curve claim" virou "no global claim is made that separation holds at some value of $r$", que é a regra RS28 do ledger.

**D-X3-LOCAL-R050 … R090 (Discussion).** Saiu "The recorded validity flag for the main curve is true/false". `main_curve_valid` é `release.main_curve_valid`: a validade da curva principal inteira, igual para todo r (`v4_exploratory_comparisons.main_curves`). Cada bloco tem agora duas frases alternativas, "The main B curve was recorded as valid." e "… as invalid.", selecionadas por `eq` sobre o valor formatado ("true"/"false"). Se o ID faltar, o bloco é recusado; se o valor for "unavailable", nenhuma das duas entra e o bloco continua legível. Como antes, a frase se repete em cada bloco selecionado (até nove).

**D-X1B (Discussion).** A frase longa virou duas, sem perder conteúdo nem binding; "signal shares" passou a "response signal shares".

**Nome da nula B.** A legenda do F1 (`v4_report_export.CAPTION_F1`), o rótulo das figuras (`v4_report_figures.FAMILY_LABEL["B"]`, usado em F1 e F2) e as notas da T1/T1s (`v4_report_tables._T1_NOTES`) trocaram "trait-state persistence" por "trait-plus-autoregressive persistence", o nome do resumo, de Results e de Related Work. O comentário INCLUDES do F1 no shell acompanhou. As notas da T1 não estavam na lista de arquivos da tarefa, mas sem elas o nome antigo continuaria na T1s (Online Resource 1).

## Registros

- `t57-shell-repin-receipt.json`: repinagem de `results` e `discussion` contra `48d4ac59`, com aceite explícito de B06, B07, D-X1B e dos nove D-X3-LOCAL (12 mudanças visíveis), B00 como comment-only e 254 regras inalteradas.
- `t57-selection-changes.json`: os `fragments` acrescentados a B06 e aos nove D-X3-LOCAL; condição do bloco, slot, operação e ordem inalterados.
- `t57-caption-digest-proof.json`: prova de bytes da renovação do digest de arquivos gerados em `test_v4_gate_only_shp` (caso com release). Reaplicar o nome antigo reproduz os três digests anteriores; valores e células não mudam; só `primary-boundary-figure` difere, e só pelo nome da nula B.

## Verificação

Testes com `nice -n 15` e BLAS em uma thread: 635 aprovados, nenhuma falha. Montador 183, que inclui 6 testes novos: frases do B06 por contagem, inclusive o caso só de tier 2; quantificador do B07; as três formas da frase de validade do X3 e a recusa sem o ID. Derivação 84, exportador 80, relatório 95 (inclui `test_frozen_files_are_untouched`), exploratório 58, projeção pública 93, gate-only 13, propagation 24 e sucessor v4.4 5. Ruff (check e format) e mypy passam nos módulos e testes tocados.

Montagem sintética com `tectonic --only-cached` (Tectonic 0.17.0, classe Springer da compilação anterior, SHA-256 `36d0c327…`). Caso PASS derivado de `passed-shp`, com duas fronteiras diferentes, uma sustentada censurada e fronteira não monótona em r: exit 0, sem erro LaTeX, sem overfull e com B06, B07, B08.main.4, D-X1B e D-X3-LOCAL-R060 selecionados. Caso não PASS `failed-G0`: exit 0, sem erro e sem overfull. A Conclusion montada mantém a paragrafação nos dois ramos.

## Fora do escopo

As amostras sintéticas versionadas em `experiments/exploratory/detection-boundary-v4/report/samples/` ainda mostram o nome antigo no F1, F2 e T1. Elas são prévias de revisão marcadas como SYNTHETIC; regenerá-las com `render_samples.py` muda PNGs dependentes de plataforma. Os JSONs de auditoria de 30/09 continuam como registro histórico, porque dependem de ensaios em `/private/tmp` que foram apagados.
