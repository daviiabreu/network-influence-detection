# Conformidade da submissão ao JCSS — pacote de 30/09/2026

Auditoria realizada em **29/09/2026** sobre `31090f59f3dce56a6420775081aa2400976dddb2`, branch `docs/jcss-submission-package`. A data do nome identifica o pacote solicitado. O manuscrito ainda não está pronto para submissão: resultados, declarações, acesso aos artefatos e decisões humanas permanecem abertos. Este checklist e o [rascunho de declarações](../drafts/2026-09-30/declarations-draft.tex) não constituem aprovação científica nem publicação de dados/código.

`M/` = `studies/ic-2026-2027/publications/jcss-manuscript/`; `S/` = `studies/ic-2026-2027/`. Todos os localizadores `arquivo:linha` abaixo são relativos a essas raízes, na base auditada, salvo o rascunho novo. Ausência é localizada no ponto de integração esperado. Foram lidos `main.tex`, todos os arquivos de `sections/`, os arquivos gerados alcançáveis, `author-guidelines.md`, `pipeline/review/response-tracker.md` e os checklists/notas anteriores. Os arquivos `sections/systematic-map*.tex` existem, mas não são incluídos pelo `main.tex` atual.

Estados: **atende** = o aspecto delimitado foi verificado; **falta** = há lacuna editorial ou de pacote demonstrada; **depende do Owner** = exige fato, decisão ou atestação humana não disponível. Um item pode atender à forma e ainda ter pendência em outro item. A coluna fonte liga à URL oficial e ao ID do excerto literal, inventariado uma única vez abaixo; o nome de seção delimita a regra. A auditoria original propunha correções ao coordenador. O fechamento técnico abaixo registra as alterações de `docs/submission-readiness` sobre a base `346e2c5c`, sem commit; os demais localizadores e recibos continuam históricos.

## Atualização estrutural T59 — 09/10/2026

A ordem da montagem passa a ser texto principal, declarações, Apêndice A
(ODD+D), referências e Supplementary Material. O Apêndice A não tem floats
(a classe sn-jnl numeraria um float de apêndice como A1); o suplemento reinicia cada contador em S1,
com destinos hyperref distintos. As chamadas no texto principal identificam
os floats suplementares. O slot X1–X2 e a transferência da tabela de
fronteiras X7 para depois do resumo X7 permanecem ativos. Os localizadores
e fatos da auditoria original abaixo são históricos; a verificação desta
alteração fica em [t59-report.md](t59-report.md).

## Fontes oficiais e excertos

Páginas públicas lidas nesta auditoria, sem login, microdados, contorno de paywall ou restrições de robôs. Os trechos são curtos; as exigências são descritas de forma resumida no quadro. As páginas de suporte detalham as políticas, sem substituir regras específicas do periódico.

| ID | Fonte, seção e URL | Trecho literal |
| --- | --- | --- |
| J1 | [JCSS][jcss], General Information | “any length” |
| J2 | [JCSS][jcss], Title Page | “Author information” |
| J3 | [JCSS][jcss], Abstract | “150 to 250” |
| J4 | [JCSS][jcss], Keywords | “4 to 6” |
| J5 | [JCSS][jcss], Text Formatting | “[iicol]” |
| J6 | [JCSS][jcss], References / Citation | “square brackets” |
| J7 | [JCSS][jcss], Electronic Figure Submission | “fonts” |
| J8 | [JCSS][jcss], Supplementary Information / Spreadsheets | “.csv” |
| J9 | [JCSS][jcss], Supplementary Information / Numbering | “Online Resource” |
| J10 | [JCSS][jcss], Title Page / declarações | “Statements and Declarations” |
| J11 | [JCSS][jcss], Important Note | “three reviewers” |
| J12 | [JCSS][jcss], Title Page / LLMs | “copy editing” |
| J13 | [JCSS][jcss], Manuscript Submission | “approved” |
| P1 | [Springer journal policies][policies], Author contributions | “statement of responsibility” |
| P2 | [Springer journal policies][policies], AI / Core expectations | “Human accountability is non‑transferable” |
| P3 | [Springer journal policies][policies], AI / Authors | “Disclose AI use” |
| P4 | [Springer journal policies][policies], Summary of requirements | “Declarations” |
| P5 | [Springer journal policies][policies], Corresponding author | “cover letter” |
| P6 | [Springer journal policies][policies], Image integrity | “version numbers” |
| D1 | [Research data policy][data-policy], seção 1 | “data availability statement” |
| DS1 | [Data availability statements][data-statements], conteúdo da declaração | “secondary data reuse” |
| DT1 | [Sensitive data][sensitive-data], dados restritos | “necessary rights and permissions” |
| DA1 | [Write a data availability statement][data-help], orientação | “conditions of use or restrictions” |
| DR1 | [Sensitive data sharing expectations][sensitive-help], orientação | “terms of use” |
| DU1 | [Reused existing data][reused-data], orientação | “reference list” |
| C1 | [Code policy][code-policy], For Journals | “GitHub link only is not sufficient” |
| CS1 | [Software and code sharing][code-help], orientação | “permanent identifiers” |
| AIW1 | [AI use in manuscript preparation][ai-writing], Visual content | “model and purpose of use” |
| AIW2 | [AI use in manuscript preparation][ai-writing], Transparency / visual content | “AI Declaration” |
| AIR1 | [AI use in research practice][ai-research], Research framework | “Describe tool and purpose” |
| AIG1 | [AI guidance][ai-guidance], How can authors use AIGC? / Core principles | “tool versions, usage dates, prompts” |
| AIG2 | [AI guidance][ai-guidance], FAQ / divulgação | “should be declared” |
| AIG3 | [AI guidance][ai-guidance], FAQ / revisão linguística | “does not need to be declared” |
| CL1 | [Cover letter][cover-letter], checklist | “not under consideration by another journal” |
| CL2 | [Cover letter][cover-letter], checklist | “All authors have approved the manuscript” |
| S1 | [Licença pública SHP/SWISSUbase][shp-contract], Usage License | “exclusive use” |
| S2 | [Licença pública SHP/SWISSUbase][shp-contract], Usage License | “third party” |
| S3 | [Licença pública SHP/SWISSUbase][shp-contract], Usage License | “sign the contract individually” |
| S4 | [Licença pública SHP/SWISSUbase][shp-contract], Usage License | “Source: Swiss Household Panel (SHP)” |
| S5 | [Licença pública SHP/SWISSUbase][shp-contract], Usage License | “financed by the Swiss National Science Foundation” |
| SF1 | [FORS / Download SHP-data][shp-access] | “Log in with your SWITCH edu-ID” |
| SF2 | [FORS / Download SHP-data][shp-access] | “accept the usage contract” |

