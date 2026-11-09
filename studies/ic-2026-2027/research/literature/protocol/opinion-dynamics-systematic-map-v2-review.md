# Protocolo v2 para revisão

O [protocolo executável](opinion-dynamics-systematic-map-v2.json) é sucessor do
v1 e permanece como candidato para revisão. Nenhuma aprovação, exclusão ou
calibração humana é inferida deste documento. As decisões técnicas retomam as
instruções de Davi na conversa do Claude de 7 de setembro: manter a linhagem
histórica, usar inglês no texto completo, mapear revisões para snowballing,
reservar Crossref para identificadores, acrescentar arXiv e manter DBLP por
uma rota oficial funcional. O v1 e suas evidências permanecem intactos.

A janela fica em 1970-01-01 a 2026-09-07. Os últimos cinco anos formam um
estrato de análise, sem excluir fundadores do mapa. A aquisição não filtra pelo
idioma inferido dos metadados; inglês é verificado na etapa de texto completo.
O filtro de tipos do OpenAlex inclui `conference-paper`, além de artigos,
preprints e revisões. Revisões alimentam mapeamento e rastreamento de citações,
sem virar estudos primários automaticamente.

São três índices de descoberta com consultas executáveis: OpenAlex, arXiv e
DBLP. As dez famílias geram 34 consultas literais: dez no OpenAlex, dez no
arXiv e 14 no DBLP. Crossref é a quarta fonte de apoio, para recuperação de identificadores
e metadados de candidatos já encontrados. Ele está na política suplementar,
com uma página de até 20 candidatos por tentativa documentada, sem paginação
de descoberta nem publicação de e-mail pessoal. Essa separação evita que o
executor transforme recuperação de metadados numa busca geral por relevância.

## Evidência que mudou a busca

Os diagnósticos foram executados pelo código do repositório, usando a
credencial dedicada do OpenAlex em cabeçalho, com bytes brutos e checkpoint de
cada página fora do Git. Os 16 trabalhos conhecidos foram consultados por
interseção entre cada consulta e seus identificadores. Isso mede pertinência
ao conjunto de resultados, sem recuperar o corpus inteiro. Não mede a posição
na busca irrestrita nem substitui a calibração com julgamentos humanos.

A busca padrão inclui texto completo. Nos blocos propostos pelo Claude, ela
devolveu 109.288 resultados para consenso, 108.519 para vieses e 99.445 para
validação empírica. A comparação com título e resumo mostrou que a pesquisa
estava alcançando muitos registros pelo texto indexado, além dos metadados.
O v2 declara título e resumo explicitamente. O bloco de consenso também
amarra a expressão genérica sobre chegar a consenso à probabilidade e inclui
os termos dos modelos de influência social. Seus resultados caíram para 1.225.

Com essa correção, os 12 seeds de modelos primários continuam recuperáveis
pelas consultas. O artigo de Clifford e Sudbury é um sentinela de linhagem,
com exclusão de domínio esperada; o review de Castellano e colaboradores entra
pela rota de seed secundário declarada. Ambos ficam visíveis na matriz como
ausentes das consultas, sem alterar seus resultados para fazê-las passar.
Os seeds conhecidos foram usados no desenvolvimento das consultas e não são
um conjunto independente de verificação.

| Bloco | Tema | Total no OpenAlex, título/resumo |
| --- | --- | ---: |
| Q01 | Dinâmica, formação e evolução de opinião | 7.629 |
| Q02 | Confiança limitada e mistura de crenças | 872 |
| Q03 | Consenso, médias e influência social | 1.225 |
| Q04 | Voter, q-voter e regras discretas | 996 |
| Q05 | Cultura e opiniões/ações | 1.771 |
| Q06 | Redes adaptativas | 159 |
| Q07 | Modelos cinéticos e compromisso | 54 |
| Q08 | Assimilação enviesada e influência negativa | 1.628 |
| Q09 | Base empírica e validação | 960 |
| Q10 | Agentes com modelos de linguagem | 112 |

