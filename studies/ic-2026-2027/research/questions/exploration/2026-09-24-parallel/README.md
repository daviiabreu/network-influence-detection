# Preparação científica paralela — 24/09/2026

Davi pediu mais agentes, mantendo GPT-6 Sol/high, e informou que poderá usar
Claude depois. Esta rodada explora oportunidades e viabilidade; não executa
triagem canônica, escolhe tema, altera protocolo ou amplia os pilotos encerrados.
O mapa amplo permanece. A escolha final depende da síntese aceita.

## Divisão efetiva

| Responsável | Entrega própria | O que não duplica |
| --- | --- | --- |
| Pesquisa da área, tarefa existente | Corpus, metadados, referências, coorte e calibração; estrutura do manuscrito | Não repete os levantamentos abaixo |
| Engenharia, tarefa existente | Correção da falha concreta e cobertura restante da matriz | Não começa outra infraestrutura científica |
| Venues, tarefa existente | Correção do landscape e requisitos editoriais verificados | Não decide a contribuição nem escreve resultados |
| Subagente Sol/high: validade empírica | `empirical-identifiability-leads.md`: 2–3 perguntas candidatas, antecedentes próximos, observação e acesso a dados | Não reabre o piloto de previsão nem adota referências |
| Subagente Sol/high: mecanismos | `mechanism-generalization-leads.md`: 2–3 perguntas candidatas sobre dimensões, exposição, interações coletivas ou aprendizado social | Não reduz o mapa a parada/fragmentação |
| Subagente Sol/high: viabilidade | `experimental-reuse-and-cost.md`: módulos reutilizáveis, custos medidos, hipóteses de escala e lacunas | Não executa benchmarks ou campanhas duplicadas |
| Subagente Sol/high: revisão do desenho, segunda rodada | `design-review.md`: confrontar hipóteses, comparações e critérios das quatro propostas | Não refaz a busca de antecedentes reservada à contrarrevisão posterior |
| Central | Comparação das propostas, dependências, revisão e integração | Não contabiliza número de agentes como avanço científico |

Os três primeiros subagentes concluíram seus memos no mesmo worktree isolado,
com arquivos distintos. A central leu as entregas, ajustou uma fronteira de
autorização no memo de custo e iniciou um quarto Sol/high, em contexto separado,
para revisão do desenho. Os quatro ajustes foram incorporados pelos autores e
reconferidos pelo revisor em [design-review.md](design-review.md). Nenhum escreve
no candidato da matriz ou nos arquivos de outro agente. Não foram criadas novas
tarefas de coordenação no aplicativo. A estrutura do repositório passou 7/7;
esse check documental não valida os enunciados científicos dos memos.

## O que cada proposta precisa trazer

Uma pergunta refutável; o resultado anterior mais próximo; a diferença ainda
não demonstrada; hipótese e alternativa; unidade de observação; comparação
mínima; dados/código disponíveis e restrições; critério de abandono; e incertezas
que impedem escolher a pergunta. A extensão de leitura deve distinguir resumo,
texto integral e inspeção de código. Não inferir novidade da ausência de um
artigo numa busca curta.

Os [pilotos existentes](../../exploratory-claim-map.md) já produziram resultados
exploratórios limitados. A previsão não atingiu seu critério central; o piloto
de fragmentação não justificou por si só o tema principal. Reusar implementação
é diferente de ampliar amostras para procurar um resultado favorável.

## Próxima rodada, somente quando houver entradas

1. Revisão independente de novidade: procurar antecedente que torne cada
   contribuição redundante. É uma boa entrega para Claude.
2. Revisão estatística: examinar unidade experimental, dependência entre
   repetições, controles, incerteza e critérios de sucesso/abandono antes de
   uma nova campanha.
3. Preparação de reprodução: vincular comandos, ambiente, sementes e artefatos
   de uma implementação escolhida. Não confundir isso com executar um protocolo
   ainda não aprovado.
4. Escrita antecipada: preencher contexto e métodos sustentados; manter método
   proposto separado do executado. Resultados, resumo final e conclusão dependem
   da evidência; a estrutura segue a orientação de Henrique e o template da venue.

Essas atividades não exigem quatro novos coordenadores. Cada uma recebe um
pacote fechado e retorna um artefato verificável ao responsável existente.
Leituras exploratórias podem anteceder a conclusão do corpus; inclusão,
extração e síntese canônicas continuam seguindo seus próprios contratos.

## Limite de capacidade e caminho crítico

A central tem três slots de subagentes nesta rodada. Não lançar um quarto
antes de liberar um slot. Os coordenadores existentes controlam seus próprios
subagentes; antes de ampliar ali, conferir a lista de entregas para evitar
duplicação. Mais chamadas não resolvem acesso a uma fonte, decisão científica,
tempo medido de simulação ou uma hipótese sem informação identificável.

O próximo marco é uma comparação examinável de perguntas e custos, não um
tema escolhido automaticamente. A estimativa do manuscrito será revista com
esse material. Não prometer redução proporcional ao número de agentes.

O [handoff para Claude](claude-independent-review.md) está preparado, mas não
foi enviado nem executado. Nenhuma nova conta, gasto ou mudança de modelo no
pipeline canônico está autorizada por essa preparação.
