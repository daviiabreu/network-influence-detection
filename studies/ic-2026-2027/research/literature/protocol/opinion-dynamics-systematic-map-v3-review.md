# Mapeamento v3: expansão temática e rastreamento de referências

Este sucessor implementa a [instrução de execução ampla](../../decisions/2026-09-11-broad-research-execution.md).
O [protocolo executável](opinion-dynamics-systematic-map-v3.json) conserva as
perguntas, critérios de elegibilidade, triagem, extração, avaliação de qualidade
e síntese do v2. A atualização amplia descoberta e identificação; não estabelece
que toda referência seja um estudo elegível ou que o mapa esteja concluído.

A janela de publicação passa de 1970-01-01–2026-09-07 para
1970-01-01–2026-09-11. A data de cada resposta continua registrada. A aquisição
v2 e seus resultados permanecem imutáveis; a execução v3 é nova e deve ser
identificada pelo próprio protocolo, aprovação, código e recibos.

## Origem da ampliação

A [verificação de cobertura](../search-design/2026-09-11-coverage/README.md)
congelou 64 candidatos antes de consultar sua presença no corpus v2: 38 tiveram
correspondência por DOI, dois somente por título normalizado e 24 não tiveram
correspondência exata. Estes últimos exigem investigação de identidade e
elegibilidade; não são 24 omissões científicas confirmadas. A seleção é
intencional e não estima recall populacional. Consultas derivadas desse
resultado não podem reutilizar o conjunto como uma verificação independente.

As três bibliografias suplementares são:

| Origem | Referências | Arestas DOI | Evidência registrada |
| --- | ---: | ---: | --- |
| Starnini et al., *Opinion dynamics: Statistical physics and beyond*, manifestação arXiv v1 | 835 | 720 | [Arestas e locators](../search-design/2026-09-11-coverage/starnini-reference-edges.json) |
| Flache et al., revisão de modelos de influência social, JASSS 2017 | 174 | 126 | [Texto oficial e arestas](../search-design/2026-09-11-coverage/flache-reference-edges.json) |
| *A survey on opinion dynamics: From rule-based models to data-driven and hybrid approaches*, Neurocomputing 2026 | 185 | 161 | [Depósito de referências e arestas](../search-design/2026-09-11-coverage/neurocomputing-reference-edges.json) |

São 1.194 referências, 1.007 arestas e 950 alvos DOI distintos na união das
três bibliografias. Uma referência, um identificador, uma manifestação e um
trabalho elegível são unidades diferentes. O depósito Neurocomputing distingue
DOIs fornecidos pela editora dos resolvidos por Crossref; os alvos ainda
precisam de reidentificação. Referências sem DOI ou com link malformado continuam
em filas explícitas, sem normalização silenciosa ou exclusão por acesso.

## Consultas de descoberta

As dez famílias originais continuam presentes. As seis expansões são:

| Família | Lacuna investigada |
| --- | --- |
| Q11 | Dinâmica de crenças, sistemas de crenças e mudança de atitudes |
| Q12 | Aprendizagem social, crenças e aprendizagem bayesiana ou não bayesiana |
| Q13 | Naming game, convenções sociais e minorias comprometidas |
| Q14 | Polarização e câmaras de eco fora da expressão “opinion dynamics” |
| Q15 | Interações de grupo, hipergrafos e dinâmica de consenso de ordem superior |
| Q16 | Intenção de voto, regras de maioria e opiniões ideológicas |

O plano contém 60 consultas temáticas: 17 arXiv, 25 DBLP e 18 OpenAlex.
As diferenças de quantidade refletem traduções e partições explícitas, não
sessenta temas independentes. OpenAlex pesquisa título e resumo; arXiv usa
campos de metadados explícitos; DBLP usa substrings de título em blocos pequenos.
As traduções não são consideradas semanticamente equivalentes entre índices.

A sondagem inicial Q14 no OpenAlex retornou 11.265 resultados declarados,
acima das 100 páginas de 100 registros. O plano divide o período em
1970–2009, 2010–2019 e 2020–2026, com intervalos contíguos, sem descartar
resultados. A restrição ao sentido humano/social foi ampliada para incluir
crenças, atitudes e cultura; o total antigo não é apresentado como medição
desse literal final. Uma segunda sondagem do literal final mediu 1.001,
2.349 e 8.733 resultados, respectivamente, nas três partições; nenhuma excedeu
o teto individual. Essas sondagens preservaram somente a primeira página e
não contam como aquisição concluída. No arXiv, dois blocos preservam a união e
respeitam o limite de tamanho da consulta. Atingir qualquer teto ainda produz
resultado incompleto, exigindo continuação registrada.

