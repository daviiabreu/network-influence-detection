# Revisão focada v1: proposta para leitura

Este texto foi redigido por um agente de IA (Claude) em 18/09/2026 para a
leitura de Davi como Research Owner e revisado no mesmo dia depois de uma
revisão metodológica independente. Acompanha a
[proposta de protocolo](opinion-dynamics-stopping-review-v1-proposal.json) e o
[rascunho da nova versão do estudo](../../decisions/2026-09-18-focused-review-study-version-draft.md).
As decisões D1 a D11 do
[pacote de 18/09](../preparation/2026-09-18/review-design-decision-packet.md)
continuam com Davi; o que segue descreve o que a proposta faria se ele aprovar
D1.

O JSON usa contratos que existem no ramo de integração
`feat/focused-review-integration` e ainda não no ramo principal: o acesso
`prior_acquisition` da consulta ao corpus, a disposição `not_retrieved` e a
opção `not_reported_allowed` dos campos de extração, além da autoridade de
ausência limitada ao pool integral de texto completo. Validado na árvore
integrada, o protocolo passa em
`research-workbench systematic-review validate-protocol`, com hash canônico
`d971dc37b6097ba70f81584ab236840399ca918753235ec83034a05d41a38966` e hash de
bytes `0ed494cc9b40740eacb7038b09acbc534214ebc31a5e9dd1f7394178dd53b9d8`, e as
cinco requisições são preparadas e validadas sem rede. O validador do ramo
principal recusa o arquivo, porque desconhece esses contratos. Não restam
marcas `PLACEHOLDER` no JSON. Falta, por desenho, a emenda de referências
descrita na seção sobre calibração.

## Motivo e data

A auditoria de 17/09/2026 mostrou que o mapa amplo aprovado, o
[v4](opinion-dynamics-systematic-map-v4.json), terminou a aquisição com 54.570
observações e 46.400 obras propostas, sem triagem, e com a calibração de
desenvolvimento em `fail`. O v4 não tem campo de extração para critério de
parada, convergência ou contagem de grupos, e nenhuma das suas 1.027 consultas
usa termos de parada ou terminação. O censo exigiria de 84 a 93 mil chamadas de
triagem de título e resumo, com o harness atual executando uma chamada por vez.
Em 18/09, o pacote comparou três desenhos e recomendou encerrar o v4 na
aquisição e abrir uma revisão sistemática focada no tema candidato.

A [carta do estudo](../../charter/study-charter.md) define o formato. As
linhas 127 a 129 pedem uma nova versão vinculada do estudo quando muda o alvo
de avaliação, como acontece ao trocar um mapa da área por uma revisão de um
tema. As linhas 10 e 11 deixam a pergunta final da IC para depois da síntese
aceita; por isso a revisão testa um candidato sem escolhê-lo. As linhas 80 a 82
reservam a Davi a mudança de protocolo, e as linhas 121 a 125 admitem o
resultado negativo de um desenho registrado.

## O que a revisão pergunta

O candidato vem da [exploração de 12/09](../../questions/exploration/2026-09-12/README.md)
e do [piloto A](../../../experiments/exploratory/fragmentation-pilot-v1/README.md):
em simulações de confiança limitada sobre redes esparsas ou modulares fixas, um
critério de parada por tolerância ou por horizonte pode declarar uma partição
final antes de os grupos estarem separados. O piloto observou um único caso,
ligado a uma implementação que mantém a partição em memória, e encontrou um
antecedente de 2018. O [mapa das afirmações](../../questions/exploratory-claim-map.md)
registra esses limites, e a revisão pode rejeitar o candidato.

As perguntas cobrem os critérios de parada e seu relato (rq1), a identificação
dos grupos finais e as verificações de que a partição não muda mais (rq2), os
resultados analíticos de convergência e terminação com suas hipóteses sobre a
rede (rq3), as análises de sensibilidade ao critério de parada (rq4) e o
veredito sobre o candidato (rq5).

O veredito se divide em três afirmações registradas no protocolo, cada uma
julgada como sustentada, refutada ou indeterminada a partir dos valores
extraídos das obras incluídas. Os resultados do piloto não entram como
evidência.

- Prática (`candidate_gap_practice`). Base: simulações de confiança limitada
  em redes esparsas, ou modulares, com topologia fixa. Contam como não
  verificadas as que param só por tolerância ou horizonte, sem checagem de
  separação, garantia analítica, continuação após a parada ou comparação de
  critérios. É sustentada com pelo menos duas não verificadas que sejam ao menos
  metade das que relatam a regra; é refutada quando há ao menos duas que
  relatam e as não verificadas são menos da metade; é indeterminada quando
  menos de duas relatam. A parcela que não relata a regra é informada à parte.
