# Preparação da coorte disjunta v2 do mapa amplo

Em 25/09/2026, esta frente preparou insumos sem selecionar obras da coorte, executar triadores ou produzir referências. O recibo C4 ainda é a fronteira de seleção. A suíte de desenvolvimento `3044d04` conserva o resultado `fail`; nenhum resultado desta preparação altera esse estado.

## Exposição histórica

O inventário privado `exposure-inventory-v3-partial.json` registra 303 casos de três versões da suíte de desenvolvimento, mais 50 fichas legadas, consolidados em 100 IDs de obra propostos. Para cada obra retém identificadores, manifestações, hashes de páginas bibliográficas, hashes de texto integral quando presentes e tarefas de origem. Os insumos são ligados por SHA-256 no próprio arquivo. Seu SHA-256 é `d08a6c150652be1e16dadc16389bd52d85ec19edc737871a7b39e6c61d2e2a99`.

`complete=false` é obrigatório enquanto não forem auditadas as demais tarefas efetivamente exibidas a agentes, incluindo execuções fora dessas suítes, tarefas piloto e possíveis aliases de obras. O inventário não estabelece identidade C4: usa os agrupamentos históricos apenas para reservar material. Antes de fechá-lo, registrar os caminhos, hashes e contagens de cada store auditado; acrescentar todos os IDs, identificadores, manifestações, páginas e hashes integrais encontrados; resolver aliases contra a projeção C4; bloquear qualquer identidade pendente. O arquivo atual é um predecessor imutável. A correção será um sucessor privado com manifesto de vínculo, nunca edição deste arquivo.

## Textos integrais retidos

O pool privado `oa-pool-v2/manifest.json` registra 50 PDFs do arXiv sob CC BY 4.0 ou CC0, escolhidos mecanicamente entre observações da aquisição v3. A aquisição conferiu título e ID na página primária, guardou o hash da página, a URL da licença e do PDF, os bytes PDF em CAS privado e os hashes do texto nativo de cada página por `pypdf`. São 111.224.889 bytes PDF. O manifesto tem SHA-256 `7df642376cd0709d64e581d07f63fd65879035b808642033c98fe38da8316c12`. Diretórios são `0700`, arquivos `0600`. Não houve sobreposição de ID de obra, identificador, página bibliográfica de qualquer manifestação nem hash PDF com o inventário v3. As 140 tentativas sem retenção têm motivo no manifesto.

As páginas primárias são reabertas e retidas, byte a byte, em `oa-pool-v2/landing-sha256/`, sob os hashes registrados no manifesto. O primeiro pool, `oa-pool/manifest.json` (`814a4151a11d9100220d6c15b8188a6e365cf5db66c362a4afc9840f0bf7eb49`), fica como predecessor privado: 13 de seus 50 itens compartilhavam páginas bibliográficas com material exposto e não podem ser usados como reserva disjunta.

O pool é **provisório**: essas obras não foram selecionadas da projeção C4 e a auditoria integral de exposição ainda está aberta. Depois de C4, revalidar identidade, licença, hash do PDF e disponibilidade de texto nativo; importar cada obra elegível pela interface nativa de `FullTextRecord`, com locadores reproduzíveis pelo parser vinculado ao protocolo. Somente as que passarem esses gates contam para as 50 obras distintas de calibração de texto completo. Se restarem menos de 50, adquirir reservas adicionais antes de montar tarefas FT. Nenhum PDF ou texto integral está em Git.

`acquire_oa_pool.py` usa `pypdf` do ambiente travado do workbench; sua saída permanece fora dos dois projetos instaláveis.

## Sorteio após C4

`cohort_v2.py strata` exige o recibo nativo `corpus-screening-bridge-2` concluído, sua projeção exata e os registros originais vinculados pelo recibo. Produz um JSON privado `cohort-v2-c4-strata-1` com uma entrada por obra C4 em `representatives`: `work_id`, `manifestation_record_id`, hashes das páginas originais, família Q01–Q16, fonte (`openalex`, `arxiv`, `dblp`), presença de resumo, período anterior a 1995 e campos para identidade/alias e hashes integrais. Obras sem representante Q ficam marcadas e são recusadas. Revisar a tabela contra os registros originais e preencher aliases ou hashes integrais conhecidos antes do sorteio, criando um sucessor vinculado se necessário. `cohort_v2.py sample` reabre os registros originais e rejeita qualquer mudança nos campos derivados, além de exigir um sucessor fechado do inventário de exposição. O programa rejeita exposição por obra, ID de origem, identificador, manifestação, página bibliográfica e hash integral, e reserva identidades pendentes.

