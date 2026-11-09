# Desenho da revisão até 31/10: pacote de decisão

Preparado em 18/09/2026 para Davi, Research Owner. É uma proposta: não
aprova protocolo, não adota referências e não registra decisão em seu nome.
As estimativas vieram de agentes de IA com papéis separados (três defensores,
um verificador e um crítico); concordância entre eles não é prova. Os scripts,
saídas e resumos usados estão em
`~/.local/state/research-workbench/review-design-20260918/`, cujo
`MANIFEST.sha256` tem SHA-256
`a07eaab81eae9ecb45f63c99aae302220cb5e7b5fd4e24710a8f860341611f2d`.

## Situação

A [carta do estudo](../../../charter/study-charter.md) fixa 31/10/2026 para a
pesquisa, o pacote de reprodutibilidade e o manuscrito pronto para submissão.
Restam 43 dias. O protocolo aprovado,
[v4](../../protocol/opinion-dynamics-systematic-map-v4.json), é um mapa amplo
de dinâmica de opiniões cuja aquisição terminou com 54.570 observações e
46.400 obras propostas. Nada foi triado; a calibração de desenvolvimento
continua `fail`.

O v4 não tem campo de extração para critério de parada, convergência ou
contagem de grupos, e nenhuma das 1.027 consultas contém termos de parada ou
terminação. O censo do v4 exigiria de 84 a 93 mil chamadas de triagem de
título e resumo com dois revisores, depois 5 a 6 mil textos completos. No
harness atual as chamadas são sequenciais e uma única resposta inválida
interrompe a etapa. A governança vigente pede uma escolha sua por exclusão,
por par de duplicata e por conflito. A cota do Codex também pesa: a página de
preços da OpenAI estima de 200 a 2.000 mensagens por cinco horas para o
`gpt-5.6-sol` no Pro 20x (50 a 500 no Pro 5x; seu nível provavelmente é o 20x,
mas isso é inferência) e fala em limites semanais. O `gpt-5.6-sol` caberia na
cota, se passar na calibração.

## Alternativas examinadas

Cada linha traz a estimativa do próprio defensor da alternativa, não uma
medida.

| Alternativa                               | Volume de triagem  | Estimativa do defensor para revisão e artigo até 31/10            | Limitação principal                                                                                               |
| ----------------------------------------- | ------------------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Censo do v4 com engenharia                | 84–93 mil chamadas | 25–35%                                                            | Textos completos, ~47 h suas, e não trata critérios de parada                                                     |
| Triagem priorizada com parada estatística | ~48 mil chamadas   | 20–25%                                                            | Economia de 30–50% aqui; a Cochrane (Handbook 6.5.1, §4.6.6.2) não recomenda a eliminação automática por essa via |
| Revisão focada no tema candidato          | 3–5 mil chamadas   | 50–60% (estimada com uma camada de amostra que recomendo retirar) | Recall depende da estratégia; exige nova versão do estudo                                                         |

Uma camada de mapa amplo por amostra aleatória também foi examinada. Não
encontramos orientação da CEE, da Campbell, do JBI ou da Cochrane que a
sustente, e recomendo descartá-la.

A estratégia focada combina termos de confiança limitada com termos de
dinâmica de opiniões associados a parada ou fragmentação. Aplicada a títulos
e resumos, ela seleciona 2.051 propostas, entre cerca de 1.364 e 2.186 obras
conforme as duplicatas pendentes se resolvam. Uma segunda implementação da
mesma estratégia reproduziu a contagem com diferença de 0,4%, o que mostra
reprodutibilidade, não validade. Contra uma lista de 47 trabalhos conhecidos
montada por IA depois da estratégia, ela recuperou 38 dos 43 presentes no
corpus (88%; intervalo de 95% de 75% a 95%). Entre os perdidos há um trabalho
dentro do tema, Jabin e Motsch (2014). Ao menos quatro artigos matemáticos de
convergência nem estão no corpus. Um quarto do corpus (11.756 propostas) não
tem resumo.

## Recomendação

Descontinuar o mapa amplo v4 na etapa de aquisição, relatando-o assim no
PRISMA, e abrir uma nova versão vinculada do estudo com uma revisão
sistemática focada no tema candidato exploratório: critérios de parada,
convergência e diagnóstico de fragmentação em simulações de dinâmica de
opiniões de confiança limitada e modelos próximos, com atenção a redes
esparsas. A carta exige nova versão quando muda o alvo de avaliação
(`study-charter.md:127-129`), e a pergunta final da IC continua dependendo da
síntese aceita (`study-charter.md:10-11`). A revisão focada testa esse
candidato; se a síntese não sustentar a lacuna, a pergunta não é selecionada
e o resultado negativo é registrado.