- Certificado (`candidate_gap_certificate`). É refutada se alguma obra
  incluída provar ou citar um certificado restrito às arestas da rede ou aos
  pares de componentes ligados por arestas. O critério de Meng, Van Gorder e
  Porter (2018), que exige grupos separados por pelo menos o limite de confiança
  no espaço de opiniões, é um certificado global: vale em qualquer grafo, checa
  todos os pares de grupos e não refuta esta afirmação. Ele entra como
  antecedente direto, com o qual um certificado restrito teria de ser comparado,
  como a checagem de fontes do piloto já apontava. Se a obra de 2018, que já
  está na seleção, contasse como certificado para redes esparsas, a afirmação
  nunca poderia ser sustentada.
- Consequência (`candidate_gap_consequence`). É sustentada se alguma obra
  incluída relatar que mudar a regra, a tolerância, o horizonte ou a precisão
  alterou a contagem de grupos, seus tamanhos ou a classificação entre consenso
  e fragmentação em redes esparsas ou modulares. É refutada se pelo menos duas
  obras relatarem essas análises em redes desse tipo, com tolerâncias ao menos
  tão grandes quanto as usadas na prática, sem nenhuma mudança. Fica
  indeterminada, e é relatada como não testada, nos outros casos.

O veredito geral é refutado quando qualquer afirmação é refutada e sustentado
quando prática e certificado são sustentados e a consequência não é refutada,
dizendo se ela já foi mostrada ou continua sem teste. Nos demais casos fica
indeterminado. Sustentado é condição necessária, e não suficiente, para
escolher uma pergunta: as linhas 121 a 125 da carta também pedem novidade
plausível, importância, falseabilidade, baselines viáveis, caminho de validação
e recursos compatíveis, e esse julgamento é de Davi.

## Diferenças em relação ao v4

| Parte do protocolo            | v4                                                          | Proposta                                                                                                       | Motivo                                                                                              |
| ----------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Identidade                    | `opinion-dynamics-systematic-map-v4`, 4.0.0, 14/09          | `opinion-dynamics-stopping-review-v1`, 1.0.0, 18/09, `supersedes` v4                                           | Nova linhagem de revisão; o schema não tem campo `derived_from`                                     |
| `review_kind`                 | `systematic_mapping`                                        | `systematic_review`                                                                                            | Perguntas fechadas sobre um tema, com regra de decisão                                              |
| Título, objetivos e perguntas | Mapa de famílias, validação e reprodutibilidade (rq1 a rq4) | Parada, convergência, grupos finais e veredito sobre o candidato (rq1 a rq5)                                   | Alvo de avaliação novo                                                                              |
| Definições                    | 4 termos                                                    | 16 termos: os 4 anteriores e mais 12                                                                           | Campos novos, afirmações do candidato e procedimentos de validação                                  |
| Escopo                        | 1970-01-01 a 2026-09-11, inglês, três tipos de publicação   | Igual                                                                                                          | O corte acompanha o corpus; obras posteriores podem ser citadas como contexto, fora da contagem     |
| Fontes                        | arXiv, Crossref, DBLP, OpenAlex                             | arXiv, OpenAlex e o corpus do v4                                                                               | O corpus vira fonte; DBLP e Crossref já estão no corpus, e o Crossref não serve para busca temática |
| Buscas                        | 1.027                                                       | 5: uma sobre o corpus, duas no arXiv, duas no OpenAlex                                                         | Estratégia focada e buscas suplementares pequenas                                                   |
| Elegibilidade                 | 6 critérios                                                 | 8 critérios                                                                                                    | População e conceito novos, com condições explícitas para modelos próximos                          |
| Deduplicação                  | Algoritmo 2, identificadores tipados                        | Igual                                                                                                          | Sem motivo para mudar                                                                               |
| Triagem                       | Semente 20260903                                            | Semente 20260918; demais valores iguais                                                                        | Sorteio novo para um conjunto novo                                                                  |
| Referências de calibração     | `calibration_reference_policy` presente                     | Ausente; entra numa emenda v1.1                                                                                | A calibração 5 e a ponte C4v2 exigem um sucessor aprovado que acrescente só essa política           |
| Texto completo                | `pending_retrieval`                                         | `not_retrieved`                                                                                                | Textos não obtidos recebem disposição terminal adotada por Davi (D9)                                |
| Busca suplementar             | Sete métodos, com checagem manual no Google Scholar         | Oito métodos: sai o Google Scholar, entram a checagem por itens conhecidos e a amostra de não capturados       | Validação da estratégia (D6)                                                                        |
| Campos de extração            | 6                                                           | 17: os 6 do v4 e mais 11                                                                                       | Nenhum campo do v4 trata de parada; todo estrato precisa de um campo de origem                      |
| Qualidade                     | 4 critérios                                                 | 5, com `quality.termination_reporting`                                                                         | O relato da parada é o objeto central                                                               |
| Síntese                       | Mapa descritivo, matriz de lacunas, narrativa; 7 estratos   | Tabulação estruturada, matriz de lacunas, narrativa e teste do candidato; 8 estratos, todos campos de extração | Regra de decisão registrada                                                                         |
| Conclusão                     | 4 critérios                                                 | 11 critérios                                                                                                   | Registram regras que o schema não tem onde guardar                                                  |
| Emendas, atualização, PRISMA  | Iguais                                                      | Iguais                                                                                                         | Sem motivo para mudar                                                                               |

