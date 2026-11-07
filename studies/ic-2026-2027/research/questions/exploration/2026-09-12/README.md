# Propostas de pesquisa e venues de referência

A proposta mais concreta para aprofundar é **verificar quando uma simulação declara fragmentação antes de os grupos realmente se separarem**. Ela tem uma pergunta estreita, código de referência identificado e um contraexemplo analítico pequeno. Recomendo começar por sua avaliação de viabilidade e reservar a segunda proposta — previsão probabilística de opiniões — como alternativa com maior dependência de reprodução e dados.

Esta é uma recomendação exploratória para a IC. Nenhuma pergunta final, venue, exclusão bibliográfica ou síntese científica foi aceita. A entrega organiza duas propostas fundamentadas, seus testes iniciais e cinco venues de referência. O panorama amplo e a busca executada sustentam a navegação; a triagem e a síntese formais continuam nas etapas descritas em [READINESS](../../../literature/READINESS.md).

## Comparação das propostas

| Proposta | Pergunta concreta | Por que merece avaliação | Principal risco |
| --- | --- | --- | --- |
| **A — Certificação da fragmentação** | O contraste entre redes esparsas e densas sob exposição adaptativa permanece quando o critério de parada garante que os componentes não voltarão a interagir? | Há uma falha de suficiência demonstrável num microcaso, um antecedente recente e uma implementação pública com licença MIT. | O caso pode ser raro ou não alterar resultados relevantes; uma correção técnica isolada pode ser insuficiente para um artigo. |
| **B — Previsão probabilística e congelamento** | A preferência por modelos que quase não mudam opiniões depende do alvo de avaliação, depois de separar aleatoriedade da dinâmica e amostragem dos participantes? | Um benchmark recente já observa congelamento; a distinção entre previsão central e distribuição preditiva permite um teste específico. | O contraste pode não produzir resultado novo; código do benchmark, acesso ao ESS e modelo de observação precisam ser resolvidos. |

As duas têm hipóteses que podem falhar. A escolha entre elas deve considerar os resultados do primeiro teste, a leitura dos antecedentes e a síntese do estudo, e não a promessa de um resultado positivo.

## Proposta A: quando os grupos estão realmente separados?

Em modelos de confiança limitada, pessoas simuladas se aproximam quando suas posições estão suficientemente próximas. A exposição adaptativa acrescenta pesos às ligações, alterando a chance de uma interação. O preprint de Thompsky, Wu, Porter e Luo usa esse mecanismo e compara diferentes redes. Seu critério numérico encerra a simulação quando a diferença interna de opiniões de cada componente efetivo fica abaixo da tolerância. O teorema que identifica esses componentes como grupos definitivos exige uma rede completa e tolerância menor que o limite de confiança.[^a]

Isso abre uma pergunta verificável sobre redes esparsas: uma ligação hoje inativa pode voltar a permitir influência depois que os agentes se aproximam de outros vizinhos? A conta abaixo demonstra que sim em um estado construído. Ela não mede a frequência desse estado nem reproduz as simulações publicadas.

Considere quatro agentes e apenas três ligações: A–B, C–D e A–D. A confiança é 0,1; a tolerância para parada é 0,01. Uma interação permitida substitui as opiniões do par pela média.

| Momento | A | B | C | D | Situação |
| --- | ---: | ---: | ---: | ---: | --- |
| Inicial | 0 | 0,009 | 0,096 | 0,105 | A–B e C–D são dois componentes efetivos, ambos com diferença interna 0,009; o critério aceita parada. |
| Depois de A–B interagirem | 0,0045 | 0,0045 | 0,096 | 0,105 | A–D ainda está fora da confiança. |
| Depois de C–D interagirem | 0,0045 | 0,0045 | 0,1005 | 0,1005 | A–D tem diferença 0,096 e pode voltar a transmitir influência; os quatro agentes estão conectados no grafo efetivo. |

A aritmética foi executada com frações exatas, preservando entradas, parâmetros e trajetória no [registro do contraexemplo](stopping-counterexample.json). O que foi demonstrado é a insuficiência do teste de diâmetro como garantia geral para uma rede esparsa. Isso não refuta o teorema para redes completas, não afirma que a rotina externa verifica parada no instante inicial e não demonstra que o resultado agregado do artigo mudará. A conta segue a atualização simétrica do código publicado; uma inconsistência de sinal nas fórmulas do manuscrito está documentada no memo mecanístico e na revisão independente.

