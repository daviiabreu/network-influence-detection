# Acesso a dados e reprodução do antecedente empírico

Consulta em 24/09/2026. Dossiê exploratório das pistas 1 e 2 de
[`empirical-identifiability-leads.md`](empirical-identifiability-leads.md),
considerando a [revisão do desenho](design-review.md) e o
[mapa de afirmações](../../exploratory-claim-map.md). Nenhum microdado humano
foi adquirido. Os números de Gestefeld e Lorenz abaixo são relatos dos autores,
salvo as auditorias explicitamente identificadas. Este texto não escolhe questão,
adota referência, aprova protocolo ou altera o mapa sistemático amplo v4.

## Antecedente Gestefeld e Lorenz

No [artigo JASSS 26(4):9](https://www.jasss.org/26/4/9.html), consultado em
24/09/2026, os autores relatam ajuste a 1.235 distribuições de sete itens de
confiança institucional do ESS, em países e anos de 2002 a 2018. Para SHP,
usam confiança no governo em ondas anuais de 1999 a 2009: 50.008 transições
de 10.627 pessoas. Também houve o item em 2011, 2014 e 2017, excluído da
análise de transições anuais. O modelo original trabalha com opiniões
contínuas arredondadas em 11 categorias. O artigo relata 4.875 configurações,
dez réplicas por configuração e 48.750 simulações; 41.163 saídas foram
aproveitadas após o critério de estabilidade. Esses são tamanhos do estudo
publicado, não amostras verificadas de novo neste dossiê.

O artigo aponta para [o depósito OSF `fsbda`](https://osf.io/fsbda/),
consultado novamente em 24/09/2026. As primeiras tentativas falharam por 403
na ferramenta web e por DNS no `curl`. Com a rede restaurada, a
[API do nó](https://api.osf.io/v2/nodes/fsbda/)
e a [lista de arquivos](https://api.osf.io/v2/nodes/fsbda/files/osfstorage/)
abriram. O nó é privado, acessível pelo link de visualização publicado no artigo. Contém três
CSVs derivados, nenhum arquivo de código e nenhuma licença indicada nos
metadados. Os três downloads, URLs e SHA-256 constam da
[sonda](../../../../experiments/exploratory/antecedent-reproduction-gestefeld-lorenz/README.md);
os bytes ficaram fora do Git. Não se presume autorização de redistribuição.

A [sonda executada](../../../../experiments/exploratory/antecedent-reproduction-gestefeld-lorenz/README.md)
reimplementa a equação de atualização e usa os parâmetros de ajuste individual
da tabela 3, 800 agentes, 1.000 passos fixos e mais 24 passos. O
[log](../../../../experiments/exploratory/antecedent-reproduction-gestefeld-lorenz/run-2026-09-24-v3.log)
registra o comando, a semente `20230924`, Python 3.12.13 em macOS arm64,
0,349 s e o resultado: média categórica 6,68, com 580/800 agentes mudando
de categoria em 24 passos. Essa é uma confirmação computacional limitada de
distribuição deslocada coexistindo com mudança individual sob a regra e
parâmetros publicados. Não replica o código dos autores, o critério de
estabilidade, os ajustes ESS/SHP, a matriz de transição empírica, o ganho da
cognição motivada, R² ou D_micro. A análise SHP publicada usou microdados
cujo acesso e redistribuição são tratados abaixo.

A [auditoria dos três CSVs depositados](../../../../experiments/exploratory/antecedent-reproduction-gestefeld-lorenz/run-2026-09-24-deposit.log)
recontou 1.235 linhas ESS e 15 SHP (14 anos e uma linha de ajuste com base em
microdados). A tabela ESS deposita 161 linhas para `trstprt` (partidos) e 179
para `trstprl` (parlamento), ao contrário das contagens desses dois tópicos na
Tabela 1 do artigo. O CSV de simulações contém 44.788 linhas de 4.498 IDs de
parâmetros, contra 41.163 saídas estabilizadas relatadas no artigo. O intervalo
de R² já calculado no CSV SHP é 0,565–0,877, compatível com o 0,56–0,88
arredondado do texto. Essas verificações não refazem o ajuste e as divergências
não podem ser atribuídas a uma causa sem código e histórico de seleção.

## Matriz de acesso e de identificação

| Fonte | Acesso, uso acadêmico e redistribuição | Cobertura e tamanho confirmado | Papel nos leads e limite |
| --- | --- | --- | --- |
| ESS, rodadas 1–9 (2002–2018) | Download gratuito após cadastro curto no ESS Data Portal; licença de dados CC BY-NC-SA 4.0, portanto pesquisa de graduação sem finalidade comercial é compatível, com atribuição e compartilhamento de adaptações na mesma licença. A ESS recomenda vincular ao portal em vez de hospedar cópias em sites externos, exige citar edição e identificar alterações. [Prospecto ESS](https://www.europeansocialsurvey.org/sites/default/files/2024-04/prospectus_updated.pdf), [termos ESS](https://www.europeansocialsurvey.org/contact/disclaimer), consultados em 24/09/2026. | O antecedente usa 1.235 distribuições instituição–país–ano de 2002–2018: 161 para parlamento e 179 para cada uma das outras seis instituições. Os tamanhos de pessoas em cada célula não constam do artigo e dependem de extração do portal. [Gestefeld–Lorenz, §§ dados e Tabela 1](https://www.jasss.org/26/4/9.html), consultado em 24/09/2026. | Lead 1: histogramas de amostras transversais, nunca transições individuais ou exposição. Lead 2: não fornece pares pessoa–onda. |
| CRONOS-2 + ESS rodada 10 (2020–2022/2023) | Arquivos CSV/Stata/SPSS gratuitamente no ESS Data Portal, após cadastro curto, para uso não comercial; mesma licença ESS CC BY-NC-SA 4.0 nos dados comuns. Apenas duas variáveis sensíveis da onda 5 foram retiradas e pedem licença especial da Sikt; elas não são necessárias para estes leads. [Guia oficial CRONOS-2, §§ 4 e acesso](https://www.europeansocialsurvey.org/sites/default/files/2023-07/CRONOS2_user_guide_e01_0.pdf), [termos ESS](https://www.europeansocialsurvey.org/contact/disclaimer), consultados em 24/09/2026. | 12 países, recrutamento a partir da ESS10; 10.474 participantes recrutados (soma da Tabela 5), 6.493 entrevistas completas ou parciais na onda 1 e 6.032 na onda 4 (soma da Tabela 6; Hungria só ondas 1–2, portanto excluída da onda 4). Ondas 1/4 em 2021–2023 conforme grupos de países. As somas por onda NÃO são o número de pessoas com resposta válida ao mesmo item nas duas ondas. [Guia, Tabelas 1–6](https://stessrelpubprodwe.blob.core.windows.net/data/cronos2/CRON2_user_guide_e01_0.pdf), consultado em 24/09/2026. | Lead 1: pares pessoa–item–onda para os três itens repetidos, após parear os códigos de cada onda e verificar traduções nacionais. Lead 2: candidatos para matriz de transição e perdas, mas sem âncora independente de erro de resposta. Os codebooks oficiais confirmam três itens repetidos com mesmo rótulo e escala 0–10, sob códigos diferentes nas ondas 1 e 4, detalhados abaixo. Nenhuma rede ou fonte de exposição entre pessoas foi encontrada na documentação. [Página ESS CRONOS-2](https://www.europeansocialsurvey.org/methodology/methodological-research/modes-data-collection/cronos), [guia, § 3](https://stessrelpubprodwe.blob.core.windows.net/data/cronos2/CRON2_user_guide_e01_0.pdf), consultados em 24/09/2026. |
| Swiss Household Panel (SHP), “Living in Switzerland” | Gratuito, mas requer conta SWITCH edu-ID e aceite individual do contrato via SWISSUbase. FORS limita o acesso a pesquisadores e estudantes afiliados a universidade/instituição de ensino superior ou pesquisa, para pesquisa ou ensino acadêmico: uma IC de graduação afiliada é em princípio elegível, sujeita à verificação e ao contrato. Uso comercial proibido; nenhum dado pode ser cedido a terceiro, e cada membro da equipe assina separadamente. Publicações exigem citação e envio ao SHP; mudanças de tema devem ser notificadas. Não incluir microdados em Git. [FORS: dados e passos](https://forscenter.ch/projects/swiss-household-panel/data/), [políticas FORS](https://forscenter.ch/about-fors/policies/), [FAQ FORS](https://forscenter.ch/projects/swiss-household-panel/faq/), [contrato SWISSUbase](https://www.swissubase.ch/fr/catalogue/studies/6097/20679/datasets/932/3861/contract/usage-license), consultados em 24/09/2026. | O antecedente usa confiança no governo federal em 1999–2009, 50.008 deslocamentos anuais de 10.627 indivíduos; 2011, 2014 e 2017 são excluídos da transição anual por intervalo desigual. São números da publicação, não da versão atual. A documentação FORS informa amostras iniciais de 12.931 membros de domicílios (1999), 6.569 (ampliação 2004), 9.945 (2013) e 7.557 (2020), que NÃO são números de entrevistados válidos para esta análise. [Gestefeld–Lorenz, § SHP](https://www.jasss.org/26/4/9.html), [documentação FORS](https://forscenter.ch/projects/swiss-household-panel/documentation/), consultados em 24/09/2026. | Lead 1: confiança repetida e transições individuais; não identifica quem influenciou quem. Lead 2: resposta ordinal repetida + indicadores de participação, sem teste–reteste/validação externa identificados. A FAQ confirma `idpers` para junção, `SHP_MP` para participação em cada onda, `STATUS$$=0` para entrevista individual completa e `STATHH$$=1` para domicílio; `FILTER$$` separa amostras. No catálogo oficial da onda 2017, `P17P04` é “Trust in Federal Government”; `INT1704` registra intenção de participar na próxima onda (não participação efetiva), e `WI17LP...` são pesos longitudinais. A matriz oficial de variáveis por onda confirma `P$$P04` em cada ano de 1999–2009; os códigos expandidos e limites estão detalhados abaixo. [FAQ FORS](https://forscenter.ch/projects/swiss-household-panel/faq/), [catálogo FORS onda 19](https://devisu.forscenter.ch/index.php/catalog/1086/data-dictionary/F1/?offset=300), consultados em 24/09/2026. |
| The Arnhem School Study, módulo secundário (TASS), dado citado em Tang–Snijders–Flache | O [registro oficial DANS](https://ssh.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/DANS-ZC6-JHDK), versão 2.3, declara DANS Licence e pedido de acesso a arquivos habilitado. O catálogo marca o codebook, três formatos do conjunto e os questionários das ondas 4–7 como restritos. O portal institucional rotula o registro “Open Access”, mas isso não libera os arquivos; redistribuição depende dos termos e de permissão do titular. A [política DANS para arquivos restritos](https://support.dans.knaw.nl/en/support/solutions/articles/80001156134-how-can-i-make-use-of-files-with-restricted-access-) descreve solicitação ao titular. Elegibilidade de estudante/uso em IC depende da decisão do titular e dos termos específicos, não confirmada. [registro institucional](https://research.rug.nl/en/datasets/the-arnhem-school-study-tass-secondary-school-module/), [instruções DANS](https://support.dans.knaw.nl/en/support/solutions/articles/80001156134-how-can-i-make-use-of-files-with-restricted-access-), [licença DANS](https://dans.knaw.nl/wp-content/uploads/2022/01/DANS_Licence_EN.pdf), consultados em 24/09/2026. | Módulo secundário ondas 4–7 (set/2008–mai/2010). Artigo usa ondas 5 (dez/2008, 1.246 respondentes, 88,1%) e 6 (jun/2009, 1.220, 86,0%); após exclusões, 46 classes e 1.019 adolescentes, dos quais 991 em ambas. São números do artigo, não inspeção do arquivo. [Tang et al., § Data](https://www.jasss.org/28/1/2.html), [registro institucional](https://research.rug.nl/en/datasets/the-arnhem-school-study-tass-secondary-school-module/), consultados em 24/09/2026. | Lead 1: único candidato nomeado com opinião individual, exposição em rede e dois tempos. Variáveis relatadas: nomeações dirigidas de melhores amigos dentro da classe nas duas ondas; gosto pela roupa rap/hip-hop de 1 a 5 nas duas ondas; sexo; classe/tamanho. Os formatos `.POR`, `.SAV` e `.tab` constam no depósito restrito; os campos internos não foram inspecionados. Participação em ambas fornece atrito básico; não foi localizada âncora independente de erro da medida. Lead 2: resposta ordinal repetida, com arquivos sujeitos a pedido de acesso; a população menor de idade exige análise institucional antes da aquisição. [Tang et al., § Data](https://www.jasss.org/28/1/2.html), consultado em 24/09/2026. |

## Variáveis exigidas por nível de observação

### Conferência dos itens nos codebooks oficiais

O [catálogo ESS do CRONOS-2, onda 1](https://ess.sikt.no/en/study/2f6d663c-8174-4f99-8289-b41e06051a7d/58)
(edição 1.2, arquivo `CRON2W1e01_2`) e o da
[onda 4](https://ess.sikt.no/en/study/4194bee2-e8dd-4738-9785-f26c460f5136/43)
(edição 1.0, arquivo `CRON2W4e01`) oferecem metadados de variável e códigos de
resposta. A consulta de 24/09/2026 à API oficial do catálogo encontrou os
seguintes pares:

| Conteúdo do item | Onda 1 | Onda 4 | Comparação |
| --- | --- | --- | --- |
| Confiança nas pessoas que trabalham no setor público | [`w1q16`](https://ess.sikt.no/en/variable/82bfb274-6846-4a2a-a3e4-ce8995d3e2c4) | [`w4q61`](https://ess.sikt.no/en/variable/28d18b0c-0458-4767-bd4d-0162a5417934) | Mesmo rótulo em inglês e escala 0–10. |
| Confiança no governo local | [`w1q17`](https://ess.sikt.no/en/variable/b8fc2415-dbdb-4028-82c4-4d54b19304bb) | [`w4q62`](https://ess.sikt.no/en/variable/5ce80a5b-2c33-4ed2-b11a-e4ce152271c2) | Mesmo rótulo em inglês e escala 0–10. |
| Confiança no governo nacional do país | [`w1q18`](https://ess.sikt.no/en/variable/7f46631b-7be7-496f-8f92-b9affb38f221) | [`w4q63`](https://ess.sikt.no/en/variable/4248cf6f-bd5a-4c19-b43b-079fb5296df8) | Mesmo rótulo em inglês e escala 0–10. |

Em todos os seis registros, 0 significa nenhuma confiança, 10 confiança
completa e 99 é ausência de resposta. O campo de pergunta das ondas 1/4 traz
o mesmo alvo; na onda 4, o catálogo apresenta o enunciado introdutório
integralmente em `w4q61` e apenas o alvo em `w4q62`/`w4q63`. Isso confirma
três candidatos para pareamento, não a quantidade de pares válidos nem a
equivalência de traduções nacionais. Não são os sete itens transversais do ESS
usados por Gestefeld e Lorenz.

Para SHP, a [matriz oficial FORS de variáveis por onda](https://forscenter.ch/wp-content/uploads/2025/02/shp_variables_by_waves.xlsx)
(SHA-256
`cc20b1bfa3a53bf9abe0fc73d2d987f4ce5b3937d1f8e73347944655261ceb9e`,
aba `INDIVIDUAL ANNUAL FILES`, linha 1020) marca `P$$P04`, “Trust in Federal
Government”, em cada coluna de 1999 a 2009, deixa 2010 vazio e volta a
marcar 2011, 2014 e 2017. O [inventário FORS de 2012](https://forscenter.ch/wp-content/uploads/2022/02/wp_2_2012.pdf)
também registra `P$$P04` na faixa W01–W13; a matriz detalhada é a evidência
para os anos efetivamente marcados. Pela substituição de `$$` pelos
dois dígitos do ano, os códigos para 1999–2009 são `P99P04`, `P00P04`,
`P01P04`, `P02P04`, `P03P04`, `P04P04`, `P05P04`, `P06P04`, `P07P04`,
`P08P04` e `P09P04`; o [catálogo da onda 2017](https://devisu.forscenter.ch/index.php/catalog/1086/data-dictionary/F1/?offset=300)
confirma a forma expandida `P17P04`. A matriz verifica presença e rótulo, mas
não fornece a redação completa, códigos de ausência ou pesos de cada onda;
essas propriedades ainda exigem os questionários e arquivos anuais contratados.

**Lead 1.** Para o nível de marginais ESS, extrair `cntry`, rodada/ano, peso apropriado e sete itens `trstprl` (parlamento), `trstlgl` (sistema legal), `trstplc` (polícia), `trstplt` (políticos), `trstprt` (partidos), `trstep` (Parlamento Europeu) e `trstun` (ONU), descartando códigos 77/88/99 como respostas válidas. Esses nomes e códigos estão no [protocolo oficial ESS10, Tabela F.1b](https://stessrelpubprodwe.blob.core.windows.net/data/round10/survey/ESS10_data_protocol_e01_7.pdf), consultado em 24/09/2026; verificar variações por rodada antes de combinar 2002–2018. Para transições, exigir item igual, identificador da pessoa, onda/data, peso longitudinal ou procedimento explícito, modo de coleta e indicadores de resposta/ausência. No CRONOS-2, `cntry`+`idno`+`mode` é chave oficial de junção entre arquivos, e `c2weight` é peso ajustado por não resposta para cada onda; esse peso sozinho não resolve seleção para o subconjunto que respondeu às DUAS ondas. [Guia CRONOS-2, § combinação e pesos](https://stessrelpubprodwe.blob.core.windows.net/data/cronos2/CRON2_user_guide_e01_0.pdf), consultado em 24/09/2026. Para exposição efetivamente observada, TASS tem nomeações de amizade dirigidas por onda, mas amizade é proxy de oportunidade, não contato efetivo ou direção comprovada de influência. [Tang et al.](https://www.jasss.org/28/1/2.html), consultado em 24/09/2026.

**Lead 2.** SHP requer `idpers`, confiança no governo federal na onda `t` e `t+1`, `STATUS$$`, participação longitudinal de `SHP_MP`, `FILTER$$`, data/onda, modo de entrevista e pesos longitudinais (a nomenclatura precisa ser verificada para o recorte final). CRONOS-2 requer `cntry`+`idno`+`mode`, um dos três pares de códigos e rótulos comprovados nas ondas 1/4, indicadores de conclusão/omissão, recrutamento, `c2weight` e covariáveis prévias da ESS10; o guia cita `vote`, `brncntr`, `gndr`, `agea`, `maritalb`, `domicil`, `eisced`, `pdwrk`, `region`, `viepol` e `fairelc` no ajuste de não resposta. Esses são preditores de resposta, NÃO âncoras independentes do erro do item. [Guia CRONOS-2, § pesos](https://stessrelpubprodwe.blob.core.windows.net/data/cronos2/CRON2_user_guide_e01_0.pdf), [FAQ FORS](https://forscenter.ch/projects/swiss-household-panel/faq/), consultados em 24/09/2026. Nenhuma fonte oficial consultada documenta teste–reteste próximo, entrevista de validação ou medida externa que identifique a matriz de erro para esse mesmo item. A análise de sensibilidade pode declarar uma região hipotética conjunta, mas não apresentar um ranking empírico identificado.

## Passos humanos de Davi

1. **ESS/CRONOS-2 (cadastro, não aprovação científica):** abrir o [Data Portal](https://www.europeansocialsurvey.org/data-portal), criar a conta pessoal solicitada pela ESS, consultar os termos, entrar e baixar CSV das rodadas ESS de interesse, ESS10, CRONOS-2 integrado ou ondas 1/4 e codebooks/questionários correspondentes. Guardar versões, DOI e hashes em armazenamento autorizado; observar a licença CC BY-NC-SA 4.0 e citar o arquivo exato. Não é necessário pedir a licença especial da Sikt para as duas variáveis de identidade da onda 5 porque não entram neste plano. [Prospecto ESS](https://www.europeansocialsurvey.org/sites/default/files/2024-04/prospectus_updated.pdf), [guia CRONOS-2](https://www.europeansocialsurvey.org/sites/default/files/2023-07/CRONOS2_user_guide_e01_0.pdf), consultados em 24/09/2026.
2. **SHP (contrato individual):** entrar na [página de download FORS](https://forscenter.ch/projects/swiss-household-panel/data/), seguir para SWISSUbase > Datasets > “Living in Switzerland” (edição/ondas relevantes) > Start download; criar/usar SWITCH edu-ID, declarar afiliação e objetivo de IC, ler e aceitar pessoalmente o contrato, baixar em área privada. Cada integrante que acessará os dados deve repetir o procedimento; ninguém repassa o arquivo. Se a afiliação brasileira não for reconhecida no cadastro ou a interpretação do contrato for incerta, escrever para `swisspanel@fors.unil.ch` antes de usar os dados. Não cabe contrato de ensino adicional salvo se o uso for em disciplina/seminário compartilhado. [FORS: instruções](https://forscenter.ch/projects/swiss-household-panel/data/), [FAQ FORS](https://forscenter.ch/projects/swiss-household-panel/faq/), [políticas FORS](https://forscenter.ch/about-fors/policies/), consultados em 24/09/2026.
3. **TASS (só se a decisão científica exigir exposição real):** abrir o [registro do módulo secundário](https://research.rug.nl/en/datasets/the-arnhem-school-study-tass-secondary-school-module/) e seguir o DOI `10.17026/dans-zc6-jhdk` ao DANS Data Station; após login, conferir aba Terms e Files. O depósito marca pedido de acesso habilitado: selecionar os arquivos necessários, explicar IC, ondas 5/6 e campos, aceitar pessoalmente os termos e aguardar autorização do titular; pedir esclarecimento sobre uso por graduando e divulgação de agregados. Não redistribuir microdados nem registrar conteúdo restrito no Git. [DANS: acesso restrito](https://support.dans.knaw.nl/en/support/solutions/articles/80001156134-how-can-i-make-use-of-files-with-restricted-access-), [licença DANS](https://dans.knaw.nl/wp-content/uploads/2022/01/DANS_Licence_EN.pdf), consultados em 24/09/2026.

Não foi possível verificar: número de respostas válidas por célula ESS;
tamanho de pares completos com resposta válida entre ondas 1/4 do CRONOS-2;
redação integral, modo e pesos de confiança no SHP entre 1999–2009;
existência de uma âncora independente para erro de resposta em qualquer dos
painéis; termos pessoais de acesso e campos específicos do TASS; e licença e
código original do antecedente Gestefeld–Lorenz. Nenhuma dessas lacunas deve
ser preenchida com os totais de entrevistas ou com os valores publicados para
uma seleção diferente.

Na nova tentativa de 24/09/2026, [termos](https://www.europeansocialsurvey.org/contact/disclaimer)
e [portal ESS](https://www.europeansocialsurvey.org/data-portal) responderam HTTP 200;
o [DOI TASS](https://doi.org/10.17026/dans-zc6-jhdk) redirecionou ao
Data Station oficial, cuja API forneceu licença e inventário. As primeiras
falhas de 502 e DNS foram contingências da tentativa anterior. A [página SWISSUbase consultável](https://www.swissubase.ch/en/catalogue/studies/6097/latest/datasets/932/2297/overview)
mostrou a versão anterior 5.1 e orienta a escolher a versão publicada mais
recente; não substitui o contrato ou o download pessoal. As classes de acesso
acima continuam baseadas nas fontes oficiais que puderam ser lidas, com as
incertezas indicadas.

## Decisão de custo por pista

Para a pista 1, a análise decisiva mais barata com os insumos de fato
disponíveis é um microcaso enumerado de dois mecanismos com o mesmo gerador,
trajetórias e canal de medida: demonstrar marginais iguais ou quase iguais e
transições distintas, depois reaplicar máscaras de observação de histograma,
pares individuais e fonte identificada às mesmas trajetórias. Fixar tamanho
e custo da amostra. Isso testa a possibilidade lógica do ganho incremental;
não testa influência em humanos. Dados ESS comuns permitiriam apenas a camada
de marginais. Sem díades com fonte de opinião observada, não se testa a terceira
camada como efeito empírico.

Para a pista 2, a análise decisiva mais barata é construir duas matrizes de
transição latente e dois canais conjuntos de resposta e atrito que induzam a
mesma distribuição observada. Só depois procurar âncoras independentes para
delimitar uma região conjunta de erro e seleção; caso não existam, o resultado
defensável é o contraexemplo/limite de identificação. Nem a resposta ordinal
isolada nem o ajuste livre do erro e do atrito aos mesmos pares identificam
um ranking entre persistência e dinâmica. Um painel permissível com item
repetido permitiria comparar previsões observadas, mas inferência de opinião
latente exige âncora externa e verificação de pesos, modo e perda entre ondas.

Essas duas tarefas analíticas cabem antes de qualquer acesso humano ou campanha
de simulação. A comparação com dados humanos e a reivindicação de novidade
seguem condicionadas à síntese e às decisões do Research Owner.
