# Protocolo v5: mapa priorizado por saturação conceitual

Em 25/09/2026, este protocolo implementa a decisão vinculante de Davi delegada
a agentes, itens 21–22 do log privado. É sucessor ligado ao v4, que permanece
imutável. A identificação completa é `opinion-dynamics-systematic-map-v5-prioritized`,
para distingui-lo da proposta anterior v5 de atualização editorial. O JSON
homônimo usa `ReviewProtocol` e `PrioritizedMappingPolicy` do workbench.
A aprovação metodológica está adotada sob delegação, pendente de ratificação;
o estado técnico `review_candidate` não implica calibração nem produção pronta.
Juízos de Owner foram feitos por agentes, sem verificação humana.

O produto é um mapa amplo de mecanismos, famílias de modelos, validação, dados
e lacunas declaradas, com cobertura medida. Não é um censo exaustivo. O universo
de busca, perguntas, fontes, datas, idiomas e rastreabilidade são herdados do
v4. A seleção da pergunta do artigo continua separada. Não se infere novidade
científica da ausência no mapa.

## Identidade, camada 0 e ordenação

O artefato de aquisição v3 é lido sem alteração. A projeção determinística une
DOI normalizado, arXiv sem sufixo de versão, ou a chave completa de título
normalizado + ano + primeiro autor. Título isolado nunca une obras. NFKC,
casefold e tokens alfanuméricos normalizam título e autoria; nomes abreviados
não são expandidos por hipótese. Identificadores contraditórios conservam os
componentes separados e um par pendente. Todos os membros e observações são
preservados; as contagens iniciais são propostas de obra, não identidade final.
A política `deduplication_policy` preserva as regras exatas herdadas; a política
`prioritized_mapping_policy` acrescenta explicitamente a chave bibliográfica e
adjudicação tardia. Pares ambíguos exigem adjudicação somente quando ambos forem
triados; não podem inflar a contagem de inclusões distintas. A frente C3 pode
fornecer decisões nativas verificadas, mas suas propostas não são fusões adotadas.

Revisões/surveys são localizados por título ou autodescrição de revisão no
resumo. A lista é candidata, com falsos positivos possíveis, e é triada primeiro
por A/B calibrados; divergências seguem consenso Claude Fable + GPT Astra e coordenador. Secundários pertinentes definem
um quadro de categorias com definições, exemplos e locadores. O arquivo
`mapping-extraction-frame-v5.json` é a base de codificação, ainda não o quadro
congelado após camada 0. Secundários não entram no mínimo de 500 primários.
Artigos de revisão identificados posteriormente são acrescentados à camada 0.

A representação local é TF-IDF com frequência logarítmica e suavização de IDF,
normalizada por documento. O classificador linear Rocchio usa centroides de
inclusões focadas e referências positivas adotadas. Na inicialização não há
negativos presumidos: itens sem rótulo não são exclusões. Depois de cada lote,
as decisões finalizadas e adotadas atualizam centroides positivo e negativo;
`uncertain` não treina nenhum dos dois. A média da similaridade lexical ampla
e do escore do classificador fornece o escore de relevância. Não há chamada de
modelo para ordenar nem dependência nova. O vocabulário é ajustado sobre o
corpus; isso usa metadados sem usar rótulos da coorte.

Estratos de escore de largura 0,02 precedem qualquer qualidade. Dentro deles,
revisão por pares com evidência, depois citações/(2026 − ano + 1), com denominador
mínimo 1, podem desempatar; seguem escore e ID. Sem evidência, qualidade é
neutra. Os insumos atuais não permitem esses sinais. Sementes focadas enviesam
a ordem e a saturação; qualidade bibliométrica poderia favorecer campos e
trabalhos mais citados. Ambos os vieses serão declarados.

## Coorte e gate de título/resumo

Congelar o ranking inicial antes de A/B. Sortear 20 obras elegíveis por decil
do ranking inteiro, total 200; RNG local, semente `20260925 + decil`. Reservar
casos de desenvolvimento, exposições inventariadas, os 200 títulos do diagnóstico,
obras da revisão focada, sementes e pares de identidade pendente. Igualdade de
título reserva conservadoramente possíveis manifestações; não as funde. Registrar
probabilidade de seleção de cada estrato. Sem 20 elegíveis em algum decil,
interromper a preparação; não redistribuir silenciosamente.

O inventário histórico disponível é parcial. O pacote é preparável para Claude,
mas sua liberação como verificação independente exige fechar as exposições
faltantes e revalidar aliases. Uma contaminação encontrada exige coorte sucessora,
sem alterar a congelada. O plano v2 anterior de estratos Q01–Q16 e espera global
por C4 é substituído aqui por decis de ranking e identidade tardia. A separação
de exposições permanece obrigatória; a antiga meta de 60 positivos não é um
novo gate oculto do v5.

O adendo de 25/09 substitui a regra original de referência só por Claude:
Claude Fable e GPT Astra produzem referências independentes para todas as fichas,
apenas com a tarefa entregue, modelo, critério, justificativa e locadores.
O coordenador adjudica divergências com evidência. A amostra aleatória
pré-fixada de 10% (20 fichas) conserva uma auditoria adicional cega. Relatar
acordo nas três classes e revisar independentemente cada lote antes da adoção
nativa. Não há referência humana e as famílias se sobrepõem às dos triadores;
a independência é de execução, não de família em relação aos triadores. Referências assistidas medem concordância com referências
adotadas por agentes, não acurácia humana independente. A amostra R/P nunca vira
referência de calibração, mesmo tendo sido classificada por Claude.