## Recuperação de identificadores

Além da descoberta, há 936 consultas Crossref por DOI conhecido e 31 consultas
arXiv por identificador explicitamente citado. Esses 967 lookups não são
contabilizados como novas buscas temáticas. Os DOIs vêm das três bibliografias,
do desafio de cobertura e de leads oficiais registrados, incluindo a verificação
do título ausente no OpenAlex. A descoberta de venues acrescentou o artigo
[Unmasking conversational bias in AI multiagent systems](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0355458)
e o [preprint arXiv:2501.14844](https://arxiv.org/abs/2501.14844), ausentes da
coleta v2 por identificador e título exato. As manifestações são candidatas
à reconciliação; sem identificador compartilhado, não são fundidas por inferência.

Crossref deve usar somente o filtro de DOI exato na normalização 3. O DOI
continua como literal da estratégia, mas não é repetido em
`query.bibliographic`: a sondagem real mostrou zero resultados para o DOI PLOS
existente quando ambos os parâmetros eram combinados, contra um registro com
o filtro isolado. A confirmação seguinte retornou página vazia. As respostas
anteriores permanecem preservadas; as normalizações 1 e 2 conservam suas URLs.
Cada lookup admite até duas páginas de 20 registros: a resposta identificada
e, quando necessária, a página vazia que confirma o fim do cursor. Não há
expansão textual livre de Crossref. O DOI arXiv usa a rota oficial arXiv;
`10.5281/zenodo.13787981` permanece separado para uma fonte própria, sem
supor que Crossref seja sua agência. Ausência no provedor não exclui o alvo.

## Identidade e composição

A deduplicação v2 interpreta a lista de identificadores como uma lista
explícita de tipos permitidos, sem ordem de precedência: DOI, arXiv, DBLP e
OpenAlex. Categorias e identificadores malformados permanecem nos originais,
sem unir trabalhos. DOI compara maiúsculas e minúsculas somente em ASCII,
conforme o [DOI Handbook](https://www.doi.org/doi-handbook/html/).
Versões do mesmo identificador arXiv podem compartilhar a identidade da obra;
a versão da manifestação e seus bytes continuam preservados, conforme a
[documentação arXiv](https://info.arxiv.org/help/arxiv_identifier.html).

Identificadores incompatíveis e correspondências apenas de título geram filas,
sem fusão nem exclusão automática. Múltiplos identificadores de um tipo também
podem representar aliases ou problemas de metadados; a fila conserva a evidência
e não declara por si só que são artigos diferentes. Títulos ausentes continuam
ausentes nas observações. O título da obra pode vir de outra manifestação
comprovada do mesmo grupo; os dois registros OpenAlex sem título têm uma
manifestação DBLP com DOI compartilhado e título presente. A versão v1 e seus
hashes de replay não são substituídos.

## Continuidade e condição de conclusão

A aquisição deve preservar bytes, consultas, respostas, limites e falhas e
reproduzir os resultados offline. A projeção histórica ocupava aproximadamente
99 MB; a execução ampliada usa CAS com limite explícito de 512 MB por artefato,
sem alterar os limites individuais de respostas HTTP. O operador registra esse
valor; não afirma que o CLI histórico de 100 MB aceite os agregados novos.

O rastreamento continua por referências e citações, com reidentificação dos
alvos e registro de produtividade marginal após deduplicação e elegibilidade.
A regra continua sendo duas rodadas consecutivas sem novos trabalhos elegíveis.
As três bibliografias iniciais não satisfazem essa regra por si só.

O pacote de calibração deve conter fontes reais e campos de julgamento humano
vazios até que Davi os preencha. A aprovação de execução não registra leitura
humana, resolve conflitos ou faz exclusões finais. Calibração, triagem, textos
completos, extração, qualidade, síntese, revisão independente e aceite permanecem
entregas concretas a executar e verificar, sem serem substituídas por contagens
de consultas ou testes de software.
