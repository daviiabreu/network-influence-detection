# Resultado da pesquisa ampla de venues e literatura

Em 12 de setembro de 2026, a descoberta de venues chegou a **235 candidatas** e
a aquisição bibliográfica encerrou as **1.027 consultas registradas**, com
**54.570 observações**. A busca foi ampliada e executada. A revisão sistemática
continua incompleta: o agrupamento automático gerou 46.400 propostas de trabalhos,
mas ainda há pendências de identidade e metadados, calibração humana, triagem,
leitura integral, extração e síntese.

| Frente | Resultado disponível | Limite atual |
| --- | --- | --- |
| Venues | 235 identidades, encontradas em 436 consultas de descoberta | Não representa todas as venues existentes; muitas políticas continuam desconhecidas |
| Verificação de venues | Nove campos examinados independentemente em 29 periódicos | Não confirma integralmente as políticas das 235 candidatas |
| Busca bibliográfica | 60 consultas temáticas e 967 recuperações por identificador, todas encerradas | Encerrar as consultas não prova cobertura integral da área |
| Preparação e agrupamento | 54.570 observações preservadas em 46.400 propostas de trabalhos | Nove pendências de título, dez conflitos de identificadores e possíveis duplicatas aguardam resolução |
| Comparação de cobertura | 64 de 64 DOIs de referência recuperados; 59 pelas buscas temáticas | Diagnóstico após ampliação dirigida, sem estimativa independente de recall |
| Mapa conceitual | 11 famílias e eixos organizados com 14 fontes | Orientação exploratória, anterior à seleção dos estudos |

O [inventário de venues](venues/search-design/2026-09-11-broad-web/reviewed-results.md)
contém 187 periódicos, 44 conferências, uma série de anais e três workshops.
O [relatório de verificação](venues/source-checks/2026-09-12-review-summary.md)
reúne as checagens independentes dos 29 periódicos e distingue afirmações
delimitadas, conflitos e informações desconhecidas. Cada candidata mantém
suas fontes e limitações. A preferência por participação remota de nível 2
ou superior, dando prioridade aos níveis mais altos, continua registrada.
Uma etapa eletrônica de submissão não basta para pontuar todo o percurso do
autor. A adequação ao artigo permanece adiada até existir um manuscrito.

Na literatura, a janela de publicação é de 1º de janeiro de 1970 a 11 de
setembro de 2026. As buscas temáticas cobrem dinâmica de opiniões, influência,
confiança limitada, modelos voter, cultura, redes adaptativas, cinética,
polarização, dados empíricos, LLMs, crenças e atitudes, aprendizado social,
convenções, interações de grupo e votação. Três bibliografias acrescentaram
1.194 referências, com 950 DOIs distintos antes da validação e do registro das
recuperações. O [protocolo legível](literature/protocol/opinion-dynamics-systematic-map-v3-review.md)
explica as escolhas; os [resultados por consulta](literature/searches/2026-09-12-v3-acquisition-results.json)
preservam todas as buscas, inclusive as duas que retornaram zero observações.

| Fonte | Consultas temáticas | Consultas por identificador | Páginas | Observações |
| --- | ---: | ---: | ---: | ---: |
| arXiv | 17 | 31 | 90 | 4.917 |
| Crossref | 0 | 936 | 1.871 | 935 |
| DBLP | 25 | 0 | 77 | 6.153 |
| OpenAlex | 18 | 0 | 435 | 42.565 |
| Total | 60 | 967 | 2.473 | 54.570 |

Há 49.333 identidades de registros nos provedores. Esse número inclui
representações distintas do mesmo trabalho entre fontes e não é uma contagem
de artigos únicos. A [auditoria das 435 páginas OpenAlex](literature/searches/2026-09-12-openalex-pagination-audit.json)
encontrou repetições já presentes nas respostas e divergências entre IDs
distintos e totais declarados em seis consultas. Essas diferenças permanecem
documentadas; não permitem calcular quantos estudos faltam.

O [mapa exploratório da área](literature/search-design/2026-09-12-area-map/README.md)
organiza a leitura por representação da opinião, mecanismo de mudança,
estrutura de interação, resultado coletivo e relação com dados. Ele ajuda a
distinguir, por exemplo, consenso de aprendizado sobre um estado externo e
polarização de segregação da rede. Suas interpretações estão ligadas às fontes
consultadas; ainda não são conclusões extraídas de um corpus selecionado.

O [diagnóstico da preparação](literature/searches/2026-09-12-v3-preparation-diagnostic.json)
encontrou dez observações sem título. Uma tem outras manifestações tituladas
ligadas pelo mesmo DOI; nove não têm. Há também 14.878 observações sem resumo.
O [inventário de metadados ausentes](literature/searches/2026-09-12-v3-missing-title-records.json)
preserva os identificadores e localizadores originais. A primeira etapa de corpus
falhou ao tentar representar um trabalho sem título. O
[sucessor com pendências explícitas](literature/run-records/2026-09-12-corpus-metadata-successor.md)
resolveu essa limitação técnica: o resultado completo foi gerado e reproduzido,
com 46.391 propostas tituladas e nove sem título. A fila contém 20.964 pares de
registros, correspondentes a 10.754 pares de propostas em 4.990 grupos ligados
por possíveis duplicatas. Esses grupos ainda precisam de revisão; não são
duplicatas confirmadas nem uma contagem de decisões humanas necessárias.
Dez propostas também preservam conflitos de identificadores.

As verificações editoriais são evidência separada: não foram
inseridas silenciosamente nos registros, e títulos de livros resenhados não
substituem títulos ausentes de resenhas.
As notas dos [sete primeiros casos](literature/search-design/2026-09-12-area-map/missing-title-evidence.md)
e dos [dois casos adicionais](literature/search-design/2026-09-12-area-map/additional-missing-title-evidence.md)
distinguem títulos verificados, rótulos de resenha sem título e limites de acesso.

Para avançar, é preciso resolver as pendências propostas de metadados e
identidade com evidência e decisões registradas, preservando a aquisição atual.
O [resultado do agrupamento](literature/searches/2026-09-12-v3-corpus-proposals.json)
continua marcado como incompleto e não libera a triagem. A triagem
automatizada depende de decisões humanas de referência: o
[material local de calibração](http://127.0.0.1:8767/) contém 50 casos
preparatórios para Davi avaliar. É possível exportar as decisões como
`minhas-decisoes-calibracao.json`. Esse material não substitui a calibração
medida nem autoriza decisões científicas atribuídas ao pesquisador.

Também permanecem as fontes suplementares previstas, incluindo exportações
controladas de editoras e rodadas de citações guiadas por estudos elegíveis.
Não houve exclusão automática por falta de título, resumo, acesso ou retorno
de uma fonte. Triagem calibrada, auditorias humanas, avaliação dos textos
completos, extração e síntese são etapas seguintes, não resultados já obtidos.

O [registro de execução](literature/run-records/2026-09-11-broad-acquisition-v3.md)
documenta a interrupção inicial, a correção e o sucessor que encerrou a coleta.
A aquisição, a preparação e as propostas foram reproduzidas sem alterar as
evidências anteriores. A revisão de código `51e45ce5a725d0a9c83eae5d96ea04c070de078c`
passou as matrizes completas em macOS e Ubuntu: 3.498 testes do workbench,
seis do estudo, verificações de estrutura, lint, tipos e instalação dos dois
pacotes. Esses resultados validam a execução técnica; o estado científico
atual está detalhado em [READINESS](literature/READINESS.md).