Para cada revisor A/B, recall é `include` previsto entre referências `include`,
com Wilson bilateral de 95% e seu limite inferior relatados. `uncertain` não é
acerto de inclusão nessa medida. O gate é recall observado ≥0,95 em ambos;
falsas exclusões são contadas e relatadas, não constituem gate zero-loss.
Relatar também prevalência, incertezas e resultados por decil; as métricas brutas
não estimam automaticamente a população excluída do quadro amostral. Ausência
de positivos impede medir recall. Se falhar, revisar o prompt uma única vez e
usar nova coorte disjunta. Falha posterior continua explícita. O avaliador TA
separado não depende da calibração FT/extração histórica, que permanece falhada.
Os manifests sucessores `screener_{a,b}_v7.toml` ficam `draft`/`unassigned`.
A começa em GPT Luna via Codex; Sol somente após falha de calibração. B usa
Claude Sonnet 5 via executor headless no Max; Haiku 4.5 somente se calibrado.
O adaptador Claude e sua validação são pré-requisitos de produção ainda não
executados nesta entrega offline. Registrar chamadas por lote e planejar a
carga conforme quota verificada no momento da execução; os valores do adendo
são um snapshot, não capacidade atual garantida.

## Lotes, extração e parada

Depois da camada 0, lotes de 500 seguem relevância, exceto um último lote menor
quando não houver 500 restantes. A/B recebem tarefas cegas; Claude Fable + GPT Astra e o coordenador adjudicam
conflitos. Cada inclusão recebe os dez campos de mapeamento, com evidência
localizada, antes de avançar. Uma amostra aleatória pré-declarada de 10% do lote
é revisada independentemente antes de adoção. O driver prepara planos e aceita
recibos ligados por hash à adoção do coordenador e à revisão; nunca chama modelos.

Parar somente quando houver, conjuntamente:

1. Pelo menos 500 obras primárias incluídas, distintas e com identidade resolvida.
2. Duas transições consecutivas de lotes sem categoria nova em qualquer dimensão
   e sem alteração maior que 2 pontos percentuais na proporção acumulada de
   qualquer categoria. São necessários três snapshots: antes, após lote 1 e após
   lote 2. Cada categoria usa todas as inclusões primárias como denominador;
   categorias multilabel não somam necessariamente 100%. `not_reported` é estado
   explícito com evidência, nunca substituto de extração pendente. O quadro é
   versionado; mudança de definição/granularidade reinicia as duas transições.
3. Auditoria aleatória sem reposição de 400 propostas do restante congelado,
   ou todo o restante se menor. Amostra, semente, hash do snapshot e todos os
   resultados ficam registrados; não se substituem itens difíceis. Nenhuma
   incerteza ou extração pendente vira negativo. Categorias ausentes detectadas
   na auditoria exigem retomar lotes, registrar a categoria e reiniciar a
   avaliação sobre o restante atualizado.

O estimador de relevantes ainda não triados após a auditoria é
`(N − n) × positivos/n`. O relatório mostra intervalo de Wilson escalado para
`N − n`, descritivo e aproximado, sem correção de população finita nem garantia
simultânea em auditorias repetidas. É contagem de propostas; duplicatas tardias
podem superestimar obras. O intervalo não é gate de recall. A ausência de uma
categoria na amostra não prova sua ausência no restante. A regra não contém
mínimo percentual triado, sequência de negativos ou rendimento mínimo.

Sem resumo em todas as observações, aplicar regra 1: não excluir por ausência
de modelo/domínio; marcar `uncertain` e recuperar metadados ou texto antes de FT.
Exclusões sustentadas apenas por metadados inequívocos continuam permitidas.
Retriagem: os casos de desenvolvimento permanecem históricos; as interpretações
V3-06/20/21/24/27/28/32/35/48 informam tarefas novas. Resultados v4 não são
promovidos retroativamente ao v5.

## Relato e base metodológica

O fluxo PRISMA 2020 distingue observações, propostas deduplicadas, ambiguidades,
ranqueados, camada 0, triados, incluídos, pendências e não triados. Não triados
não recebem razão de exclusão inventada. Relatar curvas recall@k dos conjuntos
conhecidos com denominador completo, inclusive ausentes; posições das próprias
sementes são diagnóstico de treino. Relatar cobertura da auditoria, vieses,
fracassos e decisões sob delegação sem verificação humana.

As [fontes verificadas e seus localizadores](../preparation/2026-09-25/prioritized-screening-v5-sources.md)
incluem Cochrane cap. 4, SAFE, Callaghan e Müller-Hansen e PRISMA 2020, além de
Lukersmith et al. para saturação em scoping/mapping e Dixon-Woods e Guest et al.
para sua operacionalização conceitual/temática. Esta é uma adaptação explícita,
sem atribuir às fontes a validação dos limiares escolhidos. As mudanças contra
v4 são censo → mapa priorizado saturado, zero-loss → relato, identidade global
→ tardia e Owner humano → agente delegado pendente de ratificação.

O gate TA v5 é `prioritized_batches.assess_calibration`; o avaliador histórico
combinado de triagem/extração não deve ser usado como declaração de aprovação
TA v5. Assertions literais e gates de extração desse avaliador são preservados
para os formatos históricos, sem substituírem o relatório específico v5.

O recibo de lote liga cada categoria a bytes UTF-8 identificados por SHA-256,
faixa de linhas e trecho literal. A revisão independente deve cobrir exatamente
a amostra sorteada. O driver rejeita adoções de planos bloqueados. Disposições
nativas de identidade `distinct` liberam os pares correspondentes; `merge`
exige sucessor da projeção e histórico remapeado antes de continuar. Não se
apaga silenciosamente uma obra já incluída. Os marcadores de prontidão do plano
são pré-condições externas: o driver offline não prova calibração, inventário
fechado ou autorização do executor e não executa triagem.
