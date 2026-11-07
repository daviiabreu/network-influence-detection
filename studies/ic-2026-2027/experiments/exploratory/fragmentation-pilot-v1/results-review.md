# Revisão independente dos resultados do piloto

Data: 12/09/2026. Estado: as afirmações numéricas delimitadas conferem com os
artefatos revistos; nenhum achado acionável aberto. Os atrasos de 80, 1.170 e
19.802 tentativas são relativos à parada por diâmetro recalculado. No caso 35,
o atraso em relação ao observador com cache é de 290 tentativas.

Esta revisão constitui evidência por agente em contexto isolado. Não é
aceitação científica, reprodução da campanha publicada ou avaliação de
novidade. Foram lidos `analysis-input.json`, `run-manifest.json` e os quatro
JSONL locais indicados pelo manifesto. Posteriormente, o escopo foi ampliado
somente para a conclusão candidata em `recommendation-input.md`, sem ranking
anterior ou justificativa dos autores. Não foram consultados README, outras
recomendações, ranking, histórico ou outros relatórios. A implementação já
revista foi usada nas verificações de conteúdo e em duas regenerações pequenas.
Somente este arquivo foi escrito; os outputs não foram alterados.

## Integridade e contagens

Os quatro SHA-256 e tamanhos dos JSONL coincidem com o manifesto. Cada arquivo
contém um cabeçalho, índices de trajetórias consecutivos iniciando em zero e
um registro final `completed`, cujas contagens coincidem com as linhas reais.
Revisão do código, especificação, limites de tentativas e ambiente coincidem
entre cabeçalhos e manifesto. Os quatro mapas `source_sha256` são idênticos e
todos os seus hashes conferem com os arquivos atuais. O vínculo de
`analysis-input.json` ao SHA-256 do manifesto também confere.

| Fase | Trajetórias | Certificadas | Censuradas | Falhas numéricas |
| --- | ---: | ---: | ---: | ---: |
| Benchmark | 10 | 8 | 2 | 0 |
| Controles | 10 | 10 | 0 | 0 |
| Principal | 112 | 108 | 4 | 0 |
| Sensibilidade | 16 | 16 | 0 | 0 |
| Total | 148 | 142 | 6 | 0 |

As quatro censuras principais são os índices 100, 108, 110 e 111, todos de
`modular200`, com 100.000 tentativas e sem parada de nenhum dos três observadores.
Os dez controles terminaram com um componente efetivo. Nenhuma linha contém
`numerical_error`; opiniões finais, pesos positivos e finitos, conservação da
média e a ordem das contagens de eventos foram conferidos. Os maiores desvios
absolutos da média são `5.551115123125783e-17` no benchmark,
`1.1102230246251565e-16` nos controles, `2.220446049250313e-16` no principal e
`4.440892098500626e-16` na sensibilidade.

As 28 células principais foram recalculadas diretamente das linhas, sem usar
o agregador da implementação, e coincidem com `primary_cells`. O mesmo vale
para as contagens e listas de ocorrências de todas as fases. Os pares de modelos
compartilham efetivamente grafo, opiniões, sementes e identificadores de
réplica. Cada uma das 16 linhas da sensibilidade tem exatamente um par principal
com os mesmos inputs e modelo; não são novas unidades amostrais.

## Partições e caso 35

Entre as 108 paradas principais observadas, apenas o índice 35 apresenta
interação receptiva posterior entre grupos declarados e partição final
diferente para o observador com cache. Nenhuma das 108 paradas por diâmetro
recalculado apresenta esses dois indicadores. Os demais grupos de execução
também não contêm ocorrências desses indicadores.

Para conferir as partições sem reutilizar a rotina da implementação, foram
construídas listas de adjacência a partir das opiniões registradas e da regra
estrita `abs(x_i - x_j) < c`, seguidas de busca em profundidade. Todas as
partições finais conferem. Nos snapshots, foram conferidos cobertura dos nós,
diâmetro declarado e separação dos intervalos; as partições dos observadores
recalculado e certificado também coincidem com a reconstrução independente.

O caso principal 35 usa ER N=100, `c=0.1`, modelo adaptativo, réplica de grafo 0,
réplica de opinião 1 e sementes de grafo/opinião/eventos
`2027111200 / 2027111211 / 2027111221`.

| Observador | Tentativa | Grupos declarados | Grupos efetivos reconstruídos | Maior diâmetro efetivo | Separação aceita |
| --- | ---: | ---: | ---: | ---: | --- |
| Cache | 10.500 | 13 | 12 | 0.011388675737996734 | Não |
| Diâmetro recalculado | 10.710 | 12 | 12 | 0.009477880906879343 | Não |
| Certificado | 10.790 | 12 | 12 | 0.006710478682043108 | Sim |

Portanto, na parada do cache a partição já está desatualizada e o maior diâmetro
efetivo excede a tolerância 0,01. Essa ocorrência não é uma falha empírica da
equação 31 recalculada no estado corrente. A primeira interação receptiva
posterior que cruza os grupos do cache ocorre na tentativa 10.789, na aresta
`(20, 99)`, com opiniões anteriores
`0.23706083463396405` e `0.2425956390836365`. Esse evento foi reconstruído
diretamente da sequência de atualizações e coincide com `first_cross_event`.

A linha de sensibilidade 3 usa os mesmos inputs e tolerância 0,001. Os três
observadores param na tentativa 12.270, todos com 12 grupos, sem discrepância
de partição ou cruzamento posterior registrado. O resultado permite afirmar
que a discrepância desaparece nessa repetição específica com tolerância menor;
não estabelece uma solução geral por ajuste de tolerância.