Os quatro critérios de exclusão do v4 (data e idioma, produto não acadêmico,
domínio sem opinião humana, ausência de modelo computacional) continuam, com
casos de fronteira novos. Um método geral de detecção de regime estacionário
testado só em modelos que não são de opinião fica fora da contagem e pode ser
citado como contexto. Toda obra da família de confiança limitada é incluída,
relate ou não sua regra de parada, porque a falta desse relato é uma das
coisas medidas. Obras de outros modelos de opinião só entram se o texto
completo atender a pelo menos uma de quatro condições: (a) critério de parada,
convergência ou terminação além de um horizonte fixo simples; (b) procedimento
declarado de identificação dos grupos finais; (c) análise de sensibilidade dos
resultados à regra de parada, tolerância, horizonte ou precisão; (d) tratamento
declarado das execuções que não pararam ou de estados metaestáveis. Resultados
analíticos de convergência desses modelos, como provas sobre DeGroot ou
Friedkin-Johnsen, servem apenas de contexto, o que mantém a rq3 restrita à
confiança limitada. Uma simulação com agentes LLM que para após um número fixo
de rodadas só entra se atender a (b), (c) ou (d). Na primeira versão deste
rascunho, qualquer simulação com horizonte e qualquer prova de convergência de
outro modelo entrariam.

## Buscas

### Consulta ao corpus

A consulta usa a gramática `corpus_boolean_v1`, integrada a partir de
`feat/focused-search-sources`: termos, frases entre aspas, truncamento à
direita com radical de pelo menos três caracteres, `AND`, `OR` e `NOT` com
parênteses obrigatórios ao misturar operadores, e normalização NFKD, casefold e
remoção de acentos, com tokens `[a-z0-9]`. A primeira versão deste rascunho
usava expressões regulares, que o adaptador não executa. A tradução literal dos
blocos do rascunho de 17/09, feita no ensaio sem rede de 18/09, seleciona 3.876
observações e 2.058 obras propostas, o mesmo conjunto do casador por tokens do
rascunho; a versão com expressões regulares dava 2.051, com 23 obras a mais e
16 a menos, por diferenças de separadores.

Antes de Davi fixar sua lista de itens conhecidos, a proposta acrescenta três
grupos de termos, cada um combinado da mesma forma que os demais blocos:
`hegsel*`, `hegelsm*`, `krause*`, `"2r conjecture"` e `"bounded trust"` no bloco
de confiança limitada, que cobrem grafias erradas e o processo de médias de
Krause (mais 20 obras); `clustering` no bloco de fragmentação (mais 170); e
`"asymptotic behavio*"` no bloco de parada (mais 62). Juntos acrescentam 250
obras e recuperam Jabin e Motsch (2014), que a lista montada por IA mostrou
como perda. Das 168 obras que entram só por `clustering`, dez mencionam
"clustering coefficient"; mantive o termo simples, porque um `NOT` excluiria
também registros que tratam dos dois assuntos. Esses acréscimos vieram de
sondagens no próprio corpus e ficam declarados como desenvolvimento pós-hoc.
Davi pode desfazê-los antes de fixar a lista.

A consulta final tem 4.340 caracteres e seleciona 4.258 observações (2.905 do
OpenAlex, 1.011 do arXiv, 278 do DBLP e 64 do Crossref), que correspondem a
2.308 obras propostas; 164 delas não têm resumo. O casamento é por observação:
outras 337 manifestações das obras selecionadas, que não casam por conta
própria, não entram, e os parceiros não selecionados de candidatos a duplicata
também não. O fechamento de duplicatas da primeira versão saiu, porque a fonte
não o executa. A fonte segue o contrato integrado: `source_id` `corpus_query`,
adaptador `corpus_query_v1`, acesso `prior_acquisition`, classe `restricted`,
formato `review_observations_json` e dois filtros de fixação:
`observations_sha256`, com o hash das observações projetadas, e
`acquisition_receipt_sha256`, com o hash do recibo da aquisição anterior. O
recibo de preparação do corpus `fa934b8b…` liga os dois: conferi com os
contratos reais do ramo de integração que seu `inputs.acquisition` é o recibo
fixado e seus `records` são as observações fixadas, e que o recibo da aquisição
aponta o protocolo v3, a execução
`opinion-dynamics-map-v3-broad-20260911-interrupted-1` e o relatório
`edfa4847…`. A gramática integrada ficou mais restrita (recusa caracteres que
somem na normalização, palavras parecidas com operadores e alternativas só
negadas); a consulta passa por ela e continua selecionando as mesmas 4.258
observações.