O link de autoria das diretrizes redireciona para [Springer journal policies][policies]. O link legado de imagens com IA retornou erro técnico da ferramenta; não foi contornado nem tratado como política integralmente lida. Foram lidas as políticas atuais acessíveis de [escrita][ai-writing], [pesquisa][ai-research] e [orientação de IA][ai-guidance]. O tutorial de redação ligado às orientações de arte solicita cadastro; a etapa cadastrada não foi acessada. As normas de arte necessárias estão na página JCSS.

Há diferenças entre textos: JCSS dispensa somente a revisão linguística delimitada por J12; P3 e AIG2 pedem divulgação, enquanto AIG3 mantém a dispensa. A recomendação desta auditoria é conservar a divulgação factual já necessária pelos usos generativos registrados. JCSS recomenda contribuições; P1 exige especificá-las. A política corporativa de código C1 está em implantação gradual; CS1 explicita essa transição. O arquivo versionado é requisito deste pacote solicitado, sem afirmar que todo periódico Springer exige abertura irrestrita na primeira submissão. `author-guidelines.md` e o checklist de 27/09 são registros anteriores, não a fonte definitiva dessas políticas atuais.

## Quadro de conformidade

### Forma, extensão e conteúdo

| Exigência / natureza | URL e excerto | Estado | Local exato e evidência atual | Correção / próxima verificação |
| --- | --- | --- | --- | --- |
| Extensão sem teto numérico; evitar excesso | [JCSS][jcss], General Information, J1 | depende do Owner | `M/main.tex:93`, `M/main.tex:105`; PDF atual: 42 páginas e 25.936 palavras incluindo suplemento, apêndice e referências | Justificar a extensão ou condensar o pacote; avaliar transferências ao suplemento após resultados. Não converter orçamento local em limite da revista. |
| Estrutura clara; até três níveis | [JCSS][jcss], Text / Headings, J5 | atende | `M/main.tex:34`, `M/main.tex:45`, `M/main.tex:51`, `M/main.tex:56`, `M/main.tex:61`; `M/sections/appendix-odd.tex:145` | Estrutura numerada compilada e níveis delimitados; reavaliar legibilidade quando resultados forem integrados. Não há sequência IMRaD obrigatória identificada. |
| Título conciso e informativo | [JCSS][jcss], Title Page, J2 | depende do Owner | `M/main.tex:21`; título de trabalho; `M/pipeline/review/integration-log-2026-09-28.md:293` | Ratificar ou abreviar o título extenso, preservando o escopo científico. |
| Nomes, afiliações, correspondente/e-mail | [JCSS][jcss], Title Page, J2 | depende do Owner | `M/main.tex:21` até `M/main.tex:31`: nenhuma definição de autor/afiliação; PDF p.1 sem autoria | Completar folha de rosto e metadados do sistema com os humanos aprovados; revisão single-blind não demanda anonimizar autoria. Rascunho: `M/pipeline/drafts/2026-09-30/declarations-draft.tex:9`. |
| ORCID se disponível; Google Scholar de cada autor | [JCSS][jcss], Title Page / Important Note, J2 e J11 | depende do Owner | `M/main.tex:31`; `M/pipeline/review/response-tracker.md:59` | Obter IDs e URLs verificados; ORCID é condicional, Google Scholar é solicitado no fluxo. Rascunho: `M/pipeline/drafts/2026-09-30/declarations-draft.tex:12`. |
| Resumo: 150–250 palavras | [JCSS][jcss], Abstract, J3 | atende | `M/main.tex:26`: 250 palavras pela função do checker; sem citações bibliográficas e sem sigla ROC indefinida | Faixa atendida no rascunho; recontar após substituir os campos de resultados, sem folga no teto atual. |
| Resumo e conclusão com resultados efetivos | [JCSS][jcss], General Information / Criteria, J1 | falta | `M/main.tex:26`; `M/sections/conclusion.tex:1`; `M/sections/results.tex:19` | Integrar somente resultados liberados e validados ou o ramo autorizado de falha do gate. A conformidade de extensão do resumo não fecha seu conteúdo. |
| Quatro a seis palavras-chave | [JCSS][jcss], Keywords, J4 | atende | `M/main.tex:29`: cinco palavras-chave | Confirmar aderência ao artigo final; manter a faixa após eventual revisão. |
| Fonte editável + PDF; montagem técnica do rascunho | [JCSS][jcss], Source Files / Text Formatting, J5 | atende | `S/experiments/package_jcss_submission.py:129`; `M/main.tex:4` e `:7`: mesma classe, estilo numérico e `iicol`; pacote privado com 28 arquivos, manifesto SHA-256 e PDF recompilado | A montagem inclui dependências alcançáveis, classe e estilo locais; coleta figuras geradas e T1s quando existem, sem substituir por amostras. A árvore atual mantém placeholders e não contém esses artefatos reais. Permissões de upload do template e pacote científico final permanecem pendentes; vendor não entra no Git. |
| Replicação e adequação metodológica | [JCSS][jcss], General Information / Criteria, J1; [políticas][policies], Data transparency, P2 | depende do Owner | `M/sections/methods.tex:207`, `M/sections/methods.tex:221`, `M/sections/discussion.tex:30`; `M/pipeline/review/response-tracker.md:12` e `:54` | Fechar objeções científicas e decisões de interpretação com evidência; manter limites explícitos. Esta auditoria não lê resultados selados nem ratifica o protocolo. |