Uma condição complementar candidata usa os intervalos de opiniões dos componentes. Se os intervalos permanecem separados por pelo menos o limite de confiança em toda ligação-base entre componentes, as médias internas não conseguem criar a primeira interação externa. Esse argumento depende de atualização convexa, confiança fixa e rede-base fixa; ruído, repulsão, confiança adaptativa e mudança de ligações exigem outra análise. A condição certifica separação, mas pode ser conservadora e não garante um tempo de parada finito em todos os casos.

**Diferença em relação ao que já existe.** Sîrbu et al. já estudam viés, fragmentação e convergência lenta; também distinguem tipos de contato na contagem de tempo. Kan et al. já tratam redes adaptativas e tamanho finito; Li et al. já adaptam confiança; Hegselmann já investiga dificuldades numéricas. Portanto, acrescentar topologias, variar precisão ou contar contatos ativos não delimita novidade. A contribuição possível é demonstrar onde uma classificação de fragmentação é confiável e se isso muda uma conclusão sobre o mecanismo de exposição. A busca de antecedentes do certificado continua necessária.[^b][^c][^d][^e]

**Teste inicial proposto.** Reproduzir um controle numérico limitado do trabalho de 2026, com DW uniforme e DW com pesos adaptativos. Para cada trajetória, registrar o momento da parada aproximada e continuar a mesma sequência de eventos até o certificado ou um limite de execução explícito. Começar com rede completa, rede esparsa e rede modular; variar tamanho a grau constante separadamente de densidade a tamanho constante.

Os resultados principais seriam a frequência de partições que mudam depois da parada, a diferença pareada no tamanho e número dos grupos e o tempo até a certificação. Trajetórias que atingirem o orçamento permanecem censuradas; não contam automaticamente como fragmentadas. A comparação precisa preservar a unidade de réplica: semente, realização da rede e condição inicial.

**Regra de investimento.** Um piloto de aproximadamente uma semana é uma estimativa de planejamento, sem benchmark realizado. Deve começar com dez execuções curtas para medir custo e dimensionar um lote pequeno de trajetórias pareadas. Só ampliar se o problema aparecer além do exemplo construído e alterar um contraste cientificamente interpretável, ou delimitar uma região de confiabilidade útil. Se a diferença desaparecer sob uma tolerância justificável, já estiver resolvida na literatura ou for apenas um caso raro sem consequência, preservar a reprodução e abandonar essa linha como tema principal. O [memo mecanístico](mechanism-evidence.md) detalha controles, condições matemáticas e critérios candidatos.

## Proposta B: prever uma distribuição, incluindo sua incerteza

Moor-Smith e Carpentras comparam quatro modelos, calibram em observações anteriores e avaliam observações posteriores. Eles já encontram situações em que o ajuste favorece parâmetros que praticamente congelam as opiniões. Seu objetivo de calibração faz média da distância entre cada realização simulada e a distribuição observada; o texto já reconhece dificuldades ligadas à variabilidade das saídas.[^f]

A proposta investiga outro alvo: a distribuição preditiva dos **histogramas que poderíamos observar** numa próxima onda. Ela inclui duas fontes de variação: diferentes trajetórias da população e diferentes amostras de participantes. Uma população que não muda ainda produz pesquisas amostrais diferentes. Esse mesmo processo de observação precisa ser aplicado ao baseline sem mudança.

O desenho compara três avaliações sobre as mesmas previsões: distância média por realização, distância de uma previsão central explicitamente definida e um score probabilístico do ensemble de histogramas. O energy score é uma ferramenta estatística já existente para essa terceira avaliação, e não uma técnica nova proposta pela IC.[^g] Primeiro se mantém o ajuste e muda apenas a avaliação; em uma etapa separada, cada perda pode orientar o ajuste, com orçamento e informação iguais.

O teste proposto é de um passo: todos os braços recebem a mesma distribuição observada na onda anterior e preveem o mesmo histograma na onda seguinte. Categorias, amostragem, intervalo temporal e informação disponível são comuns. Comparam-se as ordenações dos modelos dentro de cada score; valores numéricos de perdas diferentes não são comparados diretamente. A especificação do [memo empírico](empirical-evidence.md) fixa esse alvo e o estimador do score, para que uma diferença não seja consequência de dar mais informação a um braço.