### Buscas suplementares

No OpenAlex e no arXiv, a primeira consulta passou a usar só os nomes dos
modelos: `Hegselmann OR Deffuant OR "Krause model" OR "relative agreement model"`.
Nenhuma consulta do v4 nomeava esses modelos. A versão anterior exigia também
termos de convergência e deixava de fora, por exemplo, o artigo de Häggström
(2012) sobre o modelo de Deffuant, que a consulta atual recupera. As contagens
feitas em 18/09, só de totais, foram 630 no OpenAlex e 214 no arXiv, abaixo
dos limites de 2.000 e 1.000 registros. As consultas sobre critério de parada e
regime estacionário em modelos baseados em agentes aplicados a opinião
continuam, com 43 e 13 resultados na contagem do revisor.

As consultas temáticas no Crossref saíram. O `query.bibliographic` não tem
lógica booleana, os totais foram de 3,0, 3,4 e 0,8 milhões de registros, e o
limite de páginas sempre cortaria a lista por relevância. O Crossref continua
apenas na recuperação exata de DOI durante o encadeamento de citações.

### Encadeamento de citações

A regra aprovada no v4 continua: parar após duas rodadas consecutivas sem nova
obra elegível depois da deduplicação. As sementes são as obras incluídas no
texto completo e as revisões encontradas na triagem. O ramo
`feat/focused-search-sources` implementa estratégias do OpenAlex só com filtro,
`cites:` para a frente e `cited_by:` para trás, com uma obra por estratégia.
Como as sementes de cada rodada só são conhecidas depois da triagem, as
estratégias de cada rodada entram por emenda datada antes da execução. Se uma
rodada trouxer mais de 3.000 registros novos, ela para até uma decisão
registrada de Davi, porque os artigos clássicos de Deffuant e de Hegselmann e
Krause têm milhares de citações. As exportações da ACM e do IEEE continuam
sendo de Davi e, se não forem feitas antes da triagem de título e resumo, são
relatadas como não executadas, com o motivo.

## Validação da estratégia

### Itens conhecidos

Davi escolhe duas revisões publicadas e monta a lista com as referências delas
que atendem à elegibilidade deste protocolo, a juízo dele. A lista é fixada
antes da execução registrada da consulta. Como o rascunho da estratégia já
rodou sobre o corpus em 17 e 18/09, quem monta a lista não abre
`outputs/focused_ids_final.json` nem as saídas do ensaio sem rede. Opções de revisões, com DOI conferido no Crossref em 18/09:

- Bernardo, Altafini, Proskurnikov e Vasca, "Bounded confidence opinion
  dynamics: A survey", Automatica 159, 111302 (2024),
  `10.1016/j.automatica.2023.111302`;
- Proskurnikov e Tempo, "A tutorial on modeling and analysis of dynamic social
  networks. Part II", Annual Reviews in Control 45, 166–190 (2018),
  `10.1016/j.arcontrol.2018.03.005`;
- como alternativa, Lorenz, "Continuous opinion dynamics under bounded
  confidence: A survey", International Journal of Modern Physics C 18,
  1819–1838 (2007), `10.1142/S0129183107011789`.

O casamento com o corpus é pré-especificado no protocolo (`known_item_check`):
DOI normalizado, depois identificador arXiv, depois título normalizado igual,
com ano a no máximo um de distância. Um sorteio com semente divide a lista em
metades de desenvolvimento e de teste, cada uma com seu hash. A metade de
desenvolvimento pode orientar mudanças antes do congelamento; a de teste é
avaliada uma única vez na estratégia congelada e precisa ter pelo menos 30
itens presentes no corpus, senão Davi acrescenta uma terceira revisão antes do
sorteio. O recall é relatado com intervalo de Wilson de 95%, no total e
separadamente para itens que nomeiam um modelo de confiança limitada e para
itens de modelos próximos. O limiar é 0,90 sobre a estimativa pontual total.
Uma estratégia sucessora só é aceita depois de passar pelo mesmo limiar numa
nova metade de teste, montada a partir de uma revisão ainda não usada. Na
primeira versão deste rascunho, uma sucessora seria aceita sem novo teste.
Itens ausentes do corpus medem a cobertura das buscas suplementares e do
encadeamento.

### Amostra de não capturados