### Declarações, dados e código

| Exigência / natureza | URL e excerto | Estado | Local exato e evidência atual | Correção / próxima verificação |
| --- | --- | --- | --- | --- |
| Declarações pertinentes antes da bibliografia | [JCSS][jcss], Title Page / Competing Interests, J10; [políticas][policies], P4 | falta | `M/main.tex:71` tem o cabeçalho correto; `M/main.tex:91` contém apenas um placeholder | Integrar declarações individualizadas após resolver os campos do rascunho; a presença do cabeçalho é tudo que o checker normal verifica. |
| Financiamento, inclusive apoio material, conforme aplicabilidade | [políticas][policies], Competing interests / Funding, P4 | depende do Owner | `M/main.tex:91`; `M/pipeline/drafts/2026-09-30/declarations-draft.tex:18` | Informar financiadores, números de apoio e destinatários reais; repetir no sistema. Não declarar ausência de financiamento nem usar apoio ao SHP como apoio a este artigo sem confirmação. |
| Interesses financeiros e não financeiros | [JCSS][jcss], Competing Interests, J10; [políticas][policies], P4 | depende do Owner | `M/main.tex:91`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:24` | Recolher declaração de cada autor; confirmar eventual ausência, sem inferi-la do repositório. |
| Ética e consentimentos conforme aplicabilidade | [políticas][policies], Disclosures and declarations, P4; [dados sensíveis][sensitive-help], DR1 | depende do Owner | `M/main.tex:77` e `:78`; `M/sections/appendix-odd.tex:131`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:28` | Distinguir simulação sintética da eventual análise secundária SHP. Confirmar aprovação/dispensa/não aplicabilidade, consentimento de participação e de publicação; não inventar comitê ou consentimento novo. |
| Contribuições e responsabilidade humanas | [políticas][policies], Author contributions, P1 e P2 | depende do Owner | `M/main.tex:91`; `M/sections/methods.tex:239` e `:241`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:48` | Nomear somente humanos e suas contribuições reais; obter aprovação final. Trailers de agentes não determinam autoria humana. |
| Agradecimentos em seção própria / folha de rosto | [JCSS][jcss], Acknowledgments, J2; [políticas][policies], Authorship definition, P1 | depende do Owner | `M/main.tex:66`: cabeçalho vazio, hoje após a conclusão | Confirmar pessoas/apoio e posicionamento pedido pelo JCSS na folha de rosto. Rascunho condicional em `M/pipeline/drafts/2026-09-30/declarations-draft.tex:128`. |
| Declaração de dados: sintéticos, acesso e restrições | [Research data policy][data-policy], D1; [Data availability statements][data-statements], DS1; [orientação][data-help], DA1 | falta | `M/main.tex:76` a `:81`: natureza sintética, restrição SHP e rota pública de acesso descritas; localização final em aberto | Rota pública SHP atendida por AV01; ainda separar os acessos finais a dados sintéticos, agregados e fontes secundárias; preencher acessos reais no rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:54`. Nenhum depósito está confirmado. |
| SHP via SWISSUbase, contrato pessoal, sem redistribuição | [FORS][shp-access], SF1–SF2; [licença SHP][shp-contract], S1–S3; [Sensitive data][sensitive-data], DT1 | atende (rota pública) | `M/main.tex:83`–`:84`; `M/claim-evidence.md:420` (AV01): rota FORS → SWISSUbase, escolha da onda, SWITCH edu-ID e aceite do contrato | Instruções públicas verificadas em FORS, Download SHP-data, passos 1–7. A frase anterior sobre contrato e restrição foi preservada literalmente. Não atesta obtenção de acesso, assinatura do Owner ou dataset efetivamente utilizado. |
| Dataset/versão SHP realmente utilizados e citação | [Reused existing data][reused-data], DU1; [JCSS][jcss], Data citation, J6 | depende do Owner | `M/main.tex:78`; `M/references.bib:559` cita um guia, não o dataset analisado; âncora ainda planejada em `M/sections/appendix-odd.tex:135` | Confirmar ocorrência da análise, release, arquivos/ondas, data e DOI; citar o dataset se usado. A licença pública consultada mostra versão 9.0 / DOI `10.48573/swnc-bn46` e aviso de versão anterior: não atribuir essa versão ao estudo. |
| Reconhecimento SHP/FORS/SNSF e crédito em saídas SHP | [licença SHP][shp-contract], S4–S5 | depende do Owner | `M/main.tex:66`; `M/generated/shp-anchor.tex:5`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:130` | Se dados SHP forem efetivamente usados, incluir reconhecimento institucional e o crédito S4 em tabelas/figuras correspondentes; conferir que agregados não identificam pessoa/domicílio. Não inserir reconhecimento de uso empírico ainda não ocorrido. |
| Declaração de código e condições de acesso | [Code policy][code-policy], C1; [Software and code sharing][code-help], CS1 | falta | `M/main.tex:79` e `:81` têm revisão, mas nenhum link final; `git remote -v` aponta GitHub | Identificar código, acesso e documentação no bloco `M/pipeline/drafts/2026-09-30/declarations-draft.tex:75`. Consulta pública não autenticada à API GitHub retornou 404: acesso público não está demonstrado. Não inferir inexistência do repositório desse retorno. |
| Repositório + versão arquivada persistente | [Code policy][code-policy], C1; [Software and code sharing][code-help], CS1 | depende do Owner | `M/main.tex:81`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:82` | O pacote local com hashes não comprova arquivo público nem identificador permanente (CS1). Fornecer tag, licença e DOI da versão arquivada, verificar depósito/acesso e acrescentar citação. Zenodo/CoMSES são possibilidades registradas em `S/publications/reproducibility/data-availability.md:12`, não depósitos existentes. |
| Separar código congelado e módulos posteriores | [políticas][policies], Data transparency, P2; [JCSS][jcss], replication, J1 | atende | `M/main.tex:79` e `:80`; `M/sections/methods.tex:203`; `M/sections/appendix-odd.tex:137` | Preservar `375138418f7f9e4528f0c2466f4600a76fee1bad` e registrar versões efetivamente usadas de relatório, figuras, wrapper e âncora. As informações presentes delimitam o escopo, não provam arquivo completo ou reprodução externa. |