O corpus adquirido vira uma fonte registrada. A estratégia é congelada, com
hash, antes de qualquer triagem, e complementada por buscas pequenas sobre
teoria de convergência e terminação e sobre detecção de regime estacionário
em simulação, além do encadeamento de citações até duas rodadas consecutivas
sem nova obra elegível, que é a regra já aprovada. Os cerca de 44 mil
registros não selecionados aparecem no fluxo como fora da estratégia focada,
não como excluídos por triagem. Isso também é uma forma de exclusão
automática por estratégia de busca, como a de qualquer consulta a uma base; o
estreitamento depois de examinar o corpus é o principal risco de viés e fica
declarado com data e motivo.

No código atual, um protocolo sucessor que muda buscas, elegibilidade ou
campos de extração não pode herdar o corpus do v4. Por isso a revisão focada
terá aquisição própria: sua primeira busca aplica a estratégia às observações
do v4, identificadas por hash, e as buscas suplementares entram na mesma
aquisição. Preparação do corpus, deduplicação e metadados rodam então sobre
2 a 3 mil registros; cerca de 1.257 cartões de duplicata tocam o conjunto,
contra 10.754 no corpus inteiro. Nenhum dos nove registros sem título, Africa
Today incluído, cai no conjunto focado ou no fechamento de suas duplicatas.

## Decisões pedidas

**D1. Nova versão do estudo.** Encerrar o v4 na aquisição e abrir a nova
versão com o protocolo focado. O rascunho já existe e passou por revisão
metodológica independente:
[proposta](../../protocol/opinion-dynamics-stopping-review-v1-proposal.json),
[nota de revisão](../../protocol/opinion-dynamics-stopping-review-v1-review.md)
e [registro da versão](../../../decisions/2026-09-18-focused-review-study-version-draft.md).
A estratégia revisada seleciona 4.258 registros, ou 2.308 obras, e deixa
50.312 registros (44.092 obras) fora do filtro. O rascunho usa contratos que
já estão no ramo de integração, mas ainda não no principal, e só valida com o
código desse ramo. A política de referências da calibração entra depois, numa
emenda v1.1 que depende de D5. Recomendo aprovar
depois da sua leitura, junto com as escolhas abertas listadas na nota de
revisão (duas revisões para a lista de controle, termos acrescentados,
alocação da amostra e limiares das subafirmações). Consequência: o artigo cita
uma revisão focada e resume a aquisição ampla em um parágrafo descritivo. A
proposta v5 de metadados deixa de ser necessária e seria retirada
formalmente, com os registros preservados.

**D2. Adjudicação assistida.** Propostas geradas por regra ou IA, adotadas por
você em lote depois de uma auditoria aleatória estratificada dimensionada para
erro de até 2% com 95% de confiança quando a amostra não tem erro; um erro
devolve a faixa inteira para revisão. Na triagem de título e resumo,
divergências e respostas incertas seguem para o texto completo. Exclusões
concordantes são adotadas em lote após auditoria. Exclusões no texto completo
continuam individuais; o volume estimado é de 400 a 550 textos avaliados.
Recomendo sim. Sem isso, mesmo a revisão focada exigiria milhares de escolhas
individuais.

**D3. Versões do mesmo trabalho.** Preprint e versão publicada, e depósito em
repositório e artigo, contam como uma obra quando autores e ano são
compatíveis. Recomendo sim. Sem isso, os cartões dessa faixa (4.079 no corpus
inteiro, algumas centenas no conjunto focado) passariam a julgamento
individual.

**D4. Revisores de IA.** Revisor A em `gpt-5.6-sol` e revisor B em
`gpt-5.6-terra`, pelo Codex, ambos calibrados de novo. Recomendo essa
combinação porque reduz, sem eliminar, erros correlacionados e cabe na cota
para cerca de 4 mil chamadas. A alternativa é o Claude como revisor B: rodaria
em série, o que é aceitável nesse volume, mas exige repinar a política do host
e não permite orquestrar pelo Claude Code durante a execução. A política de
tentativas acompanha: até três tentativas idênticas por tarefa, todas retidas;
se as respostas divergirem, a obra segue para o texto completo, como em D2.

**D5. Calibração.** O histórico de ajuste continua "desconhecido". Os 50 casos
antigos viram conjunto de ajuste declarado, e a calibração usa 50 obras novas
sorteadas do conjunto focado, com referências propostas por IA e adotadas por
você, como no v4. O resultado é relatado como concordância com referências
adotadas, não como recall absoluto. Se falhar de novo, proponho uma segunda
rodada com prompt revisado e novo sorteio; se falhar outra vez, você triaria
em dupla com um revisor de IA, sem exclusão automática. Recomendo sim.

