# Pré-registro secundário: confiabilidade de P$$P04 no SHP

27/09/2026. Preparado antes de receber ou acessar microdados SHP. Este documento
e o [JSON](shp-reliability-preregistration.json) são congelados por SHA-256 no
registro separado de congelamento. A análise é secundária e independente do
gate v4 de `a*(r)`, que já estava em execução. Alterações futuras exigem sucessor
datado, motivo e exposição de resultados; os bytes congelados não são editados.

## Pergunta, população e estimando

Estimar a proporção da variância observada de `P$$P04` atribuída ao estado
latente transmitido entre ondas anuais, entre pessoas entrevistadas no Swiss
Household Panel (SHP), 1999–2009. O item pergunta confiança no governo federal
em Berna, de 0 a 10. `P99P04` a `P09P04` são ligados por `idpers` nos arquivos
individuais anuais. Códigos negativos e respostas vazias são ausência; respostas
fora de 0–10 interrompem o processamento. A versão contratada, os questionários
e a redação/codificação de cada onda serão conferidos pelo Research Owner antes
da execução. Divergência de item ou de escala suspende a âncora.

Modelo de medida: `Y_it = μ_t + Z_it + ε_it`, com erro centrado, independente
entre ondas e independente do estado. A confiabilidade anual é
`r_t = Var(Z_t)/(Var(Z_t)+Var(ε_t))`. Em onze ondas, `Z_1` tem variância livre;
`Z_t = φ Z_{t-1}+η_t`, com `φ` e `Var(η)` constantes e variância de erro
`Var(ε)` igual nas ondas. Médias anuais são livres. Estimar por máxima
verossimilhança gaussiana FIML sobre todos os padrões observados, sob MAR,
incluindo respondentes com uma onda. O ponto de âncora é **r de 2004**, a onda
central fixa da janela, com IC de Wald de 95% obtido da informação observada.
Relatar também cada `r_t`, erro-padrão, φ, variância de erro, log-verossimilhança,
AIC, BIC, N válido por onda e N completo. A curva em onze ondas é o ajuste
primário desta análise; não se escolhe ano ou especificação por resultado.

Para cada trinca consecutiva 1999–2001 até 2007–2009, ajustar médias e matriz
de covariância irrestritas por FIML. Heise (1969): confiabilidade comum à
trinca `r = ρ12ρ23/ρ13` no modelo de estabilidade de primeira ordem.
Wiley–Wiley (1970): variância do erro comum `θ = V_2 − C12 C23/C13` e
`r_t = 1−θ/V_t`. A confiabilidade da onda central coincide algebricamente nos
dois modelos; a de borda no Wiley–Wiley pode diferir. Relatar estimativas,
erros-padrão modelares da onda central, N completo, AIC e BIC. Covariâncias
não positivas, `θ≤0`, `r` fora de (0,1), não convergência ou informação não
positiva são falhas declaradas, nunca truncadas para obter um número favorável.

## Amostragem, ausência e modo

O SHP iniciou amostra em 1999 e incorporou outra em 2004. O ajuste principal
usa todos os respondentes elegíveis identificados nos arquivos anuais, com
médias de onda livres. O pressuposto MAR condiciona a inferência aos valores
observados e ao modelo; não identifica atrito dependente de opiniões não
observadas. Relatar N por onda, N com alguma resposta, N completo e diferenças
entre FIML e ajuste apenas dos casos completos. Uma segunda sensibilidade
restringe a pessoas com resposta válida antes de 2004: é uma **proxy de entrada
observada**, não uma identificação da coorte SHP_I. A coorte verdadeira e pesos
longitudinais, se usados em um sucessor, exigem o arquivo mestre e método de
variância para amostra complexa; não serão inferidos de `idpers`. Não tratar os
erros-padrão modelares como inferência com desenho amostral complexo. Se o
atrito for MNAR, relatar o limite de identificação e não converter o IC modelar
em garantia.

O período 1999–2009 antecede os modos alternativos oferecidos a partir de 2010;
o protocolo de campo era telefônico. Conferir no guia e documentação da versão
baixada. Se uma onda do recorte tiver modo diferente ou mudança de redação,
suspender comparabilidade e emitir sucessor antes de usá-la; não excluir onda
depois de ver `r`. A não resposta do item não vira zero e nunca se faz imputação
pontual. FIML usa padrões incompletos sob MAR.

## Escala, sensibilidade e diagnósticos

Principal: tratar 0–10 como contínua, pela comparabilidade direta ao canal
contínuo de `a*(r)`. Sensibilidade ordinal: correlações policóricas bivariadas
com limiares estimados das marginais de cada par, aplicando a identidade de
Heise a cada trinca. É diagnóstico de dependência da escala e usa pares
completos; não substitui o FIML multi-onda nem é uma probabilidade de erro
ordinal identificada. Relatar estimativas inadmissíveis como tais.