A amostra é um procedimento de validação: não é fonte de identificação nem
medida de recall. O quadro são as obras propostas que casam com o bloco geral
de dinâmica de opiniões, não têm nenhuma observação selecionada e não estão
ligadas a uma obra selecionada por candidato a duplicata. No corpus atual são
7.524 obras, divididas em um estrato de risco alto, com termos de convergência,
comportamento assintótico, grupos, consenso, equilíbrio, regime estacionário
ou polarização (2.690 obras), e o restante (4.834). São sorteadas 150 obras do
primeiro estrato e 50 do segundo, com semente fixa, e só essas 200 são
triadas, pelo mesmo processo, depois da calibração e antes da triagem principal
de título e resumo. A estimativa de obras elegíveis perdidas é
2.690·x₁/150 + 4.834·x₂/50, com intervalos exatos por estrato. Obras elegíveis
encontradas entram na síntese como identificadas por outros métodos.

Qualquer obra elegível na amostra obriga a uma estratégia sucessora que cubra
seu vocabulário antes da triagem principal. A regra anterior, de três ou mais
obras, tinha pouco poder: com 200 sorteios simples em 7.682 obras, a chance de
disparar era 0,08 com 38 perdas, 0,32 com 77, 0,58 com 115 e só chegava a 0,80
com cerca de 163. Com cerca de 400 inclusões, um recall de 0,90 admite até 44
perdas. Com o gatilho de uma obra e a alocação 150/50, a chance de disparar com
44 perdas é de 0,70 a 0,92, conforme a fração delas no estrato de risco alto
vá de proporcional ao tamanho a total; com 77 perdas, de 0,88 a 0,99. Se as
perdas estiverem todas no outro estrato, a chance com 44 cai para cerca de
0,37. O desenho aposta que as perdas se concentram no estrato de risco alto, e
essa aposta fica declarada. A primeira versão deste rascunho também somava ao
sorteio o fechamento de duplicatas, que levaria a cerca de 336 obras triadas; o
estimador agora usa apenas as 200 unidades sorteadas.

## Estreitamento depois de ver o corpus

O principal risco de viés é que o recorte foi decidido depois de examinar o
corpus. O tema candidato surgiu da navegação pelos títulos do mesmo corpus em
12/09. A estratégia foi escrita por agentes em 17 e 18/09, que viram suas
contagens, compararam o resultado com uma lista de 47 trabalhos montada depois
da estratégia (38 dos 43 presentes no corpus foram recuperados) e, nesta
revisão, acrescentaram termos a partir de sondagens no corpus. Nenhuma dessas
comparações vale como validação.

Para limitar esse risco, a estratégia é congelada pelo hash do protocolo antes
de qualquer triagem, a metade de teste da lista de Davi é avaliada uma única
vez, a amostra de não capturados é triada antes da triagem principal, e as
buscas com outro vocabulário e o encadeamento procuram o que a estratégia
perdeu. O artigo deve contar, nos métodos, que o mapa amplo foi interrompido na
aquisição em 18/09/2026 por inviabilidade de prazo, que a revisão focada foi
definida depois de explorar o corpus adquirido, o que os autores da estratégia
viram e como ela foi verificada. Os resultados valem para o tema assim
definido e não como amostra imparcial da área.

## PRISMA

O v4 é relatado como mapa descontinuado na aquisição, num parágrafo
descritivo: 1.027 consultas, 54.570 observações, 46.400 obras propostas e
nenhuma triagem. A aprovação do v4 permanece como registro histórico.

No fluxo da revisão focada, a identificação lista as 54.570 observações do v4
por fonte (42.565 do OpenAlex, 6.153 do DBLP, 4.917 do arXiv e 935 do
Crossref) e os registros das buscas suplementares por fonte; o encadeamento de
citações fica na coluna de outros métodos. As 50.312 observações fora da
estratégia, que correspondem a 44.092 obras propostas, aparecem em "removidos
antes da triagem, outros motivos: filtro lexical focado", e o filtro é
descrito no PRISMA-S como limite da busca. A amostra de não capturados aparece
numa caixa lateral de validação; obras elegíveis achadas nela entram pela
coluna de outros métodos. Cada caixa diz se conta registros (observações) ou
obras. Textos não obtidos entram em "Reports not retrieved". A troca do mapa
pela revisão focada é relatada no item 24c como desvio do protocolo registrado
(v4).

## Triagem, calibração e decisões em lote

A proposta segue D2, D4 e D5 do pacote. Na triagem de título e resumo, dois
revisores cegos julgam cada obra; divergências, respostas incertas e respostas
diferentes entre tentativas idênticas seguem para o texto completo. O harness
permite até três tentativas contadas e cinco no total por tarefa, retém todas
e não conta falhas de cota, de início ou de cancelamento. Uma atribuição
divergente ou uma cadeia esgotada vai para a fila de Davi, que a encaminha em
lote ao texto completo, como prevê D2. Exclusões concordantes são adotadas por
Davi em lote depois de uma auditoria aleatória estratificada, dimensionada para erro de até 2% com 95%
de confiança quando a amostra não tem erro: cerca de 149 itens por faixa sem
correção para população finita, menos nas faixas pequenas. Um erro devolve a
faixa inteira para revisão. No texto completo, cada exclusão continua sendo
decisão individual de Davi, com volume estimado de 400 a 550 textos avaliados.
A regra de D3, que trata preprint e versão publicada como uma obra quando
autores e ano são compatíveis, entra na deduplicação como adjudicação proposta
por regra e adotada em lote.