### IA, figuras, referências e suplemento

| Exigência / natureza | URL e excerto | Estado | Local exato e evidência atual | Correção / próxima verificação |
| --- | --- | --- | --- | --- |
| Divulgação generativa em Methods | [JCSS][jcss], Title Page, J12; [políticas][policies], P3 | depende do Owner | `M/sections/methods.tex:233` a `:241`; `M/pipeline/review/integration-log-2026-09-28.md:294`; `M/pipeline/review/response-tracker.md:56` | Local correto, inventário incompleto. Fechar Q4 e integrar divulgação factual; a tabela abaixo delimita o que o repositório registra. |
| Uso de IA na pesquisa: finalidade e validação | [AI research][ai-research], AIR1; [AI guidance][ai-guidance], AIG1 | depende do Owner | `M/sections/methods.tex:236` e `:241`; `M/claim-evidence.md:366`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:110` | Completar tarefa/modelo/versão/data, entradas, saídas, prompts ou descrições permitidas e validação humana. Não substituir supervisão comprovada por concordância de agentes. |
| IA na redação, software e crítica; responsabilidade | [AI writing][ai-writing], AIW2; [políticas][policies], P2–P3 | depende do Owner | `M/sections/methods.tex:238`; `M/claim-evidence.md:367`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:93` | Conservar os papéis comprovados e marcar os demais. Autores devem verificar citações e conteúdo; o rascunho não atesta que ratificação/revisão humana já ocorreu. |
| Figuras digitais finais, programa e fontes incorporadas | [JCSS][jcss], Electronic Figure Submission, J7; [políticas][policies], Image integrity, P6 | falta (arte real); geradores atendem | `S/src/ic_study/analysis/v4_report_figures.py:146` e `:155`; `S/experiments/exploratory/detection-boundary-v4/report/render_samples.py:117`; dez amostras PDF vetoriais regeneradas | PDFs sem raster interno, fontes TrueType incorporadas e versão Matplotlib no Producer; manifesto de amostras vincula entradas, módulos e saídas. O mapa também produz PDF vetorial. Arte real, mapas FigN/IDs e revisão após release continuam dependentes dos resultados. |
| Resolução, dimensões, legibilidade e acessibilidade | [JCSS][jcss], Artwork / Line Art / Accessibility, J7 | atende nas amostras; falta arte real | `S/src/ic_study/analysis/v4_report_figures.py:132`, `:549`, `:641`, `:917`, `:1130`; `S/src/ic_study/analysis/map_saturation_figures.py:485` e `:573`; PDFs/PNGs sintéticos inspecionados | Tipo mínimo 8 pt na largura de destino: 76 mm para F3 e 160 mm para painéis largos, inclusive F5; larguras conferidas na classe local (sn-jnl.cls:233–247, coluna 76 mm, bloco 160 mm), altura até 175 mm para evitar redução automática. Paleta Okabe–Ito, símbolos N/P/I/V no inventário, rótulos nominal strength/signal share; notas de censura e invalidação fora dos pontos. Textos do mapa antes em 7 pt agora em 8 pt; legenda em duas colunas para caber no bloco de 160 mm. PNG de amostra em 150 dpi é preview; a arte de linha é PDF vetorial. Conferir arte real na sua inserção final. |
| Figuras/tabelas: citação sequencial e legenda | [JCSS][jcss], Figure Numbering / Tables, J7 | falta | `M/sections/results.tex:22` a `:29`; `M/generated/primary-boundary-figure.tex:5`; `M/sections/supplement-exploratory-x1-x2.tex:56` e `:77` | Legendas e números existem, mas nenhuma das dez figuras e seis das nove tabelas alcançáveis têm chamada por referência no texto atual. Integrar os shells autorizados e conferir primeira chamada/ordem, painéis e legendas; separar numeração de figuras se mover conteúdo para SI externo. |
| Permissões e origem; IA visual quando aplicável | [JCSS][jcss], Permissions, J7; [AI writing][ai-writing], AIW1–AIW2 | depende do Owner | `M/generated/shp-anchor.tex:5`; `M/main.tex:93`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:114` | Auditar as figuras finais e eventuais reutilizações; obter permissões reais e citar origem. Uso de IA visual permanece [OWNER]; se houver, documentar modelo/finalidade e contribuição na declaração e legenda, com dados verificáveis. Não declarar ausência de IA visual antes do inventário. |
| Referências numéricas, itens citados e DOI completo | [JCSS][jcss], References, J6 | atende | `M/main.tex:7` e `:117`; PDF pp.38–42, 58 entradas; `M/references.bib:288` e `:570` | Checker: 58 chaves usadas/77 definidas, sem duplicatas ou chaves não resolvidas; `.bbl` contém somente 58 itens, 55 com macro que expande DOI em URL completa. Os 19 registros não usados no `.bib` não são 19 referências excedentes no PDF. |
| Itálico em nomes de periódicos/livros | [JCSS][jcss], Reference list, J6 | atende | `M/main.tex:11`–`:13`; `S/experiments/package_jcss_submission.py:44`: macros de títulos e ajuste mínimo de `make.tag` no `.bst` privado; PDF pp.39 e 41 inspecionadas | Periódicos, livros/proceedings e o fallback sem páginas (Lucas 2023) ficam em itálico. URL longa é quebrável. Mesma classe e nome do estilo; SHA original/ajustado no manifesto. A cópia oficial externa permanece intacta. |
| Estatuto de publicação e atualização bibliográfica | [JCSS][jcss], Reference list, J6 | depende do Owner | `M/references.bib:288`, `:300`, `:314`; preprints explicitamente identificados; `M/sections/related-work.tex:13` e `:70` | Conferir versões publicadas/aceitas disponíveis na submissão e tratamento dos preprints pela regra editorial. Não converter preprint em artigo revisado por pares nem declarar toda leitura integral concluída (Q7 tem limites em `M/pipeline/review/response-tracker.md:24`). |
| T1s como suplemento eletrônico CSV | [JCSS][jcss], SI / Spreadsheets, J8 | falta | `M/main.tex:12` e `:13`; `S/src/ic_study/analysis/v4_report_export.py:1247`; `S/experiments/exploratory/detection-boundary-v4/report/samples/T1s_a_star_all_units_synthetic.csv:1` | O exportador prevê `generated/T1s_a_star_all_units.csv` quando existe release; arquivo real ausente no manuscrito. Não submeter o CSV `_synthetic` de ensaio como resultado. Preparar `ESM_1.csv` apenas do relatório liberado e validado, preservando hash e origem. |
| Citação, metadados e legenda do suplemento | [JCSS][jcss], SI / Submission / Numbering / Captions, J8–J9 | falta | `M/main.tex:13` apenas define a macro; usos estão no shell não integrado, `M/pipeline/drafts/2026-09-28/results-shells.tex:477` e `:573` | Acrescentar chamada efetiva no manuscrito, legenda, nome consecutivo e título/artigo/periódico/autores/afiliação/e-mail no arquivo. Ver seção T1s abaixo; manter CSV utilizável e conferir o arquivo que será publicado sem reedição. |

### Carta e metadados do fluxo

| Exigência / natureza | URL e excerto | Estado | Local exato e evidência atual | Correção / próxima verificação |
| --- | --- | --- | --- | --- |
| Carta ao editor; conteúdo e fatos condicionais | [Cover letter][cover-letter], CL1–CL2; [políticas][policies], P5 | falta | `M/main.tex:21`, `M/sections/results.tex:19`; `M/pipeline/review/response-tracker.md:58`: pacote final pendente; nenhuma carta na pasta auditada | Preparar carta após resultado autorizado: título/tipo, questão, contribuição demonstrada, aderência ao escopo, extensão e correspondente. Declarar reutilização/manuscritos relacionados quando aplicável. Não foi demonstrada exigência incondicional de upload de carta pelo JCSS; conferir o fluxo vigente. |
| Originalidade, exclusividade e aprovação dos autores/instituição | [JCSS][jcss], Manuscript Submission, J13; [Cover letter][cover-letter], CL1–CL2 | depende do Owner | `M/main.tex:91`; `M/pipeline/review/response-tracker.md:58`; rascunho `M/pipeline/drafts/2026-09-30/declarations-draft.tex:13` | Obter confirmação humana antes das garantias na carta/sistema. Não afirmar que todos aprovaram ou que não há submissão concorrente por ausência de registro. |
| Editor sugerido + três revisores independentes | [JCSS][jcss], Important Note / Suggesting reviewers, J11 | depende do Owner | `M/pipeline/review/response-tracker.md:59`; nenhuma lista aprovada | Selecionar nomes, independência e e-mails institucionais; se necessário, identidade verificável por página/publicações/ID na carta. Diversidade institucional/geográfica é recomendação. Não contatar pessoas nem apresentar agentes internos como pareceristas humanos independentes. |

## Inventário de IA permitido pelo registro público do estudo

Estes são registros versionados e trailers consultados, não uma verificação dos logs privados ou da identidade de execução. O remoto configurado não foi comprovado publicamente acessível. A atribuição no Git é evidência do que foi registrado; não completa automaticamente o identificador de API, a versão ou a supervisão humana de cada tarefa.

| Papel / fase | Identificação realmente registrada | Evidência exata | Lacuna a conservar |
| --- | --- | --- | --- |
| Aquisição, triagem e síntese da revisão focada | GPT-6 via Codex | `S/research/literature/preparation/2026-09-24/focused-related-work-report.md:3`; protocolo correspondente `S/research/literature/protocol/2026-09-24-focused-related-work-review-draft.md:77` | [OWNER: identificadores/versões por tarefa e verificações humanas]; não atribuir arbitrariamente uma variante Sol/Astra. |
| Desenho e crítica do memo | Claude | `S/research/questions/exploration/2026-09-24-parallel/claude-design-review.md:3`; `claude-memo-critique.md:1` no mesmo diretório | [OWNER: modelo exato por sessão]. |
| Revisão de novidade das candidatas | Claude (Opus 5.5) | `S/research/questions/exploration/2026-09-24-parallel/claude-novelty-review.md:3` | [OWNER: versão/identificador de execução, extensão e validação]. |
| Propostas e críticas cruzadas antes de v4 | Codex e Claude | `S/research/decisions/2026-09-24-paper-decoupling-ratification-list.md:7`; `S/research/questions/exploration/2026-09-24-parallel/amendment-critique-codex-on-synthesis.md:1` | [OWNER: modelos por papel]; o registro não certifica independência humana. |
| Desafio adversarial à revisão focada | Claude | `S/research/literature/preparation/2026-09-25/claude-novelty-challenge.md:3` | [OWNER: modelo, versão e ratificação]; relatório detalhado anterior privado não lido. |
| Busca de posicionamento e dossiê | Claude, sessão remota | `S/research/literature/positioning-a-star-r/dossier.md:3`; limites em `M/sections/supplement.tex:39` e `:41` | [OWNER: modelo/versão]; não preencher datas/URLs ausentes do log reconstruído. |
| Redação de Methods/Verification/disponibilidade; ODD; auditoria de claims; integração/revisões | Atribuição Claude Opus 5.5 nos trailers | `git show -s 25cc280b`, `8dc8d547`, `cc28df93`, `a3e3bc84`; consolidado em `M/claim-evidence.md:366` e `:367` | [OWNER: confirmar versões/tarefas e revisão humana]; trailer não equivale a coautoria humana. |
| Docking do modelo e da inferência | `claude-opus-5-5` no primeiro registro; Claude Opus 5.5 nos trailers do segundo | `S/validation/docking-v4/RECONSTRUCTION.md:3`; `S/validation/inference-docking-v4/RECONSTRUCTION.md:3`; `git show -s 76fecc20 55d027b5 ac5576ac`; `M/sections/verification.tex:69` | Sessões separadas não provam independência de famílias ou validação científica humana. |
| Revisão interna, assistência adicional e figuras finais | Inventário final não registrado | `M/pipeline/review/response-tracker.md:27` e `:56`; integração Q4 `M/pipeline/review/integration-log-2026-09-28.md:294` | [OWNER: modelos e papéis, inclusive redação/código/IA visual ainda não identificados]; não declarar ausências. |

O mapa amplo tem seu próprio inventário em `S/research/literature/run-records/2026-09-28-broad-map-v5-1-production.md:7`: `gpt-5.6-luna`, `claude-sonnet-5`, `claude-opus-5-5`, `gpt-6-astra` e `gpt-6-sol`, com papéis/alterações por fase nas linhas 7–12. `M/sections/systematic-map.tex:27` e `:39` também registram produção/calibração, inclusive histórico de `claude-fable-5-1` e tentativa de `gpt-5.6-sol`. Como esses arquivos não são incluídos no PDF auditado, esses modelos não foram misturados à declaração da revisão focada. [OWNER: reavaliar a inclusão desse histórico se o mapa integrar a submissão.]

Nenhum log privado, prompt restrito, microdado SHP ou saída selada foi consultado para completar Q4. O rascunho contém o que está documentado e mantém os campos pessoais e a atestação de revisão/ratificação em `[OWNER: ...]`.

## T1s e carta: montagem posterior do pacote

T1s deve manter o inventário de todas as unidades do relatório autorizado, com status, gaps, censura e denominadores, em vez de selecionar somente unidades favoráveis. O CSV de ensaio em `report/samples/` contém valores artificiais. Não foi executado o exportador contra dados reais nesta tarefa.

Após a liberação, o coordenador deve conferir o CSV exportado contra o manifesto, guardar o hash do original e produzir uma cópia de submissão chamada `ESM_1.csv`. Para combinar metadados obrigatórios e CSV regular, a proposta desta auditoria é acrescentar colunas de metadados constantes (`article_title`, `journal`, `authors`, `corresponding_affiliation`, `corresponding_email`) às linhas da cópia, sem alterar valores científicos; documentar a transformação e ambos os hashes. Não inserir linhas livres que quebrem o cabeçalho, nem tratar um README separado como cumprimento automático de metadados em cada arquivo. A legenda proposta, a ajustar ao conteúdo real, é: “Online Resource 1. Full released inventory of comparison units, with execution status, gaps, first and sustained boundaries and censoring.” Autoria/contacto e a existência do release permanecem [OWNER]. Confirmar a preservação da leitura tabular no sistema de submissão.

A carta não foi redigida como garantia de uma submissão final inexistente. Seu roteiro concreto é: [OWNER: data, editor, autores/correspondente e tipo]; título ratificado; questão e contribuição que os resultados validados sustentarem; conexão com ciência social computacional; explicação da extensão/suplementos; links de artefatos confirmados e instruções de acesso SHP; [OWNER: originalidade/exclusividade/aprovações]; material relacionado ou reutilizado, se houver; sugestões de editor/revisores e conflitos pertinentes. A guia de carta e as normas de autoria acima fundamentam cada parte. Não existe autorização para enviar carta ou submeter o artigo nesta tarefa.

## Recibo de compilação e checks do estado atual

Cópia temporária: `/private/tmp/jcss-submission-package-20260930/manuscript/`. Todos os arquivos originais foram copiados antes de criar estes dois entregáveis; `source-sha256.json` ao lado da cópia registra os 61 arquivos originais. A compilação não inclui `declarations-draft.tex`.

Classe e estilo copiados de `~/.local/state/research-workbench/springer-template/`, sem inclusão em Git:

| Arquivo | SHA-256 |
| --- | --- |
| `main.tex` original | `278b38201c7039d5e70ea4f8007a0e18ea65a9c6ae2efc69d0f3a67bd45fdfdb` |
| `sn-jnl.cls` | `36d0c3273a59d48dc6a9c7b080dfa1ec50dc10229d8751568d1f2e490ffa5ecc` |
| `sn-mathphys-num.bst` | `b3a7c7fbcc1e7f9619de634fcea2f5bb7a245818a5942bc576e40ea001633332` |
| PDF compilado | `017288ca8e0a70f3f2ab62685ed9590ca333c583b05cb692421215e95454bd71` |

A primeira tentativa com `nix shell nixpkgs#tectonic --command tectonic main.tex` falhou ao obter fontes TeX por HTTP 429. Não houve insistência no endpoint. O cache existente em `~/Library/Caches/TectonicProject.Tectonic` foi copiado para `offline-tex-cache/` na raiz temporária, e Tectonic 0.17.0 compilou somente com recursos locais:

