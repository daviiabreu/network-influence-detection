# Revisão independente da ponte de identidade

Não foram encontrados defeitos acionáveis de especificação ou de padrões no escopo revisado. A ponte pode seguir para integração técnica; esta conclusão não aprova identidades, corrige metadados ou libera o corpus para screening.

## Escopo congelado

Revisão direta de `2bfa4ea33b637fa1a3fc61cdffac8ad3ffba4ded` para `1b4b1ae7716b656762dcce3023940b29707ef83e`, no checkout privado `corpus-identity-transition-20260913`. Foram examinados os cinco arquivos do diff: o módulo `review_corpus_identity.py`, seus testes e os processos de revisão, corpus e adjudicação. O diagnóstico anterior `identity-transition-plan.md` não foi usado como descrição da implementação.

SHA-256 do diff: `f6e23f0b9201d1812e32b9794111a66626e02698e8b6fa8473f239146b00189b`. SHA-256 do módulo: `9ad379af195e6bcdc1c3f15cd95a87fd8da4e83f761c650053326fe1758a954b`.

Foram conferidos arquitetura, instruções dos dois projetos e processos de revisão sistemática, corpus, adjudicação e validação de engenharia. A inspeção incluiu os contratos e os caminhos existentes de metadata, preparação, aquisição, deduplicação, operação durável e fila nativa. O `repository_commit` do contexto mantém a vinculação da aprovação do protocolo; ele não substitui o registro separado da revisão do código usado na execução.

## Integridade conferida

| Requisito | Evidência |
| --- | --- |
| Pai integral reproduzido | `_derive`, linhas 182–202, reabre o recibo schema 2 e chama o replay de metadata, que reproduz preparação e aquisição. Confere recibo e referência completos; não confia só nos totais declarados. |
| Partição sem perdas | Linhas 207–236 preservam as obras sem título, recusam candidatos que as toquem e exigem igualdade exata de obras tituladas e candidatos após deduplicação sob a mesma política. IDs, membros e sinais não são recalculados de forma permissiva. |
| Linhagem e fontes | Linhas 185–245 exigem novo contexto, protocolo/revisão herdados, hash exclusivo do pai e fontes exatas. Os testes recusam alteração de contexto, pai forjado, bytes corrompidos e pai válido ligado ao runtime de outro corpus. |
| Subfila nativa separada | Linhas 246–309 derivam contexto próprio e mantêm o resultado agregado `incomplete`. A publicação usa `DedupeQueueInputs` e `prepare_adjudication_queue`; o recibo da transição não valida como `CorpusStageReceipt`. Não há handler que promova o corpus. |
| Pendências preservadas | O recibo carrega propostas sem título, candidatos de metadata, conflitos e fontes integrais do pai. Um probe concluiu apenas a fila nativa sintética e confirmou que as nove ausências de título e os dez conflitos continuam no agregado incompleto. |
| Replay e recuperação | Linhas 362–397 usam o armazenamento de operações e comparam recibo e bytes derivados. Preparação repetida retorna os mesmos artefatos; replay não altera o snapshot; despacho incerto exige reconciliação. |

Não houve violação concreta de manutenção ou convenção nos arquivos alterados. O uso dos contratos e do armazenamento existentes mantém as responsabilidades dentro de `orchestration`; não foi introduzida política científica nova.

## Verificação executada

Resultado independente: **27 testes passaram em 2,36 s** — os 25 testes do novo módulo e dois probes adicionais, todos com fixtures sintéticas. `git diff --check 2bfa4ea 1b4b1ae` também passou. O interpretador veio do ambiente do workbench, com `PYTHONPATH` explicitamente apontado para o checkout revisado; o caminho do módulo importado foi conferido antes dos testes.

O primeiro probe criou dois pais sintéticos válidos e distintos e tentou preparar a transição do corpus B com o runtime de metadata do corpus A: a operação foi recusada sem novas escritas. O segundo completou a subfila de identidade na fixture com nove títulos ausentes e dez conflitos, depois reproduziu o agregado byte a byte: `incomplete`, sem liberação de screening e com todas as pendências retidas.

Comando executado no checkout revisado:

```bash
PYTHONPATH=workbench/src:workbench \
  /Users/davi/Documents/github/research-workbench/workbench/.venv/bin/python -m pytest -q --tb=short \
  workbench/tests/workflow/test_review_corpus_identity.py \
  /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/identity-transition-review/SYNTHETIC/test_review_probes.py \
  --basetemp /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/identity-transition-review/SYNTHETIC/run-1 \
  --override-ini addopts= \
  --junitxml /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/identity-transition-review/SYNTHETIC/test-results.xml
```