O protocolo mantém os identificadores `screener_a` e `screener_b`; a escolha
dos modelos (D4 recomenda `gpt-5.6-sol` e `gpt-5.6-terra`) fica na
configuração dos agentes. A calibração usa 50 obras novas sorteadas da seleção
focada; os 50 casos do v4 passam a ser material de ajuste declarado, e o
histórico de ajuste continua "desconhecido". Os limiares são os do v4: recall
mínimo de 0,95, nenhuma falsa exclusão e auditoria de 20% das obras da
calibração, com o resultado relatado como concordância com referências
adotadas. Se falhar, D5 prevê uma segunda rodada com prompt revisado e novo
sorteio e, depois dela, triagem de Davi em dupla com um revisor de IA, sem
exclusão automática. A ordem fica: calibração, amostra de não capturados,
triagem principal.

A adoção em lote e a auditoria das exclusões concordantes não têm campo
próprio no schema e estão nos critérios de conclusão e nesta nota. O limite de
tentativas e o encaminhamento de atribuições divergentes ou esgotadas já estão
no harness do ramo de integração.

A calibração com referências propostas por IA e adotadas por Davi precisa de
`calibration_reference_policy`, que a proposta ainda não traz. No ramo de
integração, a calibração 5 exige essa política com `source_protocol_sha256`
igual ao hash do protocolo de origem, e a ponte C4v2 só passa de um protocolo
de aquisição para um sucessor aprovado que mude a identidade e essa política.
Como esta revisão é o próprio protocolo da aquisição, o caminho é o mesmo do v3
para o v4: aprovar esta v1, que roda a aquisição, e uma emenda v1.1 que só
acrescente a política, ligada ao hash canônico da v1 e ao da proposta aprovada
em D5. A emenda depende dessa decisão e por isso fica para depois dela.

## Textos completos

Segundo D9, os textos abertos são obtidos automaticamente pelo arXiv e pelo
OpenAlex, Davi fornece pelo acesso institucional os que faltarem, e o restante
recebe `not_retrieved`, relatado como "Reports not retrieved". O JSON declara
essa disposição em `unavailable_disposition`. Ela nunca é atribuída
automaticamente: Davi a adota em lote, por decisão sobre um pedido que lista as
tentativas registradas de cada obra, e só vale para obras em que nenhuma
tentativa obteve bytes. A declaração precisa estar no protocolo da aquisição,
porque a importação de texto completo exige a mesma política no protocolo de
origem e no de destino; como esta revisão tem aquisição própria, a condição é
atendida. Artigos teóricos pagos são os que mais correm o risco de ficar sem
texto.

## Extração, qualidade e síntese

Os seis campos do v4 continuam. Entram onze: tipo de regra de parada e seus
parâmetros, diagnóstico de convergência ou terminação, método de identificação
dos grupos, detalhes de esparsidade, análise de sensibilidade da parada,
hipóteses das garantias analíticas, tipo de garantia (`guarantee_type`),
classe de esparsidade (`network_sparsity_class`), propriedades estruturais da
rede, incluindo modularidade e topologia fixa (`network_structure_flags`), e
tipo de estudo (`study_type`). As três afirmações do candidato dependem dos
valores desses quatro últimos campos. Além disso, o sintetizador nativo procura cada estrato pelo
identificador de um campo de extração, e um estrato sem campo seria ignorado
sem aviso; no plano 8 a síntese é externa, mas os estratos seguem a mesma
regra. Pelo mesmo motivo, o ano de publicação saiu dos estratos e será
tabulado a partir dos metadados.

O estado explícito `not_reported` vale para quinze dos dezessete campos, com
`not_reported_allowed: true`; ficam de fora `model_family` e `study_type`,
porque toda obra incluída tem um modelo e um tipo de evidência. Esse estado não
tem localizador e só pode ser usado quando o texto completo chega como o pool
inteiro em blocos (`whole_text_blocks_v1`), da obtenção automática de acesso
aberto. Mesmo nesse caso ele cobre só a projeção textual: figuras, imagens de
tabelas e material suplementar não são examinados, e um campo relatado só ali
pode sair como `not_reported`. Em pools selecionados, o campo ausente continua
não resolvido. O verificador precisa confirmar, contestar com um trecho do
mesmo pool ou mandar a Davi cada ausência. O literal `not_reported` fica fora
dos valores permitidos, e em `guarantee_type` a falta de garantia é esse mesmo
estado. Os quatro campos do v4 com cardinalidade `zero_or_more` passam a
`one_or_more`, com a ausência sempre explícita. Pelo desenho do ramo, a
produção ainda não roda tarefas desse tipo: falta a autorização que liga cada
papel calibrado ao pool de texto inteiro.

