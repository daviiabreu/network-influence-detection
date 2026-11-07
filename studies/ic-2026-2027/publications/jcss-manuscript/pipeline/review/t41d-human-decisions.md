# T41d — propostas não aplicadas e decisões humanas

A T41c prevalece. As seções fixas não estão autorizadas nesta tarefa. A lista abaixo conserva as questões de revisão; B05, B11, duplicação de exposição e X1b já receberam correções T41c, que não foram revertidas. A nova regra de contagem positiva vale somente no resumo. Nenhuma mudança de seleção em Results, Discussion ou Conclusion foi feita.

Decisões T53

Estas observações não autorizam alterar condições ou bindings. Mantêm os trechos atuais até uma decisão do coordenador.

| Localizador | Problema e decisão necessária |
| --- | --- |
| B1b-G0, results-shells.tex:151; B1b-G1c, :193; B1b-G2c, :265 | São os períodos mais difíceis dos ramos de falha, mas o montador divide suas cláusulas por expressões literais. Em `src/ic_study/analysis/v4_manuscript_assembly.py:382–417`, `_criterion_text` usa `; `, `, `, `the stage recorded `, ` and a standardized`, `, and at ` e `, against `. Uma divisão natural em vários períodos alteraria a transformação usada para selecionar apenas critérios/comparações que falharam. Decidir uma representação de cláusulas independente dessas frases antes de reescrever. Não há proposta para essas três linhas. |
| P5-b.range, results-shells.tex:720 | `compose_documents`, v4_manuscript_assembly.py:614–615, retira a cláusula de igualdade quando B06 é selecionado usando o padrão literal `, and at every value.*?equalled it\.`. A frase é aceitável e fica intacta; separar as duas afirmações exigiria rever essa transformação. |
| B05/RS18, results-shells.tex:402 | B05 pode ser selecionado por banda não monotônica mesmo com `n_dip = 0`. No ensaio invalid-main surge “At 0 values ... so the sustained boundary ...”. Decidir a seleção independente da sentença sobre quedas; não trocar esse zero por “some”, nem retirar o binding. |
| B11/RS34, results-shells.tex:518–520; P7-c1, :753 | Em incomplete-tier2, invalid-main, passed-shp e unavailable, B11 aparece por `n_channel_not_assessed > 0`, embora `n_pairs_compared = n_obs_exceeds = n_channel_dependent = 0`. As frases sobre AUC superior e separação dependente do canal continuam presentes; depois P7-c1 declara ausência de comparação. Há que decidir seleção por sentença para as linhas 518–520. O significado científico dessas frases pode ser mantido, mas seu uso com contagens zero não é corrigível só com redação. A proposta de :521 é independente disso. |
| B06/RS18–RS23, results-shells.tex:422–423 | A seleção permite que apenas uma unidade de tier 2 difira entre primeira e sustentada. Nesse caso, a contagem contra B e “At ... of them” podem ser zero. Decidir se as sentenças sobre B são selecionadas por suas próprias contagens; não introduzir informação de tier 2 em bindings de tier 1. |
| B07/RS28, results-shells.tex:439 | “no statement is made that separation holds for some value of r as a whole-curve claim” mistura um quantificador pontual e uma afirmação sobre a curva inteira. A linha 438 pode ser simplificada, mas :439 requer que o responsável confirme a afirmação exata que quer excluir. Trocar por um teste global, uniformidade de separação ou inexistência de separação criaria interpretação nova. |
| P6, results-shells.tex:729–739; B10, :495, :500–501 | As listas de r elegíveis, pareados e classificados são bindings distintos. Mesmo que sejam iguais em uma montagem, não se pode condensá-las em uma faixa ou em “the same values”, nem eliminar uma lista, sem decisão sobre os bindings e suas condições. As propostas só reorganizam a frase ao redor das listas. |
| B1a/P2 e B00/P1–P10; v4_manuscript_assembly.py:626–630, :650–651 | A ordem P1–P10 e a união de fragmentos por linhas em branco deixam a seção fragmentada. Aproximar o objeto principal da abertura ou agrupar sentenças vizinhas em um único parágrafo exige decisão de composição. Os exemplos abaixo preservam a ordem e as quebras do montador; não simulam uma melhoria de layout ainda não autorizada. |
| B00, results-shells.tex:649–696 | Estes são comentários INCLUDES de legendas, não frases visíveis selecionadas por este shell. Contêm “trait-state persistence”, etiquetas de status e NS/P/CI/CV. Não podem ser editados nesta tarefa. Se a harmonização de legendas com `trait-plus-autoregressive persistence (B)` for desejada, requer revisão específica do texto emitido e de suas instruções. Não pressupus que essas legendas comentadas sejam o texto efetivamente gerado. |

