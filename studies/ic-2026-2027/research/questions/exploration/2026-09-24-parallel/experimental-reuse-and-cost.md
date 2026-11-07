# Reuso científico e custo experimental — auditoria offline

24/09/2026. Inventário do checkout `5d6723e`, sem nova simulação, benchmark,
validação de objetos externos ou consulta bibliográfica. Os números abaixo são
registros dos pilotos de 12/09, não tempos medidos hoje. O estado da pergunta
continua `none selected` em `research/questions/research-questions.md`; a
revisão sistemática ainda não entregou corpus aceito, calibração aprovada e
síntese (`research/literature/READINESS.md`, “Current audited state”).
Caminhos sem prefixo são relativos a `studies/ic-2026-2027/`.

## O que já foi executado

“Ainda não houve execuções científicas” seria enganoso. Há duas campanhas
**exploratórias científicas completas**, com protocolo, especificação, código,
sementes, manifestos, objetos JSONL externos por hash, revisão de resultados e
mapa de afirmações. Elas não são validação registrada nem escolhem tema, venue
ou tese (`research/questions/exploratory-claim-map.md`, “Afirmações e fronteiras”
e “O que falta”). O runtime de revisão, calibração e replay é outro eixo; seus
testes e aquisições não substituem esses resultados científicos nem a síntese.

| Campanha | Desenho e resultado delimitado | Fonte reproduzível |
| --- | --- | --- |
| A: parada/fragmentação em DW simétrico, rede fixa | 10 benchmark + 10 controles + 112 principais + 16 sensibilidades = 148 trajetórias; 142 certificadas, seis censuradas. No principal, 108 certificadas e quatro censuradas. Só `pilot:35` teve cruzamento posterior e partição final diferente para o observador com grupos em memória; nenhuma das 108 paradas do observador recalculado teve esse evento. O caso 35 passou de 13 grupos declarados na tentativa 10.500 a 12 certificados na 10.790; no par com tolerância menor, os três observadores terminaram com 12 grupos na 12.270. | `experiments/exploratory/fragmentation-pilot-v1/analysis-input.json`: `/phase_counts`, `/adverse_case`; `run-manifest.json`: `/phases/pilot`, `/phases/sensitivity`; JSONL `pilot`, `trial_index=35`, e `sensitivity`, `trial_index=3`; `results-review.md`, “O caso” e “Tempos”. |
| B: previsão sintética de histogramas | 16 células × 30 trajetórias por lote: 480 principais, 480 de precisão com os **mesmos dados**, 480 de confirmação novos; 960 identidades de dados, mais 32 benchmarks excluídos. Zero das oito células dinâmicas passou o contraste pré-fixado em qualquer lote: ES melhor e média W1 pior que baseline, ambos com IC pontual além de 1%. No controle sem atualização, ES escolheu dinâmica em 42/120, 36/120 e 40/120 trajetórias nos três lotes. | `experiments/exploratory/probabilistic-forecast-pilot-v1/analysis-input.json`: `/primary_criterion_cells_by_phase`, `/criterion_replicated_all_three`, `/controls`; `run-manifest.json`: `/runs`; `results-review.md`, “Afirmações atômicas”. |

A não demonstra frequência geral de falha: redes e entradas são reutilizadas,
quatro censuras principais são inconclusivas, e não se executou a campanha do
artigo externo (`fragmentation-pilot-v1/protocol.md`, “Amostras e custo”;
`README.md`, “O caso”). Um antecedente de 2018 já combina separação e pequena
amplitude interna (`source-check.md`); certificado genérico não é novidade.
A decisão registrada foi guardar a discrepância como nota de reprodutibilidade
e encerrar a expansão dessa rodada (`README.md`, “Decisão e próximos passos”).

