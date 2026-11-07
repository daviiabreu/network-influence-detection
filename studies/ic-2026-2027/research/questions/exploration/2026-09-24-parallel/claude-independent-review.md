# Handoff preparado para Claude — revisão científica independente

Usar quando Davi disponibilizar Claude e a central tiver congelado o pacote
de propostas desta rodada. Não iniciar avaliação enquanto os arquivos ainda
estiverem sendo escritos. Este arquivo não é uma autorização de execução do
pipeline, de experimentos ou de adoção científica.

## Objetivo e entradas

Contestar as contribuições candidatas e o desenho mínimo, em contexto novo,
sem editar resultados anteriores. A central fornecerá o SHA Git, lista de
arquivos e seus hashes; não basta uma pasta de trabalho mutável. Começar por
`research-questions.md`, `exploratory-claim-map.md`, os dois memos de perguntas
e o inventário de viabilidade desta rodada. Ler as fontes primárias citadas e
buscar antecedentes contrários quando necessário.

O pacote pode conter resultados exploratórios públicos; não deve conter casos
selados, rótulos de holdout, credenciais, fontes restritas ou chaves privadas.
Não substituir a referência de calibração por uma decisão do revisor.

## Divisão recomendada se houver capacidade

Uma primeira revisão procura antecedentes que já respondem às perguntas e
condições em que a contribuição seria trivial. Outra examina desenho,
identificabilidade e inferência estatística. Contextos separados são preferíveis;
nenhum deles precisa ver a recomendação final ou o veredito do outro antes de
terminar sua análise. Ambos podem receber as mesmas evidências necessárias.

Para cada pergunta, responder:

- Qual é o antecedente mais próximo, com trecho/seção e leitura efetiva?
- A diferença proposta é científica, apenas implementação ou ainda ambígua?
- A observação permite distinguir as hipóteses e os mecanismos declarados?
- Há vazamento, pseudorreplicação, seleção pós-resultado ou comparação desigual?
- Qual controle ou contraexemplo barato poderia encerrar o investimento?
- Que evidência faltante pode mudar a recomendação?

## Saída e fronteira

Entregar um Markdown por eixo com achados priorizados, fontes primárias,
consequência concreta e recomendação `descartar`, `reformular` ou `investigar`.
Separar defeitos demonstrados de riscos ainda não medidos. Uma recomendação de
investigar não aprova protocolo nem afirma novidade. Informar o que não pôde
ser lido e o que uma busca limitada não permite concluir.

Não alterar a pergunta oficial, o corpus, referências adotadas, runs concluídos
ou código compartilhado. Não ampliar pilotos encerrados nem instalar serviços.
A central confrontará os pareceres com as fontes antes de apresentar a decisão
ao Research Owner. Modelos diferentes podem repetir o mesmo erro: concordância
entre eles não substitui evidência ou aceite científico.
