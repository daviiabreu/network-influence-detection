# Metadados de submissão ao JCSS — rascunho P05

Preparado em 30/09/2026 na base `00c8dc3d`, ramo `docs/jcss-cover-letter-20260930`. Os valores abaixo distinguem conteúdo versionado, composição condicional e fatos a confirmar pelo responsável. Atualização de 01/10/2026: as escolhas pendentes foram feitas pelo coordenador sob delegação do Owner (decisões 161–163); não resta campo `[OWNER]`. Não foi acessado o portal nem realizada submissão.

A referência de requisitos é o [checklist de 30/09](../../review/jcss-submission-checklist-2026-09-30.md), especialmente CL1, CL2, P5 e “Carta e metadados do fluxo”. Os IDs de fontes na tabela são os desse checklist. Não se presume que cada declaração tenha um campo separado no portal: repetir a informação nos campos que o fluxo efetivamente apresentar.

## Identificação, título e classificação

| Campo | Valor preparado / pendência | Fonte do valor e do requisito |
| --- | --- | --- |
| Periódico | Journal of Computational Social Science | Checklist; [diretrizes JCSS](https://link.springer.com/journal/42001/submission-guidelines). |
| Título | Detection boundaries for nominal partner drift against matched persistence in synthetic opinion panels | Escolha de 01/10/2026 sob delegação do Owner (decisão 161); idêntico em `main.tex`, carta e sistema. |
| Título curto, se o sistema pedir | Detection boundaries in opinion panels | Argumento curto de `\title` em `main.tex`; não há exigência de campo separado documentada no checklist. |
| Tipo de artigo | Artigo completo de pesquisa, forma mantida também nos ramos de falha do gate. [NO DIA: escolher o rótulo de artigo completo que o portal oferecer, por exemplo “Research Article”.] | Decisão 99/Q1 e correção 101 nas [decisões de interpretação](../2026-09-28/results-interpretation-decisions-2026-09-29.md). Consulta web limitada à ambiguidade deste campo: [JCSS, General Information](https://link.springer.com/journal/42001/submission-guidelines), permite artigo completo ou nota curta; não comprova o nome do menu no sistema. |
| Palavras-chave | Opinion dynamics; Social influence; Panel data; Measurement error; Model discrimination; Agent-based model | `\keywords` de `main.tex`; checklist J4: quatro a seis, seis aqui. Decisão 161. |
| Idioma | Inglês | `main.tex`, [carta](cover-letter.md) e [shell do resumo](../2026-09-28/results-shells-abstract.md). |
| Autores e ordem | Davi Abreu da Silveira (primeiro autor e correspondente); Henrique Mohallem Paiva (orientador, último autor, henrique@inteli.edu.br). | Decisão 161; `main.tex`, bloco de autores. |
| Afiliações | Inteli – Instituto de Tecnologia e Liderança, São Paulo, SP, Brasil, para os dois autores. | Decisão 161; `main.tex`, `\affil`. |
| Correspondente | Davi Abreu da Silveira, Inteli, daviabreudasilveira@gmail.com (email pessoal; o da Abstra é só de trabalho). | Decisões 161 e 170. |
| ORCID | Davi cria o ORCID no dia da submissão, se o sistema pedir; o do orientador vem com os dados dele. | Checklist J2: campo condicional. Decisão 161. |
| Google Scholar | Preencher só se o campo for obrigatório no fluxo; Davi não tem publicações anteriores. | Checklist J11. Decisão 161. |

## Resumo e carta

O valor do campo resumo é o texto inglês composto a partir do [shell do resumo](../2026-09-28/results-shells-abstract.md), não o resumo ainda incompleto de `main.tex`. [PÓS-LIBERAÇÃO: colar o resumo montado e conferir igualdade entre manuscrito e sistema.] O requisito de extensão vem de J3: 150–250 palavras, sem referências não especificadas nem abreviações indefinidas. Definir AUC na primeira ocorrência ao preparar o texto simples do campo. A extensão atual do `main.tex` não valida uma composição posterior.

| Campo / seleção | Fonte e regra para preencher |
| --- | --- |
| Texto fixo do resumo | Baseline conciso em “Composition and budget”, seguido da limitação comum sobre leis, canal e discriminador; fonte: shell do resumo e decisões 91, 99/Q2 e 101/Q17. Preservar o texto prescrito, fazendo apenas a expansão necessária da abreviação. |
| Gate aprovado | Uma sentença G; avaliação com novas sementes após exposição parcial e emenda; B02 quando aplicável; H-B, H-BD ou B03 com D-after-B03 somente quando permitido; P6-a/P6-empty, B10 e B06 conforme condições do shell. Fonte: export validado e shell, sem valores preenchidos neste rascunho. G0/G1b/G1c/G2 aprovados e G2c em curso não selecionam esse ramo. |
| Permissão entre mecanismos | `v4.mechanisms.allowed` controla toda frase entre mecanismos, inclusive opcionais. Com zero, só B e a marca B02 quando pertinente. Com um, H-BD/D-after-B03/B10 ainda dependem do conjunto comum pertinente. Contagens pareadas usam `v4.bd.n_eligible`, a lista explícita `v4.bd.r_eligible` e IDs regionais pareados, nunca totais não mascarados por família. Conjunto comum vazio implica H-B e P6-empty. Fonte: decisão 91 e shell. |
| Cláusula obrigatória X6 | “The exploratory check at r = 0.70 found below-nominal interior coverage.” Somente se `v4x.x6.x6a.band.vs_d1.primary.reading`, efetivo após sensibilidade da precisão de referência, for `failure` ou `subnominal`. Usar o agregado exploratório validado e preservar seu rótulo. `inconclusive`/sem leitura não dispara; X6b, cobertura pontual, verdade populacional e leitura secundária gaps-as-misses não substituem esse gatilho. Fonte: shell e decisão 91. |
| Opcionais e orçamento | Primeiro que couber, na ordem: três cláusulas B09 (largura finita, extremo fora da grade, extremo censurado), B04, B05, B08, B11, B14. Não retirar anterior para encaixar posterior; não retirar obrigatórias, inclusive X6. Contar o texto preenchido com `paper_check.py`, incluindo a lista de r e a expansão de AUC. Fonte: decisão 101/Q17, registrada na correção final da decisão 99 no arquivo de interpretação. |
| Conteúdo fora do resumo | Nenhuma leitura X3, X4 ou X7. X5 permanece em Discussion/Conclusion; alvos derivados 0.60/0.80 ficam no suplemento. Nenhuma faixa é chamada de melhor valor; B03 cobre nove grades completas, P5-b somente fronteiras atingidas. Fonte: decisões 91 e 101/Q18. |
| Falha B1b-G2c | Baseline conciso + sentença de desenho exigindo todas as etapas + sentença B1b-G2c + encerramento X e limitação comum. Somente falha registrada do G2c. Forma de artigo completo, Methods sem mudança. Fonte: shell e decisões 99/Q1–Q2 e 101; não reescrever o resumo como outro estudo após o resultado. |
| Janela encerrada B1d | Mesma composição de falha, selecionando apenas B1d no fechamento fixo `2026-10-19T02:59:00Z`, sem falha anterior ou stop e com etapa ausente/incompleta. Relatar nos Results etapa, tarefas concluídas/planejadas e ausência de tier. Trabalho posterior pertence somente a possível sucessor. Fonte: shell e decisão 99/Q3. |
| Carta ao editor | [cover-letter.md](cover-letter.md), Parte I mais exatamente um parágrafo da Parte II. [PÓS-LIBERAÇÃO: só extensão, DOI e o parágrafo da Parte II; os fatos e atestações foram decididos em 01/10.] Fonte: checklist CL1–CL2/P5 e “Carta e metadados do fluxo”. A obrigatoriedade de upload da carta não foi demonstrada no checklist; conferir o campo no fluxo efetivo. |

Os únicos ramos de falha preparados são B1b-G2c e B1d. O estado público fornecido para a tarefa informa G2 aprovado às 10:01 UTC de 30/09, 700/700 e zero falhas; não há resultado confirmatório nem leitura dos exploratórios selados disponível para preencher os campos. A carta segue as mesmas seleções obrigatórias do resumo; somente opcionais efetivamente retidos no resumo final podem ser transportados para ela.

## Declarações e disponibilidade

| Campo | Valor preparado / pendência | Fonte do valor e do requisito |
| --- | --- | --- |
| Originalidade / publicação prévia | Trabalho inédito, sem preprint nem versão anterior publicada. | Decisão 161; busca OpenAlex sem produção anterior de Davi (lista de revisores). |
| Exclusividade | Não está em avaliação em outro periódico. | Decisão 161. |
| Aprovação dos autores e instituição | Todos os autores aprovam o manuscrito final antes do envio; o orientador aprovou o desenho e as emendas (decisão 161) e recebe o PDF final no dia da submissão. | Checklist CL2 e J13. |
| Financiamento / apoio material | “No funding was received for conducting this study.” Apoio material do Inteli (computadores do laboratório) nos agradecimentos. | Decisão 161; `main.tex`, Funding e Acknowledgements. |
| Interesses concorrentes | “The authors have no relevant financial or non-financial interests to disclose.” | Decisão 161; `main.tex`. |
| Ética | “Not applicable: the study analyses simulated data, its exploratory reliability anchor uses anonymized Swiss Household Panel microdata obtained under the SHP data-use contract, and no data were collected from people for this study.” | Decisões 161 e 162; `main.tex`. |
| Consentimento de participação | Não se aplica (coberto pela frase de ética). | Decisão 161. |
| Consentimento de publicação | Não se aplica. | Decisão 161. |
| Contribuições e responsabilidade | CRediT em `main.tex`: Davi — conceptualization, methodology, software, formal analysis, investigation, visualization, project administration, writing; Henrique Mohallem Paiva — supervision, resources, writing (review and editing). | Decisão 161. |
| Agradecimentos | Inteli, pelos computadores do laboratório; frase obrigatória do SHP (“This study has been realized using the data collected by the Swiss Household Panel (SHP), which is based at the Swiss Centre of Expertise in the Social Sciences FORS. The project is financed by the Swiss National Science Foundation.”). | Decisões 161 e 162; licença de uso SWISSUbase. |
| Material relacionado / permissões | Nenhum. | Decisão 161. |
| Uso de IA | Texto final em Methods, “Use of generative AI” (M54/M55), por modelo e papel; agentes não são autores; autores assumem a responsabilidade. | Decisão 161; tabela de evidência em `ai-disclosure-evidence.md`. |
| Disponibilidade dos dados sintéticos | Depósito único no Zenodo, aberto na submissão, licença MIT para todo o material próprio; DOI preenchido no dia. | Decisão 161; `coord/deposit-options-20260930.md`. |
| Dados secundários | Âncora SHP incluída: *Living in Switzerland Waves 1-26 + Long file + Beta version Wave 27*, versão 12.0, DOI 10.48573/haxy-c230 (DOI geral 10.48573/pjmf-8s41), ondas 1999–2009, só a variável PyyP04 e idpers; só agregados saíram do diretório restrito. Figuras e tabelas com SHP levam “Source: Swiss Household Panel (SHP)”. O contrato exige enviar ao SHP uma cópia do artigo publicado. | Decisão 162; `main.tex` AV01; `references.bib` (`shpgroup2026data`). |
| Disponibilidade de código | No mesmo registro Zenodo (MIT), com a árvore congelada `375138418f7f9e4528f0c2466f4600a76fee1bad` identificada; o repositório canônico continua privado. | Decisão 161. |
| Versões posteriores e reprodução | [PÓS-LIBERAÇÃO: revisões efetivamente usadas para relatório, figuras, wrapper e eventual âncora, com manifestos e ambiente, preenchidas pelo coordenador.] Delimitar essas versões da árvore congelada. | `main.tex`, blocos de disponibilidade; checklist P2/J1 e separação da code closure. Não atribuir reprodução bit a bit a plataformas não validadas. |

## Editor e revisores sugeridos

A lista de candidatos, com fontes e checagem de independência, fica fora do repositório, em `coord/jcss-suggested-reviewers-20260930.md`, porque sugestões de revisores são confidenciais no fluxo editorial.

O fluxo documentado pede um editor e três revisores, não uma lista opcional presumida. Fonte: checklist J11 e “Carta e metadados do fluxo”, [JCSS, Important Note](https://link.springer.com/journal/42001/submission-guidelines). As sugestões podem não ser acolhidas. Não há nomes aprovados disponíveis e ninguém deve ser contatado para preencher este rascunho.

| Campo | Nome, afiliação e contato | Identidade, adequação e independência |
| --- | --- | --- |
| Editor sugerido | Escolhido em 01/10 (decisão 161); nome e dados no arquivo confidencial de coordenação. | Verificação no arquivo confidencial. |
| Revisor 1 | Escolhido em 01/10 (decisão 161); nome e dados no arquivo confidencial de coordenação. | Verificação no arquivo confidencial. |
| Revisor 2 | Escolhido em 01/10 (decisão 161); nome e dados no arquivo confidencial de coordenação. | Verificação no arquivo confidencial. |
| Revisor 3 | Escolhido em 01/10 (decisão 161); nome e dados no arquivo confidencial de coordenação. | Verificação no arquivo confidencial. |

Usar informação de identidade verificável na carta quando necessária; considerar diversidade institucional/geográfica, que o checklist registra como recomendação. Agentes internos não são revisores humanos independentes. Não inventar um período universal de conflito que as fontes não especificam; conferir as perguntas do sistema e documentar a verificação do responsável.

## Metadados do suplemento e fechamento do formulário

O checklist J8–J9 documenta título, periódico, autores e afiliação/email do correspondente em cada suplemento. Para a cópia de submissão de T1s, a proposta é `ESM_1.csv`, chamada Online Resource 1, com colunas constantes `article_title`, `journal`, `authors`, `corresponding_affiliation`, `corresponding_email`, mantendo o CSV regular. [PÓS-LIBERAÇÃO: conferir inventário e legenda contra o arquivo final; autores e contato conforme a decisão 161.] Fonte: checklist, “T1s e carta: montagem posterior do pacote”. Valores científicos vêm apenas do export autorizado; esta proposta não afirma que o arquivo final existe.

Antes de copiar os valores para o sistema, o coordenador confere o resumo e o parágrafo da carta contra os mesmos exports validados e as decisões 91/99/101; os responsáveis completam as atestações e verificam acessos, identificadores e pessoas. A inclusão da âncora em ramo de gate segue B1-SHP/decisão 101, separada e sem curva, fronteira ou F6; o caminho gate-only ainda requer a extensão de vinculação documentada se esse ramo for escolhido. Isso não fornece valores à carta nem autoriza leitura de dados restritos.

[NO DIA: Davi lê o PDF final, o orientador aprova o mesmo PDF, e Davi faz o envio na própria conta, conferindo os campos que o portal apresentar.] As exigências e o upload da carta continuam sujeitos à conferência operacional do fluxo, sem transformar estes rascunhos em autorização de envio.
