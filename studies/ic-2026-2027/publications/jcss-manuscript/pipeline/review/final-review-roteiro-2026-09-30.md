# Roteiro da revisão adversarial final do manuscrito JCSS

Preparação do item M06 de `remaining-work-review-20260930.md`, em 30/09/2026, no ramo `docs/final-review-roteiro-20260930`, base `00c8dc3d`. Este roteiro será executado depois de M05, sobre uma montagem com Results selecionados, figuras reais, catálogos e PDF correspondentes. Não é uma revisão já realizada nem aceite científico.

O estado informado para esta preparação é G0, G1b, G1c e G2 aprovados; G2 terminou às 10:01Z de 30/09, com 700/700 e zero falhas; G2c está em curso. Isso não fornece uma curva confirmatória nem resultados de X3/X4/X6/X7. Esses números operacionais não substituem as entradas da revisão final.

## 1. Pré-condições e pacote de leitura

O coordenador fornece uma montagem imutável em uma pasta nova de revisão, fora das áreas proibidas, com lista explícita dos arquivos permitidos e manifesto SHA-256. Todos os revisores recebem os mesmos bytes. Não procurar os originais seguindo caminhos privados nos manifestos. As proibições continuam depois da liberação: não ler `sealed-v4-*`, inclusive `sealed-v4-exploratory-x3-x7`, em qualquer lugar; `coord-20260925/v4-tier-logs/`, `coord-20260925/v4-gate-logs/`, `coord-20260925/v4-release/`; nem qualquer `restricted/`. Não usar ou citar microdados SHP. Agregados SHP só entram se fornecidos e aprovados para este pacote.

Os comandos de liberação, agregação e exportação pertencem ao coordenador, conforme o [RELEASE-RUNBOOK](../../../../experiments/exploratory/detection-boundary-v4/report/RELEASE-RUNBOOK.md) e o [POST-RELEASE](../../../../experiments/exploratory/detection-boundary-v4-exploratory/POST-RELEASE.md). M06 recebe seus produtos; não executa esses comandos. A liberação confirmatória e a disponibilidade exploratória são condições separadas. Não antecipar a leitura exploratória porque os hosts terminaram, nem supor que uma falha do gate libera seus registros por repetição.

| Entrada real no pacote permitido | Conferência antes de ler resultados |
| --- | --- |
| `main.pdf`; `main.tex`; todos os `.tex`, `.bib` e ativos alcançáveis por seus inputs | Hash do PDF e de cada fonte/ativo contra o manifesto de M05; revisão Git exata da montagem; recibo de compilação desse mesmo estado. Não usar o hash de um PDF de ensaio ou de 29/09 como alvo final. |
| `released-curves.json` e `release-record.json`, em cópias fornecidas após liberação | SHA-256 dos bytes das curvas igual a `released_curves_sha256` do recibo; hash do recibo igual ao vinculado no manifesto do relatório. Conferir `condition`, `released_utc`, inventário e registro de encerramento dos produtores. `inventory-complete` exige as 414 curvas; `declared-close` preserva unidades incompletas. Não há liberação parcial. |
| Relatório real: `manifest.json`, tabelas T1/T3/T4, CSVs registrados e figuras F1–F6 aplicáveis | Hash de cada entrada/saída contra o manifesto; `synthetic: false`; revisão e estado limpo do código de reporting. Exigir tabelas/figuras do ramo escolhido, não todas em um ramo sem curvas. T2 não é uma saída registrada. F3 é exploratória. |
| `result-values.json` final; catálogo confirmatório completo; catálogo final combinado quando houver exploratórias | Mesma montagem e mesmos hashes de origem. O JSON de valores contém exatamente os IDs citados na árvore compilada; o catálogo completo conserva os demais. Conferir `report_manifest_sha256`, revisão e hash do exportador; no catálogo exploratório, fontes/JSON Pointers ou derivações e hashes de entradas. Colisão de IDs na junção é erro mesmo com valores iguais. |
| `x1b.json`, `x3.json`, `x4.json`, `x5.json`, `x6.json`, `x7.json` e JSON de comparações, conforme disponibilidade declarada | Cópias autorizadas dos agregados; manifestos e hashes de origem/exportação; união sem duplicatas e ausências contabilizadas. Agregação X3–X7 em `3334ac0f96268a76d62c3b68a9705cb7fe05587e`; reporting posterior identificado separadamente. A comparação vincula o mesmo par curvas/recibo. Não abrir stores para completar lacunas. |
| `generated/T1s_a_star_all_units.csv`, cópia `ESM_1.csv` e manifesto do pacote-fonte | SHA-256 do CSV original e da cópia; transformação documentada acrescenta apenas metadados, preservando linhas e valores científicos. Inventário inclui falhas, gaps e censuras. Figuras e suplementos chamados pelo PDF estão no pacote entregue. |
| Resumos públicos do gate, critérios, segunda vinculação e cópia aprovada do sucessor G1c | Conferir hashes vinculados no relatório e os predicados registrados de cada estágio. Um recibo estrutural ou campo `pass` sozinho não prova o critério científico. Sem cópia permitida/evidência suficiente, registrar impedimento de verificação; não abrir a origem proibida. |
| `freeze-v4.json`, documentos, critérios e fontes públicas vinculados; registro de execução/exposição | Conferir os hashes do freeze, incluindo ambiente e closure. Confirmatório executado no freeze `375138418f7f9e4528f0c2466f4600a76fee1bad`; os módulos de relatório, figuras e exportação posteriores têm outra proveniência. Não exigir que a integração atual execute o preflight congelado. |
| `claim-evidence.md`, shells, decisões, revisões anteriores e recibos de fechamento posteriores | Fixar seus hashes no pacote. Identificar cada fechamento e o que ainda depende de saída real ou do Owner. Os números Q dos shells e do integration-log são séries diferentes. |
| `number-audit.csv` do ensaio combinado e registro de sua versão | Necessário como modelo de formato, nunca como evidência científica. Preservar seu cabeçalho literal e ordem de colunas na auditoria real; guardar seu hash e a correspondência dos campos antes de começar. |