O critério de qualidade novo pergunta se a regra de parada, os parâmetros, o
tratamento das execuções que não pararam e a identificação dos grupos permitem
reproduzir os estados finais declarados. A síntese continua exigindo duas obras
por afirmação, sem metanálise e sem afirmação de novidade. A classe de
esparsidade usa a definição `sparse_network`: grau médio constante quando o
número de agentes cresce, ou menor que 10% do número de agentes.

## Execução no plano 8

O ramo de integração executa a revisão focada com o plano 8, que implementa a
simplificação proposta em D10. As etapas nativas vão da calibração à
verificação da extração; síntese, avaliação de qualidade e revisão adversarial
ficam fora do pipeline e entram por hash no aceite. Isso muda o que o aceite
exige, e o JSON não tem campos para registrar essas regras.

O verificador de extração roda sem calibração, porque o protocolo não a exige.
Davi precisa autorizá-lo por decisão sobre um pedido que fixa o manifesto, o
vínculo do modelo, o plano de auditoria e a base `not_required_by_protocol`, e
o relatório declara o papel como não calibrado. Campos marcados como
verificados só contam como validados depois que Davi audita uma amostra deles,
sorteada com semente e tamanho declarados no plano, e confirma cada item; um
item contestado deixa a execução em `revision_required`. O tamanho e a
semente da amostra ainda não foram escolhidos.

O aceite liga quatro artefatos externos por hash: a avaliação de qualidade, ou
um desvio aprovado por Davi que a dispense; a síntese; a revisão adversarial; e
as disposições de Davi sobre os achados dessa revisão. Os critérios de
qualidade do protocolo, inclusive `quality.termination_reporting`, só entram
por essa avaliação externa. O pipeline confere que os bytes existem, são
distintos e não pertencem à própria execução. O conteúdo fica fora do alcance
dele: não verifica se as afirmações citam extrações validadas nem se o revisor
adversarial trabalhou isolado. O teste das três afirmações do candidato
acontece na síntese externa, e a verificação de que ele seguiu as regras
registradas cabe a Davi no aceite. O relatório nativo mantém avaliação e
síntese como etapas ausentes.

Os limites de processamento de texto completo (tamanho descomprimido, páginas,
saída, memória e tempo) são declarados no plano, dentro dos tetos do contrato,
e fixados no início da execução. Uma rodada de obtenção que use outros limites
precisa registrar o desvio.

## Retirada das propostas v5

A [proposta v5](opinion-dynamics-systematic-map-v5-proposal.json)
(`b8e6d160a270201e3cb7fb7116d3bfcfb626db4cf8ba2278494b4af80469ba4d`) e sua
[revisão editorial](opinion-dynamics-systematic-map-v5-editorial-refresh-proposal.json)
(`4c4eda364e780acd86ce367b1d7b7bd5854f4c3352f6f15a01b735a649a568e5`) só
acrescentam ao v4 a política de metadados para os nove registros sem título do
corpus inteiro. Conferi que nenhum dos nove, Africa Today incluído, está na
seleção da consulta revisada ou no quadro da amostra. Se D1 for aprovado, as
duas propostas são retiradas: arquivos, hashes e notas de revisão ficam como
estão, sem aprovação, e a retirada é registrada na decisão da nova versão e
numa nota acrescentada às duas notas de revisão. As decisões sobre os nove
registros deixam de ser necessárias. Se uma busca suplementar trouxer um
registro sem título, uma emenda posterior pode reaproveitar o desenho da
política v5.

## Vínculos e hashes