Os probes e recibos permanecem privados em `/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/identity-transition-review/`. Hash do probe: `9bae45da9a6c465a184922e6ef7123d2f1b93efa7b864da125de7d4cf3d92db7`. Hash do JUnit: `9cad7bdc80fda5bddc50da1b2213533286c59a24281236821cfc12aae2d23acb`. `review-evidence.json` contém os hashes dos cinco arquivos revisados.

## Limites

Não foram alterados código, candidatos ou artefatos reais. As decisões presentes nos probes são exclusivamente sintéticas; nenhuma decisão humana de pesquisa foi produzida. Não houve chamadas de modelo nem execução de suíte científica. A revisão não executou a matriz completa, Ruff ou mypy novamente; os resultados informados pelo autor e a integração da coordenação são evidências separadas.

A aplicação ao corpus real ainda precisa conservar o CAS e os journals integrais, configurar o limite explícito de bytes adequado aos registros retidos, registrar a revisão exata do código/driver e verificar o replay resultante. Completar a subfila de identidade continuará insuficiente para resolver metadata ou os conflitos de prontidão do corpus.


## Adendo — conferência independente do resultado real

O resultado real não apresentou achados acionáveis no escopo conferido. O
agregado continua `incomplete` e a subfila nativa está em
`awaiting_owner_action`, sem liberação de screening. Este adendo preserva
integralmente a revisão anterior, cujo SHA-256 é
`e11bf090b757e1ea81ab3dfeb9f568d471d170527bb62ea9dce696e8f20995c4`.

Foram lidos diretamente os JSONs finais e os objetos correspondentes do CAS
em `~/.local/state/research-workbench/corpus-preparation-20260913/identity-transition-v1/`
e `~/.local/state/research-workbench/broad-research-20260911/acquisition-v3/artifacts/`.
O verificador desta revisão não importou o driver nem chamou `prepare`,
`replay` ou o algoritmo de deduplicação. Reconstituiu a seleção a partir dos
registros do pai e comparou integralmente os objetos e seus bytes canônicos;
a comparação de obras e candidatos usa a deduplicação do pai como referência.

### Conteúdo e partição

| Verificação independente | Resultado |
| --- | --- |
| Registros do pai, IDs distintos | 54.570 |
| Registros selecionados, IDs distintos | 54.561 |
| Registros retidos nas propostas sem título | 9 |
| Interseção entre selecionados e retidos | 0 |
| União dos dois grupos | Igual ao conjunto integral do pai |
| Obras tituladas | 46.391 objetos integralmente iguais ao pai |
| Candidatos de identidade | 20.964 objetos e IDs integralmente iguais ao pai e à fila original |
| Pendências de metadados | 9 objetos preservados, iguais à deduplicação e à fila originais |
| Conflitos de prontidão | 10 objetos preservados, iguais ao recibo e à fila originais |
| Fontes vinculadas | 1.536 referências integrais preservadas |

A seleção foi derivada filtrando exclusivamente os nove IDs retidos e
ordenando os registros restantes por `record_id`. A lista resultante coincide
com cada campo dos 54.561 registros publicados e com seu SHA-256 canônico.
A associação entre obras e manifestações também forma uma partição exata
sem repetição. Nenhum candidato de identidade toca uma observação retida
sem título. As nove propostas retidas continuam com `canonical_title=null`.
Foram recalculados os digests internos das duas deduplicações e conferido o
vínculo entre a deduplicação nova e os bytes exatos da seleção.

O recibo local é byte a byte o objeto do CAS indicado em `receipt-ref.json`.
As referências do pai, dos registros, da deduplicação e da fila foram
conferidas em hash, tamanho, classe de acesso e caminho. A subfila contém
somente contexto, entradas e entradas submetidas, sem decisão humana.
Seus registros, deduplicação, protocolo e fontes coincidem com as referências
esperadas. Os contextos do agregado e da subfila são distintos e seus hashes
foram recalculados. O recibo preserva os códigos de pendência do pai,
`screening_ready=false` e `scientific_eligibility_assessed=false`.

### Seis novos objetos do CAS

A diferença entre o inventário preexistente e as árvores atuais contém
exatamente seis objetos. Todos foram lidos e conferidos em hash, tamanho,
caminho endereçado pelo conteúdo e modo sem permissão de escrita. O pedido
operacional e sua resposta foram reconstituídos por serialização canônica
independente, além dos quatro artefatos diretamente referenciados pelo recibo.