Antes de interpretar a âncora, conferir convergência, matriz de informação,
limites dos parâmetros, φ, variâncias positivas, AIC/BIC, resíduos máximos
de correlação contra os casos completos, discrepância das nove trincas, efeitos
de casos completos e da proxy pré-2004, heaping em 5, extremos 0/10 e
contagens de ausência por onda. Não escolher modelo por menor AIC; o contraste
é diagnóstico. Se alguma trinca ou ajuste principal falhar, registrar a falha
e não publicar um ponto empírico único até revisão vinculada. A regra de
revisão pode ser motivada por diagnóstico, mas não alterar retroativamente
este pré-registro.

Intervalo baseado nos dados: IC modelar de Wald para r de 2004; relatar
separadamente o envelope mínimo–máximo das nove estimativas Heise como
sensibilidade de especificação, sem chamá-lo de IC. A diferença entre ambos
indica dependência de suposições. Não combinar ou arredondar para escolher uma
célula de grade. Somente resultados agregados (estimativas, erros-padrão,
estatísticas de ajuste e contagens) saem do diretório restrito. Nenhuma linha,
identificador, célula pequena de indivíduos ou microdado entra em prompt,
log, commit ou relatório.

## Relação com a curva v4 e ilustração

Apresentar `r̂_2004` como ponto destacado sobre a **grade v4 congelada**
`R={0,50;0,55;0,60;0,65;0,70;0,75;0,80;0,85;0,90}` e seu IC como intervalo
de incerteza empírica. Se o ponto ou intervalo cair fora da grade, mostrar
fora dela sem extrapolar `a*(r)`. Não muda grade, forças `G`, alvos 0,70 e
0,60/0,80, nulos, regras confirmatórias, bandas, censura ou ordem dos gates.
Não usar resultados de `a*(r)` para escolher `r`, especificação, recorte ou
diagnóstico. A âncora não valida o mecanismo social nem converte curva sintética
em estimativa causal humana.

Ilustração exploratória, em seção separada e rotulada: descrever distribuição
anual agregada de `P$$P04`, taxas agregadas de resposta, persistência entre
pares consecutivos e a posição da âncora frente à curva congelada. Sem ajuste
de efeito social, afirmação causal ou seleção de força. Suprimir qualquer
célula publicável menor que 10 e não exportar tabelas por pessoa.

## Fontes metodológicas verificadas em 27/09/2026

- [Heise (1969)](https://doi.org/10.2307/2092790), *American Sociological Review* 34:93–101: separa estabilidade verdadeira de erro em três ondas. Identidade usada acima; metadados e texto reproduzido consultados, sem presumir que pressupostos valem no SHP.
- [Wiley e Wiley (1970)](https://doi.org/10.2307/2093858), *American Sociological Review* 35:112–117: modelo de erro constante em painel; metadados e exposição metodológica conferidos, texto original não acessado integralmente.
- [Alwin (2007)](https://www.wiley-vch.de/en/areas-interest/mathematics-statistics/margins-of-error-978-0-470-08148-8), *Margins of Error*: editora confirma livro e capítulos sobre métodos longitudinais; conteúdo integral não lido.
- [Alwin, Baumgartner e Beattie (2018)](https://academic.oup.com/jssam/article-abstract/6/2/212/4201741), *JSSAM* 6:212–239: resumo editorial relata dependência da confiabilidade do número de categorias; não fornece estimativa para este item.
- [Hout e Hastings (2016)](https://www.sociologicalscience.com/download/vol-3/november/SocSci_v3_971to1002.pdf), *Sociological Science* 3:971–1002: artigo integral sobre confiabilidade de itens GSS em painéis de três ondas e seus limites.
- [Lucas e Donnellan (2012)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3475500/), *Social Indicators Research* 105:323–331: artigo integral usa STARTS uni e multivariado para satisfação com a vida, distinguindo traço, estado e erro; outro item, não âncora SHP.
- [Antoun e Cernat (2026)](https://doi.org/10.18148/srm/2026.v20i2.8525), *Survey Research Methods* 20:181–192: estimativas quase-simplex de 14 indicadores em sete países, inclusive Suíça; confiabilidade de autoavaliações varia entre itens e países. Metadados e resumo institucional consultados; não atribuí número a `P$$P04`.
- [Guia SHP 2026](https://forscenter.ch/wp-content/uploads/2026/03/shp_user_guide.pdf), §§ 2 e 6: ondas, amostras, modo, chave `idpers` e cautela sobre desenho complexo. [Contrato SWISSUbase](https://www.swissubase.ch/en/catalogue/studies/6097/latest/datasets/932/3605/contract/usage-license): acesso pessoal e proibição de repasse a terceiros.