B reinicializa N=50 agentes a cada onda, usa amostras de 55/550, 25/150
tentativas, duas ondas de treino e duas de teste; não acompanha população
persistente, não reproduz o ESS e não infere causalidade
(`probabilistic-forecast-pilot-v1/protocol.md`, “Alvo e mecanismo” e
“Evidência e limites”). A célula episódica `pulsed_dw-a150-n550` mostrou na
confirmação ES −21,39% e média W1 +1,56%, mas o IC da diferença W1 cruza zero;
W1 do centro já melhora 11,04%. O contraste pré-fixado falhou. O piloto foi
encerrado sem iniciar ESS (`README.md`, “Contraste central” e “Decisão”).
Diferenças de geometria entre ES euclidiano e W1 ordinal, e antecedentes com
Brier, impedem transformar troca isolada de ranking em novidade
(`source-check.md`; `README.md`, “Geometria e antecedentes”). Novos parâmetros
ou sementes para encontrar sinal favorável exigiriam pergunta justificada e
protocolo sucessor; não são continuação oportunista dos pilotos.

## Código reaproveitável, com fronteiras

`src/ic_study/models/deffuant.py` fornece estado, atualização simétrica,
amostragem de arestas ponderadas e componentes. `simulation/fragmentation.py`
fornece partição efetiva, critérios de diâmetro/separação e `simulate` com
parada em memória, recalculada e certificada. Valem para confiança estrita,
opiniões escalares, atualização convexa e topologia-base fixa; a margem numérica
não é prova com aritmética intervalar (`fragmentation-pilot-v1/protocol.md`,
“Modelo e fontes”). `analysis/fragmentation_pilot.py` gera redes/entradas,
executa as quatro fases e resume; seu desenho, sementes e caps são específicos
do piloto, não defaults de um futuro artigo.

`models/histogram_forecast.py` contém kernel sintético e sementes derivadas por
hash; `metrics/histogram_scores.py` mede média W1, W1 do centro, ES, média L2 e
L2 do centro; `analysis/forecast_pilot.py` organiza células, treino/teste,
previsões em ensemble, intervalos e JSONL. O kernel usa reinicialização
condicional e aritmética inteira para os limiares; a transferência para dados
humanos ou população persistente requer novo modelo e validação, não mero
reuso de nome. `validation/experiments.py` verifica formato, vínculos, hashes,
linhagem e afirmações dos pilotos; é um validador offline, não árbitro de
novidade ou suficiência estatística. Testes científicos estão em
`tests/scientific/test_fragmentation.py` e `test_histogram_forecast.py`; os
fluxos em `tests/integration/test_fragmentation_pilot.py`,
`tests/integration/test_forecast_pilot.py` e
`tests/integration/test_experiment_validation.py`. As revisões originais reproduziram casos e
scores, mas esta auditoria não reabriu os objetos externos.

## Custo medido e como dimensionar outra hipótese

| Fonte | Medição no ambiente registrado nos manifestos, Python 3.12.13/arm64 | Projeção anterior, não medição |
| --- | --- | --- |
| A, `fragmentation-pilot-v1/run-manifest.json` `/phases/*/elapsed_seconds` | benchmark 0,779 s; controle 0,189 s; principal 24,333 s; sensibilidade 1,806 s; soma 27,107 s. | `budget-decision.json`: pior taxa 42.844 tentativas/s; 112 trajetórias a 100 mil tentativas projetadas em 298,76 s, sob a regra conservadora; cap escolhido 100 mil. |
| B, `probabilistic-forecast-pilot-v1/run-manifest.json` `/runs/*/elapsed_seconds` | benchmarks R32/R64: 0,614/1,230 s; principal R32: 18,764 s; precisão R128: 80,937 s; confirmação R128: 79,476 s; três lotes analíticos 179,178 s. | `budget-decision.json`: 278,89 s projetados para a configuração R128, com margem; teto 1.200 s. |

Inventário do host atual, somente leitura: Apple M5, 10 CPUs lógicas, 16 GiB
de RAM (`sysctl` em 24/09). Os manifestos históricos registram arm64/macOS,
mas não vinculam as execuções a esse modelo de CPU. Não há medição de VPS,
paralelismo, aquecimento, memória de pico, I/O de reprodução completa, revisão
humana ou integração. Os tempos não devem
ser usados como prazo de artigo nem multiplicados cegamente por máquina.

