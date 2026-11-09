# Lote de decisão da calibração ampla

Este pacote organiza a menor revisão humana útil sobre a calibração real já
executada. As 50 referências de título/resumo e os seis campos de extração já
foram adotados; não se solicita nova aprovação geral.

## Estado preservado

A execução `3044d04` completou 101 casos e permanece desenvolvimento com
resultado `fail`: recall de 87,5% para A e 100% para B, uma falsa exclusão,
14 divergências de julgamento e extração ainda sem auditoria científica do
responsável. A suite tem SHA-256
`efaf237f3ab0b028bd82ca5a92c43bde25d350cf7ad2d308a4808b9ef5ae7f81`;
o resumo, `48193b0056f375f99ff6101c7bb89023460a3a49058b825d4f69aac84098ab15`.

O material importado é `calibration-development-1`, não uma `calibration-4`
produtiva. O histórico de ajustes continua `unknown`; não foi localizada uma
suite real não sintética `calibration-4`. A execução e seus casos ficam
congelados como desenvolvimento já exposto, qualquer que seja a decisão abaixo.

## Fato sobre ajustes anteriores

Registrar uma destas situações sem inferir a partir da ausência de registros:

- nenhum ajuste anterior com estes casos;
- ajustes anteriores identificados, com descrição e alcance;
- histórico não reconstruível.

Se Davi não puder atestar uma das duas primeiras, recomendo registrar
`não reconstruível`. Uma declaração posterior não torna a execução já observada
uma verificação independente.

## Nove fichas de triagem

O pacote privado `screening-decision-packet-20260916/` foi reaberto e mantém
todas as decisões do responsável vazias. `packet.json` tem SHA-256
`b1a251be432130950503fb5b36053bb45422cf23b3438fd536cc99f4bc33ce17`;
`REVIEW.md`, `dbbfd7c721801d065f7d707f05f18295543262136567b1fa641530dff7ec8028`.
As fichas são:

- `V3-24`, *Negative Influence Minimizing by Blocking Nodes in Social Networks*;
- `V3-35`, *Whose Opinion to Follow in Multihypothesis Social Learning?*;
- `V3-48`, *Twitter sentiment analysis for the estimation of voting intention*;
- `V3-27`, *A Novel APP Recommendation Method Based on SVD and Social Influence*;
- `V3-06`, *Integrating a consensus-reaching mechanism with bounded confidences*;
- `V3-20`, *A discrete boltzmann-type model of swarming*;
- `V3-32`, *Agnostic Sequential Rationality*;
- `V3-21`, *Reidentifying The Compromise Model in The Analytical Decision Process*;
- `V3-28`, *Generative Agents at Work*.

Para cada ficha, a decisão deve separar três respostas: se a saída era
sustentada pelo input original, se a referência original precisa de sucessor e
qual referência deve valer numa futura tarefa enriquecida. Fonte encontrada
depois não pode ser tratada como se estivesse no payload medido.

Propostas assistidas para a primeira dessas respostas, a conferir nas fichas
privadas antes de registrar a decisão científica:

| Ficha | Recomendação diante do input medido | Distinção a preservar |
| --- | --- | --- |
| `V3-24` | Conservar `include` como referência; aceitar `uncertain` de A como limiar defensável para título sem resumo, não como falsa exclusão. | O código editorial `other` não prova produto não acadêmico. |
| `V3-35` | Conservar `include`; reavaliar `exclude` de A, pois os resumos descrevem aprendizado social e incorporação de opinião de especialistas. | Não exigir simulação populacional quando o critério abrange influência social. |
| `V3-48` | Manter `uncertain` para o título sem resumo. | Estimar intenção de voto não prova dinâmica, mas tampouco prova sua ausência; manuscrito posterior é outra tarefa. |
| `V3-27` | Manter `uncertain` para o título sem resumo. | Julgar separadamente as razões de A e B; influência social em recomendação não resolve o mecanismo. |
| `V3-06` | Tratar `include` de A como limiar plausível, sem classificar como erro a incerteza preservada. | Consenso com confiança limitada não explicita, no título, participantes e mudança de opinião humana. |
| `V3-20` | Manter `uncertain` para o título sem resumo. | A fonte editorial posterior sobre entidades modeladas não integrava o input original. |
| `V3-32` | Manter `uncertain` até decidir se condicionamento de crenças em jogos dinâmicos satisfaz a definição operacional. | O resumo original existia; não excluir teoria apenas por não ser simulação. |
| `V3-21` | Manter `uncertain` para o título sem resumo. | A descrição dos anais e a designação de pôster são externas ao input medido. |
| `V3-28` | Manter `uncertain` para o título/metadados originais. | Agentes administrativos não equivalem automaticamente a opiniões; resumo institucional posterior é outra tarefa. |

## Seis fichas de extração

O pacote privado `extraction-decision-packet-20260916/` também foi reaberto.
`packet.json` tem SHA-256
`7ac338a31a7299acf59564c27de420caa9f9b8fb0c905cbbf1b84e0bcf677b60`;
`REVIEW.md`, `10f0284d769fde72388bba0d3c74f84c7e29882120d85e63ef238b1c03e4e2e5`.
As fichas cobrem `empirical_grounding`, `evidence_gaps`, `model_family`,
`network_topology`, `reproducibility_artifacts` e `validation_method`.

Para cada campo, registrar separadamente suporte na fonte, completude,
preservação de números, unidades e negações, tratamento de proxies e uma
disposição nativa `equivalent`, `substantive_difference` ou `unresolved`. A
última representa um julgamento ainda inconclusivo depois da revisão, não a
ausência de decisão que os campos vazios preservam hoje. Se a
referência adotada for insuficiente, definir um sucessor com localizadores
adequados. Diferença textual isolada não é erro factual.

A [auditoria de fonte](../../../../../../docs/research/systematic-review-extraction-source-audit.md)
já conferiu que os seis valores medidos têm suporte nos localizadores fornecidos;
isso não decide equivalência nem completude. Para tornar a revisão pontual:

| Campo | Ponto específico para decisão do responsável |
| --- | --- |
| `empirical_grounding` | Verificar se omitir conjuntos e alvos adicionais altera o conteúdo exigido; a referência adotada agrega fatos fora de seu único localizador. |
| `evidence_gaps` | Decidir se as limitações de simulação em outra página são necessárias além das três limitações retornadas. |
| `model_family` | Comparar a caracterização de EvoBot, confiança limitada e Lorenz, não a igualdade literal do texto. |
| `network_topology` | Julgar se rede dirigida de seguidores e comunidades Louvain bastam para a topologia pedida. |
| `reproducibility_artifacts` | Separar declaração de repositório público de prova de execução ou completude dos artefatos. |
| `validation_method` | Decidir quais avaliações e testes devem constar; o localizador da referência adotada cobre só parte de seu valor agregado. |

## Consequência

As decisões corrigem referências apenas por sucessores e não mudam o resultado
histórico `fail`. Depois delas, ainda será necessário preparar uma coorte de
verificação cientificamente disjunta e referências reais para triagem de texto
completo, quatro papéis de apoio e revisão global. Fixtures e ensaios sintéticos
não suprem esses materiais.
