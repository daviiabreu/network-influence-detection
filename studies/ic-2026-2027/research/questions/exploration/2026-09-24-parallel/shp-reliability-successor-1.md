# Sucessor 1 do pré-registro secundário: confiabilidade de P$$P04 no SHP

28/09/2026, antes de receber ou acessar microdados SHP: o diretório restrito existe com modo 0700 e está vazio. Este é um sucessor datado e vinculado de [shp-reliability-preregistration.md](shp-reliability-preregistration.md) (SHA-256 `73e157217db02297ac011e61284252f9728f584a0a2e6c00a8903d8c0abb7800`), congelado por [shp-reliability-freeze.json](shp-reliability-freeze.json) (SHA-256 `0bb175914e9ce7e15398d28d5de9f5d02fff77d11e98b8d560b05d8e3359f10d`). Os bytes do pré-registro original não mudam. Não há exposição de resultado: nenhum dado SHP foi acessado, o gate v4 de `a*(r)` está em execução e nenhum tier confirmatório começou. O [JSON](shp-reliability-successor-1.json) traz a mesma especificação em forma legível por máquina.

## Motivo

O parecer adversarial interno de 28/09/2026 (`publications/jcss-manuscript/pipeline/review/referee-report-2026-09-28.md`, item R2-M4) aponta três limites na leitura da âncora contra a curva v4.

O primeiro é o traço. O ajuste principal é um quase-simplex sem traço estável. Se o processo tiver um traço, como o nulo B da v4 supõe, estimadores da família simplex atribuem mal o platô das defasagens longas. No exemplo do parecer, com correlações latentes `λ+(1−λ)φ^k`, `λ=φ=0,5` e confiabilidade 0,70, a identidade de Heise dá cerca de 0,63. As três sensibilidades congeladas (Heise, Wiley–Wiley e Heise policórico) pertencem à mesma família e não detectam esse viés.

O segundo é a escala. O `r` da simulação é a fração de sinal do canal contínuo antes da alocação por postos em 11 categorias equiprováveis. A âncora trata a escala 0–10 do SHP como contínua. As duas quantidades não estão na mesma escala, e o pré-registro original só afirma que são comparáveis de forma aproximada.

O terceiro é a onda de 2004, que é também a primeira entrevista da amostra de refrescamento. O `r` de 2004 mistura respondentes novos e antigos.

Este sucessor acrescenta uma sensibilidade de traço, uma ponte sintética entre os estimadores de âncora e o `r` da simulação, e uma descrição da onda de 2004. Nada do pré-registro original é removido ou substituído. A âncora principal continua sendo o `r` de 2004 do quase-simplex em onze ondas, com o mesmo intervalo, e todas as regras de falha, diagnóstico, privacidade e uso na curva continuam valendo.

## Adição 1: sensibilidade traço–estado–erro (STARTS)

Modelo de Kenny e Zautra (1995): `Y_it = μ_t + T_i + S_it + ε_it`. O traço estável `T_i` tem variância `σ²_T`. O estado segue `S_it = φ S_i,t−1 + η_it`, com `S` de 1999 de variância livre e `φ` e `Var(η)` constantes entre ondas consecutivas. O erro `ε_it` tem variância igual nas ondas. Traço, estado e erro são mutuamente independentes e independentes entre pessoas, e as médias anuais são livres. A confiabilidade anual é `r_t = (σ²_T + Var(S_t)) / (σ²_T + Var(S_t) + σ²_ε)`, a mesma razão entre variância latente e variância observada do ajuste principal.

A estimação é por máxima verossimilhança gaussiana FIML sobre todos os padrões observados, sob MAR, com a mesma amostra, o mesmo tratamento de ausência e a mesma escala contínua do ajuste principal. Variâncias entram em log e `φ` pela tangente hiperbólica, como no quase-simplex. Os valores iniciais ficam fixados em código antes de qualquer acesso aos dados.

Relatar `r` de 2004 com IC de Wald de 95% pela informação observada (método delta), cada `r_t`, `σ²_T`, `φ`, `Var(η)`, a variância inicial do estado, `σ²_ε`, a fração de traço na variância latente de 2004, `σ²_T / (σ²_T + Var(S_2004))`, log-verossimilhança, AIC, BIC e o resíduo máximo de correlação contra os casos completos.

São falhas declaradas, relatadas como tais e nunca truncadas: não convergência; informação observada não positiva definida; qualquer variância abaixo de 10⁻⁴ vezes a variância observada média; `|φ|` acima de 0,99; `r_t` fora de (0, 1). O STARTS tem identificação fraca em painéis curtos e produz soluções inadmissíveis com frequência (Lüdtke, Robitzsch e Wagner 2018). Nenhuma priori, restrição adicional ou valor inicial escolhido depois de ver os dados será usado para obter uma solução admissível. Se o ajuste falhar, a falha é o resultado.

