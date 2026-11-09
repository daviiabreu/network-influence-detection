# Revisão independente de identidade e preparação da calibração

Revisor: `metadata_primary_sources_v4`. Data local: 13/09/2026
(America/Sao_Paulo). Escopo: candidatos de identidade, recuperação do material
antigo e, quando disponibilizado como candidato final, o sucessor de 50 casos.
O relatório de metadados autorado por este revisor não integra a revisão.

Nenhum achado bloqueante foi encontrado na compactação da fila de identidade
ou na preservação e recuperação do formulário antigo. A revisão do novo lote
v3 permanece pendente de disponibilização do candidato final. Este resultado
parcial não confirma prontidão científica, execução de calibração ou aceitação
do corpus.

## Candidatos examinados

| Candidato | SHA-256 examinado |
| --- | --- |
| `identity-audit.md` | `f40866c10789027eacaccf72e87f033b15d9dcd25224a3622a1c9afe2f0f6510` |
| `identity-audit.json` | `d4f34ac648efe79c26c2e978eeeb1319fe052eaf3ebef643fc26187126834be1` |
| `calibration-readiness.md`, recuperação do material antigo | `13a183a085b4c21b2b3e4bf36f5b4f903a6b66302d2679d941668ef27f3920cc` |
| Cartões privados `review-cards.json` | `4779f20d33072b10d68c18e4535555ad7684b7e1333c4c5441a9ec525059086f` |

A rubrica aplicada foi a preservação integral dos candidatos e das evidências,
a distinção entre agrupamento de revisão e identidade científica, a reprodução
da seleção, a disjunção por obra e página de evidência e a ausência de
julgamentos humanos fabricados. Foram consultados o
[processo de revisão](../../../../../../docs/process/systematic-review.md),
o [processo de calibração](../../../../../../docs/process/systematic-review-calibration.md)
e a implementação corrente de identidade para interpretar os formatos.

## Recontagem independente de identidade

A conferência reconstruiu o grafo a partir do CAS de deduplicação, da fila e das
observações originais; não executou o gerador do autor. O processo leu os
registros localmente e retornou apenas contagens, IDs, hashes e comparações.
Não imprimiu resumos nem textos integrais. Os três artefatos de entrada foram
validados por SHA-256 antes do cálculo.

| Quantidade reconstruída | Resultado |
| --- | ---: |
| Observações / IDs de observação únicos | 54.570 / 54.570 |
| Propostas de obra | 46.400 |
| Propostas com título / sem título | 46.391 / 9 |
| Candidatos originais preservados exatamente uma vez | 20.964 |
| Pares de obras propostas | 10.754 |
| Componentes | 4.990 |
| Obras / observações nesses componentes | 12.025 / 15.950 |
| Maior componente | 44 obras |
| Componentes de duas / três / quatro obras | 3.492 / 1.168 / 254 |

A partição cobre cada observação original uma única vez. O conjunto completo de
componentes reconstruídos coincide com o dos cartões. Cada cartão contém
exatamente os `candidate_id` do par de obras correspondente; cada ID aparece
uma vez no conjunto de cartões. Os campos bibliográficos das 12.025 propostas
nos cartões são iguais aos do CAS, e os campos de origem correspondem aos
registros originais. `owner_decisions` está vazio.

| Categoria | Pares de observações | Cartões |
| --- | ---: | ---: |
| Conflito com identificador tipado compartilhado | 442 | 442 |
| Ponte sintática arXiv/DOI | 4.750 | 1.951 |
| Somente título | 15.772 | 8.361 |
| Total | 20.964 | 10.754 |

A classificação acima também foi recalculada. A categoria agregada de cada
cartão segue a precedência declarada, mas preserva as contagens das categorias
de cada candidato. As ligações `arxiv:ID` e `doi:10.48550/arxiv.ID` permanecem
pistas sintáticas no candidato; não há disposição de identidade nem inclusão
científica derivada delas. O documento mantém explícita a ausência de
verificação individual dessas ligações.

Os 14 hashes e tamanhos de entradas/fontes citadas em `verified_artifacts`
foram conferidos. Para os dez bloqueios de DOI plural, os índices de bindings
foram resolvidos diretamente nos snapshots SPARQL originais: DOI, ID DBLP,
título, ano e veículo coincidem com os campos publicados pelo candidato. A
conferência atesta a presença na fonte, sem afirmar equivalência bibliográfica
entre os DOIs. Nenhum corpus ou snapshot original foi alterado nesta revisão.

## Material antigo de calibração

Os bytes atuais de `owner-material/material.json` e `owner-material/index.html`
correspondem ao recibo original `preparation.json`:

| Artefato | SHA-256 conferido |
| --- | --- |
| `material.json` | `8b6004bdde869957b38d825c7c5674de98c5886b8dc85877fe2b2542e67756ce` |
| `index.html` | `aba608e72251c0e0f7dffe58cce21bcc687afbb64efe89bd649f16359b841068` |

Há 50 `work_id` distintos e cinco casos em cada uma das famílias Q01–Q10.
Os quatro campos de referência do modelo estático original estão vazios nos
50 casos. As flags continuam `formal_calibration_suite=false` e
`fresh_v3_source_binding_pending=true`, com aquisição v2 e critérios v3.
Não foi atribuído ao material o estado de suíte válida ou calibração aprovada.

Uma requisição HTTP direta a `http://127.0.0.1:8767/` retornou 200 e o hash
exato do HTML original. As requisições a `/material.json`, `/preparation.json`
e ao caminho do diretório irmão retornaram 404. Essa conferência não abriu o
navegador, não executou o JavaScript, não acessou `localStorage` e não procurou
ou leu arquivos de respostas humanas. A verificação dos campos vazios usou
somente o modelo estático ligado ao hash original.

A reprodução independente da nova seleção, sua disjunção por obra e página e
a preservação de referências vazias serão avaliadas quando o sucessor v3
estiver concluído. Essa parte não é coberta pelo resultado acima. Não houve
execução de modelos, calibração científica ou matriz completa de testes.


## Adendo — revisão final do formulário e scaffold v3

O candidato final v3 foi examinado depois da revisão acima. Este adendo
preserva integralmente os bytes da avaliação anterior, cujo SHA-256 é
`634ced35cab81b99dbeea3113ae9e78e111a9b01fc140964a03bff5bca8b6995`.

**Achados priorizados:** nenhum defeito material P1, P2 ou P3 foi encontrado
no escopo de preparação examinado. A pendência de revisão do sucessor,
registrada anteriormente, fica atendida por este adendo. Permanecem pendentes
a autoria humana, o histórico de ajuste, a validação da suíte preenchida e a
execução científica. A revisão não aprova calibração, elegibilidade ou corpus.

### Artefatos congelados examinados

| Artefato | SHA-256 |
| --- | --- |
| `calibration-readiness.md` | `4a6cd12ca65d44f7124b0f580bd45db2293a13979ce9c12e6872558a84335038` |
| Scaffold com extração | `8c00d9c368a0049c1dd2bdb2e28301b5e61deb323778ca7d6adc258484731902` |
| Seleção com extração | `316b118739cb6e6eebd3b7cebe748d805124bda4523a7fb9e404a7c5278b62e7` |
| Auditoria de sobreposição com desenvolvimento | `97ab0148462af98d0fe42b277cb93000bae1f74546728dea20e57bbc8b377207` |
| `form-binding.json` | `6e32974f83f57d25f9d00bfabe1bf94a611230296818e34128300e71b9237230` |
| HTML v3 | `3861d7e5d7698e394583f3b5454ac974eb39ac9cc91705a1431657faec849a2f` |
| Pacote embutido, serialização canônica sem o próprio digest | `9a698c9f7422ea95f7aa39e01ec15965f340f1df8fc8b1399f072bd83e74ae8e` |
| `FullTextRecord` | `ac9adff69ca7c58bee0882a38b2b9df1aa54a014ca707dc9baac2e57e4c07396` |
| PDF arXiv:2508.17711v3 | `a7eea3ee9fbdaf40403b2a0fc5de2c2fd780021aa853fef0aecff01c2c986f0c` |

Os arquivos de seleção, scaffold e recibos examinados pertencem a
`~/.local/state/research-workbench/broad-research-20260911/calibration-preparation-v3-extraction-20260913/`.
O HTML e o PDF públicos pertencem a `owner-form-v3-20260913/` no mesmo diretório
base. Nenhum desses candidatos foi editado pela revisão.

### Seleção, vínculos e exposição anterior

A seleção foi reconstruída independentemente a partir da projeção original e
da deduplicação CAS, usando a semente 20260913, a preferência de fonte,
a ordenação SHA-256, a substituição por fonte disponível e os dois casos
anteriores a 1995. O resultado coincide com a ordem exata dos 50 casos e dos
respectivos representantes. A execução de reconstrução não chamou o gerador
do autor.

A reserva legada foi rederivada por identificadores da mesma fonte nas
manifestações originais: cada caso legado aponta para uma única proposta v3,
formando 50 obras e 75 páginas reservadas. A nova seleção tem interseção zero
com essa reserva por obra e por hash de página. Também não contém observações
presentes em candidatos de identidade pendentes.

