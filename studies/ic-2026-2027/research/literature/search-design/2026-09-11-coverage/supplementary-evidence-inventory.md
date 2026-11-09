# Evidência suplementar retida

Conferência local de 16 de setembro de 2026, sem nova coleta ou alteração dos
registros. A ausência de um recibo no novo ledger de métodos não significa
ausência de atividade anterior: há bibliografias extraídas, recuperação de
identificadores e diagnósticos de consultas preservados. Esses materiais ainda
precisam ser vinculados às obrigações do protocolo para uma disposição formal.

## Bibliografias e fontes

| Manifesto | Fonte retida | Referências | Arestas DOI | DOIs distintos |
| --- | --- | ---: | ---: | ---: |
| [Starnini](starnini-reference-edges.json) | HTML arXiv 2507.11521v1 | 835 | 720 | 720 |
| [Flache](flache-reference-edges.json) | HTML oficial JASSS 20(4)2 | 174 no manifesto; 175 na fonte | 126 | 126 |
| [Wang / Neurocomputing](neurocomputing-reference-edges.json) | Depósito Crossref de 10.1016/j.neucom.2026.133705 | 185 | 161 | 158 |

Os arrays foram recontados. A união contém 950 DOIs em 1.007 arestas, para
1.194 entradas nos manifestos, com sobreposição; Flache e Wang acrescentam 230
DOIs à união de Starnini. Os 720 localizadores de Starnini e os 126 de Flache
existem nos respectivos HTMLs retidos e contêm os links DOI registrados. As 161
arestas de Wang correspondem exatamente ao campo DOI e à atribuição
`doi_asserted_by` das referências depositadas no Crossref. Isso comprova o
vínculo documental observado, não a identidade científica ou a inclusão do alvo.
Os recibos das fontes datam de 12/09/2026, às 01:25:12 UTC para Starnini e
01:38:32–33 UTC para Flache/Wang. São anteriores à aprovação do protocolo3 às
01:59:30 UTC; permanecem evidência exploratória anterior, sem alterar essa data.

A revisão independente encontrou uma omissão no manifesto Flache: o HTML
preservado tem 175 parágrafos identificados na seção de referências, mas somente
174 aparecem no manifesto. O localizador `allahverdyan2014`, correspondente a
*Opinion dynamics with confirmation bias* (PLoS ONE, 9(7), e99557), não consta
das arestas nem dos localizadores sem DOI. A contagem foi confirmada na fonte.
Os 174 registros e o total de 1.194 acima continuam sendo os denominadores dos
manifestos originais; não representam extração integral das três bibliografias.
A referência omitida permanece pendente de reconciliação explícita. Esta nota
não lhe atribui DOI, identidade validada ou elegibilidade, nem altera o manifesto.

O [sucessor da extração Flache](flache-reference-edges-v2.json), SHA-256
`d176f43f2c5c511d7a9e2349291053d967b1cf542dfc13714c874ff0f7469745`,
vincula o hash do predecessor e a mesma fonte. Seus 126 localizadores com DOI e
49 sem DOI cobrem exatamente os 175 parágrafos identificados. O novo localizador
permanece sem DOI: a página JASSS não fornece esse vínculo. Com esse sucessor,
as três extrações representam 1.195 referências; as 1.007 arestas e a união de
950 DOIs permanecem iguais. Nenhuma consulta aprovada ou execução foi alterada.

Há uma proposta de reconciliação entre fontes, separada dessa correção: a resposta
arXiv já adquirida em `search.arxiv.q01`, SHA-256
`b201fd154406be648bf8329e23e72f9ee08d1a578a744b665f60c55afeb4fa91`,
contém a entrada `http://arxiv.org/abs/1411.4328v1`, o título correspondente,
A. E. Allahverdyan e Aram Galstyan, `PLoS ONE 9(7), e99557 (2014)` e o DOI literal
`10.1371/journal.pone.0099557`. O apêndice liga essa página à observação
`arxiv.cfa8bc60e268d48b33815680`. Portanto, a omissão na extração de Flache não
comprova um artigo ausente da aquisição. Ela também não permite transferir o DOI
para a fonte JASSS ou fundir manifestações sem resolução própria de identidade.

Starnini conserva 113 referências sem DOI e [dois links malformados](starnini-unresolved-reference-links.json).
Flache conserva 48 referências sem DOI; Wang conserva 24. Estes dois últimos
manifestos mantêm `target_identity_verified=false` em todas as arestas e
`eligible_primary_study_count=null`. Starnini declara explicitamente que não
estabeleceu inclusão científica nem saturação. Nenhum desses campos foi alterado.