Hashes fixos de referência, sem substituir os hashes futuros da montagem:

| Referência | Valor esperado |
| --- | --- |
| SHA-256 de `freeze-v4.json` | `99c4277235d4f2303b6f009d6ead8287a5d71372744dd6781e1e2d1847710837` |
| `code_sha256` do freeze | `db9d6eadb5019d691a8c73703d511d0337dc49834bb219d168a27693df0e0acd` |
| Digest aprovado do sucessor G1c, decisão 46, conforme runbook | `a945e8484791f886289d51b083886854b4f540f6b26dcf1463d8d4c9dcd9a4d6` |
| Classe `sn-jnl.cls` do pacote já conferido | `36d0c3273a59d48dc6a9c7b080dfa1ec50dc10229d8751568d1f2e490ffa5ecc` |
| Estilo oficial `sn-mathphys-num.bst` | `b3a7c7fbcc1e7f9619de634fcea2f5bb7a245818a5942bc576e40ea001633332` |
| Estilo privado ajustado, quando essa variante for a usada | `da3ea79308465dc48dbc39294a090140c1e0fc31bf317e2d56f39f3fab9ee39a` |

Os hashes de documentos, critérios, inventário, código e ambiente são os registrados no freeze. Não inventar um digest para um produto ainda inexistente. A variante do estilo e qualquer sucessor legítimo precisam estar identificados no manifesto; divergência inexplicada interrompe a leitura. O vendor continua fora do Git.

Se G2c falhar, a decisão 99/101 permite o artigo completo com Methods preservados, ramo `B1b-G2c` seguido de `B1-END` e resumo fixado. Se o gate não terminar no fechamento, usar `B1d`, com estágio, completos/planejados e nenhum tier executado. Não exigir curvas/recibo/F1–F3/T1/T4 nesse pacote: exigir T3/F4 reais e registro público estável do desfecho. Resultados posteriores ao fechamento só pertencem a possível sucessor. G0/G1b/G1c/G2 e waste-guard já foram superados neste histórico; seus shells não são alternativas vivas. Em falha de G2/G2c, os registros por repetição continuam fechados; reportar apenas critérios autorizados.

`B1-SHP`, se aplicável, é texto exploratório separado depois de `B1-END`, sem F6, curva ou fronteira. Requer agregado aprovado e vínculo de todos os cinco IDs `v4.shp.*` e nove constantes, como B13; a extensão gate-only do exportador ainda era pendência na base deste roteiro. Se ela não estiver concluída, devolver a montagem para correção, sem redigitar valores. Sem análise, informar que não foi realizada e o motivo. Esta contingência não dispensa pré-condições das exploratórias.

## 2. O que permanece fechado e o que será revisto

Ler os [pareceres iniciais](referee-report-2026-09-28.md), a [auditoria de claims](claim-audit-2026-09-28.md), o [integration-log](integration-log-2026-09-28.md), o [response tracker](response-tracker.md), a [verificação Q7](q7-tse-full-text-check-2026-09-29.md), as [restrições X3–X7](x3-x7-reading-restrictions-2026-09-29.md) e o [checklist de submissão](jcss-submission-checklist-2026-09-30.md). Usar também o [kit de revisão](adversarial-review.md), o [modelo de parecer](report-template.md) e o [template ODD 2020](odd-2020-template.md).