Foram regenerados independentemente os resultados completos do principal 35
e da sensibilidade 3, usando os inputs preservados, sementes e parâmetros dos
cabeçalhos. Todos os campos de `Result.to_dict()`, após normalização JSON,
coincidem exatamente com os campos persistidos. Foram apenas essas duas
regenerações, mais a reconstrução da sequência curta do evento central.

## Tempos e censura

Exatamente três trajetórias principais têm certificação posterior à parada por
diâmetro recalculado:

| Índice principal | Perfil/modelo | Diâmetro | Certificado | Diferença |
| --- | --- | ---: | ---: | ---: |
| 35 | `er100`, adaptativo, c=0,1 | 10.710 | 10.790 | 80 |
| 61 | `er200`, adaptativo, c=0,3 | 7.137 | 8.307 | 1.170 |
| 64 | `er100_dense`, uniforme, c=0,1 | 5.675 | 25.477 | 19.802 |

A única inversão de sinal individual ocorre no par uniforme 60/adaptativo 61:
ER N=200, `c=0.3`, réplica de grafo 1 e réplica de opinião 0. O uniforme para
na tentativa 8.104 pelos três critérios. No adaptativo, a parada aproximada
é 7.137 e a certificada é 8.307. A diferença adaptativo menos uniforme muda de
−967 para +203 tentativas. Isso é uma comparação individual, não uma inversão
global ou evidência de um mecanismo geral.

As 14 medianas por célula e seus denominadores foram recalculados; conferem
com `paired_cell_time_differences`. Existem 53 pares completos de 56 possíveis.
As células `modular200` com c=0,1 e c=0,3 usam respectivamente três e dois pares
completos; as demais usam quatro. As medianas descrevem apenas esses pares
completos. As censuras permanecem explícitas nas contagens e não podem ser
tratadas como tempos conhecidos ou ausência de falha.

## Conclusão candidata

A evidência sustenta preservar o caso como resultado da reprodução da lógica
de parada e encerrar a expansão deste piloto. A matriz prevista foi concluída;
o resultado observado distingue o observador com cache da condição recalculada
e não fornece, sozinho, base suficiente para escolher a direção como tema
principal da IC. Encerrar este lote delimitado é compatível com os limites da
evidência e não equivale a refutar a direção ou demonstrar ausência de efeitos
raros em outras configurações.

A proposta de examinar depois outra viabilidade pode ser tratada como próximo
passo operacional. O conteúdo ou mérito comparativo dessa outra proposta não
foi revisto; esta revisão não endossa sua prioridade científica, seleciona uma
pergunta ou autoriza nova campanha.

A frase candidata sobre ter atingido o limite de execução foi interpretada
como conclusão da matriz prevista, não como consumo do orçamento de tempo nem
atingimento do cap em todas as trajetórias. Os valores de tempo registrados
não demonstram esgotamento dos vinte minutos e 142 trajetórias certificaram
antes do cap. A formulação inequívoca é que a matriz de execuções prevista
para este piloto foi concluída.

## Limites da verificação

Foram verificadas integridade de arquivos, aritmética dos resumos, estados
registrados e reexecução dos dois casos centrais. Os outros eventos individuais
não foram integralmente regenerados. Tempos de parede foram conferidos como
valores registrados, sem repetir a medição de desempenho. Não foi feita uma
nova auditoria da escolha de orçamento.

Os resultados permanecem descritivos de uma amostra pequena e aninhada. Zero
ocorrências no diâmetro recalculado não estabelece correção universal nem uma
taxa populacional de falha. As quatro censuras principais sequer atingiram
parada aproximada; não aumentam o denominador de paradas examinadas. O
benchmark, os controles e a sensibilidade não elevam o tamanho da amostra
principal. O certificado continua sujeito às hipóteses do modelo e à limitação
de aritmética finita já declaradas. Nenhuma conclusão de novidade, prioridade
de pesquisa ou aceitação científica foi examinada ou emitida aqui.

## Hashes do escopo revisto

Código: `a394f28e66868b0c5d2c9f6d032b5394bb354073`.
Especificação: `4fc30997b27ee759e69e39e4a922a8c79f2342367cb29a664639bafcb37efe8c`.
Ambiente de execução e regeneração: Python 3.12.13, Clang 21.1.4,
`macOS-26.6.2-arm64-arm-64bit`; RNG `random.Random` MT19937.

| Artefato | Bytes | SHA-256 |
| --- | ---: | --- |
| `analysis-input.json` | — | `7422ee1e161825ecc768ba840559ff64e5626aeda3396d24683af2e952af4a01` |
| `run-manifest.json` | — | `14161a72a02036264e0e99eb75782c94a5a1765bd8c56d6e110c7c8c2f7b30e5` |
| `recommendation-input.md` | — | `54929a1496d7f05a5a4cf957c35aaea072f6506022035c1f1514aeed40544dd8` |
| JSONL benchmark | 1.059.208 | `11778292d7c8c7f1dabaab0f45788653babb01f9fe8bbdc05618674712cd5ee4` |
| JSONL controles | 874.583 | `7567d4d06296ac24ebe60fa4406c62089655ae8f57b0b6d5cafb806ae0200112` |
| JSONL principal | 9.566.808 | `8fd935191e3f8f5a06da9c27bfdf9dec425925e014d5a1b8cafbf4fa0114bad3` |
| JSONL sensibilidade | 363.575 | `fb7dec341b089cb3ea81c7e490ff0d50444caa2821a58d767ebe6ebd1f74e856` |

Os caminhos locais completos dos quatro JSONL estão no manifesto vinculado.
Eles foram lidos diretamente desses caminhos e nenhuma cópia derivada foi
usada como substituta dos artefatos originais.