Para um desenho futuro já autorizado, estimar **trabalho serial** como
`T ≈ C·r·h·(G_truth + m·R·G_member + m·R²·S_pair) + I`, onde C=células,
r=trajetórias por célula, h=ondas, m=candidatos, R=membros do ensemble,
G=custo de gerar um desfecho/membro (inclui tentativas), S_pair=custo de
comparar um par para ES e I=serialização/validação. A parte quadrática vem
dos pares do ES
em `metrics/histogram_scores.py`. Para A, usar soma de tentativas realmente
executadas por perfil e censura, não apenas `trajetórias × cap`. Coeficientes
e I são **desconhecidos** para nova hipótese/hardware. Medir um lote curto
predefinido sem olhar resultados, registrar p50/p95 e pior caso por célula,
projetar com margem e fixar cap antes de analisar sinais, como nos dois
`budget-decision.json`. Testar a projeção com um lote sentinela congelado;
se exceder orçamento, reduzir desenho por regra prévia ou registrar limite.
Não misturar ajuste de R com nova evidência independente.

## Sequência independente e dependências científicas

Já é possível, sem corpus aceito: inventariar contratos dos módulos e casos
analíticos; conferir links, hashes e disponibilidade dos objetos por meio do
validador offline **quando houver uma tarefa de reprodução autorizada**;
construir uma tabela de custo dos dois desenhos medidos; explicitar unidade de
análise, censura, seeds, modelos e limitações em um rascunho de protocolo.
Esse preparo não executa uma nova campanha nem promove resultados antigos.

Hipóteses, rascunhos e um piloto exploratório delimitado e autorizado podem
preceder a síntese aceita, como ocorreu com A e B. Uma nova campanha precisa
de escopo, critérios, orçamento e protocolo próprios; uma mudança material de
pergunta, modelo ou dados requer decisão científica explícita. Continuidades
reversíveis já abrangidas pela autorização operacional não exigem reconfirmação.
A **escolha final** da pergunta e a validação registrada dependem da síntese,
checagem de novidade, baselines, dados/licenças, estimando, unidade de análise,
efeito relevante, critérios de abandono e revisão do desenho. Para uma campanha
autorizada: testes analíticos e revisão isolada do kernel; benchmark **só de
custo**; lote exploratório limitado; decisão de parar ou protocolo sucessor;
depois, quando cabível, validação registrada com seeds/dados/condições
independentes e revisão estatística. Cada transição preserva inputs e outputs
imutáveis (`docs/process/research-lifecycle.md`;
`experiments/exploratory/README.md`).

## Handoff para Claude e revisores

1. Começar por `research/questions/research-questions.md`,
   `exploratory-claim-map.md` e os `protocol.md`, `spec.json`,
   `run-manifest.json`, `results-review.md` e `reproduce.md` de A e B. Usar
   seletores da tabela acima e objetos externos apenas após verificar SHA-256.
   Não tratar paths locais nos manifestos como acesso garantido.
2. Designar revisão de **novidade** por fontes primárias e corpus aceito,
   separada de revisão **estatística**: unidade, pareamento, censura, intervalos
   pontuais/multiplicidade, seleção no treino, pseudorreplicação e poder. Os
   revisores recebem desenho e evidências permitidas; rótulos selados de
   calibração/holdout não entram em prompts, ajuste ou escolha experimental.
3. Entregar pergunta e protocolo versionados, lista de inputs autorizados,
   código/lock/revisão, sementes separadas para custo/ajuste/teste, limites de
   execução, manifestos e JSONL completos por hash, análise com seletores e
   relatório de resultados negativos/censuras. Reproduzir em checkout limpo e
   distinguir verificação de integridade, revisão independente e aceite do
   Research Owner. Sem alterar saídas concluídas; correções são sucessores.

Bloqueio científico atual: corpus/síntese e pergunta final não aceitos. Nenhum
novo experimento, benchmark ou execução remota foi feito nesta auditoria.