A revisão final verifica aplicação aos resultados e regressões da montagem. Não refaz as auditorias textuais encerradas, as buscas bibliográficas nem docking, calibração, gate ou simulações. Correções já documentadas do argumento mean-field, terminologia, separação do mapa, exposição, plataformas e Q7 permanecem fechadas no alcance verificado. Q7 não certifica leitura integral das três obras inacessíveis; conferir que a redação final conserva os limites dos resumos. Um novo problema nesses trechos só volta se houver alteração, regressão ou evidência contraditória localizada.

As [decisões de interpretação](../drafts/2026-09-28/results-interpretation-decisions-2026-09-29.md), seções 82, 91 e 99 com a correção 101, governam a montagem; 89 está consolidada em 91. Não recuperar uma opção antiga porque o tracker ainda a chama de aberta. A regra per-r de 82 foi substituída por 91. As limitações científicas que uma correção textual não resolveu continuam limitações; não se exige nova análise para fingir que foram encerradas. Necessidade real de novo estudo vai ao Owner como proposta de sucessor.

## 3. Personas e prompts para colar

O coordenador entrega o pacote da seção 1 e informa o caminho permitido, revisão, hash do PDF e escopo de saída. Cada bloco abaixo é um prompt completo. Usar cinco contextos separados, sem mostrar pareceres das outras personas antes do fechamento. Uma pessoa/agente não assume duas personas no mesmo contexto. Registrar identidade real do agente/modelo, data e material lido; separação de papéis não equivale a independência humana ou de famílias de modelos. Não há revisão por pares do periódico nesta etapa.

Cada achado tem ID de persona, severidade, página/tabela/figura do PDF, fonte `arquivo:linha` ou JSON Pointer/linha CSV, claim/ID numérico quando houver, evidência, correção mínima e condição objetiva de fechamento. Referenciar um achado de outra área como encaminhamento; não emitir um segundo parecer sobre ele. Nenhuma persona edita o manuscrito.

### Editor do JCSS — ED

```text
Atue como editor cético do JCSS na revisão interna final M06. Use apenas o
pacote permitido fornecido pelo coordenador, fixando revisão e SHA-256 do PDF.
Leia este roteiro e os fechamentos anteriores. Não leia sealed-v4-* (inclusive
sealed-v4-exploratory-x3-x7), coord-20260925/v4-tier-logs/, v4-gate-logs/,
v4-release/ ou qualquer restricted/. Não use/cite microdados SHP. Não siga
caminhos de origem proibidos. Não edite, commite, publique ou contate pessoas;
não rode suites, simulações nem baixe pacotes. Checks locais só pontuais,
sequenciais, um processo, com OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1.

Seu escopo é contribuição, adequação ao JCSS e prontidão editorial do pacote.
Leia título, resumo, introdução, trabalhos relacionados, Results, figuras,
discussão, conclusão, checklist e declarações finais. Julgue se os resultados
entregam a pergunta delimitada, se a novidade respeita a busca verificada e
se a extensão/suplemento ajudam o leitor. Confira autoria, declarações, IA,
aprovações humanas, carta/metadados, 150–250 palavras e 4–6 palavras-chave
contra o checklist datado; sinalize necessidade de atualização oficial das
normas no dia do envio. Não invente fatos pessoais ou aprovação do Owner.
Não refaça estatística, ODD, auditoria numérica, hashes ou revisão linguística:
encaminhe a dúvida à persona responsável. Não reabra decisões 82/89/91/99/101.

Entregue parecer ED em PT-BR: identidade/data/escopo/hash, recomendação
pronto para avaliação externa / revisão menor / revisão maior / parar,
razão editorial curta, achados com localizador/evidência/correção/condição de
fechamento, e decisões ainda necessárias do Owner. Não preveja aceitação
pelo periódico. Consenso de agentes não autoriza submissão.
```

### Métodos estatísticos — ST

