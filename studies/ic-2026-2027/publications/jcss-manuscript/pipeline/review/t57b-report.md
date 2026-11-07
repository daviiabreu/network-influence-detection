# T57b — nota comum das células X3, DS09, prévias e crédito do SHP

Data: 01/10/2026. Origem: pedidos do coordenador depois de revisar a T57, sob a delegação do Owner (decisão 161). Base: `9425167a`. Tudo foi aplicado antes da liberação de qualquer resultado dos tiers. Nenhum dado selado, log de tier, diretório restricted ou dado SHP foi aberto: o crédito do SHP foi feito só no código. Nenhum arquivo congelado mudou.

## O que mudou

**Células X3 (Discussion, DS10).** Com várias células selecionadas, a T57 repetia a frase de validade e a ressalva em cada uma. Agora:

- Os nove blocos D-X3-LOCAL-R* ficam só com a frase de magnitude, intervalo e classificação, terminada em "; the reported classification was \texttt{…}.". A margem saiu dessa frase.
- Um bloco novo, D-X3-LOCAL-NOTE, é selecionado exatamente quando a condição de pelo menos um bloco local vale (`any` sobre as nove referências). Com ordem 990 no DS10, ele entra uma vez, depois da última célula selecionada. Ficou depois, e não antes, porque "Each classification" e "These cell contrasts" retomam o que acabou de ser lido.
- A nota diz a margem declarada, a validade da curva principal B por extenso e a ressalva no plural ("These cell contrasts are conditional on fitting and training; they neither validate the whole curve nor estimate its frozen boundary.").
- Os marcadores ficam nas linhas que sustentam cada afirmação: DS03 DS10 RS21 na frase por r; DS03 DS10 na margem; RS15 nas frases de validade; DS01 DS03 DS10 RS15 na ressalva.

Os catálogos confirmatório e exploratório não têm ID de validade no nível da liberação. Por isso a nota lê a cópia em r = 0,50 de `release.main_curve_valid` (`v4x.comparisons.by_r.0-5.main_curve.main_curve_valid`). Um teste mostra que a escolha é segura: ele constrói liberações sintéticas com curva principal válida e inválida, passa pelo caminho do produtor (`main_curves`, `compare_exploratory` e o achatamento do exportador exploratório) e confere que as nove cópias trazem o mesmo valor da liberação. O comportamento da T57 se mantém: um ID ausente recusa o bloco, e "unavailable" omite a frase de validade.

**DS09.** "so this draft makes no priority claim" passou a "so this article makes no priority claim". Fica fora do pedido outra ocorrência de "this draft": `sections/supplement.tex`, M83 ("at this draft").

**Prévias do relatório.** As condições para regenerar foram verificadas: `render_samples.py` está no repositório, duas execuções seguidas deram arquivos idênticos byte a byte e nenhum teste fixa os bytes das prévias. As anteriores eram de `346e2c5c`. As novas mostram:

- o nome novo da nula B;
- as colunas de lacuna por propagação da emenda v4.4 na T1 e na T4;
- as demais mudanças de legenda, eixo e tabela desde então.

O manifesto registra `771cff78`, com o código de relatório limpo. As prévias não contêm legendas de LaTeX, então o crédito do SHP não as altera.

**Crédito do SHP.** A licença de uso do SHP exige "Source: Swiss Household Panel (SHP)" em figuras e tabelas que usam dados do SHP. O F6 é a única figura ou tabela gerada que mostra valores da âncora: nenhum outro arquivo gerado vincula um ID `v4.shp.*`, e no ramo só de gate a âncora aparece apenas em prosa. A frase entrou no fim de `CAPTION_F6`, no F6 de `report/captions.md` e no comentário INCLUDES do F6 no shell de Results. Esta última é uma mudança só de comentário (B00), com 34 regras deslocadas uma linha.

## Registros

- `t57b-shell-repin-receipt.json`: repinagem de `discussion` contra `b26c3ac8`, com aceite explícito dos nove blocos locais e 258 regras inalteradas. O diff associou as frases removidas de D-X3-LOCAL-R090 às frases idênticas do bloco novo e propôs as linhas 807–827; o locator explícito fixou R090 nas suas próprias linhas (807–815).
- `t57b-selection-changes.json`: a retirada dos `fragments` T57 dos nove blocos locais e a regra nova D-X3-LOCAL-NOTE, com os SHA-256 do registro antes e depois.
- `t57b-results-repin-receipt.json`: repinagem de `results` contra `70ac7dbf` pela linha do crédito no comentário do F6.
- `t57b-caption-digest-proof.json`: prova de bytes da renovação do digest de arquivos gerados em `test_v4_gate_only_shp` (caso com release e SHP). Sem a frase, a exportação reproduz os três digests da T57; valores e células não mudam; só `shp-anchor` difere, e só pela frase.

## Verificação

Testes com `nice -n 15` e BLAS em uma thread: 642 aprovados, nenhuma falha. Montador 188, com 9 casos novos no lugar dos 4 da T57: nota com três, uma e nenhuma célula; validade true, false e unavailable; flag ausente; e a prova das nove cópias da flag com curva válida e inválida. Derivação 84, exportador 80, relatório 95 (inclui `test_frozen_files_are_untouched`), exploratório 58, projeção pública 93, gate-only 15 (2 casos novos: só o `shp-anchor` leva o crédito), propagation 24 e sucessor v4.4 5. Ruff (check e format) e mypy passam nos arquivos tocados, e `scripts/check_repository.py` passa nas 7 checagens.

Montagem sintética PASS derivada de `passed-shp`, com três células X3 selecionadas (r = 0,60, 0,75 e 0,90) e compilada com `tectonic --only-cached` no commit final: exit 0, sem erro LaTeX e sem overfull. A nota aparece uma vez, depois da terceira célula, e a margem e a ressalva aparecem uma vez cada.

## Observações fora do escopo

- Os blocos D-X3-LOCAL têm ordem 892–980 no DS10, depois dos blocos de X4 e X7, embora o cabeçalho diga "D3 after D-X3-READINGS". No texto montado, as células X3 vêm logo depois da discussão do X7. A ordem não foi mudada: a composição dos slots fica para depois da leitura do texto montado.
- Os valores da âncora SHP também aparecem em prosa: B1-SHP no ramo só de gate e os blocos de Results e Discussion que citam `v4.shp.*`. A cláusula da licença citada fala de figuras e tabelas, então esses trechos não mudaram.
- Os arquivos F6 isolados (PDF e PNG do relatório) não trazem a frase dentro da imagem; ela está na legenda. Se essas figuras forem distribuídas fora do artigo, pode ser preciso uma nota na própria imagem.