Essas contagens foram observadas em 8 de setembro UTC, com corte de publicação
fixado no dia 7. A soma de 15.406 inclui sobreposições e não é o tamanho do
corpus. Uma faixa de referência para a união do OpenAlex vai de 7.629 a 15.406
registros, tomando esses totais observados como base, antes de deduplicação por
trabalho e da contribuição das outras fontes. As consultas ocorreram em um
índice dinâmico; a aquisição aprovada deverá medir a união efetiva. Não
há fundamento para prometer que a triagem caberá numa única janela de uso.
Quatro blocos bastariam para cobrir os seeds conhecidos, mas o v2 mantém as
dez famílias: reduzir só por esse conjunto de ajuste ocultaria temas e
literatura recente que ele representa mal.

O teto é de 100 páginas com 100 registros por literal em cada índice. Ele
comporta os totais medidos do OpenAlex; nas outras fontes é um limite
operacional explícito, sujeito ao diagnóstico e à paginação efetiva. Atingir
um teto produz estado incompleto. Não autoriza descartar o restante. DBLP
pesquisa substrings de título combinadas por OR, e arXiv pesquisa os campos
de metadados declarados na API; as diferenças de tradução ficam literais no
JSON. DBLP e arXiv não aplicam o corte de data no provedor nesta versão:
o registro original deve sustentar a data durante a elegibilidade. Uma data
incompleta permanece incerta, sem exclusão por suposição.

No DBLP, Q03, Q04 e Q06 foram divididos em subblocos de até dois termos.
Uma sondagem com 90 segundos de timeout no cliente demonstrou que o servidor
cancelava o filtro após cerca de 30 segundos. A divisão mantém a união exata
dos termos e a ordem das famílias, sem ampliar timeout ou contornar limites
do provedor. A equivalência é dos predicados num grafo fixo; contagens dos
subblocos se sobrepõem, e a paginação limitada não prova igualdade do corpus
efetivamente observado. Os pilotos e seus sucessores ficam vinculados na
matriz de resultados.

## Próximos atos do estudo

Após revisão do protocolo concreto, a aprovação pode ser registrada com o hash
e a revisão do Git pelo agente, sem pedir que Davi copie hashes. A aquisição
deve produzir o corpus e os casos de calibração. Davi é o responsável pelas
exportações controladas de ACM/IEEE, pelos julgamentos de referência e pela
auditoria da amostra e das extrações. O scaffold existente prepara os casos,
mas nenhum agente registra uma leitura humana que não ocorreu. Aceite do
landscape e da síntese continua posterior aos artefatos e à sua revisão.

As exportações são métodos suplementares previstos, ainda sem consultas
registradas neste candidato. O importador atual aceita apenas o perfil IEEE
RIS, que exige fonte, consulta literal, permissão e sessão de exportação
vinculadas ao protocolo. ACM ainda não tem importador implementado. Antes de
incorporar esses registros ao corpus, será necessário registrar as consultas
e os limites num sucessor e validar o formato real exportado. A aprovação das
consultas por API não torna essas rotas automaticamente executáveis. O
[contrato de aquisição](../../../../../docs/process/systematic-review-acquisition.md#controlled-ieee-ris-import-and-mixed-composition)
descreve essa fronteira.

O plano de triagem mantém dois revisores cegos por registro, lotes retomáveis e
fila de decisões do owner. Não converte o mapa em amostragem de conveniência
para fazê-lo caber num orçamento ainda não calibrado.

As consultas completas, incluindo a emenda do bloco Q03, estão no JSON. Os
insumos diagnósticos estão em [search-design](../search-design/2026-09-07/README.md).
A matriz legível e os hashes dos diagnósticos estão em
[resultados reproduzidos](../search-design/2026-09-07/results.md).
A delimitação de campos segue a
[referência oficial de busca do OpenAlex](https://help.openalex.org/api/searching/)
e seu [mapeamento de título/resumo](https://help.openalex.org/access/oql-spec/).
A divulgação de consultas e limites segue o objetivo de rastreabilidade do
[PRISMA-S](https://link.springer.com/article/10.1186/s13643-020-01542-z).