```text
Atue como revisor de métodos estatísticos na revisão interna final M06.
Use só o pacote permitido e registre revisão e SHA-256 do PDF. Leia este
roteiro e os fechamentos. Proibido ler sealed-v4-* (inclusive
sealed-v4-exploratory-x3-x7), coord-20260925/v4-tier-logs/, v4-gate-logs/,
v4-release/ e qualquer restricted/; usar/citar microdados SHP ou seguir
essas origens. Não edite/commite/publique, rode suites ou simulações, nem
baixe pacotes. Checks pontuais sequenciais em um processo, com
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1.

Seu escopo é validade da inferência e aplicação das condições da seção 5.
Leia Methods, Verification, Results, resumo, discussão/conclusão e
suplementos estatísticos; critérios/resumos públicos do gate, curvas
liberadas, agregados, comparações e catálogos permitidos. Verifique AUC
por painel, empates, agrupamento por rede, treino/matching/teste separados,
condicionamento ao sucesso e retries; max-t, logit, studentização em cada
replicação, quantil higher, piso 2.7729 e bias fora da variância. Bandas são
simultâneas por r, não entre r. Gate de dispersão não certifica cobertura.
Confira inversão inclusiva versus cruzamento estrito, primeira/sustentada,
gaps, censuras, não atingimento e invalidação principal. Aplique 91/99/101,
universos das faixas, denominadores X6 e gatilho primário D1 após precisão.
X4 é referência condicional oráculo; X7 não demonstra teto de informação.
SHP agregado não calibra inferencialmente a curva. Não redesenhe protocolos.
Auditoria literal de números/hashes é RP; mecanismos/ODD são AB; edição é ED;
clareza linguística é TX. Encaminhe, sem duplicar seus trabalhos.

Entregue parecer ST em PT-BR com identidade/data/hash/material não lido,
veredito e achados localizados com evidência, menor correção e condição de
fechamento. Entregue a conferência de cada condição da seção 5: valor/fonte,
ramo selecionado e frase permitida ou removida. Limite não testado permanece
limite; nova análise necessária vira proposta ao Owner, não comando de execução.
```

### ABM, dinâmica de opiniões e ODD+D — AB

```text
Atue como revisor de ABM/dinâmica de opiniões e ODD+D na revisão final M06.
Use só o pacote permitido, com revisão e SHA-256 do PDF. Leia este roteiro
e fechamentos anteriores. Proibido ler sealed-v4-* (inclusive
sealed-v4-exploratory-x3-x7), coord-20260925/v4-tier-logs/, v4-gate-logs/,
v4-release/ ou qualquer restricted/; usar/citar microdados SHP ou seguir
essas origens. Não edite/commite/publique, rode suites ou simulações, nem
baixe pacotes. Checks pontuais sequenciais, um processo, com OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1.

Seu escopo é fidelidade do mecanismo e documentação para reimplementação
conceitual. Leia descrição do modelo, interpretação substantiva, apêndice
ODD+D, template ODD, declarações e trechos públicos de código citados.
Confira sete elementos ODD, onze conceitos e razões para N/A; scheduling,
parceiros dirigidos, transporte por ranks, padronização, inicialização,
observação, households, canais e famílias A–E. Confira a extensão ODD+D:
processos de decisão humanos representados ou ausentes, fundamento e
justificativa da abstração; não atribua cognição ou validação empírica que
o gerador não tem. Separe padrões impostos de padrões emergentes,
descrição do modelo de experimentos, geometria SHP de dados observados,
drift nominal de influência causal e argumento de primeira ordem de prova
exata. Verifique se novas interpretações dos resultados respeitam esses
limites. Não refaça docking nem reabra o mean-field já corrigido sem regressão.
Inferência/seleção de ramos é ST; hashes/números/acesso são RP;
contribuição editorial é ED; redação é TX. Encaminhe dúvidas dessas áreas.

Entregue parecer AB em PT-BR, com identidade/data/hash/escopo, veredito,
lacunas do ODD+D ou afirmações mecanísticas novas, cada uma com localizador,
evidência, correção mínima e condição de fechamento. Falta de dado ou
controle não vira resultado negativo nem autorização de novo experimento.
```

### Reprodutibilidade e dados — RP