**Hipótese verificável.** Em determinadas combinações de variabilidade, espaçamento temporal e amostragem, uma avaliação por realização pode preferir uma dinâmica quase estática enquanto uma avaliação da distribuição preditiva distingue o gerador dinâmico. A hipótese rival é que as avaliações concordam ou que o ganho desaparece com mais observações. Trocar o alvo não torna a métrica anterior errada, e um bom score não identifica automaticamente parâmetros psicológicos ou influência causal.

**Teste inicial proposto.** Começar com geradores sintéticos conhecidos: um dinâmico, um realmente sem mudança e um com drift exógeno. Usar parâmetros conhecidos como controle e parâmetros estimados como problema separado. Preservar treino, validação, sementes e informação disponível. Só depois tentar transporte para ondas futuras do ESS, respeitando escala, pesos, desenho amostral e mudanças de coleta.

**Regra de investimento.** O teste precisa reconhecer tanto dinâmica quando há informação suficiente quanto ausência de dinâmica nos controles. Se preferir mudança sob um gerador constante, houver vazamento ou a diferença desaparecer com maior precisão Monte Carlo, não prosseguir para conclusões empíricas. Resultado favorável em dados sintéticos apenas justificaria a etapa seguinte. A transferência para o ESS pode falhar e deve ser relatada como tal.

O risco de acesso é real. O benchmark principal não teve um repositório de código identificado nas fontes consultadas; o portal ESS falhou nesta verificação. Um estudo auxiliar de inferência tem um depósito publicado vazio e um sucessor com arquivos; o sucessor foi inspecionado, mas não executado. Ele usa Python/TensorFlow e Julia e não substitui o benchmark principal. O [memo empírico](empirical-evidence.md) registra oito antecedentes, os alvos matemáticos, as licenças e as dependências. A implementação inicial pode ser pequena e sintética; a viabilidade da proposta completa ainda precisa ser demonstrada.

## Por que não desenvolver uma terceira proposta com LLMs agora

A leitura dessa linha encontrou antecedentes diretamente sobre formato, memória, sensibilidade a instruções, validação com participantes e transferência de uma medida local de influência para grupos. O apêndice de EASE já retira lembretes da opinião anterior para testar seu efeito; DEBATE já inclui referências escalares e verificações de convergência; Yang já mede influência e limita sua transferência entre modalidades.[^h][^i][^j]

Esses resultados tornam fracas as propostas genéricas que estavam ao alcance da primeira leitura. Não demonstram que a área esteja esgotada. A recomendação é manter a linha no mapa e retomá-la se surgir uma pergunta mais específica, com dados e custo verificados. Os [nove antecedentes de LLMs](llm-evidence.md) preservam manifestações, extensão da leitura e limites. Não houve execução de modelos de linguagem ou aquisição de dados de participantes.

## Cinco venues para orientar a pesquisa

A lista é provisória e considera as duas propostas e alternativas de comunicação computacional. As condições abaixo são referências editoriais, não adequação final ao artigo ou estimativas de aceitação. As cinco rotas ainda têm **participação remota `unknown` na escala do protocolo**: há etapas eletrônicas documentadas, mas a verificação das obrigações autorais completas permanece aberta. Logo, o atendimento à preferência por níveis 2–5 ainda precisa ser confirmado.

| Venue | Relação com as propostas | Condição prática já verificada |
| --- | --- | --- |
| **JASSS** | Referência inicial para simulação social, validade e reprodutibilidade. Pode servir a A ou B se o resultado esclarecer o processo social modelado. | O guia solicita apoio de £800/€1.000/US$1.300; obrigatoriedade não ficou inequívoca. Não foi classificada como gratuita. |
| **Journal of Computational Social Science** | Alternativa para comparação de modelos e validação computacional orientada a uma pergunta social. | Rota de assinatura sem APC; OA opcional com cobrança. Ausência de APC não certifica ausência de todo encargo possível. |
| **Physical Review E** | Mais relevante para A se houver resultado mecanístico ou matemático acompanhado de evidência numérica convincente. | APC opcional de US$2.910 na tabela de 2026; demais condições dependem da rota e opções de produção. |
| **Computational Communication Research** | Alternativa se o recorte esclarecer exposição, influência ou comunicação. A ligação é menos direta para um resultado puramente numérico. | Política declara ausência de APC. Um precedente de 2026 usa redes de agentes LLM para estudar influência. |
| **PLOS Complex Systems** | Possível quando a conclusão tiver relevância transversal para sistemas complexos. | APC-base observado de US$3.165; regras de redução conflitantes foram preservadas, sem desconto presumido. |

