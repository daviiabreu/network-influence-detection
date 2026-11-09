# Revisão das pendências do formulário — 14/09/2026

Davi autorizou a continuação com “perfeito, pode seguir” após o [primeiro rascunho](README.md). A consulta adicional examinou os 17 casos destacados, com fontes de editoras, autores e instituições. Três subagentes produziram os achados; a coordenação revisou as propostas e seus suportes. São propostas de autoria da IA, sem decisão humana ou calibração científica implícita.

| Proposta | Primeiro rascunho | Após consulta |
| --- | ---: | ---: |
| Incluir para avaliação posterior | 16 | 19 |
| Excluir pelos critérios | 21 | 29 |
| Incerto | 13 | 2 |

Onze julgamentos mudaram após obtenção de informação adicional. As outras 33 linhas fora da consulta e os seis campos extraídos do PDF permanecem iguais. O [formulário revisado](http://127.0.0.1:8770/) apresenta as novas fontes e conserva o primeiro rascunho como histórico.

## Achados por caso

A tabela resume a interpretação da IA sob o protocolo v3. Inclusão significa avançar para avaliação posterior; propostas baseadas em resumos não substituem a elegibilidade de texto completo. As limitações de cada consulta constam no formulário e no JSON local.

| Caso | Antes → depois | Evidência e interpretação |
| --- | --- | --- |
| V3-03 | incluir → incluir | O resumo editorial descreve evolução iterativa das opiniões dos decisores; a pendência temática foi esclarecida. [Fonte primária](https://www.sciencedirect.com/science/article/pii/S1568494624010019). |
| V3-06 | incerto → incluir | O feedback da FMEA ajusta opiniões dos avaliadores sob confiança limitada; há mudança de opinião explicitamente modelada. [Fonte primária](https://www.sciencedirect.com/science/article/abs/pii/S0950705119303430). |
| V3-12 | incerto → excluir | O resumo e a motivação do PDF tratam de processamento genético. A exclusão proposta se refere ao domínio, preservando o valor matemático do resultado. [Fonte primária](https://u.cs.biu.ac.il/~tomi/Postscripts/majority.pdf). |
| V3-19 | incerto → excluir | O resumo institucional descreve funções de escolha e rankings sobre preferências fixadas. A tese integral não foi obtida e não se excluiu pela língua do título. [Fonte primária](https://www.unizg.hr/fileadmin/rektorat/Istrazivanja/Poslijediplomski/Doktorski_programi/knjige_dr._sc/54_Knjiga_doktora.pdf). |
| V3-20 | incerto → excluir | O resumo modela orientação e alinhamento de organismos, células e partículas, sem interpretação humana de opiniões descrita. [Fonte primária](https://www.sciencedirect.com/science/article/pii/S0895717705001743). |
| V3-21 | incerto → excluir | A página dos anais descreve identificação de pesos e referências para rankings. Não descreve mudança social; o tipo pôster não foi usado isoladamente para excluir. [Fonte primária](https://aisel.aisnet.org/isd2014/proceedings2024/datascience/35/). |
| V3-24 | incluir → incluir | O PDF editorial especifica cascata independente por etapas para propagação de rumores. O artigo curto tem três páginas nos anais. [Fonte primária](https://cdn.aaai.org/ocs/ws/ws0981/7046-30785-1-PB.pdf). |
| V3-25 | incerto → incluir | O PDF relaciona escolha inicial, informação social e nova escolha. A regressão modela conformidade nos casos inicialmente incongruentes; a inclusão é uma interpretação preliminar desse modelo de mudança. [Fonte primária](https://cebd.zufe.edu.cn/neuropsychologia-yuzhen.pdf). |
| V3-27 | incerto → incerto | A prévia editorial informa SVD e Credit Distribution, mas não expõe a regra. Falta distinguir dinâmica por influência de escore social estático. [Fonte primária](https://link.springer.com/chapter/10.1007/978-3-319-27122-4_19). |
| V3-28 | incerto → excluir | O registro institucional descreve agentes que transformam solicitações de TI em tarefas Jira. O domínio é automação administrativa. [Fonte primária](https://scholarspace.manoa.hawaii.edu/items/64327268-6027-4493-bfc4-12844e169d75). |
| V3-30 | incerto → excluir | O método formaliza agentes de software e os avalia em perguntas, respostas e raciocínio matemático. A v3 de 2024 é identificada sem substituir a observação de 2023. [Fonte primária](https://arxiv.org/html/2310.08535v3); [Histórico](https://arxiv.org/abs/2310.08535). |
| V3-32 | incerto → incluir | O texto formaliza crenças condicionadas ao histórico e a ações observadas. A inclusão preliminar considera essa análise normativa de crenças durante a interação. [Fonte primária](https://arxiv.org/pdf/2608.25731). |
| V3-35 | incluir → incluir | O agente incorpora a opinião de um especialista às suas observações; o artigo explicita interpretação humana. Não se exige iteração de uma população. [Fonte primária](https://arxiv.org/html/1403.4011). |
| V3-36 | incerto → excluir | O modelo estuda aprendizagem, coleta de recursos e ferramentas em animais hipotéticos e agentes artificiais. Menções humanas na motivação foram reconhecidas, sem equipará-las a estados de opinião. [Fonte primária](https://www.cai.sk/ojs/index.php/cai/article/download/469/376). |
| V3-39 | incerto → incerto | A IEEE não retornou conteúdo e o depósito Crossref não tem resumo. Metadados de publicação não permitem decidir o método ou o domínio. [Fonte primária](https://api.crossref.org/works/10.1109/FSKD.2007.519). |
| V3-45 | incluir → incluir | O resumo editorial explicita opiniões trocadas em rede sob dinâmica de votação. O capítulo integral não foi obtido; 2020 on-line e volume de 2021 ficam preservados. [Fonte primária](https://link.springer.com/chapter/10.1007/978-3-030-65347-7_32). |
| V3-48 | incerto → excluir | O manuscrito do autor estima intenção de voto separadamente por período. Sua fórmula mede preferências, sem regra entre estados ou incorporação social. Não se presume igualdade com a versão editorial. [Fonte primária](https://briankeithn.github.io/files/2020_IDA_TAS_Final.pdf). |

Os dois casos ainda incertos são V3-27, *A Novel APP Recommendation Method Based on SVD and Social Influence*, e V3-39, *Social Conventions to Promise Learning Convergence*. Nenhum foi excluído por indisponibilidade de acesso. Em V3-03, V3-06, V3-19 e V3-20, o suporte é texto retornado pela ferramenta de busca sobre a fonte primária, identificado como tal; não se declara retenção do HTML original ou do artigo integral.

## Uso na próxima etapa

A [nota de método](followup-method.md) aplica a definição registrada de mudança por tempo ou interação e distingue modelagem de dinâmica de mera mensuração. As fontes adicionais não estavam integralmente nas tarefas originais de título/resumo. Portanto, as novas propostas não são um gabarito intercambiável daquelas tarefas: uma execução futura precisa congelar fontes compatíveis com as decisões esperadas.

Esta consulta prepara a leitura dos casos; não altera a aquisição, o protocolo, os formulários humanos ou o scaffold. O corpus amplo continua dependente de resolução de identidades e metadados, seguida dos requisitos de calibração do processo atual. Não foram executadas triagem do corpus, extração ampla ou síntese.

## Materiais do artigo de extração

O [repositório EvoBot na revisão conferida](https://github.com/kfq20/EvoBot/tree/d09c402e04135eeb8794944e580f02846448f5f1) está público e contém scripts de treinamento, configuração, ambiente e caminhos de tensores para comunidades. O [README](https://github.com/kfq20/EvoBot/blob/d09c402e04135eeb8794944e580f02846448f5f1/README.md) orienta fornecer os dados brutos. A árvore consultada não contém arquivo com nome iniciado por LICENSE, LICENCE ou COPYING; a API do GitHub não identifica licença. A inspeção não carregou tensores nem executou treinamento ou reprodução das simulações.

Essa conferência externa complementa o campo de materiais de reprodução, sem reescrever o que foi extraído do PDF. Outro agente revisou a nota de método e essa inspeção do código, sem achados acionáveis; a revisão não é uma auditoria independente dos resultados do artigo.

## Verificação e rastreabilidade

Foram conferidos 72 hashes de arquivos retidos, 17 excertos textuais por intervalos Unicode e um excerto pela imagem da página do PDF autoral. As projeções textuais de cinco PDFs foram reproduzidas byte a byte com `pdftotext -layout -enc UTF-8`. A conferência substantiva examinou as 17 propostas separadamente da validação mecânica dos trechos.

O navegador mostrou 50 casos, seis campos de extração, os dois IDs incertos e os 17 casos com consulta adicional. A expansão do trecho e do vínculo à fonte editorial funcionou e não houve erro de console observado. O formulário e o download retornaram os bytes esperados por HTTP; caminhos privados testados responderam 404.

Os artefatos estão em `~/.local/state/research-workbench/calibration-followup-20260914/`, fora do Git. O protocolo, o JSON e HTML do primeiro rascunho, o scaffold e o formulário humano v3 mantiveram seus hashes. O sucessor declara esquema `ai-authored-calibration-assistance-followup-1` e linhagem ao rascunho anterior, sem se apresentar como entrada de calibração nativa.

| Arquivo local | SHA-256 |
| --- | --- |
| `reviewed-draft.json` | `7110fbb314a58479cb93f189b9a0fe5cb23204b536c4d55d653e9fc9cfd2d826` |
| `public/index.html` | `786e381ad491e6a5ce7de9c916c387d04e6a1a05ee9d3f615435d599a1325c13` |
| `validation.json` | `411558fb92277fccef13c7c033ed43bb92055ea88cc274875a5cb4de33c8d716` |
| `screening-review.json` | `a54e5377c0a0a612399b199b54973a2b519cda360021877f349e760601c7d63b` |
| `review-method-code.json` | `4c908941e44ec53f068513ba0c8c5a9b0a3507dfc813464fe869e99902ad70b7` |
| `delivery-check.json` | `ea0614f75dc6aac81a6e2d513da2cbc5b7fdb648a19c3cb9c5650eda2eed7241` |