```sh
TECTONIC_CACHE_DIR=/private/tmp/jcss-submission-package-20260930/offline-tex-cache \
XDG_CACHE_HOME=/private/tmp/jcss-submission-package-20260930/cache \
/nix/store/l8af77awr5a678gmrbcg94pqhihd5mhs-tectonic-0.17.0/bin/tectonic \
  --only-cached --keep-logs --keep-intermediates main.tex
python3 pipeline/paper_check.py --venue jcss --pdf main.pdf
python3 pipeline/paper_check.py --venue jcss --pdf main.pdf --submission
```

Todos os comandos de manuscrito acima rodaram na cópia temporária. Logs: `/private/tmp/jcss-submission-package-20260930/compile-offline.log`, `paper-check.txt`, `paper-check-submission.txt`; log TeX completo em `manuscript/main.log`.

| Verificação | Resultado efetivo |
| --- | --- |
| Compilação offline | exit 0; PDF de 354.002 bytes |
| PDF / contagem extraída | 42 páginas; 25.936 palavras (texto integral, não só corpo) |
| Resumo / palavras-chave | 250 palavras / 5 |
| Citações / bibliografia | 54 chaves usadas / 73 registros; 54 entradas no PDF |
| Placeholders reconhecidos pelo checker | 19 |
| Comando solicitado, modo normal | **PASS**, exit 0 |
| Modo `--submission`, sem JSON final | **FAIL: 20 issue(s)**, exit 1: 19 placeholders + JSON de valores requerido |
| Log e fontes | Nenhum overfull ou aviso de referência indefinida; underfull permanece; `pdffonts` informa todas as fontes incorporadas |
| Revisão visual delimitada | PNGs das páginas 1, 13, 18, 19, 20, 26 e 38 inspecionados: autoria ausente, IA/declarações pendentes, figuras como placeholders, tabelas legíveis e bibliografia numérica |
| Rascunho de declarações isolado | Wrapper temporário com a mesma classe compilou offline, exit 0; duas páginas inspecionadas, sem overfull; não foi ligado ao manuscrito |
| Integridade e localizadores | Os 61 arquivos originais conservam os hashes; localizadores explícitos `M/` e `S/`, links locais e referências Markdown dos entregáveis resolvem |
| Whitespace dos dois arquivos novos | `git diff --no-index --check /dev/null <arquivo>` sem diagnósticos; exit 1 corresponde à diferença de arquivo novo |
| Gate estrutural do repositório | `/Users/davi/.local/bin/python3.12 scripts/check_repository.py`: exit 1; 37 links quebrados herdados, todos em `VALIDATION-FIXES.md`, fora dos entregáveis |

