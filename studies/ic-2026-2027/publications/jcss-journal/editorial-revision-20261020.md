# Revisão editorial a partir dos comentários de Henrique

Em 20/10/2026, Davi autorizou a aplicação dos comentários enviados por Henrique
por e-mail e WhatsApp. Esta revisão sucede editorialmente a versão enviada em
17/10, baseada em `d599f7b5`. As alterações permanecem no checkout da versão da
revista, sem commit ou publicação externa. O protocolo congelado, o código
científico, as sementes, os resultados liberados e o registro pré-especificado
não foram alterados.

## Recomendações e alterações

| Item | Alteração implementada |
| --- | --- |
| Título e IA | Título adotado: “Limits of Detecting Network Influence in Attitude Panels”. A seção 3.7 segue a síntese proposta por Henrique, com os detalhes preservados em S4, S9 e S11. A aprovação do manuscrito final permanece pendente. |
| Resumo | Reorganizado em problema, método, resultado principal e implicações; 195 palavras. Mantidos os limiares e a sensibilidade do ajuste exploratório, com menos detalhes operacionais. |
| Introdução | A contribuição passa a ser a investigação dos limites da discriminação. A curva de limiares é apresentada como uma comparação condicional. |
| Interpretação | Resultados e discussão distinguem AUC, poder de um teste em um painel e atribuição causal. A tradução de AUC 0,70 para poder aproximado de 0,18 mantém as hipóteses de normalidade, variâncias iguais, nível unilateral de 5% e distribuição de referência conhecida. O parâmetro a é explicitamente nominal. |
| Confirmatórios e exploratórios | Comparações confirmatórias, inclusive as indisponíveis, precedem as análises exploratórias. A combinação de confiabilidade livre e ajuste de um lag adicional não é apresentada como efeito isolado da confiabilidade. Falhas de D são atribuídas ao procedimento e à caixa declarados; a comparação global permanece indisponível. |
| Discussão | Reorganizada em torno dos modelos alternativos restritos, do conhecimento privilegiado da confiabilidade e da ausência de burn-in. Efeitos demonstrados são separados de conjecturas não testadas. |
| Conclusão | Destaca a discriminação condicional demonstrada e as sensibilidades observadas, sem anunciar identificação empírica de influência. |
| Protocolo | Equações dos modelos de persistência e detalhes do classificador foram concentrados em S3. O artigo mantém a definição do experimento, do estimando, das regras de validade e da incerteza. As dificuldades de reprodução independente aparecem no texto principal e em S9. |
| Consistência com o suplemento | Títulos, referências e declarações foram conferidos entre artigo, suplemento e carta. A tabela de auditoria S52 passou a continuar na página seguinte, preservando integralmente suas seis linhas e seu número. |

## Verificação realizada

O build do artigo e do suplemento e o `check.py` passaram: 24 e 129 páginas,
respectivamente, 8.326 palavras no corpo e 5.323 vínculos de valores. Todas as
5.323 combinações distintas de chave e literal da versão-base continuam
presentes, sem acréscimo ou alteração. Os arquivos de `values/`, `generated/`
e `archive/` permanecem idênticos à base.

Os dois arquivos de testes de empacotamento JCSS passaram, com 25 testes. A
estrutura do repositório passou nas sete verificações, e `git diff --check`
não encontrou problemas. O pacote do portal compilou isoladamente, sem o
arquivo auxiliar do suplemento, e seu texto coincide com o build do artigo.
O ZIP preparado para importação no Overleaf também compilou após extração
nova e produziu o mesmo texto. Não houve validação dentro do serviço Overleaf.

Foram renderizadas as 24 páginas do artigo e inspecionadas em conjunto, com
conferência ampliada das páginas de título, IA/resultados, conclusão e
declarações. No suplemento foram conferidos o título, os detalhes transferidos,
a declaração de IA e a tabela de auditoria. Os logs finais não contêm referências
ou citações indefinidas, caixas excedentes ou tabelas maiores que a página.
Persistem avisos sobre constantes e referências fora do catálogo de resultados
e os marcadores de submissão descritos abaixo.

Uma revisão independente Codex verificou conteúdo, convenções e preservação
numérica; seus ajustes de consistência foram aplicados, e o parecer final foi
PASS, inclusive para a alteração restrita de layout. A tentativa de revisão
Claude não executou: a organização desativou o acesso por assinatura ao Claude
Code. Não foi usada uma API paga. Esses pareceres internos não constituem
revisão por pares, aceitação científica ou aprovação de submissão.

Não foram executadas simulações, novos experimentos ou a matriz completa de
qualidade dos dois projetos; a mudança é editorial, sem alteração de código.

## Pendências de submissão

A afirmação de ausência de financiamento foi substituída por um marcador para
a bolsa de IC, cujo concedente e programa ainda precisam ser informados. A
base institucional de ética também permanece pendente. A aprovação da versão
revisada pelos dois autores precisa ser confirmada após sua leitura; a carta
tem ainda um marcador de data. O modo `--submission` recusa corretamente os
três marcadores presentes no artigo. O pacote completo contém cinco marcadores
distintos, considerando também a carta. Nenhum arquivo foi publicado no Zenodo
ou submetido à revista nesta revisão.

## Segunda rodada de revisão aprofundada

Após o pedido de revisão aprofundada, dois novos revisores Codex e o agente
coordenador conferiram a interpretação científica e a consistência editorial.
Foram corrigidas a exceção do controle sem erro em r = 0,50 (limiar de 0,30
para 0,10), a distinção entre execução concluída e comparação inelegível, o
condicionamento da AUC e as hipóteses da tradução para poder. Também foram
delimitadas as afirmações sobre agrupamento marginal, a medida exploratória
de variância, efeitos nas margens de resposta e falhas de ajuste. O resumo
passou a atribuir a sensibilidade demonstrada às hipóteses de medição e ajuste.
S9 corrige explicitamente uma promessa excessiva de regeneração do README
histórico, preservando esse arquivo e os agregados originais.

O novo build passou com 24 páginas de artigo, 129 de suplemento, resumo de
195 palavras e corpo de 8.409 palavras. Permanecem as mesmas 5.323 combinações
de chave e literal, e os 79 arquivos rastreados em `values/`, `generated/` e
`archive/` foram comparados à base e estão byte a byte idênticos. Passaram
novamente os 25 testes de empacotamento e as sete verificações estruturais.
As pendências de submissão acima permanecem. Os PDFs e o pacote desta segunda
rodada sucedem os primeiros; os arquivos já entregues foram preservados.

## Atualização de 29–30/10/2026

As pendências acima foram fechadas no commit desta atualização e no anterior,
`ec66acfa`: financiamento pela bolsa institucional de IC do Inteli (confirmado
por Davi em 22/10), declaração factual de ética sem afirmar aprovação ou
dispensa (confirmada por Davi em 29/10) e atestação de aprovação pelos dois
autores. O gate de 29/10, com um revisor Codex e um Claude, pediu a frase de
ética que separa o processamento dos microdados dos resultados agregados, a
menção ao consentimento, o registro da rodada de 20/10 no S11 e dois ajustes
de redação; todos foram aplicados. A aprovação explícita de Henrique às
declarações novas continua a ser obtida antes da publicação no Zenodo.