A comparação entre o `r` de 2004 do quase-simplex e o do STARTS é diagnóstico da dependência da âncora em relação ao traço, e não seleção de modelo. Não escolher entre os dois por AIC, BIC ou proximidade da grade. Na figura da curva, o quase-simplex continua como ponto principal; o STARTS, se admissível, aparece como sensibilidade rotulada, e, se falhar, a falha é registrada na legenda.

## Adição 2: ponte sintética entre os estimadores de âncora e o r da simulação

Esta análise é exploratória e não entra em nenhuma regra confirmatória. Ela descreve que valor cada estimador de âncora produz quando os dados vêm do gerador sintético da v4 com `r` conhecido.

Os painéis sintéticos são gerados pelo código congelado da v4 (commit `37513841`), importado sem modificação. Usam a geometria SHP do estudo (N=10.626, entradas nas ondas 0 e 5, retenção 0,89, domicílios de duas pessoas), o canal contínuo `w = √r z + √(1−r) e` e a alocação ordinal em 11 categorias equiprováveis por onda. As categorias são codificadas de 0 a 10 e tratadas como contínuas, como no SHP, e as pessoas-onda não observadas ficam ausentes.

As células são o braço de interação em todas as combinações `(a, r)` da grade congelada da v4, `G × R`, e, como referência com traço, a família nula B com `φ = 0,85` e peso de traço `η ∈ {0,25; 0,50}` em cada `r` de `R`. Em `a = 0`, o braço de interação coincide com os nulos A, B, D e E no caminho.

Os estimadores são exatamente os do pré-registro original e da Adição 1, com o mesmo código: o `r` de 2004 (onda de índice 5) do quase-simplex em onze ondas, Heise e Wiley–Wiley em cada trinca, o Heise policórico e o STARTS.

São 10 painéis por célula e família. As sementes derivam da raiz declarada `20260928` num namespace próprio, `shp-crosswalk-v1`, distinto de todos os namespaces confirmatórios congelados. Nenhuma semente confirmatória é derivada ou consumida, e nenhum resultado de gate, tier, AUC ou `a*(r)` é lido.

As saídas, por célula, estimador e família, são média, desvio-padrão, mínimo e máximo entre réplicas, com as contagens de falha. O mapa `r ↦ r̂_2004` é descritivo. Na figura, ao lado do posicionamento bruto da âncora, pode aparecer, rotulado como "ponte sintética, exploratória", o conjunto de valores de `r` da grade cujos intervalos entre réplicas contêm a estimativa SHP, para `a = 0` e para as duas referências B. A ponte não substitui o posicionamento bruto, não escolhe `r` e não altera a curva.

A execução pode ocorrer em host de exploração, fora do Mac que executa o gate e os tiers. Análise exploratória não exige a equivalência numérica entre hosts que o critério confirmatório exige, e o host fica registrado na saída.

## Adição 3: a onda de 2004

Do ajuste principal, relatar `r_2003`, `r_2004` e `r_2005` lado a lado. Relatar também o `r` de 2004 de um quase-simplex ajustado entre respondentes cuja primeira resposta válida ocorre em 2004. Esse grupo é uma proxy da entrada pelo refrescamento, com ondas de 2004 a 2009, e sua estimativa de 2004 é de borda. As duas saídas são descritivas e não substituem a âncora.

## O que não muda

A âncora principal, o IC de Wald, as trincas, as sensibilidades policórica, de casos completos e da proxy anterior a 2004, os diagnósticos, as regras de falha, a proibição de escolher `r`, ano ou especificação por resultado, e a proibição de alterar grade, forças, alvos, nulos, bandas, censura ou gates da v4. A privacidade também não muda: só agregados saem do diretório restrito.

## Implementação e congelamento

O código das Adições 1 e 3 entra em `src/ic_study/analysis/shp_reliability.py`, e o da Adição 2 num módulo novo, com testes de recuperação sobre dados simulados de parâmetros conhecidos. Um registro separado, `shp-reliability-successor-1-freeze.json`, vinculará por SHA-256 este documento, o JSON e o commit de código, e registrará o estado do diretório restrito nesse momento. A análise do SHP só deve rodar depois desse registro.

## Fontes conferidas em 28/09/2026

- [Kenny e Zautra (1995)](https://doi.org/10.1037/0022-006X.63.1.52), _Journal of Consulting and Clinical Psychology_ 63(1):52–59: modelo traço–estado–erro para dados de múltiplas ondas. Metadados conferidos no Crossref; texto integral não lido.
- [Lüdtke, Robitzsch e Wagner (2018)](https://doi.org/10.1037/met0000155), _Psychological Methods_ 23(3):570–593: problemas de estimação do STARTS por máxima verossimilhança e alternativa bayesiana. Metadados conferidos no Crossref; texto integral não lido.
- Parecer interno `referee-report-2026-09-28.md`, itens R2-M1 e R2-M4.