O rascunho foi validado separadamente em `/private/tmp/jcss-submission-package-20260930/declarations-preview/`; `compile.log`, `preview.log`, `preview.pdf` e os dois PNGs registram essa verificação. Isso confirma a sintaxe e a apresentação do fragmento, sem confirmar os fatos marcados `[OWNER: ...]`.

A falha estrutural está em `S/experiments/exploratory/detection-boundary-v4-exploratory/VALIDATION-FIXES.md:17` e demais links do mesmo arquivo, que apontam a outro worktree e a recibos locais. O arquivo é idêntico ao da base `31090f59`; não foi alterado nesta tarefa. A saída está em `/private/tmp/jcss-submission-package-20260930/repository-check.txt`. Portanto, não se registra o gate global como aprovado.

Saída literal do comando solicitado:

```text
venue: jcss; PDF: 42 pages, 25936 extracted words
abstract: 250 words; keywords: 5
citations: 54 used keys; 73 bibliography entries
placeholders: 19
PASS
```

Locais dos 19 placeholders reconhecidos: `main.tex:26`, `main.tex:91`, `sections/conclusion.tex:1`; `generated/gate-outcomes.tex:7` e `:11`; `generated/unit-status.tex:7` e `:11`; `generated/primary-boundary-figure.tex:4`; `generated/auc-profiles.tex:4`; `generated/boundary-table.tex:7`; `generated/shp-anchor.tex:4`; `generated/supplement-auc-profiles.tex:4`, `:8`, `:12` e `:16`; `generated/supplement-family-offsets.tex:4`; `generated/supplement-secondary-targets.tex:7`; `generated/supplement-low-strength-cells.tex:7`; `generated/supplement-gap-domain.tex:7`. Raiz: `M/`.

