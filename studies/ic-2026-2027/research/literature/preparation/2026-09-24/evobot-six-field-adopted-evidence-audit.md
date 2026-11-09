# EvoBot v3: auditoria dos valores de referência adotados

Rascunho público de 24/09/2026 para o caso de desenvolvimento
`verification.extractor.work.v2.e618414ee47714dd46aca671`, obra
`work.v2.e618414ee47714dd46aca671`, manifestação
`observation.e65db6d02136166dc2ac9f1cc1c09f40ac650c9a4867aeef7246bf4b3830d492`.
A fonte é [EvoBot v3](https://arxiv.org/abs/2508.17711v3), PDF SHA-256
`a7eea3ee9fbdaf40403b2a0fc5de2c2fd780021aa853fef0aecff01c2c986f0c`, com
projeção textual SHA-256
`bb25c8ac262e16494419451688283308cd23baba82226de7dbac44b45d878713`.
Foram conferidos os bytes retidos de ambos os artefatos. A suíte de desenvolvimento
SHA-256 `efaf237f3ab0b028bd82ca5a92c43bde25d350cf7ad2d308a4808b9ef5ae7f81`
e o pacote de decisão SHA-256
`7ac338a31a7299acf59564c27de420caa9f9b8fb0c905cbbf1b84e0bcf677b60`
fixam, respectivamente, a tarefa e os seis valores adotados a auditar.

Os intervalos abaixo são linhas inclusivas da projeção retida, identificada pelo
hash acima; não reproduzem trechos do artigo. O `agent_task` original continha
28 localizadores de páginas, enquanto `reference_evidence` registra vínculos
mais estreitos para a referência no caso de calibração. Cada valor adotado em
`reference_extraction.values` tem um único localizador. Esta auditoria verifica
se esse localizador sustenta todo o valor já adotado, sem acrescentar
afirmações ao valor, criar uma referência sucessora ou decidir aceitação científica.
O pacote privado de proposta está em
`/Users/davi/.local/state/research-workbench/autonomous-review-20260915/evobot-adopted-six-field-evidence-audit-20260924/packet.json`,
SHA-256 `f620c803d8e20cb731f28d471f40ad9e9519c032f6f22ebffdbf0b8f328e0d7d`
(diretório `0700`, arquivo `0400`).

## `empirical_grounding`

O valor adotado afirma: TwiBot-22 como conjunto principal de usuários, tweets e
relações de seguidores, particionado por Louvain em 12 comunidades; avaliação
do detector em Cresci-15 e TwiBot-20; simulações nos contextos de COVID-19 e
Rússia–Ucrânia; comparação de médias e dispersões dos escores de sentimento
de posts simulados e reais, tratados como proxy de opinião na escala −1 a +1.

| Parte do valor adotado | Localizador mínimo na projeção |
| --- | --- |
| TwiBot-22, relações de seguidores e 12 comunidades Louvain. | p. 4, linhas 54–65 |
| Avaliação externa do detector em Cresci-15 e TwiBot-20. | p. 7, linhas 66–70 |
| Contextos de COVID-19 e Rússia–Ucrânia. | p. 7, linhas 81–83 |
| Escores de sentimento como proxy de opinião, escala −1 a +1. | p. 7, linhas 89–94 |
| Comparação de médias e dispersões entre simulação e dados reais. | p. 7, linhas 105–135; p. 8, linhas 37–45 |

O localizador adotado, p. 4, linhas 54–69, sustenta apenas a primeira parte.
Todos os demais trechos estavam contidos no pool original de p. 7, linhas
1–94 e 95–140, e p. 8, linhas 1–103. A avaliação em Cresci-15 e TwiBot-20
é do detector; o valor não afirma treino de EvoBot nesses conjuntos.

## `evidence_gaps`

Valor adotado, transcrito do pacote de decisão: “Os autores apontam parâmetros
fixos de treinamento do detector, recursos limitados que reduziram dados e épocas,
e dificuldades de estabilidade, adaptação e robustez em escala real. Na simulação,
likes e retweets são removidos; a propagação recebe informação apenas de posts de
outros usuários, limitação associada a desvios principalmente no início.”

| Parte do valor adotado | Localizador mínimo na projeção |
| --- | --- |
| Parâmetros fixos do detector; recursos limitados, com conjunto de treino e épocas menores; estabilidade, adaptação e robustez em escala real como dificuldades declaradas pelos autores. | p. 9, linhas 46–54 |
| Exclusão de likes e retweets da simulação. | p. 4, linhas 90–94 |
| Recebimento de informação somente por posts de outros usuários e desvio observado especialmente no início da propagação. | p. 8, linhas 81–85 |

O único localizador do valor adotado é p. 9, linhas 44–56. Ele sustenta a
primeira frase, mas não as duas limitações da simulação e da propagação na
segunda. O pool original de 28 trechos já oferecia p. 4, linhas 1–97;
p. 8, linhas 1–103; e p. 9, linhas 1–98. Assim, a insuficiência é do vínculo
único da referência adotada, não da disponibilidade desses trechos na tarefa.
Os três subintervalos mínimos acima não eram localizadores exatos do pool
original; estão contidos nos três trechos de página oferecidos.

## `model_family`

Valor adotado, transcrito do pacote de decisão: “EvoBot é um agente baseado em
LLM, inicializado por SFT e refinado por DPO em aprendizado adversarial com um
detector que também se atualiza. O estudo compara a simulação de opiniões com
os modelos matemáticos de confiança limitada (Bounded Confidence) e de Lorenz,
além de baselines LLM.”

| Parte do valor adotado | Localizador mínimo na projeção |
| --- | --- |
| EvoBot como agente LLM; inicialização por SFT, refinamento por DPO e detector coadaptativo no aprendizado adversarial. | p. 1, linhas 17–30 |
| Identificação dos baselines LLM e dos modelos BC e Lorenz; formulação matemática dos dois últimos. | p. 7, linhas 136–139; p. 17, linhas 50–71 |
| Comparação da simulação de opinião entre EvoBot, BC, Lorenz e baselines LLM. | p. 8, linhas 37–45 |

O único localizador do valor adotado é p. 1, linhas 17–38. Ele sustenta a
caracterização de EvoBot na primeira frase, mas não a comparação com BC,
Lorenz e baselines LLM na segunda. O pool original de 28 trechos já oferecia
p. 1, linhas 1–91; p. 7, linhas 95–140; p. 8, linhas 1–103; e p. 17,
linhas 1–81. Portanto, a comparação já estava acessível ao extrator na tarefa
original; faltou um vínculo explícito às outras páginas no valor adotado. Os subintervalos mínimos
acima estão contidos nesses quatro trechos oferecidos, mas não coincidem com
localizadores exatos do pool.

## `network_topology`

O valor adotado descreve a direção da aresta `u → v` como “u segue v”, a
partição Louvain de TwiBot-22 em 12 comunidades com estruturas em estrela e
malha, o uso de tweets recentes de contas seguidas na simulação e a escolha
do parceiro BC entre usuários seguidos.

| Parte do valor adotado | Localizador mínimo na projeção |
| --- | --- |
| Sentido da aresta dirigida. | p. 2, linhas 76–88 |
| TwiBot-22, Louvain e 12 comunidades de topologias diversas. | p. 4, linhas 54–69 |
| Tweets recentes de contas seguidas na simulação. | p. 4, linhas 85–97 |
| Parceiro BC amostrado entre usuários seguidos. | p. 17, linhas 51–64 |

O localizador adotado, p. 2, linhas 76–88, sustenta apenas a direção da
aresta. Os outros três trechos pertencem ao pool original (p. 4, linhas
1–97; p. 17, linhas 1–81) e já têm vínculos em `reference_evidence` no nível
do caso; não são evidência nova ou um novo requisito científico.

## `reproducibility_artifacts`

O valor adotado relata o URL de código indicado pelo artigo, TwiBot-22 e
HiSim como entradas ou componentes, bibliotecas e hardware de treinamento,
e pseudocódigo, tabelas de hiperparâmetros e templates de prompts nos
apêndices.

| Parte do valor adotado | Localizador mínimo na projeção |
| --- | --- |
| URL do repositório informado pelos autores. | p. 1, linhas 40–43 |
| TwiBot-22, HiSim, bibliotecas e hardware. | p. 4, linhas 54–97 |
| Indicação das tabelas de hiperparâmetros e pseudocódigo efetivo do Algorithm 1. | p. 14, linhas 27–77 |
| Templates de prompts. | p. 19, linhas 1–30 |

O localizador adotado, p. 1, linhas 40–43, só sustenta o URL. Os demais
trechos já estavam no pool original; p. 14, linhas 45–77, com o pseudocódigo
efetivo, não integrava o `reference_evidence` mais estreito do caso. A auditoria
confere o que o artigo relata; não inspecionou o conteúdo ou o estado atual
do repositório de código citado.

## `validation_method`

O valor adotado reúne análise teórica condicional do ótimo adversarial,
avaliações e ablações do gerador e detector, comparação das estatísticas do
proxy de opinião com posts reais e modelos BC/Lorenz/LLM, teste Mann–Whitney,
simulações em comunidades com três execuções para examinar estabilidade e
avaliação externa do detector.

| Parte do valor adotado | Localizador mínimo na projeção |
| --- | --- |
| Ótimo adversarial sob condição declarada. | p. 4, linhas 47–51 |
| Avaliações empíricas e ablações de gerador e detector. | p. 5, linhas 11–15 e 71–76; p. 6, linhas 52–70 |
| Médias e dispersões do proxy contra dados reais e modelos BC/Lorenz/LLM. | p. 7, linhas 89–94 e 105–139; p. 8, linhas 37–45 |
| Teste Mann–Whitney. | p. 19, linhas 31–33 |
| Comunidades e três repetições das simulações-chave. | p. 8, linhas 32–35; p. 19, linhas 41–54 |
| Avaliação externa do detector. | p. 7, linhas 66–70 |

O localizador adotado, p. 4, linhas 47–51, sustenta só o primeiro item.
Todos os trechos restantes estão contidos no pool original de p. 5–8 e 19.
“Três execuções” não prova que toda combinação experimental foi repetida
três vezes; o teste Mann–Whitney não implica significância universal.

## Delta e decisão pendente

Nos **seis** valores efetivamente adotados, o único localizador anexado a
`ExtractedValue` sustenta uma parte, não o valor inteiro. Os trechos adicionais
já estavam disponíveis na tarefa de desenvolvimento; alguns também constam
dos 18 `reference_evidence` do caso. O contrato atual admite múltiplos
`reference_evidence` em nível de caso e os agrega à tarefa de validação, mas
cada `ExtractedValue` tem um só `locator` e os IDs de campo são únicos no
resultado. Falta, portanto, vínculo inequívoco entre **cada afirmação** e sua
evidência no valor composto — não evidência fonte nem capacidade geral de
armazenar múltiplos localizadores no caso. A frente de engenharia é dona de
qualquer representação opt-in futura; esta auditoria não altera contratos.

A [nota anterior](evobot-two-field-reference-successors.md) decompôs seis
*unidades derivadas* por campo para explorar possibilidades. Seus números,
cadências, fórmulas, métricas e granularidade adicional são detalhes
conferidos no artigo, **não** cláusulas literais dos dois valores adotados.
Não devem virar exigências científicas sem decisão explícita do Research
Owner. A opção que preserva o conteúdo adotado é manter os seis valores e
associar os trechos acima por afirmação; escolher um subconjunto de um único
localizador reduziria a cobertura. Essa escolha, a equivalência dos valores
medidos e eventual referência sucessora continuam sem decisão Owner. O
pacote privado novo registra apenas esta proposta com linhagem e hashes;
`owner_assessment=null`, `reference_successor=null` e
`scientific_acceptance=false` permanecem. A execução de desenvolvimento
`3044d04` continua `fail`; nada aqui a reclassifica.
