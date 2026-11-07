# Pistas empíricas: observação e identificabilidade

24/09/2026. Memo exploratório para o mapa amplo da IC. **LEADS, não síntese
aceita, questão escolhida, protocolo ou referências canônicas.** A novidade
abaixo é uma hipótese a testar contra a revisão sistemática ainda pendente.
Nenhum dado humano foi adquirido, nenhum modelo foi executado e nenhum resultado
novo foi medido nesta investigação.

Partida: [levantamento de 12/09](../2026-09-12/empirical-evidence.md),
[mapa de afirmações](../../exploratory-claim-map.md) e
[resultado do piloto B](../../../../experiments/exploratory/probabilistic-forecast-pilot-v1/README.md).
O piloto B completou seus lotes e nenhuma das oito células dinâmicas passou o
critério central em qualquer lote. Sua população era reinicializada por onda;
os seus scores não identificam opiniões latentes, indivíduos ou influência.
As pistas seguintes exigem **outro objeto de inferência e justificativa própria**,
não uma expansão de parâmetros para procurar o contraste ausente.

## Antecedentes diretamente conferidos

Leitura em 24/09: textos nas URLs abaixo, com foco nas seções indicadas;
não houve reprodução, exame exaustivo das referências ou aceitação científica.
Preprint e publicação da mesma obra não são contados duas vezes.