O total não é um censo de pendências: a expressão em `M/pipeline/paper_check.py:14` não reconhece `[to be filled ...]` em `main.tex:81`, `sections/verification.tex:47` e `sections/appendix-odd.tex:12`, `:22`, `:135`. O modo normal verifica rótulos, faixas e chaves, não veracidade/completude das declarações. Nenhum JSON foi fabricado para passar o modo final, e nenhuma análise científica foi executada.

## Handoff ao coordenador

Foram criados somente este checklist e `pipeline/drafts/2026-09-30/declarations-draft.tex`, desligado do `main.tex`. Antes de submeter: concluir resultados e suas decisões humanas, fechar Q4, completar autoria/declarações, comprovar acessos e versão arquivada, gerar e revisar figuras/T1s, resolver a apresentação das referências e montar a carta/metadados. Recompilar o pacote final e rodar `--submission --result-values` com o JSON validado do release. A aprovação científica continua sendo do Research Owner.

[jcss]: https://link.springer.com/journal/42001/submission-guidelines
[policies]: https://link.springer.com/brands/springer/journal-policies
[data-policy]: https://www.springernature.com/gp/authors/research-data-policy
[data-statements]: https://www.springernature.com/gp/authors/research-data-policy/data-availability-statements
[sensitive-data]: https://www.springernature.com/gp/authors/research-data-policy/sensitive-data
[data-help]: https://support.springernature.com/en/support/solutions/articles/6000237611-write-a-data-availability-statement-for-a-paper
[sensitive-help]: https://support.springernature.com/en/support/solutions/articles/6000237612-sensitive-data-or-data-about-human-participants-sharing-expectations
[reused-data]: https://support.springernature.com/en/support/solutions/articles/6000237607-my-research-didn-t-generate-data-or-i-reused-existing-data
[code-policy]: https://www.springernature.com/gp/open-science/code-policy
[code-help]: https://support.springernature.com/en/support/solutions/articles/6000237619-software-and-code-sharing
[ai-writing]: https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation
[ai-research]: https://www.springernature.com/gp/policies/editorial-policies/using-ai-in-research
[ai-guidance]: https://group.springernature.com/gp/group/ai/ai-guidance-for-researchers-editors-reviewers
[cover-letter]: https://support.springernature.com/en/support/solutions/articles/6000245674-cover-letter
[shp-contract]: https://www.swissubase.ch/en/catalogue/studies/6097/latest/datasets/932/3605/contract/usage-license
[shp-access]: https://forscenter.ch/projects/swiss-household-panel/data/