```text
Atue como revisor de reprodutibilidade e dados na revisão final M06.
Use apenas o pacote permitido, com revisão e SHA-256 do PDF. Leia este
roteiro e os fechamentos. Não leia sealed-v4-* (inclusive
sealed-v4-exploratory-x3-x7), coord-20260925/v4-tier-logs/, v4-gate-logs/,
v4-release/ nem qualquer restricted/. Não use/cite microdados SHP; não siga
origens proibidas. Não edite/commite/publique, rode suites ou simulações,
nem baixe pacotes. Checks pontuais sequenciais, um processo, com
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1. Python do estudo: o executável da venv da
integração indicado na seção 6, sem sincronizar/installar dependências.

Seu escopo é a cadeia de bytes/proveniência e a auditoria literal de TODOS
os números, conforme seções 1 e 4. Confira par curvas/recibo, datas efetiva
e nominal, manifestos, catálogos, inputs/outputs, exportadores e montagem
PDF/fontes; frozen versus reporting e limitações de plataforma. Confira
cada ocorrência numérica contra result-values/catálogo/CSV/fonte aprovada;
não limite a macros ou Results. Preserve o cabeçalho literal do
number-audit.csv do ensaio combinado. Audite vetores/legendas, T1s versus
ESM_1, suplemento, ZIP/fontes, acesso real e identificador persistente
quando declarado. Não inferir depósito/DOI/licença de um pacote local.
Agregado SHP só se aprovado, sem conteúdo individual ou caminho restrito
no produto público. Não execute reprodução por simulação; declare o alcance
da conferência offline. Julgamento estatístico de denominadores/intervalos
é ST; mecanismo é AB; fatos pessoais e submissão são ED; prosa é TX.

Entregue parecer RP em PT-BR com identidade/data/hash/escopo/limitações,
veredito e achados localizados. Entregue number-audit.csv no formato do
ensaio, sua contagem de ocorrências/status e hashes vinculados; números
sem fonte, discrepâncias e exceções explícitas. Produto auxiliar só na
pasta de saída autorizada pelo coordenador, sem alterar entradas.
```

### Redação científica — TX

```text
Atue como revisor de redação científica na revisão final M06. Use só o
pacote permitido e registre revisão e SHA-256 do PDF. Leia este roteiro
e fechamentos anteriores. Proibido ler sealed-v4-* (inclusive
sealed-v4-exploratory-x3-x7), coord-20260925/v4-tier-logs/, v4-gate-logs/,
v4-release/ ou qualquer restricted/; usar/citar microdados SHP ou seguir
essas origens. Não edite/commite/publique, rode suites ou simulações, nem
baixe pacotes. Checks pontuais sequenciais, um processo, com OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1.

Seu escopo é a comunicação no PDF final em inglês. Leia o PDF completo,
fontes e claim-evidence apenas para localizar frases. Confira encadeamento
pergunta–desenho–resultado–limite, tempo verbal, siglas, terminologia,
consistência entre resumo/Results/discussão/conclusão, legibilidade de
legendas/eixos, remissões e resíduos de shells/placeholders. Proponha
redação mínima sem mudar estimandos, condições, números ou intensidade
de evidência. Distinguir partner drift, signal share, reliability da
âncora, oráculo, exploratório, indisponível e não atingido. Não refaça
auditoria bibliográfica ou científica encerrada. Se uma frase depende
de regra estatística, encaminhe a ST; mecanismo a AB; número/hash a RP;
decisão editorial/autoria a ED, sem duplicar pareceres.

Entregue parecer TX em PT-BR com identidade/data/hash/escopo, veredito e
achados localizados. Para cada problema de redação, dê a frase inglesa
atual, substituição proposta, motivo e condição de fechamento. Não
preencha fatos do Owner nem valores ausentes para fazer o texto parecer final.
```

## 4. Auditoria de cada número do PDF

RP é o único responsável pelo CSV; ST julga os significados e universos. Auditar todas as páginas, inclusive resumo, equações, eixos, legendas, tabelas, discussão, referências e ODD. Cada ocorrência ganha uma linha; repetir um ID em três locais produz três registros. Para intervalos/faixas, conferir ambos os extremos, sinal, unidade, r, a, família/canal, denominador e condicionamento. Não aceitar um literal correto atribuído à população errada.

O arquivo real terá o nome `number-audit.csv` e o mesmo formato do ensaio combinado: cabeçalho literal, ordem de colunas, codificação e convenção de status. Na preparação de 30/09 o CSV ainda não estava disponível no diretório de ensaio consultado; por isso este roteiro não inventa seu schema. Antes de iniciar RP, o coordenador fornece o modelo e fixa seu hash. Copiar somente a estrutura, nunca as linhas sintéticas. Se faltarem campos para uma ocorrência, registrar os detalhes no campo de notas do formato e em anexo vinculado por ID, sem mudar o cabeçalho.

O mapeamento de campos do modelo precisa preservar estas informações:

| Informação por ocorrência | Conteúdo a registrar |
| --- | --- |
| Localizador | Página do PDF e bloco/tabela/figura/célula; fonte `.tex:linha` quando aplicável. |
| Identidade | ID `v4.*` ou `v4x.*`; para números sem macro, fonte documental e localizador específico. |
| Exibido / esperado | Literal no PDF e valor do JSON/CSV/fonte; transformação de formatação, unidades e arredondamento. |
| Fonte e proveniência | Catálogo e JSON Pointer/derivação, linha CSV ou documento, hash dos bytes e universo pertinente. |
| Resultado e ação | Concorda, diverge, sem fonte, ou não científico justificado, codificados nos status do modelo; correção e recheck associados. |