| Artefato                                          | SHA-256                                                            |
| ------------------------------------------------- | ------------------------------------------------------------------ |
| Proposta focada, JSON canônico                    | `d971dc37b6097ba70f81584ab236840399ca918753235ec83034a05d41a38966` |
| Proposta focada, bytes do arquivo                 | `0ed494cc9b40740eacb7038b09acbc534214ebc31a5e9dd1f7394178dd53b9d8` |
| Texto da consulta ao corpus, UTF-8                | `3e033bc990fd70e6dc86550ef83f8383dd66de4d2f2d0e42d349318a7d74fb3f` |
| Consulta traduzida do ensaio sem rede             | `0eb85a2061cefeb9066a2fa9ecefaffa1f3c5cdeb3c23848e5c12ae7f8178475` |
| Protocolo v4, JSON canônico                       | `ff8a14178e725983945c049e75181e8eeb1f3cee56a831e714cc78b09245d413` |
| Protocolo v4, bytes do arquivo                    | `390d2bc01520c3422ee37deb76e0302b8d0ce2dc229000c72ca729d56187ed74` |
| Aprovação do v4, bytes do TOML                    | `bc1f33ffa4cdcbe7c1f4bc312e911a0728345b276f728eda8695658097252017` |
| Protocolo v3, JSON canônico (aquisição)           | `fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f` |
| Recibo da aquisição, fixado na consulta           | `5aa52db3b98487a17a5c50d246c23e4c97d611a4a1c6c589119c2cf8d29bc675` |
| Relatório da aquisição, schema 5                  | `edfa48474097d7c81e441fdbe5089a924d514deabbb6baf3bbaf60e0df220a11` |
| Recibo de preparação                              | `fa934b8b065880228373d76040527a76fc7cdced9c92ebb69a31891485ccf4fa` |
| Observações projetadas, lidas pela consulta       | `772afb69e868ef3fc6cf94e79d3c1b422f11f8fba453621c0092fc65028fa5a1` |
| Obras propostas, resultado 3                      | `41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53` |
| Carta do estudo, bytes                            | `5a5da254a85e9f11b0c453e7b5492bdf652f62b5aa452b0b62693d630f29af8f` |
| Pacote de decisão de 18/09, bytes                 | `4609cddde0967044109a1d98b4d8bb0eade02d38e487d26c6dc3307230fa5677` |
| `MANIFEST.sha256` do diretório de desenho         | `a07eaab81eae9ecb45f63c99aae302220cb5e7b5fd4e24710a8f860341611f2d` |
| Rascunho da estratégia, `focused_search_final.py` | `2d563c40d5bd7a4e12ea7527ec41a14e070a2c5d039ac9a3f40b73e0cb2f68e9` |
| Fatos auditados de 17/09                          | `c1d70d0704369f06780adee29bab4c93a222a5a49a20934c009e8a8b8ac1857b` |

Os artefatos do corpus estão no armazenamento privado
`broad-research-20260911/acquisition-v3` e tiveram os hashes conferidos pelo
nome e pelo conteúdo, inclusive o recibo da aquisição, que também consta do
[registro da aquisição](../run-records/2026-09-11-broad-acquisition-v3.md).
A versão anterior desta nota dizia que esse recibo não tinha sido localizado;
ele está no armazenamento, em `sha256/5a/a5/`, e a busca anterior falhou. O
ensaio sem rede está em
`~/.local/state/research-workbench/focused-search-dryrun-20260918/` e o
diretório de desenho em `~/.local/state/research-workbench/review-design-20260918/`.

## Lacunas do schema e dependências

| Necessidade | Situação | Como a proposta lida |
| --- | --- | --- |
| Consulta ao corpus, `not_retrieved` e `not_reported` | Integrados em `feat/focused-review-integration`; ainda fora do ramo principal | JSON nos contratos integrados, validado no commit `3ae4c2b` |
| Tarefas de extração com `not_reported` em produção | Falta ligar cada papel calibrado ao pool de texto inteiro | Descrito na seção de extração; bloqueia só a extração |
| Referências assistidas | A calibração 5 e a ponte C4v2 exigem um sucessor aprovado com a política | Emenda v1.1 depois de D5 |
| Vínculo de derivação | Só `supersedes` | `supersedes` aponta o v4; o código lê esse campo como sucessor direto só nas transições de corpus, metadados e calibração, e a v1.1 usa exatamente essa leitura em relação à v1 |
| Estratégias de encadeamento por rodada | Precisam estar no protocolo antes da execução | Emenda datada por rodada |
| Adoção em lote e auditoria de exclusões concordantes | Sem campos | Critérios de conclusão e esta nota; código de D2 |
| Itens conhecidos e amostra | Sem registro tipado | Definições operacionais com o procedimento completo |
| Regras do plano 8 (verificador, aceite, limites) | Ficam no plano, não no protocolo | Descritas na seção sobre o plano 8 |
| Estratificação por valor | O particionador usa o primeiro estrato cujo campo foi resolvido | Estratos restritos a campos de extração; tabulação por valor na síntese externa |

## O que continua indefinido

As decisões D1 a D11 são de Davi. Além delas, ficam para ele: a escolha das
duas revisões da lista de itens conhecidos; manter ou desfazer os termos
acrescentados nesta revisão, antes de fixar a lista; o gatilho e a alocação da
amostra de não capturados; a trava de 3.000 registros por rodada de
encadeamento; o limite de 10% na definição de rede esparsa; os limiares das
afirmações do candidato (duas obras, metade das que relatam); a execução ou
dispensa das exportações da ACM e do IEEE; o tamanho e a semente da auditoria
dos campos verificados; e os limites de processamento de texto completo do
plano 8.

Ficam fora deste protocolo a proposta de iniciar experimentos antes da síntese
(D11), que exige emenda à carta, e a linha de previsão probabilística do piloto
B, que a revisão focada não cobre. Se D1 for recusado, este rascunho é
descartado e o v4 segue intacto.