Os três ramos de falha acima não estão exercitados pelas 16 montagens fornecidas. Foram revisados diretamente no shell e no montador, sem inventar uma montagem de falha. A aprovação atual do gate informada no pedido não serve de autorização para apagar ramos pré-registrados.


Decisões T54

Não proponho as mudanças estruturais abaixo. Elas exigiriam rever composição, seleção ou binding; não foram aplicadas nos exemplos.

| Questão | Localizadores | Decisão necessária |
| --- | --- | --- |
| A mesma lista de `r` reaparece até dentro de um único contraste | `D-H-BD:55`, `C-H-BD:63`, `D-PERMISSION:162–163`, `D-BD-PERSISTENCE:191`, `C-BD-PERSISTENCE:199`, `D-BE-PERSISTENCE:228`, `D-BC-PERSISTENCE:235`, no shell Discussion/Conclusion | Decidir se a lista do conjunto comum pode aparecer uma única vez, ou se algum binding pode migrar para uma referência tabular. A regra desta tarefa exige preservar todas as ocorrências; a proposta só reorganiza a sintaxe. |
| Etiquetas e booleanos continuam aparecendo no artigo | `D-X6-INCONCLUSIVE:374`, `D-X6-ADEQUATE:398`, `D-X3-LOCAL-R050:727–728` e as outras oito variantes; `D-X3-READINGS:461`, `D-X7-GAIN:551` | Um binding ou fragmento específico poderia apresentar um estado em inglês, mantendo a etiqueta computada no catálogo. Não transformar `true/false`, `adequate`, `far` ou `against-objection` em frases afirmativas sem esse contrato. As propostas descrevem a quantidade antes da etiqueta, mas preservam o valor literal. |
| Exposição aparece duas vezes no mesmo trecho da Conclusion | `C-EVALUATION-PASS:285` e `sections/conclusion.tex:2` | Consolidar a divulgação da exposição e o uso de novas sementes, preservando a divulgação nos ramos sem PASS. O slot PASS é condicional; apagar sua condição ou uma afirmação do texto fixo não é uma correção apenas estilística. |
| Algumas redundâncias protegem escopos distintos | `sections/discussion.tex:25–27`, `D-SHP-ADMISSIBLE:576`; `sections/discussion.tex:30`, `D-X6-DENOMINATORS:340–344` | Decidir se uma ressalva pode ser apresentada por remissão. D1 e verdade aproximada não podem se fundir, nem o envelope substituir Wald. Não suprimi ressalvas por considerar uma tabela suficiente. |
| A causa pública da ausência da âncora entra depois do shell | `D-SHP-NOT-RUN:630`; regra de mesmo ID no registro de montagem | Nas fixtures, o texto acrescentado diz `Reason: this artificial gate-only case includes no SHP run.`, mesmo em montagens com PASS. Esse texto vem do fato sintético, não do shell. A redação de uma causa real exige o fato público pertinente; não inventei causa nem corrigi a fixture. |
| Legibilidade global ainda depende de onde os blocos entram | Slots DS02, DS06, DS10 e C1/C2/C3; `v4_manuscript_assembly.py:552`, `:669` e `:674` | Mudar ordem de blocos, transferir inventários para o suplemento ou suprimir blocos em certos ramos exigiria rever composição/regras. Os exemplos mantêm a ordem original. Apenas a paragrafação dos três marcadores CN01 foi proposta, sem alterar o conteúdo ou a seleção. |

Os localizadores sem caminho nessa tabela pertencem a `publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex`. Essa análise não escolhe uma interpretação com base em dados selados.


Propostas não aplicadas nesta revisão:

| Proposta | Decisão | Motivo |
| --- | --- | --- |
| T53 2.12. B05 | retained-t41c | O trecho vigente contém a correção T41c; proposta anterior não aplicada por risco de apagar distinção, roteiro ou divulgação única. |
| T53 2.24. P1 | retained-t41c | O trecho vigente contém a correção T41c; proposta anterior não aplicada por risco de apagar distinção, roteiro ou divulgação única. |
| T54 01. DS01 — `publications/jcss-manuscript/sections/discussion.tex:4` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 02. DS02 — `publications/jcss-manuscript/sections/discussion.tex:7` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 03. DS03 — `publications/jcss-manuscript/sections/discussion.tex:10` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 04. DS04 — `publications/jcss-manuscript/sections/discussion.tex:21` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 05. DS05 — `publications/jcss-manuscript/sections/discussion.tex:24` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 06. DS06 — `publications/jcss-manuscript/sections/discussion.tex:29` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 07. DS07 — `publications/jcss-manuscript/sections/discussion.tex:32` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 08. DS09 — `publications/jcss-manuscript/sections/discussion.tex:38` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 09. DS10 — `publications/jcss-manuscript/sections/discussion.tex:41` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 10. CN01 (texto fixo) — `publications/jcss-manuscript/sections/conclusion.tex:1` | out-of-scope | Proposta para seção fixa; autorização limitada aos shells e ao abstract de main.tex. |
| T54 35. C-EVALUATION-PASS — `publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex:285` | retained-t41c | O trecho vigente contém a correção T41c; proposta anterior não aplicada por risco de apagar distinção, roteiro ou divulgação única. |
| T54 48. D-X1B — `publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex:436` | retained-t41c | O trecho vigente contém a correção T41c; proposta anterior não aplicada por risco de apagar distinção, roteiro ou divulgação única. |
| T54 90. E.twin-and-expanded-feature-boundaries — `publications/jcss-manuscript/pipeline/drafts/2026-09-30/exploratory-results-shells.tex:201` | retained-t41c | O trecho vigente contém a correção T41c; proposta anterior não aplicada por risco de apagar distinção, roteiro ou divulgação única. |