Procedimento:

1. Fixar hash do PDF, fontes, modelo de CSV, valores e catálogos. Extrair texto uma vez com `pdftotext -layout`; conferir visualmente símbolos, imagens, expoentes, sinais e tabelas que a extração perde. M05 deve fornecer os renders já produzidos; render adicional só da página problemática.
2. Percorrer a árvore compilada de inputs, não todas as alternativas dos drafts. Conferir cada `\resultnum` com `result-values.json` e sua presença no catálogo. ID ausente, extra indevido, colisão ou literal divergente é falha. Conferir também números escritos diretamente, constantes congeladas, números de X1/X2/X5, validação/docking e resultados de literatura. Estes últimos usam fontes públicas aprovadas; o catálogo não contém automaticamente tudo.
3. Conferir cada célula de T1/T3/T4 contra CSVs; fronteiras primeira/sustentada, intervalos, status e censura por unidade. Conferir as figuras contra os dados que as geraram e seus hashes. Textos/ticks de eixo têm vínculo à grade; cada ponto/banda tem vínculo à linha/célula de origem, sem estimar valor pela posição do desenho.
4. Conferir tabelas exploratórias contra agregados e catálogos, incluindo ausências/erros, covered/total, Wilson e sensibilidade de precisão. O número de jobs não é o número de repetições completas. Conferir T1s e a transformação de ESM_1 preservando inventário e valores.
5. Marcar números de página, rótulos de referência/equação/tabela, datas bibliográficas e versões como identificadores ou números não experimentais, com fonte/justificativa. Nenhuma ocorrência desaparece silenciosamente por não ser uma estimativa. Datas efetiva/nominal e números do protocolo continuam sujeitos à auditoria.
6. Arredondamento segue a formatação registrada no exportador; não criar tolerância ad hoc. Se o literal vem do catálogo, exigir igualdade de apresentação depois da normalização tipográfica documentada. Derivação sem macro precisa de fórmula/fonte e conferência pontual offline. Divergência de derivação vai a ST.
7. Encerrar com contagens de ocorrências por status, IDs únicos e números sem macro. Aceite exige zero divergências/sem fonte pendentes. Toda exceção não científica tem justificativa verificável. Hashes do CSV final e do parecer vinculam o PDF auditado.

O `paper_check.py --submission --result-values` de M05 é uma verificação necessária, de alcance mecânico. Seu PASS não substitui esta auditoria, inspeção de placeholders não reconhecidos, veracidade das declarações ou decisão humana. Não exigir contagens iguais às de ensaios que incluíram todos os ramos incompatíveis para exercitar IDs.

## 5. Conferência de seleção dos ramos

ST registra para cada bloco: predicado, valor e fonte no pacote real, universo, selecionado/omitido e página da frase. Aplicar ao corpo, resumo, legendas, discussão e conclusão; procurar comparações implícitas e sinônimos, além das marcas de shell. Cada frase mantida precisa satisfazer sua condição. O registro é conferido antes da leitura editorial, sem escolher regras pela aparência das figuras.