A reprodução nativa das 71 páginas bibliográficas conferiu seus bytes e suas
normalizações. As 78 manifestações selecionadas correspondem integralmente
às observações da projeção e aos registros reproduzidos. Foram preservados
50 casos, 13 representantes OpenAlex, 14 arXiv e 23 DBLP, incluindo os 26
representantes sem resumo. Os 120 campos selecionáveis no HTML coincidem com
os títulos/resumos disponíveis: cada texto, ID de manifestação, hash de
registro, hash de página e prefixo de locator foi comparado com a fonte
reproduzida, sem imprimir os textos.

Os 64 challenge DOIs e as 16 sementes foram relidos dos artefatos de origem,
com seus hashes conferidos. A reconstrução encontrou 133 propostas ligadas
aos leads e 218 páginas que as sustentam. Todos os 50 registros individuais
da auditoria de sobreposição coincidem com a recontagem: zero interseção por
obra, identificador ou título normalizado e **25 casos com páginas
compartilhadas**. A descrição de exposição anterior é, portanto, precisa;
não demonstra que as páginas sejam inéditas para o ajuste da triagem. O
histórico permanece explicitamente pendente, sem declaração de `no_prior_tuning`.

### Scaffold e extração

O scaffold contém 50 tarefas `screener_a`, 50 `screener_b` e uma `extractor`.
Todas as tarefas de triagem têm estágio `title_abstract`; não existe tarefa
de triagem de texto completo. Os manifests vinculados são os existentes
`screener_a_v2.toml`, `screener_b_v2.toml` e `extractor_v3.toml`, com o protocolo
v3 exato. As tarefas de triagem mantêm cada obra e todas as suas manifestações.

Julgamentos, justificativas, locators de referência, trechos de referência e
extração de referência conservam os sentinelas esperados. O histórico de
ajuste também é um sentinela. Os IDs e hashes já preenchidos nesses objetos
são vínculos de origem, sem conteúdo de referência atribuído a Davi.

Os recibos da página arXiv, da licença e do PDF conferem em hash e tamanho.
A página retida identifica a versão `2508.17711v3` e o link CC BY 4.0. O PDF
ligado ao `FullTextRecord` é o mesmo disponibilizado no formulário. Cada um
dos **28 locators foi novamente resolvido pelo resolver nativo a partir do
PDF**, com igualdade integral do objeto de evidência. Os blocos respeitam
5.000 caracteres e cobrem todas as linhas das 26 páginas, sem lacunas. Os seis
campos correspondem ao protocolo: base empírica, lacunas, família de modelos,
estrutura da rede, materiais de reprodução e método de validação. Essa
verificação não avalia a interpretação científica dos trechos nem a fidelidade
da ordem visual de tabelas e colunas.

A CLI corrente foi executada somente em `validate-calibration-suite` com o
scaffold de 14.256.404 bytes. Ela alcançou o conteúdo e retornou código 2
porque ainda existem TODOs do Research Owner. A falha esperada não foi o
antigo limite de tamanho e não constituiu execução de modelo.

### HTTP, exportação e limites da QA

Requisições estáticas independentes a `http://127.0.0.1:8768/` e ao PDF
retornaram HTTP 200 com os hashes congelados. As rotas de seleção, scaffold,
fonte de extração e diretório privado legado retornaram 404. O HTML antigo
permaneceu com seu hash original. Esta revisão não abriu perfil de navegador,
não consultou `localStorage` e não leu ou exportou respostas humanas.

**A geração de exportação foi testada com dados sintéticos.** O código exato
da função de exportação e do construtor de extração foi retirado do HTML e
avaliado em uma VM JavaScript isolada, com DOM e downloads interceptados em
memória. Foram verificados três cenários: formulário vazio; uma resposta de
triagem sintética e seis campos de extração sintéticos completos; e extração
parcial com um campo ausente. O envelope preservou os vínculos do pacote,
protocolo, scaffold e tarefas; respostas vazias não ganharam julgamentos e a
extração parcial permaneceu rascunho, sem resultado completo. Foram
interceptadas três invocações de download; nenhum arquivo foi gravado.

Esse teste cobre a lógica de geração do JSON, não a interação visual completa,
a persistência real do navegador nem o recebimento de um download pelo sistema
operacional. O recibo headless do autor foi lido como evidência complementar,
sem ser apresentado como execução deste revisor. O JSON exportado é um
envelope de referências; a conversão posterior para suíte nativa é uma etapa
separada e não foi examinada ou aprovada neste adendo. Não houve teste de
conversor, suíte completa, inferência de modelo ou calibração científica.