**D6. Validação do recall.** Antes de rodar a estratégia congelada, você fixa
uma lista de trabalhos conhecidos a partir das referências de duas revisões
publicadas escolhidas por você. Se o recall ficar abaixo de 90%, a estratégia
é revisada e registrada como sucessora. Uma amostra aleatória de cerca de 200
registros de dinâmica de opiniões que a estratégia não captura passa pela
triagem para estimar o que ficou de fora. Recomendo sim.

**D7. Buscas suplementares.** Registrar consultas em OpenAlex, arXiv e
Crossref sobre convergência e terminação dos modelos de Hegselmann–Krause e
Deffuant e sobre regime estacionário em simulação, com textos exatos e datas.
As exportações ACM e IEEE continuam suas; proponho declará-las não executadas,
com justificativa, se não couberem no prazo. Recomendo sim.

**D8. Sondagem de cota.** Confirmar o nível do plano, fixar um teto de gasto
com créditos e autorizar cerca de 200 chamadas reais para medir o consumo de
cada modelo antes da triagem. Recomendo sim.

**D9. Textos completos.** Obtenção automática por acesso aberto (arXiv,
OpenAlex); você fornece pelo acesso institucional os que faltarem; o restante
recebe `not_retrieved`, relatado como "Reports not retrieved". Artigos
teóricos pagos são o maior risco de ficarem sem texto. Recomendo sim.

**D10. Simplificação.** Dispensar as calibrações dos papéis de apoio e a
revisão global calibrada, que foram acréscimos de desenho e não exigências do
protocolo, mantendo a verificação da extração e uma revisão adversarial de
contexto isolado, como pede a carta. No código, isso exige um novo formato de
plano em que as etapas nativas vão até a extração e o aceite se apoia no hash
do relatório; síntese e revisão adversarial seguem registradas fora do
pipeline. Manter o plano atual evita cerca de dois dias de engenharia, mas
custa de 20 a 40 horas suas a mais e atrasa o início da triagem. Recomendo
simplificar.

**D11. Experimentos antes da síntese.** A carta só permite selecionar a
pergunta depois da síntese aceita. Começar os experimentos em 22/09 exige uma
emenda à carta, com o risco declarado de fixar o tema cedo; a linha do piloto
B, de previsão, não é coberta pela revisão focada. As alternativas são
esperar a síntese (cerca de 17/10) ou mover a data interna de 31/10.
Recomendo começar agora apenas o desenho experimental e a infraestrutura de
simulação, que servem a mais de um recorte, e registrar os experimentos só
depois da síntese.

## O que segue sem depender de você

A engenharia comum a qualquer desenho continua: retomada e novas tentativas
no harness, envio paralelo limitado, obtenção de textos por acesso aberto e
as propostas de deduplicação por regra, já geradas sem decisão registrada.
Também avançam, em branches separados e sem integração antes da sua
decisão, a busca registrada sobre as observações do v4, o encadeamento de
citações pelo OpenAlex, a disposição `not_retrieved`, o formato de plano
simplificado e o rascunho do protocolo focado para sua leitura. Se D1 for
recusado, esse trabalho é descartado sem afetar o v4.

## Calendário proposto

| Período     | Revisão                                                                                                               | IC e artigo                                        |
| ----------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 18–22/09    | Suas decisões; rascunho da nova versão; engenharia                                                                    | Desenho experimental                               |
| 22–25/09    | Protocolo aprovado e congelado; validação de recall; buscas suplementares; deduplicação do conjunto; sondagem de cota | Infraestrutura de simulação                        |
| 25–28/09    | Calibração com referências novas                                                                                      | Idem                                               |
| 28/09–02/10 | Triagem de título e resumo                                                                                            | Idem                                               |
| 01–08/10    | Textos completos, triagem final, encadeamento de citações                                                             | Idem                                               |
| 06–13/10    | Extração, verificação e avaliação                                                                                     | Idem                                               |
| 13–17/10    | Síntese, revisão adversarial e seu aceite                                                                             | Seleção da pergunta                                |
| 17–31/10    | Trabalhos relacionados                                                                                                | Experimentos, artigo e pacote de reprodutibilidade |

Esse calendário deixa só duas semanas para experimentos e redação depois da
síntese, o que é apertado. Um agente estimou seu tempo em 30 a 35 horas ao
longo da revisão, sem contar o trabalho da IC.