| Fonte primária e profundidade | Resultado que limita estas pistas |
| --- | --- |
| [Gestefeld e Lorenz, JASSS 2023](https://www.jasss.org/26/4/9.html), resumo, métodos, resultados ESS/SHP e discussão | Ajustam um modelo a 1.235 distribuições ESS e também a transições anuais individuais do Swiss Household Panel. Logo, combinar marginais e transições já tem antecedente; o ajuste ainda falha em extremos e opiniões neutras. |
| [Banisch e Shamon, JASSS 2024](https://www.jasss.org/27/1/17.html), resumo, calibração micro, comparação macro e discussão | Calibração de processamento enviesado por mudança individual é compatível com distribuições observadas em seis temas de energia. Consistência micro–macro, sozinha, não é uma lacuna nova. |
| [Lenti, Monti e De Francisci Morales, preprint v2](https://arxiv.org/html/2310.02766v2), §§3–5 | Comparam máxima verossimilhança e momentos simulados em BCM estocástico, incluindo interações parcialmente observadas e opiniões medidas por proxies ruidosos. Seu alvo é recuperar parâmetro em dados gerados pelo próprio modelo, não validar um mecanismo em survey humano. |
| [Borile et al., preprint v1](https://arxiv.org/html/2506.11751v1), §§2–5 | Mesmo com interações microscópicas observadas, o estimador do limite de confiança tem viés de amostra pequena, a taxa de convergência tem viés persistente e há regiões com dificuldade de identificação conjunta. Não se pode alegar que adicionar um painel torna parâmetros automaticamente identificáveis. |
| [Tang, Snijders e Flache, JASSS 2025](https://www.jasss.org/28/1/2.html), resumo, modelo, análise empírica e discussão | Em redes longitudinais de adolescentes, distinguem assimilação, influência negativa e confiança limitada com SAOM; há suporte para as duas primeiras e pouco para a última naquele caso. Discriminar esses mecanismos em painel e rede já foi feito. |
| [Moor-Smith e Carpentras, preprint v1 2026](https://arxiv.org/html/2602.00876v1), §§2–5 | Calibram no passado e testam quatro modelos em ondas futuras ESS. Os modelos em geral não superam a cópia da onda anterior e podem aprender a congelar. Benchmark temporal genérico em ESS também já está ocupado. |

Como contexto de acesso, a [ESS descreve o CRONOS-2](https://www.europeansocialsurvey.org/methodology/methodological-research/modes-data-collection/cronos)
como painel ligado à rodada 10; o [guia oficial](https://www.europeansocialsurvey.org/sites/default/files/2023-07/CRONOS2_user_guide_e01_0.pdf)
lista arquivo integrado e ondas com arquivos CSV, mas **não confirma aqui**
repetição do mesmo item de opinião com janela útil. A [licença ESS](https://www.europeansocialsurvey.org/contact/disclaimer)
é CC BY-NC-SA 4.0 para dados. Disponibilidade descrita não prova acesso
funcional, licença de código de terceiros, comparabilidade de itens ou
aprovação ética para a análise proposta.

## Lead 1 — quando a observação distingue mecanismos?

**Pergunta falsificável.** Nas mesmas trajetórias e janelas, com máscaras de
observação predefinidas e canal de erro fixo, qual informação adicional quebra
a equivalência observacional entre duas regras concorrentes: histogramas de
amostras independentes, transições da mesma pessoa ou interações com a fonte
de opinião identificada, condicionado a tamanho amostral e custo de medição?

- **Anterior mais próximo:** Lenti testa níveis de observação para recuperar
  parâmetro do BCM; Tang já distingue influência negativa de confiança
  limitada em rede longitudinal real; Gestefeld–Lorenz usam ESS e SHP.
- **Novidade precisamente não provada:** medir, para um par de mecanismos e
  **o mesmo processo de observação**, o ganho incremental de cada tipo de
  dado na discriminação fora da amostra; o resultado pode ser uma fronteira de
  impossibilidade prática, não a vitória de um mecanismo. Uma busca mais
  completa pode encontrar esse contraste já publicado.
- **Hipótese / nula:** transições individuais elevam discriminação acima de
  marginais apenas; vínculos/exposição observados elevam-na novamente.
  Nula: o ganho fora da amostra é zero ou menor que a variação entre
  réplicas, inclusive após controle de erro de medida e redes homofílicas.
- **Unidade:** no ensaio sintético, conjunto de trajetórias gerado por uma
  combinação de mecanismo, rede e canal de observação; previsões avaliadas
  em trajetórias independentes. Em dados humanos, transição pessoa–item–onda
  ou díade–intervalo quando a exposição for de fato medida. Nunca tratar
  ondas ou pessoas dependentes como réplicas de gerador.
- **Comparação mínima:** dois mecanismos completamente especificados com
  predições diferentes em pelo menos algum regime; baseline sem influência
  com persistência individual; baseline estatístico de transição, além de
  frequências marginais. Aplicar máscaras predefinidas para os três níveis
  às mesmas trajetórias, pessoas e janelas, conservando o canal de erro.
  Dentro de cada nível, os mecanismos recebem os mesmos dados, treino,
  orçamento e validação. Reportar ganho condicionado ao número de pessoas,
  ondas, medidas e custo de obtê-las; particionar por trajetória e estimar
  erro de seleção sob ambos os geradores. Não converter melhor score em
  identificação causal.
- **Dados e bloqueios:** fase lógica/sintética usa apenas regras e fontes
  abertas, mas reimplementar deve ser declarado e conferido. ESS comum tem
  cortes repetidos, não trajetórias das mesmas pessoas. CRONOS-2 é uma pista
  de painel a verificar por item/onda/peso/atrito; não oferece por si só
  rede de exposição. Dados de Tang sobre adolescentes exigem checagem de
  acesso e de ética; nenhuma aquisição está prevista aqui.
- **Falsificação barata:** antes de simular, procurar um par de parâmetros
  cuja lei de histogramas seja igual ou quase igual e cujas leis de
  transição divirjam; demonstrar isso em um caso pequeno por enumeração ou
  cálculo. Abandonar como contribuição se a diferença desaparecer com o
  mesmo canal de medida, se antecedente idêntico for encontrado ou se a
  informação adicional pressuposta não existir em dados permissíveis.
- **Gatilho do Owner:** escolher mecanismos/observáveis e reivindicação
  científica após síntese; aprovar desenho e critério antes de campanha;
  resolver acesso, licença e procedimento ético antes de dados de pessoas.

## Lead 2 — opinião latente ou resposta de questionário?

**Pergunta falsificável.** Em painéis categóricos, uma regra de mudança de
opinião continua distinguível de persistência depois de modelar explicitamente
o mecanismo que transforma opinião latente em resposta observada e os efeitos
de seleção/atrito entre ondas?

- **Anterior mais próximo:** Lenti já estuda proxies ruidosos em BCM
  sintético; Gestefeld–Lorenz calibram transições SHP; Banisch–Shamon
  ligam mudanças experimentais a distribuições. Nenhum desses resultados
  autoriza ler resposta ordinal como opinião contínua observada sem erro.
- **Novidade precisamente não provada:** teste de sensibilidade ou limites de
  identificação para **ranking entre mecanismo dinâmico e persistência**
  quando matriz de resposta, arredondamento e atrito são incluídos no mesmo
  modelo de observação de painel. Não reivindicar novo estimador genérico;
  pode existir antecedente direto fora destas seis leituras.
- **Hipótese / nula:** parte da aparente mudança e da preferência de modelo
  sob observação perfeita é explicada por erro de resposta/atrito; ranking
  fora da amostra muda em uma região conjunta dos dois canais delimitada por
  âncoras independentes. Nula: ranking e previsões de transição permanecem
  estáveis em toda essa região conjunta, inclusive se erro e atrito dependerem
  do estado latente e da onda.
- **Unidade:** resposta da mesma pessoa ao mesmo item em duas ondas, com
  identificação preservada apenas no ambiente autorizado; matrizes de
  transição e perdas em ondas futuras são agregados derivados, não novas
  observações independentes. Estado latente é variável de modelo, não dado.
- **Comparação mínima:** persistência latente + canal de resposta, modelo
  dinâmico + **o mesmo** canal, e baseline Markov observado sem interpretação
  mecanística; treino separado de ondas posteriores, mesmo tratamento de
  pesos, atrito e itens. Declarar antes quais parâmetros de resposta e
  seleção vêm de teste–reteste, validação de respostas ou outra fonte
  independente; avaliar uma região **conjunta** plausível, sem variar só
  erro ou só atrito. Ajustá-los livremente dos mesmos pares pode tornar
  dinâmica e persistência observacionalmente indistinguíveis.
- **Dados e bloqueios:** primeiro verificar metadados de CRONOS-2 e SHP:
  item repetido, identidade longitudinal, modo, pesos, ausência e licença.
  O guia CRONOS-2 não resolve essa verificação. Se só houver cortes ESS,
  não inferir matriz individual. Consentimento, proteção de dados e direito
  de redistribuição requerem conferência antes de qualquer aquisição.
- **Falsificação barata:** construir contraexemplo analítico com duas
  matrizes latentes distintas e o mesmo produto observável sob erro de
  classificação e atrito; depois verificar se âncoras independentes podem
  limitar ambos. Sem âncoras, relatar somente o limite/contraexemplo, sem
  ranking identificado ou inferência de mecanismo;
  abandonar novidade se literatura já resolver exatamente a sensibilidade
  proposta. Nenhuma nova simulação ou acesso é necessário para este passo.
- **Gatilho do Owner:** aceitar definição de opinião/medida e nível de
  afirmação, aprovar a escolha de painel e registro do teste; decidir sobre
  ética/acesso antes de microdados e sobre continuação se só limites
  negativos forem demonstráveis.

**Leitura comparativa provisória.** Lead 1 tem uma pergunta de desenho de
observação mais nítida, mas Tang é contraexemplo forte à novidade ampla e
dados com exposição real podem ser inacessíveis. Lead 2 pode começar com
uma prova pequena sem dados, mas precisa de informação independente sobre
erro de resposta para concluir algo empírico. Ambos continuam condicionados
à síntese aceita e à decisão do Research Owner; nenhum reabre o piloto B.