| Artefato | SHA-256 do manifesto | SHA-256 da fonte reaberta |
| --- | --- | --- |
| Starnini | `4f46896898b0551f96c92ee5da7f09ac9ff8143f0812fce737b8e5e1dc0cc230` | `b429006dd552984cccddb1e8080cca3c7c7fc985b2c9075bd03561c640b53da1` |
| Flache | `5b5cae67f92d334e9abacc40f64618ce1d214a796122cce19fbf26c28b13a145` | `393eed8b2105e9f9fb0c8191c4cf39e4caa4f732797bb21d4128155a5a030999` |
| Wang | `ac2931e98aa203fcd3d0d7baa288183e878bbcd5853a4e8abb3d44aae4a289dc` | `5d0d5f1ca1a7920f695c81cfe8a48c22b923c5b40609c05fd877d085f20a3496` |

## Recuperação registrada e consultas

O [protocolo3](../../protocol/opinion-dynamics-systematic-map-v3.json) registra
936 estratégias Crossref com filtro de DOI exato. Elas contemplam 919 dos 920
DOIs não-arXiv das três bibliografias. A exceção é `10.5281/zenodo.13787981`,
[explicitamente separado para fonte própria](../../protocol/opinion-dynamics-systematic-map-v3-review.md#recuperação-de-identificadores),
sem atribuí-lo ao Crossref. As outras 17 estratégias cobrem identificadores
fora dessa união. Os 30 DOIs arXiv estão representados nas 31 consultas oficiais
por identificador; a consulta adicional é `id:2501.14844`.

O apêndice retido de aquisição tem SHA-256
`2d57a34b28692e527ec508f8b8a156e3434ff52b01869099e15b2dbbd456b07a`.
Suas 1.027 estratégias correspondem integralmente ao protocolo3. Nas 936 linhas
Crossref, há 1.871 páginas e 935 observações; todas as linhas estão registradas
como `complete`, com exaustão na última página e no máximo duas páginas por DOI.
Foram reabertos e conferidos tamanho e hash dos 937 objetos brutos distintos
referenciados por essas páginas. A consulta `metadata.crossref.doi.0883`, para
`10.21338/ess11e02_0`, terminou sem registro. Ausência no provedor não é exclusão
científica. Essas páginas estão datadas de 12/09/2026, entre 03:13:51 e 04:16:23
UTC. Esta conferência verificou os artefatos e relações descritos; não
substitui o replay integral do runtime de aquisição.

A [proposta de expansão](query-expansion-proposal.json), SHA-256
`23b689b599a87b230b204048c9e71d494ba54d1bdb7afba37fa961a3d74d4730`,
contém seis famílias. Q11, Q12, Q13, Q15 e Q16 aparecem literalmente nas
estratégias OpenAlex aprovadas. Q14 foi refinada com termos de domínio e dividida
em Q14a/b/c, nas janelas 1970–2009, 2010–2019 e 2020–2026-09-11. A proposta
original não é a consulta executável final. O [desafio64](baseline-challenge-64.json),
SHA-256 `1b964cce01eceefa765874f22733a628795a1fe8cd815deed700ef2b659612cc`,
mantém 38 correspondências por DOI, duas somente por título e 24 ausências no
baseline. Os números foram recontados nos candidatos; não são recall
populacional nem falso negativo científico confirmado. Os leads posteriores
permanecem em seus registros separados, fora desse denominador.

## Relação com as obrigações do protocolo

As listas de buscas, fontes, métodos suplementares e critérios de conclusão são
idênticas no protocolo3, no [protocolo4](../../protocol/opinion-dynamics-systematic-map-v4.json)
e nas duas propostas5, incluindo a de atualização editorial. O digest canônico
de3 é `fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f`,
igual ao da aprovação de aquisição; o de4 é
`ff8a14178e725983945c049e75181e8eeb1f3cee56a831e714cc78b09245d413`.
Esses digests de contrato não são os hashes dos arquivos JSON formatados.

| Método previsto | Evidência encontrada neste recorte | Limite restante |
| --- | --- | --- |
| `secondary_study_seed` | Três fontes secundárias identificadas e retidas | Não tornam os alvos estudos primários elegíveis |
| `backward_citation_chasing` | Arestas, localizadores e pendências das três bibliografias | Não documentam duas rodadas sem novos elegíveis após deduplicação |
| `crossref_identifier_recovery` | Consultas registradas, páginas retidas e estados de execução descritos acima | Identidade, referências sem identificador e elegibilidade exigem disposição própria |
| `forward_citation_chasing` | Nenhum registro de citantes identificado nestes manifestos | Não inferir execução ou saturação a partir de referências citadas |
| `manual_google_scholar_check` | Nenhum registro desse método identificado neste recorte | Requer sua própria evidência manual |
| `controlled_acm_digital_library_export` / `controlled_ieee_xplore_export` | Nenhum export controlado identificado neste recorte | O protocolo reserva os exports a Davi; não inferir entrega por cobertura de outros índices |

O protocolo exige duas rodadas consecutivas sem novo trabalho elegível após
deduplicação, preservando seeds, arestas, consultas, datas e registros de fonte.
As fontes conferidas sustentam atividade suplementar parcial e recuperação de
identificadores. Não sustentam saturação, aceite do corpus, execução integral de
todos os métodos ou uma declaração de incompletude feita pelo Owner. A ligação
ao ledger deve preservar esta distinção e os vínculos originais.
