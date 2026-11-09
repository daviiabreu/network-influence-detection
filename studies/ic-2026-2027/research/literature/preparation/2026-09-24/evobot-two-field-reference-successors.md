# EvoBot v3: localizadores para referências de extração

Rascunho público de 24/09/2026 para o caso de desenvolvimento já exposto
`verification.extractor.work.v2.e618414ee47714dd46aca671`. Obra
`work.v2.e618414ee47714dd46aca671`; manifestação
`observation.e65db6d02136166dc2ac9f1cc1c09f40ac650c9a4867aeef7246bf4b3830d492`;
fonte: [EvoBot v3](https://arxiv.org/abs/2508.17711v3), PDF público CC BY 4.0.
PDF SHA-256 `a7eea3ee9fbdaf40403b2a0fc5de2c2fd780021aa853fef0aecff01c2c986f0c`;
projeção de texto SHA-256
`bb25c8ac262e16494419451688283308cd23baba82226de7dbac44b45d878713`;
pacote de decisão SHA-256
`7ac338a31a7299acf59564c27de420caa9f9b8fb0c905cbbf1b84e0bcf677b60`.
Os intervalos abaixo são linhas inclusivas da projeção retida. Não reproduzem
texto do artigo. As unidades separam o valor adotado para auditoria e incluem
detalhes conferidos na fonte; sua contagem não equivale a seis cláusulas
literais da referência original.

As duas fichas do pacote existente continuam com `reference_successor=null` e
`owner_assessment=null`; não foi encontrada proposta equivalente no recorte
local conferido. O novo `proposal.json` privado, em
`/Users/davi/.local/state/research-workbench/autonomous-review-20260915/evobot-reference-successor-proposals-20260924/`,
tem SHA-256
`db951fb92bd22f8f08ccf4c557f3e2fcb82512e7a11c67acae696eb830168c2e`,
diretório `0700` e arquivo `0400`. Ele contém duas propostas e opções de
granularidade, não um `ExtractionResult` executável nem uma decisão Owner; a
suíte original SHA-256
`efaf237f3ab0b028bd82ca5a92c43bde25d350cf7ad2d308a4808b9ef5ae7f81`
e o pacote anterior mantiveram seus hashes. A preparação usou o contrato no
checkout `d9f88fd` e não executou modelo ou calibração.

## `empirical_grounding`

| Unidade de afirmação derivada do valor adotado, conferida na fonte | Localizador exato mínimo na projeção |
| --- | --- |
| TwiBot-22 é o conjunto principal: grafo com cerca de 1 milhão de usuários do Twitter, quase 100 milhões de tweets e relações dirigidas de seguidor e seguido. | p. 4, linhas 54–59 |
| O tamanho do grafo levou à partição por Louvain em 12 comunidades. | p. 4, linhas 60–65 |
| O detector evoluído foi comparado ao detector original em dois conjuntos externos, Cresci-15 e TwiBot-20. O localizador documenta avaliação do detector; não demonstra treinamento de EvoBot nesses conjuntos. | p. 7, linhas 66–70 |
| As simulações de opinião em grupo consideraram a pandemia de COVID-19 (um evento por mês de janeiro de 2020 a março de 2022; 27 passos) e o conflito Rússia–Ucrânia (um evento por dia de 24 de fevereiro a 13 de março de 2022; 18 passos). | p. 7, linhas 81–88 |
| A postagem de cada usuário recebeu um escore de sentimento de −1 (negativo) a +1 (positivo), tratado como proxy de opinião, não como opinião observada diretamente. | p. 7, linhas 89–94 |
| Médias e desvios padrão dos escores são agregados ao longo dos passos; diferenças entre simulação e dados reais usam as médias e dispersões correspondentes. A tabela compara os valores reais e os modelos simulados nos dois cenários. | p. 7, linhas 105–135; p. 8, linhas 37–45 |

O localizador da referência adotada, p. 4, linhas 54–69, sustenta apenas as duas
primeiras linhas deste mapa. O valor medido apontou para p. 4, linhas 1–97 e
registrou somente TwiBot-22, tweets e relações dirigidas de seguidores. Os
demais fatos da referência adotada estão nas páginas 7–8. Na tarefa medida
original, o pool de evidências já continha p. 4, linhas 1–97; p. 7, linhas
1–94 e 95–140; e p. 8, linhas 1–103. Portanto, esses fatos não dependem de
uma tarefa enriquecida para ficarem disponíveis ao extrator. Preservar tudo
numa única referência exigiria uma mudança futura de contrato ou política de
evidência, sem reescrever a entrada histórica.

O contrato atual admite um único `EvidenceLocator` por valor e IDs de campo
únicos no resultado. Um candidato **de forma representável**, limitado à fonte que o
localizador original cobria, é: “TwiBot-22 reúne cerca de 1 milhão de
usuários, quase 100 milhões de tweets e relações dirigidas de seguidores; o
estudo particiona o grafo em 12 comunidades com Louvain”, com localizador
`projection:bb25c8ac262e16494419451688283308cd23baba82226de7dbac44b45d878713:page:4:lines:54-65`.
Esse candidato conserva 2 das 6 unidades do mapa e deixa de fora conjuntos
externos, cenários, proxy e comparação estatística. O subintervalo proposto é
reproduzível na projeção, mas não é um localizador **exato** do pool da tarefa
histórica; p. 4, linhas 1–97, é o trecho oferecido que o contém. Não inserir
o subintervalo na suíte antiga. Outro subconjunto possível é p. 7, linhas
1–94, que cobriria as unidades sobre conjuntos externos, cenários e proxy
(3 de 6), mas não TwiBot-22 nem a comparação estatística entre simulação e
dados reais. É um exemplo de alternativa, não uma recomendação de adoção.
Para conservar as 6 unidades num único campo,
é preciso um contrato ou uma política de evidência composta que aceite os
localizadores separados acima. Este mapa não é uma referência sucessora
executável nem um julgamento de equivalência, completude ou aceitação
científica.

## `validation_method`

| Unidade de afirmação derivada do valor adotado, conferida na fonte | Localizador exato mínimo na projeção |
| --- | --- |
| Ótimo da análise adversarial sob a condição `q′(x)=q(x)`, não como garantia incondicional. | p. 4, linhas 47–51 |
| Avaliações e ablações do gerador e do detector. | p. 5, linhas 11–15 e 51–97; p. 6, linhas 52–89; p. 7, linhas 14–22 |
| Comparação das médias e dispersões dos escores de sentimento, usados como proxy de opinião, entre dados reais e modelos BC, Lorenz e LLM. A escala do proxy é −1 a +1. | p. 7, linhas 89–116 e 136–140; p. 8, linhas 9–45 |
| Teste Mann–Whitney U sobre `∆Bias` e `∆Div`. | p. 19, linhas 31–40 |
| Robustez entre comunidades e sementes; os autores descrevem três repetições de cada simulação-chave, sem enumerar os valores das sementes nesse trecho. | p. 8, linhas 32–35; p. 19, linhas 41–58 |
| Comparação do detector com conjuntos externos Cresci-15 e TwiBot-20. | p. 7, linhas 66–78 |

O único localizador da referência adotada, p. 4, linhas 47–51, sustenta apenas
a primeira das seis unidades. O valor medido, por sua vez, cita p. 8, linhas
1–103, e enumera comparação empírica, teste Mann–Whitney e robustez; a
[auditoria anterior](../../../../../../docs/research/systematic-review-extraction-source-audit.md)
reconferiu esse trecho. As páginas 4–8, 19 e 26 já pertenciam ao pool da
tarefa medida original. Usá-las não cria uma tarefa enriquecida; um novo PDF,
novos trechos não fornecidos ou outra pergunta seriam mudanças posteriores.

Um candidato **de forma representável** para apenas as três classes de método
do valor medido é: “Compara estatísticas de sentimento das simulações com
dados reais e modelos-base; relata teste Mann–Whitney U e verificações de
robustez entre sementes e comunidades”, com fonte mínima p. 8, linhas 9–45.
O trecho **exato oferecido** na tarefa antiga que o contém é p. 8, linhas
1–103. Esse candidato deixa de fora, por inteiro, o teorema, as avaliações e
ablações individuais e a avaliação externa do detector; preserva apenas
parcialmente a definição do proxy e a robustez, pois a escala −1 a +1 está
na p. 7 e as três repetições estão na p. 19. O teste é documentado sem
promover todos os resultados a significativos: a Tabela 22, p. 26, linhas
1–7, inclui comparações não significativas. Preservar o valor composto da
referência adotada requer localizadores múltiplos para o mesmo campo, hoje
não representáveis no `ExtractionResult` nativo.

## Escolha científica pendente

As alternativas **não adotadas** são: escolher um subconjunto sustentado por
um localizador exato (os exemplos acima não esgotam os subconjuntos possíveis)
ou preservar o conteúdo composto com vínculos separados por afirmação,
dependente de contrato/política sucessora. No exemplo da p. 4, a cobertura de
`empirical_grounding` é de 2 das 6 unidades do mapa; no exemplo da p. 7, 3 de
6. O exemplo da p. 8 para `validation_method` cobre três classes entre seis
unidades, duas delas apenas parcialmente. Essa contagem mede
somente conteúdo e vínculos, **não** recalcula o relatório de calibração.
Com conteúdo composto, as seis unidades por campo continuam propostas, mas não cabem
como uma referência nativa de um localizador. O Research Owner precisa dizer
quais unidades são exigidas para cada campo e qual perda de cobertura, se
alguma, aceita. A pergunta mínima é: **quais unidades precisam permanecer em
cada campo e, se não couberem num único localizador, devemos preparar suporte
explícito a múltiplos vínculos ou escolher outro subconjunto sustentado?**
Nenhuma das opções
reclassifica a execução `3044d04`, cujo resultado continua `fail`.