Estado das questões históricas, para não confundir correções já integradas com decisões pendentes:

| Questão | Estado na T41d |
| --- | --- |
| B05/RS18 e B11/RS34 com zero comparações | Corrigidas pela T41c; guards por frase preservados. |
| Divulgação de exposição repetida na Conclusion | Corrigida pela T41c; C-EVALUATION-PASS continua apenas “Evaluation used new seeds.” |
| X1b histórico e projeção fornecida | Correção T41c preservada; não presumir identidade nem independência das execuções. |
| B06 em Results quando só tier 2 difere | Decisão humana pendente; o resumo recebeu guard sobre sua própria contagem, sem mudar Results. |
| B07/RS28, quantificador de curva inteira | Decisão humana pendente; a frase controvertida permanece. |
| Parser literal dos critérios e remoção de igualdade P5-b.range | Decisão humana pendente antes de reescrever cláusulas que participam dessas transformações. |
| Listas repetidas, tradução de estados, mudança de slots/layout e legendas INCLUDES | Decisão humana pendente; bindings, seleção, ordem fora do resumo e comentários mantidos. |
| DS01–DS07, DS09–DS10 e CN01 fixos | Dez propostas fora do escopo; exigem autorização específica para as seções fixas. |
| Causa real da ausência do SHP | Fato público do Owner; nenhuma causa real criada a partir dos ensaios artificiais. |

## Fechamento em 01/10/2026 (decisão 161)

O Owner delegou ao coordenador as decisões deste arquivo. Elas foram tomadas e aplicadas na T57, antes da liberação de qualquer resultado dos tiers; o registro completo está em `t57-report.md`.

| Questão | Decisão |
| --- | --- |
| DS01–DS07, DS09, DS10 e CN01 | Aplicadas as dez propostas, com quatro ajustes que preservam o sentido original: DS01 mantém a não travessia por valor de r e a frase sobre afirmações descritivas; DS02 mantém o motivo de parear B e D; DS05 atribui a mistura de entrevistas de 2004 à amostra de reposição; CN01 mantém a primeira frase original, com a nova paragrafação. |
| B06 em Results | Seleção por frase: a frase das fronteiras diferentes entra só com contagem positiva, e a frase de censura sustentada por lacuna passa a explicar a regra sem contagem. A contagem antiga contava todas as curvas válidas, não só as que diferem; ela continua no B08, selecionado sempre que essa contagem é positiva. |
| B07/RS28 | A frase passa a excluir apenas a afirmação global de que há separação em algum r, como no ledger RS28. |
| Rótulos booleanos do X3 | Os nove blocos D-X3-LOCAL ficam só com a frase de magnitude e classificação. Um bloco comum, D-X3-LOCAL-NOTE, entra uma vez depois do último deles com a margem declarada, a validade da curva principal B por extenso (escolhida pelo valor da flag; um valor ausente recusa o bloco) e a ressalva no plural (T57b). Os rótulos em `\texttt` depois de uma descrição ficam como estão. |
| Legendas INCLUDES e nome da nula B | A legenda do F1, o rótulo das figuras e as notas da T1/T1s usam "trait-plus-autoregressive persistence", como o resumo. |
| B1b-G0/G1c/G2c (parser literal) | Sem mudança: são ramos de falha do gate, que não entram no texto porque o gate passou. |
| P5-b.range, listas de r (P6/B10 e Discussion), ordem P1–P10 e slots, ressalvas redundantes | Sem mudança; a composição só se revê depois de ler o texto montado. |
| Exposição repetida na Conclusion | Já resolvida pela T41c. |
| Causa real da ausência do SHP | Continua fato do Owner; nenhuma causa foi criada aqui. |
