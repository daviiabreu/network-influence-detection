# Entrega técnica do mapa priorizado v5 — 25/09/2026

O [protocolo PT-BR](../../protocol/opinion-dynamics-systematic-map-v5-prioritized.md)
e o [JSON](../../protocol/opinion-dynamics-systematic-map-v5-prioritized.json)
implementam a decisão vinculante e seu adendo de duas famílias. O v4 está intacto.
Nenhuma chamada de modelo, adjudicação de elegibilidade ou push foi feita.

## Artefatos reproduzidos

O sucessor privado é `/Users/davi/.local/state/research-workbench/broad-map-v5-20260925/preparation-conceptual-v2`. Seu `manifest.json` liga entradas e saídas por
SHA-256. São 54,570 observações, 49,333 registros
originais distintos, 43,906 propostas após deduplicação e 2,494
pares ambíguos. Essa contagem não é o número final de obras incluídas.
O rascunho anterior confundia IDs projetados com IDs de registro original;
a correção conserva ambos e os membros da deduplicação. O pacote predecessor
foi retido com hash e registro de relocação no diretório de coordenação.

`layer-zero-list.jsonl` contém 1,302 candidatos a revisão/survey,
com título, IDs, ordem e estado pendente. Não são revisões já aprovadas.
`batch-0001.json` contém 500 obras da camada 0; o replay independente do driver
reproduziu seu plano integralmente, com zero chamadas. Há 24
pares que precisarão de disposição antes de adotar esse lote.

O [quadro de extração](mapping-extraction-frame-v5.json) preserva os seis campos
v4 e acrescenta mecanismo de influência, representação da opinião, desenho e
resultados. Códigos iniciais são provisórios, apoiados em v4 e revisões de
[Flache et al.](https://www.jasss.org/20/4/2.html),
[Lorenz](https://arxiv.org/abs/0707.1762) e
[Castellano et al.](https://arxiv.org/abs/0710.3256), com profundidade de leitura
registrada. A camada 0 ainda precisa fixar definições e granularidade.

## Diagnósticos do ranking inicial

| k | R | P | R+P | Inclusões focadas |
|---:|---:|---:|---:|---:|
| 500 | 2/25 (8.0%) | 0/28 (0.0%) | 2/53 (3.8%) | 23/130 (17.7%) |
| 1000 | 2/25 (8.0%) | 0/28 (0.0%) | 2/53 (3.8%) | 33/130 (25.4%) |
| 2000 | 10/25 (40.0%) | 0/28 (0.0%) | 10/53 (18.9%) | 45/130 (34.6%) |
| 5000 | 16/25 (64.0%) | 3/28 (10.7%) | 19/53 (35.8%) | 59/130 (45.4%) |
| 10000 | 21/25 (84.0%) | 11/28 (39.3%) | 32/53 (60.4%) | 65/130 (50.0%) |
| 20000 | 25/25 (100.0%) | 21/28 (75.0%) | 46/53 (86.8%) | 66/130 (50.8%) |
| 43906 | 25/25 (100.0%) | 28/28 (100.0%) | 53/53 (100.0%) | 68/130 (52.3%) |

[Curvas recall@k](ranking-recall-curves-v5.svg) e
[medidas estruturadas](ranking-diagnostics-v5.json). Todas as 53 fichas R/P foram
localizadas; nenhuma coincide com sementes. São rótulos de um único avaliador,
sem uso como referências ou treino. Das 130 inclusões focadas, 68 foram
localizadas; as 62 ausentes permanecem no denominador. As posições das
inclusões focadas são diagnóstico de treino. Uma correspondência de título
serve à localização/reserva, não adjudica identidade. O ranking não recebeu
ajuste posterior para melhorar estas curvas. Sem citações/revisão por pares
verificadas, os desempates de qualidade foram neutros.

## Coorte e pacote

Foram sorteadas 200 fichas, 20 por decil, das quais 50 sem resumo;
20 estão marcadas para auditoria adicional de referência. Probabilidades,
ordem e sementes estão em `cohort.json`. Houve zero interseção com as
4,867 propostas reservadas por exposição/ambiguidade,
com sementes ou com os itens do diagnóstico.

O pacote solicitado está em `/Users/davi/.local/state/research-workbench/coord-20260925/v5-calibration-packet.jsonl`,
SHA-256 `b3c67bc3cad552b7e0d848275d5700241021dbe3a550f14f9983e24273b231a4`.
Contém título, resumos/observações, IDs, escopo, critérios e tarefa com hash,
sem resposta de referência. Claude Fable e GPT Astra recebem cópias cegas;
o coordenador adjudica conflitos. A limitação de ausência de referência humana
e sobreposição de famílias com A/B é explícita.

**A independência ainda não está fechada:** o inventário da frente v2 declara
`complete=false`. O pacote está preparado, mas só pode ser liberado como coorte
de verificação após auditar as exposições faltantes e revalidar aliases.
Nada transforma o histórico de desenvolvimento falhado em calibração passada.
A frente C3 disponível contém preparação não adotada; nenhuma fusão foi
importada sem decisão nativa.

## Execução seguinte

1. Fechar inventário de exposição e revalidar a coorte. Produzir referências
   Claude Fable + GPT Astra, resolver divergências, auditar 10% e registrar adoção.
2. Calibrar A (Luna, Sol apenas se falhar) e B (Sonnet 5; Haiku 4.5 somente se
   calibrado), com recall ≥0,95 por revisor e Wilson relatado. Implementar/testar
   o executor Claude antes de produção; esta entrega só prepara lotes offline.
3. Triar camada 0, fixar quadro, resolver identidades que entrarem juntas na
   triagem, extrair com locadores e adotar cada lote após revisão independente.
4. Atualizar ranking após cada lote. Depois de ≥500 inclusões e duas transições
   estáveis, sortear/auditar 400 do restante. Categoria ausente manda retomar.

O comando de preparação é `scripts/prepare_prioritized_screening.py --help`.
O driver é `scripts/advance_prioritized_screening.py next --help`; consome
recibos nativos e índice de evidência `SHA-256 → {path, work_ids}`, verifica
bytes, faixa de linhas, trecho e obra. `saturation --help` recebe snapshots,
restante e auditoria congelados. Os comandos não despacham modelos.

## Verificação

Resultados finais dos gates e da revisão independente constam no registro
`validation-v5.md` desta pasta. Engenharia pronta não significa calibração,
referências adotadas, saturação atingida ou aceitação científica.
