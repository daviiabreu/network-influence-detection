# Avaliação de extração com paráfrases

Nota de pesquisa de 15/09/2026. Recomendação metodológica, sem alteração de
protocolo, execução de modelos ou adjudicação de respostas reais. Foram
consultadas as cinco fontes primárias abaixo e o código no commit
`0f309ce0ffc8fdc16e3089577cabba38609e23c2`.

Recomendamos manter a validação automática de estrutura e origem dos trechos
e acrescentar adjudicação explícita da fidelidade pelo responsável, por campo.
É a menor mudança defensável para esta calibração: o
[processo vigente](../../../../../../docs/process/systematic-review-calibration.md)
já exige auditoria de todos os casos de extração. Um novo modelo avaliador
exigiria demonstrar sua própria confiabilidade neste domínio.

No código inspecionado, `measure_calibration` compara o JSON canônico de
`values` e `unresolved_fields` com a referência inteira, incluindo os
localizadores contidos em cada valor. Assim, outra redação ou outro trecho de
suporte produz `extraction_reference_mismatch` mesmo quando pode preservar o
conteúdo. Isso é uma propriedade observada da implementação; não foi
executada uma calibração científica para estimar sua frequência. O
[protocolo v4](../../protocol/opinion-dynamics-systematic-map-v4.json)
define seis campos, incluindo texto livre e categorias sem vocabulário
fechado. A igualdade textual não verifica, por si, a correção científica da
referência.

O que as fontes sustentam:

- O [Cochrane Handbook, seções 5.5.2 e 5.5.5](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-05)
  recomenda extração independente por mais de uma pessoa para reduzir erros,
  regra previamente definida para divergências e preservação dos dados
  originalmente extraídos junto da resolução. Adotamos essas orientações
  sobre rastreabilidade; a revisão de uma proposta de IA por uma pessoa não
  equivale a duas extrações humanas independentes. As exigências clínicas
  específicas não são automaticamente requisitos deste estudo matemático.
- O [PRISMA 2020, item 9](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf)
  pede informar revisores, independência, resolução de divergências e, quando
  houver automação, seu uso, treinamento e validação contra extrações
  incorretas. Trata-se de orientação de relato, não de certificação de um
  comparador ou de um limiar de aprovação.
- [FActScore, Min et al. (2023)](https://aclanthology.org/2023.emnlp-main.741/)
  decompõe a geração em afirmações atômicas e mede a proporção sustentada por
  uma fonte confiável. Aproveitamos a distinção entre afirmações sustentadas e
  não sustentadas. A avaliação original de biografias não valida o método
  automaticamente para extração científica. Por nossa interpretação da
  métrica, precisão das afirmações produzidas também precisa ser acompanhada
  de completude: omitir uma limitação não cria uma afirmação falsa, mas pode
  tornar a extração inadequada.
- [BERTScore, Zhang et al. (2020)](https://arxiv.org/abs/1904.09675v3)
  compara tokens por embeddings contextuais e avalia sua associação com
  julgamentos humanos em geração de texto. Nossa conclusão é que essa
  similaridade pode ajudar a localizar diferenças, mas não demonstra que o
  PDF sustenta uma afirmação, um número ou uma interpretação causal.
- [Zheng et al. (2023), LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)
  encontra concordância útil com preferências humanas e também vieses de
  posição, verbosidade e favorecimento próprio. O estudo avalia respostas de
  assistentes; não estabelece a exatidão de um juiz para os seis campos desta
  pesquisa. Aplicá-lo como autoridade acrescentaria uma hipótese a validar.

A comparação e a regra operacional seguintes são recomendações nossas,
derivadas dessas fontes e das necessidades locais:

| Alternativa | Benefício | Limite nesta calibração |
| --- | --- | --- |
| Igualdade exata | Determinística, reproduzível e simples | Confunde diferenças de expressão e localizador com diferenças científicas |
| Embeddings ou similaridade textual | Reconhecem proximidade entre paráfrases | Um escore não demonstra suporte, ausência de contradição nem completude |
| LLM avaliador | Pode explicar divergências e considerar a fonte | Acrescenta erros, vieses e necessidade de calibração do avaliador |
| Adjudicação explícita do responsável | Examina fonte e significado; aproveita a auditoria existente | Custa leitura humana e mantém risco de ancoragem na referência assistida |

Para cada campo, propomos registrar separadamente suporte na fonte,
completude e divergências substantivas. Uma paráfrase só seria equivalente
quando mantivesse as informações exigidas pelo campo, as ressalvas, as
negações e o alcance das conclusões, sem acrescentar afirmações sem suporte.
Ter um valor em cada campo não basta para demonstrar completude.

Números devem preservar valor, sinal, unidade, população, denominador e
intervalo temporal quando aplicáveis; conversões precisam de transformação
documentada, sem tolerância numérica inventada depois da resposta. Uma medida
indireta deve continuar identificada como aproximação, sem virar observação
direta do construto. Como exemplo hipotético, “sentimento dos posts usado
como aproximação de opinião” não é equivalente a “crenças individuais
medidas diretamente”.

Um localizador alternativo pode ser admissível se o validador reproduzir o
trecho na mesma fonte autorizada e a leitura mostrar suporte ao conteúdo
atribuído. A existência dos bytes confirma a origem; o responsável avalia o
significado. Ausência de informação, ambiguidade, contradição ou campo não
resolvido devem continuar explícitos. Uma referência assistida também pode
estar errada: nesse caso, registrar revisão da referência e sua evidência em
um sucessor, sem ajustar o original silenciosamente para coincidir com a
saída.

A decisão proposta teria, para cada campo, um resultado como equivalente,
divergência substantiva ou pendente, acompanhado de justificativa e trechos.
Sua vinculação deve identificar protocolo, regra de avaliação, referência,
resposta executada e fontes por hash. O registro preservaria a comparação
automática original e a adjudicação posterior como resultados distintos.
Falhas estruturais, fontes inválidas ou conteúdo sem suporte não seriam
dispensados por uma declaração genérica de aprovação.

Essa mudança precisa ser especificada e versionada antes de sustentar uma
decisão de calibração. Atualmente, a auditoria do responsável não pode
converter uma calibração `fail` em aprovação. Portanto, esta nota não autoriza
reclassificar resultados antigos nem remover `extraction_reference_mismatch`
sem uma regra substituta explícita. A conferência das referências anterior à
execução também não substitui a avaliação das respostas que os agentes ainda
produzirão. A conclusão permanecerá limitada à concordância com referências
assistidas adotadas e aos casos avaliados; não será medida de acurácia
independente ou de cobertura da área.