| Objeto | Bytes | SHA-256 |
| --- | ---: | --- |
| Registros selecionados | 116.448.380 | `d9e9289e18df4d2db4d9554ca707bc7385025950c20a437daae7d7d58c200c9e` |
| Deduplicação para a subfila | 29.383.919 | `52db5c30e794937c45478c8677c47ee85aebbded1789add8d963128c000adb39` |
| Fila nativa | 770.086 | `fcc36f8ea40020b7d9b7ce75d1916cf0a08216c76ac168b3c5b3522695be3054` |
| Recibo da transição | 397.781 | `f01e6185740e71849e8f72211891e38cd1f97f5d3c6b050ea3b5c95186ab088b` |
| Pedido operacional | 877 | `920ad0979300e7a1adad9299ba314c24adf35658dab7f5226ef7cec308b75615` |
| Resposta operacional | 265 | `27827bc18d33f3faa44a49127c9c93fd2f7ee6de00ed15c6446f7f0382f0c901` |

### Inventários, execução e limites da evidência

Foram comparados os registros de metadados dos 11.821 arquivos preexistentes
com seus valores atuais: dispositivo, inode, tamanho, mtime, ctime, modo,
UID, GID e número de links. As 11.832 entradas do inventário retido também
conferem com o filesystem atual; suas entradas preexistentes são iguais ao
baseline, incluindo as 1.536 fontes. Os hashes dos arquivos de inventário
conferem com os vínculos registrados no resumo e nos metadados da execução.

Foram relidos e rehashados o driver e os 68 módulos registrados antes da
execução; os caminhos dos módulos permanecem dentro do checkout congelado e os hashes
coincidem com os recibos. O código de execução registrado é
`1b4b1ae7716b656762dcce3023940b29707ef83e`. A referência
`3b71a915252c7986f3dbf5310117eace4c8fa98f` continua sendo o vínculo herdado
da aprovação do protocolo no contexto, sem substituir a revisão do código
executado. O driver registra o intervalo UTC de
`2026-09-14T01:50:53.093136+00:00` a `2026-09-14T01:54:06.197647+00:00`.

A igualdade do replay nativo e sua ausência de escritas são declarações do
driver apoiadas por seus inventários; o revisor não repetiu esse replay.
A conferência própria aqui é a comparação direta dos objetos, bytes,
partição, vínculos e metadados descrita acima. O rehash de todos os
1.123.492.062 bytes dos 11.821 arquivos preexistentes foi executado pela
coordenação e está em
`integration-checks/identity-source-preservation-recheck.json`, SHA-256
`9f291392680850f070400b93e5086230e9d865f10ffa7d2bd995dc2876b7841b`.
Esse recibo foi lido e teve seu hash confirmado; o rehash integral das fontes
não é apresentado como execução deste revisor.

| Evidência da conferência | SHA-256 |
| --- | --- |
| `summary.json` | `b142684a62da2b281e40fed9dbde651d28d9fa751c4b01333269fbf20097d6a0` |
| `receipt-ref.json` | `62d0092ac3ab6be4c75577ece6dbd72e046bb57c5ad1a71d2a32090e05c06ec5` |
| `execution-metadata.json` | `b2863487506be57c3832b1a043f09c93570dd4a65fbe227a3d8eb92e587504f5` |
| Baseline preexistente | `1898a58cb3721799e04cd33d192272668e8660d4568dbdded23be390d80ea755` |
| Baseline das fontes | `60ccf9c08d7ae8c61ad69a9a4479462490c37a97d74c5d698bd9d33f16e7beb6` |
| Inventário retido | `7fae1deca8f3c01bd3b1bef1b91f65c29abb3fcbefc20a60fcfd44c7fe435cd8` |
| Inventário dos novos CAS | `b382c98c431e869d9ab9c6b0f09614e189375dd1e8b2a034f7b545575ca471ab` |
| Verificador independente | `1ffb5dcab3d1da05483f31338515c106c3ad3dedabaf5f7a339af8c43e999bef` |
| Resultado independente | `8bd8058d939111447eb325a89b91f8d90dd3aa0a0f2059119b48348a08609b6d` |

O script `check_result.py` e o recibo `independent-result.json` permanecem em
`~/.local/state/research-workbench/corpus-preparation-20260913/identity-transition-review/real-result-20260913-1KyGHN/`.
O comando usou o Python do workbench com `PYTHONDONTWRITEBYTECODE=1` e
terminou com código 0. O recibo guarda hashes e resultados de comparação,
sem textos de fontes ou julgamentos. A revisão não alterou o CAS, os
inventários da execução ou as decisões. Não produziu títulos, merges ou
rótulos humanos; não houve modelos, aquisição de rede, matriz completa ou
execução científica. A conclusão confirma a transição de preparação e suas
pendências, sem resolver a subfila ou o corpus.