## Fechamento técnico sem resultados e sem decisões do Owner

Worktree `docs/submission-readiness`, base `346e2c5c` (`integration/ic-20260928`), sem commit. Foram concluídos a montagem privada de J5, a apresentação de J6, o preparo e a validação sintética dos geradores de J7, a rota pública de D1/DS1 e quatro sobreposições parciais na seção de trabalhos relacionados. As entradas novas são Devine–Valgarðsson 2024, Schuurman–Hamaker 2019, Soni–Ramirez–Eisenstein 2019 e Lang et al. 2026; R64–R71 e BIB-20260930 registram fontes, locadores e limites de leitura. Lang foi lido no preprint vinculado ao DOI editorial, não no texto publicado. CS1 continua dependendo de depósito/acesso e identificador real do Owner.

Nenhum dado selado/restrito foi lido. Não foram alterados freeze, declarações, módulos de simulação exploratória, exportadores/tabelas/comparações protegidos, shells, POST-RELEASE ou a nota de restrições. A diferença de figuras rastreadas contém somente dez PNGs `_synthetic`; os dez PDFs novos também são amostras. Tabelas/CSV de amostra conservaram seus bytes. Nenhum exportador foi executado contra dados reais e a suíte inteira não foi rodada.

Artefatos de verificação estão sob `/private/tmp/jcss-readiness-20260930/`. Pacote entregue: `source-package-final/`, diretório 0700 e arquivos 0600, com `source-manifest.json` (28 arquivos, SHA-256/bytes, origem, marcadores e ativos ausentes). Sua cópia `package-verification-final/` foi compilada offline com a classe de `~/.local/state/research-workbench/springer-template/`. A classe conserva SHA-256 `36d0c3273a59d48dc6a9c7b080dfa1ec50dc10229d8751568d1f2e490ffa5ecc`; o estilo oficial conserva `b3a7c7fbcc1e7f9619de634fcea2f5bb7a245818a5942bc576e40ea001633332`; o estilo privado ajustado tem `da3ea79308465dc48dbc39294a090140c1e0fc31bf317e2d56f39f3fab9ee39a`. A transformação muda somente a condição de fallback de títulos; teste e revisão independente confirmaram os bytes. As macros tipográficas residem no main.tex. Isso conserva o estilo numérico exigido e deixa o vendor fora do Git.

| Medida do checker | Antes | Depois |
| --- | ---: | ---: |
| Páginas | 42 | 42 |
| Palavras extraídas do PDF integral | 25.936 | 26.341 |
| Chaves citadas | 54 | 58 |
| Registros BibTeX definidos | 73 | 77 |
| Placeholders reconhecidos | 19 | 19 |
| Resumo / palavras-chave | 250 / 5 | 250 / 5 |
| `paper_check.py --venue jcss --pdf main.pdf` | PASS | PASS |

O manifesto registra 31 marcadores com uma expressão mais ampla, que também reconhece `[to be filled ...]`; não se confunde com os 19 do checker. Figuras vetoriais reais e `generated/T1s_a_star_all_units.csv` estão ausentes e são pendências explícitas no pacote. A coleta de vetores/T1s foi exercitada com fixtures, sem usar o CSV sintético como resultado nem acrescentar metadados humanos. O PDF textual incorpora todas as fontes e não tem overfull nem referências indefinidas; underfull permanece. Bibliografia e rota SHP foram conferidas visualmente. Dez figuras v4 e duas do mapa tiveram verificação de fontes embutidas e ausência de raster interno, além da inspeção dos previews sintéticos.

| Portão / teste | Resultado |
| --- | --- |
| Estrutura: `cd workbench && uv run --locked python ../scripts/check_repository.py` | PASS, 7 checks |
| Ruff e `ruff format --check` nos seis .py tocados | PASS |
| Estudo: `uv run --locked mypy src tests` | PASS, 105 arquivos |
| Mypy adicional dos dois utilitários tocados em experiments/ | PASS, 2 arquivos |
| Testes existentes de relatório/mapa e pacote inicial | 116 passed; execução inicial durante ajustes, não recibo do snapshot final |
| Relatório e mapa: fonte mínima/dimensões, símbolos, legenda e bytes determinísticos | 29 passed; mapa revalidado após ajuste da legenda: 25 passed; após quebras das notas de F2/F4, 5 passed (inclui encaixe das notas e stop pré-G2) e 1 passed (texto de proveniência do sucessor) |
| Mapa + pacote + quatro testes de relatório após primeiros ajustes | 36 passed; layouts finais do relatório revalidados acima |
| Empacotador final, inclusive symlinks e estilo incompatível | 8 passed |
| Integridade do pacote privado | 28 hashes conferidos e modos 0700/0600 |
| `git diff --check` | PASS |

Para repetir a montagem após integrar os resultados, escolher uma pasta nova fora de Git e fornecer o PDF compilado correspondente:

```sh
cd studies/ic-2026-2027
uv run --locked python experiments/package_jcss_submission.py \
  --out /private/tmp/jcss-source-package-new \
  --template ~/.local/state/research-workbench/springer-template \
  --pdf /private/tmp/compiled-manuscript/main.pdf
```

O comando somente monta arquivos locais; não cria depósito, tag, licença ou DOI e não envia o pacote. O coordenador continua responsável pelo commit, pela integração dos artefatos autorizados e pela verificação do modo final com o JSON de valores liberado. Campos do Owner continuam abertos.