| Regra vigente | Conferência obrigatória |
| --- | --- |
| Gate e desfecho, 99/101 | Exatamente um ramo principal aplicável; aprovação completa antecede tiers/sementes confirmatórias. Falha final ou incompletude usa a contingência da seção 1. Não rerodar até passar, mudar janela ou incorporar resultado tardio. |
| Comparações entre mecanismos, 91 substitui Q8 de 82 | `v4.mechanisms.allowed == 1` exige tier 2 completo válido e curva principal válida. Se zero: retirar toda comparação entre mecanismos, local ou de manchete, incluindo H-BD, D-after-B03, B10 e frases P6/P7. Manter unidades válidas nas tabelas/figuras e marca de invalidação quando aplicável. |
| B/D e famílias C/E, 82/91 | Com permissão, B e D lado a lado em todo r; leitura só em pares gap-free. Toda contagem entre famílias usa mesmo conjunto de r, tamanho e lista explícitos (`v4.bd.n_eligible`, `v4.bd.r_eligible` e IDs regionais pareados). Conjunto vazio não produz leitura. B com banda inferior estritamente acima de 0,70 e D com banda superior estritamente abaixo em TODA a grade completa permite apenas “compatível com persistência não gaussiana, sem evidência específica de interação”. C/E usam seus mecanismos próprios; sobreposição não vira evidência de interação. |
| Fronteiras, gaps e domínio, 89 | Inversão inclusiva de a* não vira crossing estrito. Primeiro crossing antes do primeiro gap é reportável; sem crossing e com gap, censura; sem crossing em grade completa, acima da grade. Sustentada respeita último gap e forças superiores. X5: overlap inclusivo, acima/abaixo estritos. Fronteira pontual finita com extremo do intervalo censurado ainda seleciona célula, com limite explícito. X3 em a=0 e X4b fora de r∈{0,50;0,70;0,90} são fora do domínio; nunca substituídos pelo vizinho. |
| Regiões e precisão, 82/91 | Usar `region()`/T1, inclusive fronteiras 0,001/0,003 e a*=0. Nenhum corte novo de largura muda região. B09 distingue largura finita, extremo além da grade e extremo censurado por gap; precisão de uma etapa é diagnóstico separado. |
| Faixas, Q18 de 99 corrigida em 101 | B03: banda superior em a=0,90 nas nove grades B completas válidas sem atingimento pontual. P5-b: apenas primeiras fronteiras atingidas, com quantidade por região em P5-a. Mostrar ambos os extremos, nenhum como “melhor valor”. r censurado/não atingido permanece em T1/figuras e não entra como fronteira finita na faixa. Não trocar nove grades por subconjunto conveniente. |
| Controles e sensibilidades, 91 | B11 “exceeds” é pontual em forças disponíveis em ambas as unidades, sem teste registrado. “Channel-dependent” exige fronteira primeira finita no observado e ausência dela nos três controles válidos gap-free: latent masked, ordinal r=1 e latent_rank. Controle inválido/gap impede a classificação. B12 relata qualquer sensibilidade não completa válida e a degenerescência ω=1; Q22 relata diferença de região por r, sem “reversão” ou teste entre condições. |
| X6 no resumo, 91 e shell do resumo | Gatilho exato: `v4x.x6.x6a.band.vs_d1.primary.reading`, a leitura conjunta primária X6a contra D1 DEPOIS da sensibilidade de precisão. `failure`/`subnominal` exige a cláusula de cobertura interior abaixo da nominal em r=0,70 no resumo e expansão na discussão. Leitura efetiva inconclusiva não dispara a cláusula; inconclusiva/sem leitura exige dizer na discussão que cobertura interior não foi estabelecida. Não usar X6b, pointwise, verdade populacional ou gaps-as-misses para acionar o resumo. |
| X6, redação e denominadores | `adequate` permite apenas “não detectamos subcobertura sob este critério”, com covered/total e Wilson; não demonstra 95% nominal. X6a primário usa bandas inteiras completas gap-free cobrindo todas as nove forças, inclusive zero; pointwise primário usa as mesmas unidades inteiras. X6b usa pipelines celulares completos bem-sucedidos. Gaps-as-misses fica separado: em X6a todo incompleto com curva é miss conjunto e em CADA força. Sem curva/erros ficam explícitos fora dos denominadores calculados; mínimo de 100 completos e precisão da verdade preservados. |
| X3/X4/X7 e X5, 91 e restrições | Nenhum resultado X3/X4/X7 no resumo. X3 é contraste local condicionado, sem incerteza completa do matching; intervalo negativo dentro de ±0,02 relata magnitude. Solver sem raiz não prova impossibilidade. X4 é referência de rejeição oráculo, com falhas como não rejeições e referência condicionada ao sucesso separada; não é poder universal. X7 é ganho/equivalência local entre LDAs, sem teto/Bayes demonstrado. X5 fica na discussão E na conclusão, qualquer que seja a curva principal. |
| X1b/X7, 89 | Mostrar todos os r, ambas as fronteiras, intervalos e censuras. X7 compara rich versus frozen nas mesmas sementes exploratórias; a curva confirmatória ao lado é contexto, não um contraste pareado com ela. |
| Secundários, exposição e SHP, 91/99/101 | 0,60/0,80 derivados ficam só no suplemento em todo ramo com curvas; nunca promovidos ao resumo/manchete. Exposição em r=0,70 permanece incondicional, sem frase B17-b sobre destaque entre vizinhos. SHP preserva estimandos principal/STARTS/ponte, falhas e indisponibilidade; sem arredondar r para célula, extrapolar a* ou tratar faixa descritiva como intervalo inferencial. |
| Composição do resumo, Q17 de 99 corrigida em 101 | Baseline e frases obrigatórias de [results-shells-abstract](../drafts/2026-09-28/results-shells-abstract.md), incluindo novos seeds após exposição nos ramos aprovados e X6 quando obrigatório. Opcionais entram pelo primeiro que couber, nesta ordem: três cláusulas B09, B04, B05, B08, B11, B14; não retirar uma anterior para encaixar posterior. Recontar resumo preenchido: 150–250 palavras. Não cortar condição/limite obrigatório para acomodar opcionais. |