Escopos, exemplos publicados, taxas, regras e fontes oficiais estão no [memorando de venues](venue-evidence.md). **JASSS é minha referência inicial de leitura editorial; PRE ganha prioridade se A produzir uma contribuição matemática e mecanística forte.** JCSS oferece uma alternativa abrangente. A escolha principal e a reserva ficam para quando existirem contribuição e viabilidade demonstradas.

IEEE TCSS permanece como contraponto relevante; sua posição depende da contribuição em sistemas computacionais e da confirmação das tarifas vigentes. ACM e ICML continuam no inventário, sem usar a marca como substituta de aderência científica. Nenhuma chamada ou regra de 2026 foi transferida para uma edição futura.

## O que esta exploração cobriu

O trabalho partiu do inventário de 235 venues, das checagens prévias e do mapa exploratório com onze famílias/eixos. A busca de propostas concentrou-se em validação empírica, mecanismos de exposição e coletivos de linguagem porque oferecem comparações verificáveis e baselines identificáveis. As demais famílias permaneceram no panorama:

| Família ou eixo | Papel nesta exploração |
| --- | --- |
| Médias de influência e convicção | Referências e baselines; pergunta nova não estabelecida. |
| Aprendizado social e verdade externa | Exige definir sinal e estado verificável, além do acordo entre agentes; não foi aprofundado. |
| Confiança limitada | Base comum das duas propostas. |
| Imitação e maioria | Mantidas para comparação futura de famílias, sem pergunta específica escolhida. |
| Cultura e convenções | Conectadas à leitura de coletivos artificiais, com domínio conceitual distinto. |
| Crenças multidimensionais | Requerem medidas e dados adequados; não priorizadas nesta rodada. |
| Repulsão e polarização | Antecedentes empíricos e controles conceituais; fora das hipóteses do certificado A. |
| Redes adaptativas e exposição | Núcleo da proposta A; topologia-base fixa no primeiro desenho. |
| Interações de ordem superior | Antecedente linear/não linear verificado; nenhuma pergunta adicional mais forte foi delimitada. |
| Formulações cinéticas | Mantidas no mapa; aprofundamento matemático não realizado nesta rodada. |
| Dados e modelos de linguagem | Dados e observação sustentam B; nove antecedentes limitaram os recortes imediatos com LLMs. |

A tabela é organização editorial desta rodada, não uma taxonomia aceita ou justificativa de exclusão bibliográfica. Não se concluiu que essas onze entradas esgotam a área.

Foram examinados **25 trabalhos centrais: oito empíricos, oito mecanísticos e nove de LLMs**, com extensão de leitura registrada nos respectivos memos. Outros artigos, fontes metodológicas e precedentes de venues são identificados separadamente. O [cruzamento por identificadores](corpus-crosswalk.json) encontrou correspondência para 23 dos 25 nas propostas bibliográficas existentes. Ju et al. e EASE não tiveram correspondência pelos identificadores nem pelas expressões de título verificadas; ficam como leads suplementares a incorporar pelo procedimento apropriado, sem alterar a aquisição encerrada.

A [navegação por títulos](corpus-navigation.json) percorreu todos os 46.391 títulos propostos com três filtros lexicais, retornando 104, 139 e 225 propostas. Esses números incluem duplicidades pendentes e resultados irrelevantes; não são trabalhos elegíveis ou uma triagem da área. O cruzamento de 25 leituras foi construído depois da aquisição e não mede recall independente. A descoberta de dois leads adicionais reforça a necessidade das buscas suplementares.

## Viabilidade, sequência e decisões pendentes

O inventário local confirmou Apple M5, dez CPUs lógicas e 16 GiB de memória. Não foram medidos tempos de simulação, inferência ou consumo dos modelos; o VPS e o orçamento de publicação seguem sem inventário fechado. A meta de 31/10/2026 registrada na carta é para pesquisa e manuscrito pronto, sem promessa de aceite ou publicação.