Cada estrato família/fonte/resumo é ordenado por SHA-256 de `calibration-cohort-v2-20260924:` seguido do ID da obra, com o ID como desempate. A semente inteira é `20260924`. O plano tenta 12 obras por Q01–Q16, depois oito marcadas como fonte/período sub-representado e gera ondas fixas de 50; registra faltas e recusas. As metas aproximadas de representante 52/56/92 e metade com resumo orientam a escolha prévia, sem forçar cobertura inexistente. A ordem e as ondas são congeladas antes de A/B. A progressão após 200 depende das contagens das referências adotadas, não de saídas dos triadores: ≥60 `include` por estágio, ≥1 `exclude`, ≥1 `uncertain`, ≥50 obras distintas em cada estágio. FT exige uma seleção própria de fontes permitidas e retidas. Distribuições e desvios devem acompanhar qualquer medida de recall, especificidade e `uncertain`.

## Adjudicação independente

`adjudication.py prepare` só prepara tarefa real se receber recibo C4 concluído e manifesto de ordem que inclua a obra. O pacote contém a tarefa exata, seu SHA-256, registro original e seus campos utilizáveis ou o pool FT integral com locadores. `adjudication.py validate` exige saída `cohort-v2-claude-reference-proposal-1` com `task_sha256`, `work_id`, `stage`, `model_family="Claude"`, `model_id`, `judgment` (`include`/`exclude`/`uncertain`), `criterion_id`, justificativa e citações. Em TA cada citação vincula `record_id`, `raw_artifact_sha256` e campo fornecido; em FT cada citação deve ser membro literal do pool da tarefa. A saída fica `AI-proposed_pending_owner_adoption`. Validação estrutural e de locadores não prova acerto científico.

A amostra de dupla adjudicação independente é 10% das obras por estágio, arredondada para cima, ordenada por SHA-256 de `calibration-cohort-v2-20260924:double:` mais o ID. Os dois chamados Claude recebem a mesma tarefa, sem respostas GPT nem a resposta um do outro. Registrar versões, hashes de entrada e saída, concordância em três classes e desacordos; decidir os desacordos com evidência fonte. Cada lote passa por revisão independente de amostra aleatória pré-declarada antes da adoção. O `OwnerDecision` nativo individual usa `decided_by` com agente e modelo, autoridade `Davi delegation 2026-09-25 (log items 20–21)`, status `adopted under delegation, pending ratification`, hashes dos insumos, racional e localizadores. Cada registro declara que houve julgamento por agentes sob delegação sem verificação humana. TA e FT têm referências separadas. A adoção assistida mede concordância com essas referências; não estabelece acurácia independente.

O pacote piloto privado `pilot-claude-packet.json` usa uma tarefa de desenvolvimento já exposta, sem resposta de referência; SHA-256 `7f3cf2934be4a4bba6d336694024a4fd10b8283dc63db4d79cd059403073ccdd`. Ele serve para testar o formato e o validador sem tocar uma futura obra da coorte. Nenhuma chamada Claude foi feita nesta preparação.

## Sequência operacional

1. Fechar C4, reabrir seus bytes pelo CAS e registrar o SHA-256 do recibo, da projeção e dos registros originais; fechar o inventário de exposição com auditoria dos demais stores.
2. Executar `cohort_v2.py strata`, conferir a tabela e executar `cohort_v2.py sample` para congelar ordem, recusas e ondas em arquivo privado create-once.
3. Reproduzir as tarefas TA originais do C4. Preparar pacotes Claude cegos, executar adjudicação principal e dupla, validar locadores, revisar lote e registrar adoção nativa sob delegação. Não apresentar proposta como referência adotada.
4. Conferir os PDFs do pool contra C4, importar `FullTextRecord` nativo, completar no mínimo 50 fontes disjuntas, produzir tarefas FT com pool integral, repetir a adjudicação independente e só então compor a suíte de verificação.

Não há push nem merge nesta frente.