## 6. Ordem, parada e aceite

Executar em sequência para economizar CPU. Contextos separados preservam a separação dos pareceres, sem exigir processos locais em paralelo. Um único coordenador reúne os relatórios depois de fechados. Checks pontuais usam `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1`. Para Python do estudo, usar `/Users/davi/Documents/github/worktrees/research-workbench/integration/ic-20260928/studies/ic-2026-2027/.venv/bin/python -B`; não sincronizar ambientes, baixar pacotes, rodar suítes inteiras ou simulações. Reutilizar recibos válidos de M05; repetir somente check afetado por correção ou preocupação nova.

| Ordem | Trabalho | Tempo ativo estimado |
| --- | --- | --- |
| 1 | Coordenador fixa pacote/hashes/permissões, fecha pré-condições e entrega modelo number-audit | 15–25 min |
| 2 | RP confere proveniência e cada número, incluindo figuras e suplemento | 70–100 min |
| 3 | ST confere inferência e todos os predicados de seleção | 40–60 min |
| 4 | AB confere mecanismo e ODD+D | 30–45 min |
| 5 | TX lê PDF completo e propõe correções de comunicação | 30–45 min |
| 6 | ED julga contribuição e prontidão editorial no seu contexto | 20–35 min |
| 7 | Coordenador reúne pareceres, resolve duplicações e prepara pacote de decisão para o Owner | 20–30 min |

Total: aproximadamente 4–6 horas ativas, mais correções, eventual recompilação e leitura/decisão do Owner. Auditoria extensa pode ultrapassar a estimativa; o relógio não justifica amostrar números ou aceitar pendências. Nenhum ETA de simulação é inferido deste orçamento.

**Parar antes ou durante a revisão** se faltar entrada obrigatória do ramo, modelo de CSV, autorização de leitura, hash consistente ou vínculo PDF/fontes; houver mistura de fixture com resultado real; a entrada mudar durante leitura; ou a verificação exigir acesso proibido. Registrar impedimento, arquivos/hashes conhecidos e ação mínima do coordenador. Não abrir a origem para resolver. Ausência prevista pelo protocolo, com ramo e inventário corretos, permite revisar esse relato de indisponibilidade; não impede automaticamente todo artigo.

**Volta para correção:** erro literal, fonte/ID ausente, tabela/figura incompatível, ramo fora de condição, denominador errado, inferência excessiva, placeholder factual ou redação que oculta limite. Coordenador/autor corrigem em sucessor de montagem, preservando a versão examinada. Não editar saída canônica para fazê-la coincidir com o PDF. Hash novo exige nova conferência de integridade e recheck dos números/condições/páginas afetados; se mudar resultado central, universo ou contribuição, reabrir também ST/ED. Sem mudanças pertinentes, não repetir revisões encerradas.

**Vai ao Owner:** título e novidade finais ainda não ratificados; pergunta/protocolo e exposição; fatos de autoria, financiamento, conflitos, ética, contribuições e supervisão de IA; decisão sobre limitações científicas remanescentes e proposta de novo sucessor; venue em falha do gate; acesso/depósito/material publicável e autorização de submissão. O coordenador apresenta escolhas concretas e evidências, sem inventar fatos pessoais, flexibilizar freeze ou decidir verdade científica pelo consenso dos agentes. Decisões já fechadas não voltam como perguntas.

**Aceite técnico de M06:** cinco pareceres vinculados ao mesmo PDF/pacote; auditoria de todas as ocorrências numéricas, com zero divergências ou falta de fonte pendentes; todos os ramos conferidos; nenhum blocker/major aberto; correções menores concluídas e rechecadas; recibo final de M05/checker válido para esses bytes; registro explícito dos limites e itens do Owner. Este estado significa “revisão interna concluída, pacote pronto para decisão humana”. Pendência pessoal não preenchida mantém a prontidão de submissão bloqueada, mesmo com os demais checks verdes.

**Aceite científico e envio:** o Research Owner lê e decide sobre o pacote exato, com revisão e hashes registrados, e os autores aprovam a versão final. Resultado negativo, inconclusivo, censurado ou incompleto pode ser aceito como relato delimitado; não se exige resultado favorável. Agentes não certificam cobertura nominal por convenção nem ratificam a ciência. Publicação de artefatos, commit/push e envio ao JCSS são ações posteriores separadas; este roteiro não as executa nem as autoriza.

Encerrar M06 com um registro curto: hash/revisão final, pareceres e auditoria vinculados, correções encerradas, limites remanescentes, decisões reais do Owner e estado pronto/pendente. O coordenador revisa e commita os documentos; esta preparação altera somente este arquivo.