O próximo avanço científico é usar estas propostas para orientar a leitura aprofundada e a avaliação inicial, mantendo duas frentes explícitas. Na revisão, faltam resolução de identidades/metadados, referências humanas de calibração, triagem e auditorias, textos completos, extração e síntese. O [formulário local](http://127.0.0.1:8767/) contém 50 casos preparatórios; decisões produzidas por agentes não substituem as referências de Davi. A autorização para continuar permitiu preparar e verificar este material, mas não forneceu essas decisões.

Na preparação da pesquisa, A merece o primeiro esforço limitado: verificar os antecedentes do certificado, congelar a especificação do piloto e confirmar reprodução/custo. O microcaso já executado é apenas uma verificação analítica exploratória. Simulações amplas, comparação de resultados publicados, aprovação de protocolo experimental e seleção final da pergunta ainda não ocorreram. Se A não passar os critérios de relevância, B é a alternativa a avaliar; a existência de dois caminhos evita comprometer todo o prazo com uma lacuna que pode desaparecer.

## Fontes e documentação de apoio

[^a]: L. Thompsky, Y. Wu, M. A. Porter e Y. Luo. *A Bounded-Confidence Model of Opinion Dynamics with Adaptive Interaction Probabilities*, preprint, v2, maio de 2026. [Seção V.2 e teorema 4](https://arxiv.org/html/2605.20418v2). A derivação do contraexemplo neste relatório é independente; nenhum resultado agregado foi reproduzido.
[^b]: A. Sîrbu et al. *Algorithmic bias amplifies opinion fragmentation and polarization: A bounded confidence model*. PLOS ONE, 2019. [Artigo](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213246).
[^c]: U. Kan, Y. Feng e M. A. Porter. *An Adaptive Bounded-Confidence Model of Opinion Dynamics on Networks*. JCN, 2023. [Manifestação consultada](https://arxiv.org/html/2112.05856v3).
[^d]: G. J. Li, Y. Luo e M. A. Porter. *Bounded-Confidence Models of Opinion Dynamics with Adaptive Confidence Bounds*. SIADS, 2025. [Manifestação consultada](https://arxiv.org/html/2303.07563v3).
[^e]: R. Hegselmann. *Bounded Confidence Revisited: What We Overlooked, Underestimated, and Got Wrong*. JASSS, 2023. [Artigo](https://www.jasss.org/26/4/11.html).
[^f]: Samuel Moor-Smith e Dino Carpentras. *Testing the validity of multiple opinion dynamics models*, preprint de 2026, apresentado como long paper SSC 2025. [Métodos e resultados](https://arxiv.org/html/2602.00876v1).
[^g]: T. Gneiting e A. E. Raftery. *Strictly Proper Scoring Rules, Prediction, and Estimation*. JASA, 2007. [Texto dos autores](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf), seção 4.3.
[^h]: S. Sarangi et al. *EASE Configuration Facilitates A Reproducible Science of LLM Social Simulations*, preprint, 2026. [PDF](https://arxiv.org/pdf/2605.30258), apêndice C.3.
[^i]: Y.-S. Chuang et al. *DEBATE: A Large-Scale Benchmark for Evaluating Opinion Dynamics in Role-Playing LLM Agents*, preprint, versão 6 de maio de 2026. [Texto](https://arxiv.org/html/2510.25110v6).
[^j]: D. Yang. *When Is Emergent Consensus Real? A Measured Coupling Gain and a Validity Diagnostic for LLM Agent Societies*, preprint, junho de 2026. [Texto](https://arxiv.org/html/2606.22203v1).

As notas [empírica](empirical-evidence.md), [mecanística](mechanism-evidence.md), [LLM](llm-evidence.md) e de [venues](venue-evidence.md) contêm as demais fontes, consultas literais e limites de leitura. O [pacote de verificação](review-input.md) separa afirmações e desenhos da recomendação de prioridade. A [revisão independente](independent-review.md) confirmou os cálculos e apontou duas correções de especificação, registradas na [resposta à revisão](review-response.md) e [verificadas pelo revisor](review-followup.md) em nível de proposta pré-piloto. O [registro de validação](validation.json) identifica os arquivos e as verificações desta entrega. Esta documentação é exploratória e não substitui os contratos, os registros de revisão ou os aceites científicos do estudo.
