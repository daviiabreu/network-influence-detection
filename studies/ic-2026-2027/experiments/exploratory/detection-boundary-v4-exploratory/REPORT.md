# X1a e X2: relatório das análises exploratórias sucessoras da v4

Execução de 28/09/2026 das análises declaradas neste diretório ([README.md](README.md) e [declaration.json](declaration.json)), antes de qualquer resultado confirmatório da v4. As duas análises são exploratórias. Não mudam o protocolo congelado, e nenhum número daqui pode ser promovido a evidência confirmatória. O segundo estágio opcional, X1b, passou na verificação declarada e está em execução; a última seção registra o estado dele.

## Código, host e sementes

O código está em `src/ic_study/simulation/v4_exploratory.py`, com testes em `tests/unit/test_v4_exploratory.py`, e as execuções usaram o commit `2f1777bb`. O módulo importa os componentes congelados sem alterá-los. Cada unidade executada conferiu o SHA-256 dos sete arquivos congelados que importa contra `freeze-v4.json`, e todos coincidiram. Os testes fixam contra o código congelado tudo o que pode ser fixado. A reimplementação diagnóstica de `influence` reproduz a trajetória bit a bit em 32 combinações de fração, passos, repulsão e ancoragem. A composição do canal observado reproduz bit a bit a saída de `PanelSource` para o braço social, e o bootstrap reproduz as reamostragens de `score_uncertainty`. m(z) e v(z) conferem com a soma direta em N pequeno, inclusive com diferenças exatamente iguais a ±1, empates e casos em que o arredondamento põe um vizinho na borda da janela. Por Monte Carlo, m(z) e v(z)/8 coincidem com a média e a variância da deriva de rede num sorteio novo dos oito parceiros.

As execuções rodaram no host de exploração `homelab` (Linux x86_64, Intel Core i5-1335U, 12 threads lógicas), fora do Mac que executa o gate. O ambiente foi Python 3.12.13 e NumPy 2.5.3, sincronizado pelo mesmo `uv.lock`, com BLAS limitado a uma thread e 12 processos. X2 levou 3 minutos de relógio e 34 minutos de CPU. X1a levou 2 h 35 min de relógio e 24,8 horas de CPU, cerca de 25 minutos de relógio por célula. O agregado de X1a foi escrito depois, no mesmo host e no mesmo commit, pelo comando `aggregate`. Antes disso, um teste de fumaça no Mac, sob `nice`, com uma célula, 4 painéis de treino e 2 redes, só mediu o tempo; a saída dele não entra nos agregados.

As sementes derivam da raiz 20260928 no namespace `v4-exploratory-x1-x2`. Cada semente são os oito primeiros bytes do SHA-256 de `v4-exploratory-x1-x2|20260928|análise|bloco|fase|papel|índice`, o mesmo esquema dos planos congelados com outro campo inicial. Um teste registra os materiais que `SeedPlan` e `ConfirmatorySeedPlan` passam ao SHA-256 e mostra que nenhum coincide com os deste namespace. O namespace `shp-crosswalk-v1`, que usa a mesma raiz, existe só como declaração no branch `research/shp-anchor-successor-1`, sem código; a disjunção vale enquanto o material dele também começar pelo nome do namespace. Nenhuma semente confirmatória foi consumida e nenhum resultado de gate, tier ou `a*(r)` foi lido.

Os agregados estão em [`results/x1a.json`](results/x1a.json) e [`results/x2.json`](results/x2.json). Cada um registra o commit, o host, os hashes da declaração, os tempos e as sementes. Em X2 estão as 20 sementes explícitas; em X1a, a semente do bootstrap e o SHA-256 da lista ordenada das 48.000 sementes de painel de cada confiabilidade.

## Leituras escolhidas onde a declaração não fixava o detalhe

Onde a declaração deixou um detalhe aberto, ficou a leitura mais próxima do código congelado.

No X1a, o braço de interação segue o layout social de `PanelSource` nas fases de treino e referência. Usa os índices ímpares, compartilha cada rede entre dois painéis consecutivos (`índice // 4`) e passa pela mesma máscara, erro, alocação ordinal e features. O gêmeo ocupa os índices pares, que o braço nulo usa no código congelado, e tem um fluxo próprio de ξ por painel. Os dois braços usam fluxos independentes, como treino, checagem e referência no pipeline congelado.

O plano congelado usa as mesmas sementes para as nove forças de uma confiabilidade, e X1a faz o mesmo: as sementes dependem da confiabilidade, da fase, do papel e do índice, mas não de a. Em X2, as sementes dependem só da réplica e se repetem nas 36 condições.

O bootstrap sorteia com reposição, a cada reamostragem, as 2.000 linhas de rede de cada braço, independentemente entre os braços e mantendo os dois eventos de cada linha, como `score_uncertainty`. A semente é a mesma para as oito forças de uma confiabilidade, como a semente única da curva congelada. O intervalo usa os percentis 2,5 e 97,5 com a interpolação linear do NumPy. As médias de L1 a L5 usam os 4.000 painéis de referência de cada braço.

Em X2, t indexa passos, não ondas. Com 24 passos por onda entram as 240 transições de cada réplica, 2.550.240 observações, contra 106.260 com um passo. z_{t+1} é o estado depois do transporte por postos. Os nós são quantis de z_t agrupado na réplica, com a interpolação linear do NumPy; como o estado é sempre uma permutação da mesma grade, eles coincidem entre réplicas. O desvio-padrão entre réplicas usa ddof = 1.

A janela de m e v usa o mesmo predicado de ponto flutuante de `bounded_drift`, `|z_j − z_i| ≤ 1` sobre a diferença calculada. v é truncado em zero só contra arredondamento.

## X1a: braço de interação contra o gêmeo de campo médio

Cada célula treinou a LDA congelada com 2.000 painéis por braço e mediu a AUC em 2.000 redes de referência por braço, com dois eventos por rede. A tabela dá a AUC do braço de interação contra o gêmeo e, entre parênteses, o intervalo percentil de 95% do bootstrap com 1.000 reamostragens das redes de referência. O asterisco marca os intervalos que excluem 0,5. Os valores estão arredondados na terceira casa, de modo que 1,000 indica AUC de pelo menos 0,9995.

| a \ r | 0,5 | 0,55 | 0,6 | 0,65 | 0,7 | 0,75 | 0,8 | 0,85 | 0,9 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,001 | 0,492 (0,480–0,503) | 0,508 (0,494–0,521) | 0,494 (0,481–0,506) | 0,509 (0,497–0,521) | 0,501 (0,488–0,513) | 0,494 (0,482–0,506) | 0,505 (0,493–0,518) | 0,496 (0,484–0,509) | 0,509 (0,497–0,522) |
| 0,003 | 0,496 (0,484–0,508) | 0,510 (0,497–0,524) | 0,496 (0,483–0,508) | 0,510 (0,498–0,523) | 0,504 (0,490–0,516) | 0,498 (0,485–0,510) | 0,508 (0,495–0,521) | 0,500 (0,487–0,512) | 0,511 (0,499–0,523) |
| 0,01 | 0,506 (0,494–0,519) | 0,520 (0,507–0,533)* | 0,505 (0,492–0,517) | 0,517 (0,504–0,530)* | 0,515 (0,501–0,527)* | 0,510 (0,498–0,522) | 0,523 (0,511–0,535)* | 0,513 (0,501–0,526)* | 0,523 (0,512–0,536)* |
| 0,03 | 0,534 (0,523–0,546)* | 0,546 (0,534–0,560)* | 0,534 (0,521–0,547)* | 0,548 (0,535–0,561)* | 0,549 (0,535–0,560)* | 0,547 (0,534–0,559)* | 0,560 (0,548–0,571)* | 0,553 (0,541–0,565)* | 0,565 (0,553–0,577)* |
| 0,1 | 0,623 (0,610–0,635)* | 0,641 (0,629–0,654)* | 0,634 (0,622–0,646)* | 0,659 (0,647–0,671)* | 0,668 (0,656–0,680)* | 0,672 (0,661–0,683)* | 0,693 (0,681–0,704)* | 0,693 (0,683–0,704)* | 0,716 (0,706–0,726)* |
| 0,3 | 0,840 (0,831–0,849)* | 0,866 (0,858–0,874)* | 0,874 (0,866–0,881)* | 0,905 (0,899–0,912)* | 0,921 (0,916–0,927)* | 0,934 (0,929–0,939)* | 0,953 (0,949–0,957)* | 0,961 (0,957–0,964)* | 0,974 (0,971–0,977)* |
| 0,6 | 0,986 (0,984–0,988)* | 0,992 (0,990–0,993)* | 0,996 (0,995–0,997)* | 0,998 (0,998–0,999)* | 0,999 (0,999–1,000)* | 1,000 (0,999–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* |
| 0,9 | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* | 1,000 (1,000–1,000)* |

Com a = 0,001 e a = 0,003, as AUC ficam entre 0,492 e 0,511 e todos os intervalos contêm 0,5. Com a = 0,01, seis das nove células excluem 0,5, com AUC entre 0,513 e 0,523. A partir de a = 0,03 todas excluem 0,5: a AUC vai de 0,534 a 0,565 em a = 0,03, de 0,623 a 0,716 em a = 0,1 e de 0,840 a 0,974 em a = 0,3, e fica em 0,986 ou mais com a ≥ 0,6. Dentro de cada a, a AUC tende a crescer com r. Nenhum intervalo fica inteiro abaixo de 0,5.

As médias das defasagens L1 a L5 nos 4.000 painéis de referência de cada braço mostram onde está a diferença. Com a ≤ 0,01, braço e gêmeo diferem em menos de 0,0007 em qualquer defasagem. A partir de a = 0,03, a diferença (braço menos gêmeo) é positiva nas cinco defasagens em 44 das 45 células e cresce com a defasagem em 43; as exceções são duas células de a = 0,03, com r = 0,5 (L1 levemente negativo) e r = 0,6. Em r = 0,70, a diferença vai de 0,0002 em L1 a 0,0011 em L5 com a = 0,03, de 0,0005 a 0,0041 com a = 0,1 e de 0,014 a 0,046 com a = 0,9. O braço de interação guarda, portanto, mais autocorrelação nas defasagens longas do que o gêmeo, que tem a mesma média e a mesma variância condicionais da deriva.

## X2: mapa de R² da deriva

Cada réplica conferiu a trajetória diagnóstica contra `influence` congelada, e as 360 coincidiram bit a bit. A tabela dá média, desvio-padrão, mínimo e máximo das 10 réplicas. X2a é o R² parcial de D̃_t e X2b é o R² incremental além da spline, como declarado.

| Passos | b | a | X2a média | X2a DP | X2a mín–máx | X2b média | X2b DP | X2b mín–máx |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0,25 | 0 | 0,00000 | 0,00000 | 0,00000–0,00001 | 0,00000 | 0,00000 | 0,00000–0,00000 |
| 1 | 0,25 | 0,001 | 0,00054 | 0,00010 | 0,00039–0,00072 | 0,00014 | 0,00002 | 0,00011–0,00018 |
| 1 | 0,25 | 0,003 | 0,00167 | 0,00018 | 0,00140–0,00199 | 0,00044 | 0,00004 | 0,00037–0,00050 |
| 1 | 0,25 | 0,01 | 0,00552 | 0,00038 | 0,00517–0,00638 | 0,00140 | 0,00009 | 0,00130–0,00158 |
| 1 | 0,25 | 0,03 | 0,01645 | 0,00076 | 0,01561–0,01780 | 0,00397 | 0,00017 | 0,00377–0,00425 |
| 1 | 0,25 | 0,1 | 0,05398 | 0,00139 | 0,05175–0,05585 | 0,01183 | 0,00029 | 0,01138–0,01226 |
| 1 | 0,25 | 0,3 | 0,16704 | 0,00195 | 0,16414–0,16980 | 0,03035 | 0,00036 | 0,02988–0,03100 |
| 1 | 0,25 | 0,6 | 0,36842 | 0,00155 | 0,36607–0,37086 | 0,05062 | 0,00023 | 0,05031–0,05092 |
| 1 | 0,25 | 0,9 | 0,66069 | 0,00203 | 0,65849–0,66487 | 0,05887 | 0,00051 | 0,05792–0,05958 |
| 1 | 0,00 | 0 | 0,00001 | 0,00001 | 0,00000–0,00002 | 0,00000 | 0,00000 | 0,00000–0,00000 |
| 1 | 0,00 | 0,001 | 0,00068 | 0,00015 | 0,00046–0,00098 | 0,00019 | 0,00004 | 0,00012–0,00025 |
| 1 | 0,00 | 0,003 | 0,00209 | 0,00027 | 0,00175–0,00267 | 0,00057 | 0,00007 | 0,00047–0,00071 |
| 1 | 0,00 | 0,01 | 0,00709 | 0,00054 | 0,00643–0,00827 | 0,00196 | 0,00015 | 0,00176–0,00225 |
| 1 | 0,00 | 0,03 | 0,02157 | 0,00088 | 0,02036–0,02356 | 0,00611 | 0,00025 | 0,00574–0,00661 |
| 1 | 0,00 | 0,1 | 0,07475 | 0,00212 | 0,07161–0,07841 | 0,02218 | 0,00066 | 0,02116–0,02321 |
| 1 | 0,00 | 0,3 | 0,24170 | 0,00243 | 0,23782–0,24603 | 0,07714 | 0,00084 | 0,07597–0,07862 |
| 1 | 0,00 | 0,6 | 0,52876 | 0,00210 | 0,52534–0,53091 | 0,17955 | 0,00122 | 0,17757–0,18108 |
| 1 | 0,00 | 0,9 | 0,86468 | 0,00071 | 0,86293–0,86548 | 0,30548 | 0,00071 | 0,30432–0,30643 |
| 24 | 0,25 | 0 | 0,00000 | 0,00000 | 0,00000–0,00000 | 0,00000 | 0,00000 | 0,00000–0,00000 |
| 24 | 0,25 | 0,001 | 0,00056 | 0,00003 | 0,00051–0,00061 | 0,00015 | 0,00001 | 0,00013–0,00016 |
| 24 | 0,25 | 0,003 | 0,00167 | 0,00006 | 0,00157–0,00175 | 0,00043 | 0,00002 | 0,00040–0,00045 |
| 24 | 0,25 | 0,01 | 0,00552 | 0,00009 | 0,00537–0,00564 | 0,00139 | 0,00002 | 0,00134–0,00142 |
| 24 | 0,25 | 0,03 | 0,01628 | 0,00014 | 0,01599–0,01644 | 0,00391 | 0,00004 | 0,00383–0,00395 |
| 24 | 0,25 | 0,1 | 0,05299 | 0,00029 | 0,05244–0,05349 | 0,01156 | 0,00007 | 0,01142–0,01167 |
| 24 | 0,25 | 0,3 | 0,15626 | 0,00037 | 0,15546–0,15684 | 0,02789 | 0,00008 | 0,02771–0,02798 |
| 24 | 0,25 | 0,6 | 0,32612 | 0,00073 | 0,32529–0,32771 | 0,04270 | 0,00010 | 0,04255–0,04288 |
| 24 | 0,25 | 0,9 | 0,54435 | 0,00162 | 0,54159–0,54724 | 0,04148 | 0,00020 | 0,04123–0,04181 |
| 24 | 0,00 | 0 | 0,00000 | 0,00000 | 0,00000–0,00000 | 0,00000 | 0,00000 | 0,00000–0,00000 |
| 24 | 0,00 | 0,001 | 0,00071 | 0,00004 | 0,00063–0,00075 | 0,00019 | 0,00001 | 0,00017–0,00020 |
| 24 | 0,00 | 0,003 | 0,00215 | 0,00007 | 0,00202–0,00224 | 0,00058 | 0,00002 | 0,00054–0,00061 |
| 24 | 0,00 | 0,01 | 0,00719 | 0,00011 | 0,00697–0,00728 | 0,00198 | 0,00003 | 0,00191–0,00200 |
| 24 | 0,00 | 0,03 | 0,02186 | 0,00019 | 0,02141–0,02209 | 0,00618 | 0,00006 | 0,00604–0,00626 |
| 24 | 0,00 | 0,1 | 0,07534 | 0,00029 | 0,07502–0,07581 | 0,02241 | 0,00009 | 0,02228–0,02256 |
| 24 | 0,00 | 0,3 | 0,24207 | 0,00043 | 0,24145–0,24296 | 0,07754 | 0,00016 | 0,07730–0,07781 |
| 24 | 0,00 | 0,6 | 0,52869 | 0,00038 | 0,52796–0,52913 | 0,18002 | 0,00020 | 0,17968–0,18032 |
| 24 | 0,00 | 0,9 | 0,86491 | 0,00021 | 0,86458–0,86520 | 0,30573 | 0,00011 | 0,30550–0,30584 |

Com a = 0, a deriva não entra na trajetória e as duas medidas ficam no nível do acaso, abaixo de 2 × 10⁻⁵. X2a cresce quase em proporção a a. Com b = 0,25 e um passo por onda, vai de 0,00054 em a = 0,001 a 0,661 em a = 0,9; sem repulsão, de 0,00068 a 0,865. Com 24 passos os valores quase não mudam, exceto com b = 0,25 e a ≥ 0,3, em que X2a cai (0,544 contra 0,661 em a = 0,9). O maior desvio-padrão entre réplicas é 0,0024 em X2a e 0,0012 em X2b, bem abaixo das diferenças entre condições.

X2b é muito menor que X2a, mas as duas medidas declaradas têm denominadores diferentes. X2a divide o ganho de ajuste pela variância residual depois de [1, z_t]. X2b divide o ganho além da spline pela variância total de z_{t+1}, que a persistência domina: o R² de [1, z_t] vai de 0,62 a 0,94. Os R² de cada ajuste estão no JSON e permitem pôr as duas medidas na mesma escala. A spline acrescenta no máximo 0,025 ao R² da reta. O ganho da deriva além da spline, medido sobre a variância residual, fica entre 0,95 e 1,23 vez o X2a da mesma condição. A parte da deriva padronizada que a função não linear do próprio estado não explica é, portanto, quase toda a parte que a reta não explica. Na escala declarada, ela acrescenta até 0,059 da variância de z_{t+1} com b = 0,25 (a = 0,9, um passo) e até 0,306 com b = 0.

## Leitura declarada, aplicada literalmente

A declaração lê cada célula isoladamente. Um intervalo que exclui 0,5 indica que a rede acrescenta informação separável para a LDA fixa naquela célula; um intervalo que contém 0,5 não prova ausência de efeito da rede; não há correção para multiplicidade nem afirmação sobre a curva inteira. Aplicada assim, a leitura dá informação separável da rede em 51 das 72 células, todas com a ≥ 0,01, e nenhuma conclusão nas outras 21: as 18 células de a = 0,001 e a = 0,003 e três de a = 0,01 (r = 0,5; 0,6 e 0,75).

X2 não tem regra de leitura declarada além do relato de média, desvio-padrão, mínimo e máximo, feito acima.

## Limitações

O intervalo de X1a é condicional à LDA treinada: a variabilidade do treino com 2.000 painéis por braço não entra nele, como no erro-padrão condicional do código congelado. O bootstrap reamostra só as redes de referência.

O gêmeo reproduz m(z) e v(z)/8, a média e a variância condicionais da deriva de rede num sorteio novo de parceiros, mas não a forma da distribuição. A deriva de rede é a média de oito valores do kernel, e o ruído do gêmeo é gaussiano. O contraste junta, portanto, os dois efeitos que a declaração nomeia, a autocorrelação temporal do desvio da deriva e as covariâncias entre pessoas ligadas, e uma terceira diferença, de forma, que X1a não separa. As diferenças de L1 a L5 entre os braços são positivas e crescem com a defasagem, o que combina melhor com um componente persistente do que com uma diferença de forma a cada passo. Isso é uma leitura, não uma decomposição.

As células de uma mesma confiabilidade compartilham sementes, como no plano congelado. Não são réplicas independentes, o que só importaria para uma leitura entre células, que a declaração exclui.

X2 mede a deriva padronizada na escala do passo, em trajetórias latentes sem canal nem máscara. Os R² não se traduzem diretamente em AUC nem na escala observada.

Tudo rodou num único host de exploração. A declaração não exige equivalência numérica entre hosts, e ela não foi testada.

## X1b

Estado em 28/09/2026: o pipeline sucessor passou na verificação declarada, com as quatro células idênticas ao pipeline congelado byte a byte, e X1b rodou no host de exploração das 17h15 às 23h23 UTC, com o resultado na seção "Resultado" abaixo. O resultado, `a*_MF(r)` com a banda, o portão nulo, a censura e a inversão congelados, entra como sucessor deste relatório. Em nenhum caso a comparação com a*(r) é feita antes da liberação da curva confirmatória.

### Pipeline sucessor

O código está em `src/ic_study/simulation/v4_exploratory_x1b.py`, com testes em `tests/unit/test_v4_exploratory_x1b.py`, no commit `8f6f4cdb`. O sucessor roda as nove unidades do tier 1 tiradas do inventário congelado (família B, canal observado, as nove forças de G em cada r) e troca só o gerador social. `SwappedSource` herda do `PanelSource` congelado. Os painéis nulos saem do `_profiles` congelado, e os sociais mantêm o mesmo layout de índices, as mesmas sementes e o mesmo canal observado e chamam o gerador injetado: a chamada congelada de `influence`, que é o gerador original, ou o gêmeo de campo médio de X1a, com um fluxo de ξ próprio por painel. Ajuste, validação, retentativa D4, discriminante, nuisance e registro vêm de `pipeline` e `pipeline_record` congelados; banda, portão nulo, censura e inversão vêm de `complete_curve` congelado, sem cópia. Dois trechos foram reescritos porque o código congelado não tem ponto de injeção: o ramo social de `_profiles`, que chama `influence` diretamente, e o executor da célula, porque `execute_cell` congelado constrói `PanelSource` diretamente. O executor repete o congelado com a fonte trocada e grava o mesmo layout de `SealedStore`, e é esse layout que a verificação compara.

As sementes vêm de `ExploratorySeedPlan`, que tem a interface de `SeedPlan` e deriva cada fluxo do namespace `v4-exploratory-x1-x2`, raiz 20260928, análise `x1b`, com o layout de blocos congelado (2 × índice de r + tentativa). As nove forças de um r compartilham os fluxos, como na curva congelada, e a semente do bootstrap da curva sai do mesmo plano. `ExploratoryUnit` aponta `execute_cell` e `complete_curve` congelados para esse plano sem editá-los, trocando só a propriedade `seeds`. A fonte trocada recusa `SeedPlan` e `ConfirmatorySeedPlan`, e um teste registra todo material passado ao SHA-256 numa célula completa em N = 60 e mostra que nenhum começa por `ic-detection-boundary-v4`. O teste de disjunção de sementes cobre também os 18 blocos de X1b, e um teste novo confere, onde o módulo `shp_crosswalk` existe (commit `c4d683da`), que as sementes dele ficam em [2^64, 2^65), fora do intervalo de todas as sementes exploratórias. O comando `x1b` só começa com um registro de verificação aprovado do mesmo módulo sucessor no mesmo commit, e cada execução confere o SHA-256 dos 80 arquivos Python de `freeze-v4.json`. `pyproject.toml` e `uv.lock` diferem dos congelados por dependências acrescentadas depois do congelamento (matplotlib, pyreadstat e scipy); o NumPy continua 2.5.3.

Os testes fixam o sucessor ao executor congelado bit a bit numa configuração pequena, N = 60 com a = 0,03 e r = 0,5, que passa por todas as etapas até os escores. Também mostram que a fonte trocada reproduz `PanelSource` em todas as fases e tentativas e que, com a = 0, a célula do gêmeo é a célula congelada, porque sem deriva o gêmeo segue a mesma trajetória AR. Uma sondagem com o pipeline congelado em N = 60 e N = 120 escolheu essa configuração e não entra em nenhum resultado.

### Verificação bit a bit

As células ficaram fixadas no código antes de qualquer execução em tamanho declarado: (a, r) = (0; 0,9), (0,003; 0,7), (0,03; 0,5) e (0,3; 0,6). A primeira passa pelo ramo sem rede e com âncora exata, as duas seguintes são células do G2 com deriva de rede, a última tem a alto, e os quatro r usam blocos de semente distintos. Em cada célula, dois processos separados rodaram no mesmo commit, com o gerador original, as mesmas sementes exploratórias, N = 10.626 e os tamanhos congelados: um com `v4_curve.execute_cell` congelado e outro com o executor sucessor. A comparação cobre todos os arquivos do store de cada célula, byte a byte: os checkpoints de perfis de cada lote de 32 painéis de todas as fases, nomeados pelo SHA-256 do material de semente, `phases.jsonl`, `provenance.json`, `result.json`, `scores0.npy`, `scores1.npy`, `nuisance.npy`, `eta-shifts.npy`, `worker-output.log` e `seal.json`. Só `access.jsonl` fica fora, porque guarda horários e pids; a sequência de ações e chaves dele também precisa coincidir, assim como a proveniência da unidade.

| a | r | Ajuste | Arquivos | Checkpoints | SHA-256 de `seal.json` | SHA-256 de `result.json` | Idênticos |
|---:|---:|---|---:|---:|---|---|---|
| 0 | 0,9 | anchor-exact | 577 | 568 | `da6f26a2…` | `c21917a9…` | sim |
| 0,003 | 0,7 | interior | 1.211 | 1.202 | `99b5e686…` | `370cdea1…` | sim |
| 0,03 | 0,5 | interior | 1.371 | 1.362 | `4d34324c…` | `a90cfeed…` | sim |
| 0,3 | 0,6 | interior | 1.595 | 1.586 | `4687195c…` | `d167d10a…` | sim |

As quatro células foram idênticas em todos os arquivos e na sequência de acesso, e as quatro chegaram a um resultado com uma única tentativa de ajuste aceita. As três células com rede passaram por ajuste, validação, estêncil, treino, checagem, referência, jacobiano e nuisance, e a primeira passou pelo ramo de âncora exata, que não tem referência nem nuisance. A regra exigia pelo menos duas células. O registro completo, com os SHA-256 de todos os arquivos, o commit `8f6f4cdb` com árvore limpa, o host e os tempos, está em [`results/x1b-precondition.json`](results/x1b-precondition.json) (SHA-256 `1664d801…`). O módulo sucessor verificado tem SHA-256 `6053dba0…`, e os 80 arquivos Python congelados coincidiram com `freeze-v4.json`. Os logs de saída padrão dos oito processos foram gravados num único arquivo por um erro de aspas no lançador, corrigido antes de X1b; os stores e os registros de cada lado não passam por esses logs.

### Custo e projeção

Na verificação, com oito processos no host e, nos primeiros minutos, mais os quatro da sondagem descrita a seguir, uma célula levou de 12 minutos (a = 0, 18.144 painéis) a 37 minutos (a = 0,3, 50.720 painéis), e os dois lados de cada célula diferiram em até 3% do tempo. Numa célula sem retentativa, 13.072 painéis são sociais (9.072 com a = 0) e passam a ser do gêmeo em X1b, que roda com 12 processos. Uma sondagem só de tempo, com sementes fora de qualquer namespace e saída descartada, mediu com 12 processos ativos 0,066 s de CPU por painel nulo B, 0,083 s por painel social congelado e 0,112 s por painel do gêmeo (0,110 s com a = 0). Com essas taxas e as contagens de painéis da verificação, uma célula de X1b leva de 27 minutos (a = 0) a cerca de 66 minutos sem retentativa D4, e cerca de 3,3 vezes isso com retentativa, a razão entre os cenários com e sem retentativa do tier 1 em `../detection-boundary-v4/compute-projection-verified.json`. As 81 células vão para 12 shards pelo índice módulo 12, com sete células nos shards mais cheios. A projeção é de 7 a 8 horas sem retentativas, com fim por volta da 01h UTC de 29/09/2026, e de no máximo cerca de 26 horas se todas as células precisarem da retentativa, até cerca das 19h UTC de 29/09/2026. As duas ficam muito antes do limite de 15/10/2026. A agregação, com `complete_curve` congelado nas nove unidades, leva minutos.

### Lançamento

X1b começou às 17h15 UTC de 28/09/2026 no host `homelab` (Linux x86_64, Intel Core i5-1335U, 12 threads lógicas, Python 3.12.13, NumPy 2.5.3, BLAS em uma thread), no commit `8f6f4cdb`, com 12 processos destacados, um por shard, gravando em `~/v4x-runs/8f6f4cdb` no host. O lançador `~/launch-v4x1b.sh` faz checkout do commit publicado exato, sincroniza pelo `uv.lock`, confere que a árvore está limpa e inicia um supervisor que segura um lock do diretório, espera os shards e roda `aggregate`, que grava `x1b.json`. A execução é retomável: cada célula grava checkpoints de perfis e só conta como feita com o marcador de resultado, e um shard reiniciado pula as células já registradas. Uma exceção ValueError do pipeline congelado numa célula fica registrada e impede só a curva daquele r, que a agregação relata como erro de célula; lacunas de ajuste seguem a censura congelada. Como o gêmeo sem deriva segue a trajetória congelada, a célula (0; 0,9) de X1b deve repetir a da verificação em todos os arquivos, exceto a proveniência e o selo, o que pode ser conferido quando ela terminar.

### Resultado

Resumo corrigido em 29/09/2026 em resposta ao maior 1 da revisão C. Fonte: `results/x1b.json`, campos `summary` e `curves`; nenhuma análise foi executada novamente.

As 81 células terminaram sem erro, em 12 shards, com 6 h 8 min de relógio e 62,6 horas de CPU. O agregado está em [`results/x1b.json`](results/x1b.json) (SHA-256 `f4f156c5…`), escrito pelo comando `aggregate` no commit `8f6f4cdb`. As nove unidades executaram as nove forças e passaram no portão nulo, com AUC em a = 0 entre 0,497 e 0,513: todas receberam o estado operacional "completo válido". Esse estado não exige banda sem lacunas. Quatro células ficaram como lacuna, uma por perfil não monótono e três por ajuste mal condicionado; as respectivas bandas têm `band_complete: false`, e a regra congelada censura fronteiras que dependem de atravessar essas lacunas.

| r | Estado / banda sem lacunas | Lacuna (a) | Primeira fronteira pontual [intervalo invertido] | Fronteira sustentada pontual [intervalo invertido] | AUC máxima disponível (a) |
| ---: | --- | --- | --- | --- | --- |
| 0,50 | completo válido / não | 0,60 | censurada na lacuna [censurado; censurado] | censurada na lacuna [censurado; censurado] | 0,572 (0,30) |
| 0,55 | completo válido / não | 0,90 | censurada na lacuna [censurado; censurado] | censurada na lacuna [censurado; censurado] | 0,554 (0,60) |
| 0,60 | completo válido / sim | — | não atingida [>0,90; >0,90] | não atingida [>0,90; >0,90] | 0,586 (0,30) |
| 0,65 | completo válido / sim | — | não atingida [>0,90; >0,90] | não atingida [>0,90; >0,90] | 0,589 (0,30) |
| 0,70 | completo válido / sim | — | não atingida [>0,90; >0,90] | não atingida [>0,90; >0,90] | 0,626 (0,60) |
| 0,75 | completo válido / não | 0,90 | censurada na lacuna [0,30; censurado] | censurada na lacuna [censurado; censurado] | 0,674 (0,60) |
| 0,80 | completo válido / não | 0,90 | censurada na lacuna [0,60; censurado] | censurada na lacuna [censurado; censurado] | 0,667 (0,60) |
| 0,85 | completo válido / sim | — | não atingida [0,30; >0,90] | não atingida [0,30; >0,90] | 0,681 (0,60) |
| 0,90 | completo válido / sim | — | 0,30 [0,30; >0,90] | 0,30 [0,30; >0,90] | 0,717 (0,60) |

Na inversão inclusiva, a primeira banda superior que alcança 0,70 dá o limite inferior, e a primeira banda inferior que alcança 0,70 dá o superior. `>0,90` designa um extremo não atingido na grade, não um extremo numérico estimado; "censurado" preserva os campos `*_censoring` do JSON. Nos quatro r com lacuna, nem a fronteira primeira nem a sustentada pode ser descrita como não atingimento em uma grade completa. Nos r = 0,60, 0,65, 0,70 e 0,85, as grades sem lacunas não atingem 0,70 pontualmente. Só r = 0,90 tem travessia pontual, em a = 0,30 (AUC 0,7059390625); todas as estimativas seguintes continuam acima de 0,70. Seus dois intervalos invertidos são `[0.3, null]`, sem extremo superior atingido. Nenhuma banda inferior nesse r supera 0,70, inclusive nas forças seguintes, de modo que não há a alegação estrita de travessia unilateral de M74. A comparação com a*(r) fica para depois da liberação confirmatória, lado a lado e rotulada como exploratória.

## X3 a X7: base comum, pré-condições e lançamento de X5 e X7

Estado em 29/09/2026, 07h10 UTC. Esta seção registra o código sucessor das análises declaradas em [README-x3-x7.md](README-x3-x7.md) e [declaration-x3-x7.json](declaration-x3-x7.json), registradas em `85cdb8f2`, as pré-condições bit a bit de X5 e X7 e o lançamento das duas no homelab. X3, X4 e X6 são implementados em paralelo sobre a mesma base e ficam para os PCs do laboratório. X5 só pode ser lido quando estiver completo, e X3, X4, X6 e X7, só depois da liberação. Por isso nada aqui traz AUC, escore, poder, cobertura, verdade ou fronteira. Entram só código, estados de ajuste, contagens, tempos, sementes e as pré-condições.

### Código

O código está no branch `research/v4-exploratory-x3-x7-impl`. A base comum, `src/ic_study/simulation/v4_exploratory_x3x7.py`, com testes em `tests/unit/test_v4_exploratory_x3x7.py`, entrou nos commits `4f50bfad` e `332fdbd4`. Ela traz o namespace de sementes e um plano com a interface de `SeedPlan`, as unidades do tier 1 com esses fluxos, a fonte e o executor de célula sucessores, a proveniência, a selagem e a liberação, o arnês genérico da pré-condição bit a bit, o executor retomável e a linha de comando que cada análise expõe. X5 está em `v4_exploratory_x5.py` (`3915eb9e`) e X7 em `v4_exploratory_x7.py` (`1ed5ee8a`), cada um com seus testes. O lançador [`launch-x3x7.sh`](launch-x3x7.sh) entrou em `c8e4861f`, o commit publicado que rodou no homelab. A declaração fala de um módulo sucessor. O código ficou dividido numa base e num módulo por análise, para que X3, X4 e X6 sejam escritos em paralelo sem tocar em código já verificado. Os componentes congelados e os utilitários de X1 e X2 são importados sem edição.

Cada unidade executada confere antes de começar os 80 arquivos Python de `freeze-v4.json`. Ela registra o commit, o estado da árvore, o SHA-256 do `uv.lock`, o SHA-256 de cada módulo sucessor que usa (a base, os dois módulos de X1 e X2 e o da análise), os SHA-256 do README e do JSON desta declaração, o host e a classe de host. Os comandos que executam unidades ou lados de pré-condição recusam árvore suja. Uma unidade só roda depois de uma pré-condição aprovada da mesma análise, no mesmo commit, com os mesmos módulos sucessores e na mesma classe de host (modelo de CPU, sistema e hash do ambiente congelado).

As sementes seguem a declaração: os oito primeiros bytes, big-endian, do SHA-256 de `v4-exploratory-x3-x7|20260928|análise|bloco|fase|papel|índice`. O plano sucessor usa o layout congelado de blocos (2 × bloco + tentativa) e recusa gate, repetição e uma terceira tentativa. A fonte e os executores sucessores recusam `SeedPlan`, `ConfirmatorySeedPlan` e o plano de X1b. Um teste enumera os materiais de `SeedPlan` (calibração e gate), de `ConfirmatorySeedPlan`, do plano de X1b e de `v4_exploratory.derive_seed` e mostra que nenhum começa pelo namespace novo e que os conjuntos de sementes são disjuntos. Outro teste roda uma célula interior completa em N = 60 com as sementes de X3, registra todo material passado ao SHA-256 e verifica que todos os materiais de semente começam por `v4-exploratory-x3-x7|20260928|x3|`. As chamadas de semente dessa célula, repetidas nos planos congelado, de gate, confirmatório e de X1b, não produzem nenhum material do namespace novo. As sementes congeladas desses testes são calculadas só para comparação e não chegam a nenhum gerador. As sementes de `shp-crosswalk-v1` ficam em [2^64, 2^65), fora do intervalo deste namespace.

### Leituras escolhidas onde a declaração não fixava o detalhe

Cada rótulo de análise aceita as oito fases congeladas, porque as pré-condições rodam o pipeline congelado completo com as sementes da própria análise. X4 tem ainda `test`, `single-fit` e `single-null`, e os papéis são os congelados mais `resample`.

Todas as saídas de X3 a X7 ficam sob `~/.local/state/research-workbench/sealed-v4-exploratory-x3-x7/` no host que as produz. Os diretórios são 0700 e os arquivos 0600, com o SHA-256 e o log de acesso do `SealedStore` congelado. Isso vale também para X5 e para as pré-condições, porque a de X5 tem células com a > 0. Só o agregado de X5 sai de lá. Os processos de um host disputam as unidades em ordem de índice, com um lock por unidade. O lançador faz cada processo percorrer as análises na ordem de prioridade, e uma thread passa a X7 assim que X5 não tem mais unidade livre. Nenhuma unidade começa depois de 2026-10-10T02:59Z, e uma unidade terminada depois disso conta como incompleta. Os executores só escrevem na saída padrão o índice da unidade, o estado (`complete` ou `error`) e os tempos. O comando `status` mostra contagens, estados de ajuste e tempos. O `aggregate` de uma análise selada só roda depois de 2026-10-19T02:59Z ou quando existir `~/.local/state/research-workbench/coord-20260925/v4-release/release-record.json` no host, e o agregado registra o SHA-256 desse registro.

Em X5, o canal do braço de dados compõe as quatro famílias de desvio: a máscara domiciliar com retenção dependente de z̄, a confiabilidade `tenure_reliability(máscara, r, δ)` congelada e o deslocamento por onda da tendência e do degrau. Cada condição declarada ativa uma só, e com as quatro em zero o canal é o congelado bit a bit. Com β = 0, a regra é literalmente a comparação congelada u < 0,89. Com β ≠ 0, z̄ é a média do estado latente dos dois moradores na onda anterior, e α_t sai de um Newton salvaguardado dentro do intervalo que os z̄ extremos fixam. A média de p entre os domicílios ativos fica em 0,89 com erro abaixo de 10⁻¹². Com z̄ normal de DP 0,71, a implementação reproduz a conta da declaração: saída anual de 15,3% contra 7,5% nos quintis extremos com β = ln 1,5, e de 18,6% contra 5,5% com β = ln 2. A incerteza de cada célula vem de `score_uncertainty` congelado, aplicado aos escores e desvios gravados, com a semente de bootstrap do plano. Os intervalos usam a fórmula congelada de `band` (logit, piso 1/4.000) com crítico fixo de 1,96 e de 2,7729. As médias de L1 a L5 por braço usam os 4.000 painéis de checagem de cada braço.

Em X7, o desvio-padrão intrapessoal usa ddof = 0, o padrão do NumPy. As transições contam os pares de ondas consecutivas observadas de todas as pessoas, com as linhas na ordem dos grupos e a última coluna de cada linha descartada. Cada painel de treino, checagem e referência é gerado uma vez: o perfil congelado vai para o store de atributos congelados e a linha rica, com a mesma chave de checkpoint, para o store rico. Os 1.024 painéis de matching em θ̂ e nos dois pontos do estêncil são regenerados para os atributos ricos, 3.072 painéis nulos por célula interior. A LDA rica recebe a jacobiana de L1 e L2 do perfil congelado e a mesma semente de nuisance, de modo que os deslocamentos do D5 e as reamostragens de treino são os mesmos nos dois conjuntos. O ΔAUC usa um bootstrap pareado de 1.000 reamostragens com a semente `bootstrap/resample/0` da unidade e os mesmos índices de rede nos dois contrastes e em todas as forças do r.

A leitura de X7 ficou fixada no código antes de qualquer saída. "Longe" vale quando a extremidade superior do intervalo de a*_rico fica abaixo do ponto a*_x7, com uma fronteira não atingida na grade contando como além dela, ou quando os intervalos de ΔAUC ficam acima de zero em todas as forças de a*_rico até a anterior a a*_x7. "Perto" vale quando as duas fronteiras caem na mesma força e os intervalos de ΔAUC nela e nas forças vizinhas da grade cabem em [−0,02; 0,02]. Uma curva com portão nulo inválido torna o r "inválido", uma fronteira censurada o torna "censurado", e os demais casos são inconclusivos.

### Testes

Os testes fixam o código sucessor ao congelado em configurações pequenas. A fonte sucessora reproduz `PanelSource` bit a bit em todas as fases e tentativas, com e sem parâmetros, tanto com o canal neutro de X5 quanto com a fonte de atributos de X7. Numa célula interior em N = 60, (0,03; 0,5), o executor da base, o executor neutro de X5 e o pipeline de X7 com o extrator congelado reproduzem o store de `v4_curve.execute_cell` arquivo por arquivo. O executor neutro de X5 faz o mesmo na célula anchor-exact (0; 0,5). A célula de X7 com os dois extratores deixa o store congelado idêntico, salvo a proveniência da unidade e o selo, e preenche o store rico com os checkpoints esperados. Em β = 0, a máscara de X5 é a de `panel_mask`, e a condição de tenure reproduz o canal congelado do tier 4. Cada desvio muda só o braço de dados. Os atributos ricos conferem com a definição calculada de outro modo, e um atributo não finito vira lacuna numérica registrada. Os testes do executor cobrem a disputa por lock, a retomada, a recusa de tamanhos diferentes, o fechamento da janela, as permissões e a ausência de estatística na saída padrão. Os de selagem cobrem a recusa do agregado antes da liberação. `ruff check .`, `ruff format --check` nos arquivos tocados, `mypy src tests` e os 127 testes dos três módulos passaram, sob `nice`, no Mac.

### Sondagem de tempo

Antes das pré-condições, o lançador rodou no homelab, com 12 processos simultâneos, uma sondagem só de tempo, com sementes fora de qualquer namespace e painéis descartados. As médias de CPU por painel foram de 0,048 s num painel nulo B, 0,039 s num painel social congelado em a = 0, 0,041 s a 0,044 s nos braços de dados de X5 (tendência, tenure e atrito) e 0,024 s na extração dos 36 atributos ricos. São taxas menores que as de X1b (0,066 s por painel nulo). A sondagem tem poucos painéis por processo, e a projeção abaixo usa o tempo medido das células.

### Pré-condição bit a bit de X5

Em cada célula declarada, dois processos separados rodaram no homelab, no commit `c8e4861f`, com as sementes de X5, N = 10.626 e os tamanhos congelados: um com `v4_curve.execute_cell` congelado e outro com o executor sucessor com os quatro desvios em zero. A comparação cobre todos os arquivos do store de cada célula, byte a byte, exceto `access.jsonl`, cuja sequência de ações e chaves também precisa coincidir, e a proveniência da unidade. Os tempos incluem contenção, porque os 16 lados das duas pré-condições rodaram com no máximo 12 simultâneos e, entre 02h24 e cerca de 03h05 UTC, dividiram a máquina com quatro processos de uma pré-condição de X6.

| a | r | Ajuste | Arquivos | Checkpoints | SHA-256 de `seal.json` | SHA-256 de `result.json` | Minutos (congelado / sucessor) | Idênticos |
|---:|---:|---|---:|---:|---|---|---:|---|
| 0 | 0,5 | anchor-exact | 577 | 568 | `98e19518…` | `c21917a9…` | 15,7 / 16,3 | sim |
| 0 | 0,9 | anchor-exact | 577 | 568 | `24133a8a…` | `c21917a9…` | 15,6 / 16,5 | sim |
| 0,03 | 0,5 | interior | 1.371 | 1.362 | `389915f5…` | `3c231664…` | 54,1 / 57,1 | sim |
| 0,3 | 0,6 | interior | 1.659 | 1.650 | `1fee6966…` | `7c6c959c…` | 61,3 / 61,9 | sim |

As quatro células foram idênticas em todos os arquivos e na sequência de acesso, e todas chegaram a um resultado com uma única tentativa de ajuste aceita. As duas células com a = 0 passaram pelo ramo anchor-exact. As outras duas passaram por ajuste interior, validação, estêncil, treino, checagem, referência, jacobiano e nuisance. A regra exigia pelo menos duas células com resultado. O registro, verificado às 03h09 UTC, está em [`results/x5-precondition.json`](results/x5-precondition.json) (SHA-256 `6911209e…`), com o commit `c8e4861f` de árvore limpa, os SHA-256 de todos os arquivos, o host e os tempos. O módulo de X5 tem SHA-256 `017a213a…`, a base `1ab380c9…`, e os 80 arquivos Python congelados coincidiram com `freeze-v4.json`.

### Pré-condição bit a bit de X7

Mesmo procedimento, nas quatro células de X1b, com as sementes de X7: de um lado `v4_curve.execute_cell` congelado, do outro o pipeline de X7 com o extrator congelado (colunas 2:5 do perfil).

| a | r | Ajuste | Arquivos | Checkpoints | SHA-256 de `seal.json` | SHA-256 de `result.json` | Minutos (congelado / sucessor) | Idênticos |
|---:|---:|---|---:|---:|---|---|---:|---|
| 0 | 0,9 | anchor-exact | 577 | 568 | `082b3bb9…` | `c21917a9…` | 15,3 / 15,9 | sim |
| 0,003 | 0,7 | interior | 1.179 | 1.170 | `71e9db32…` | `8d860960…` | 47,7 / 49,3 | sim |
| 0,03 | 0,5 | interior | 1.275 | 1.266 | `0d7ca0f0…` | `be2694ff…` | 46,8 / 47,3 | sim |
| 0,3 | 0,6 | interior | 1.595 | 1.586 | `10346c62…` | `e6fec859…` | 50,7 / 50,8 | sim |

As quatro células foram idênticas, todas com resultado e uma única tentativa aceita. O registro está em [`results/x7-precondition.json`](results/x7-precondition.json) (SHA-256 `cc01fc6b…`). O módulo de X7 tem SHA-256 `a63627ba…`. As duas pré-condições foram aprovadas na primeira tentativa, e nenhum código sucessor precisou de correção. Os stores das duas ficam selados no homelab, em `~/.local/state/research-workbench/sealed-v4-exploratory-x3-x7/c8e4861f/precondition/`.

### Lançamento

O homelab (Linux x86_64, Intel Core i5-1335U, 12 threads lógicas, Python 3.12.13, NumPy 2.5.3, BLAS em uma thread, hash de ambiente `c9766467…`) já estava livre, porque X1b terminara. Às 02h02 UTC de 29/09/2026, o comando `launch-x3x7.sh c8e4861f ~/.local/state/research-workbench/sealed-v4-exploratory-x3-x7/c8e4861f 12 run x5,x7`, na versão do commit `c8e4861f` (SHA-256 `9602c51f…`), fez checkout do commit publicado, sincronizou o ambiente pelo `uv.lock`, conferiu a árvore limpa e iniciou um supervisor destacado, que segura um lock do diretório. O supervisor rodou a sondagem, os 16 lados das pré-condições, cada um no seu processo, e as duas verificações. Às 03h09 UTC, com as duas aprovadas, iniciou 12 workers. Cada worker roda X5 até não haver unidade livre e então passa a X7, na ordem de prioridade declarada. Quando todos terminam, o supervisor roda `status` nas duas análises e `aggregate` em X5, que é aberta. O agregado selado de X7 fica para depois da liberação. Um vigia separado roda `status` e `aggregate` de X5 assim que existirem os 72 registros, para que X5 possa ser lido sem esperar X7.

Às 06h50 UTC, X5 tinha 48 de 72 células concluídas, sem erro. O tempo de parede por célula ia de 40 a 71 minutos, com mediana de 53. Das 48, 24 aceitaram o ajuste na primeira tentativa. As outras 24 passaram pela retentativa D4 e ficaram como lacuna, sem ajuste validado. As células 48 a 59 estavam em execução e as 60 a 71 aguardavam. A projeção é que X5 termine por volta das 09h UTC de 29/09. X7 começa em cada thread à medida que X5 se esgota. Se a maior parte dos ajustes aceitar na primeira tentativa, como em X1b (81 células em 6 h 8 min com 12 processos), X7 termina por volta das 15h UTC de 29/09. Se as retentativas forem frequentes, termina até cerca das 20h UTC. No cenário desfavorável da declaração, com retentativa em todas as células, termina por volta das 10h UTC de 30/09. Todos esses horários ficam muito antes do corte de 2026-10-10T02:59Z.

Depois do lançamento, `launch-x3x7.sh` ganhou um sucessor em `cd8d47a3` (SHA-256 `201b7d65…`). Cada commit lançado passa a ter seu próprio worktree ao lado do clone, `research-workbench-v4x-<commit>`, e o lançador confere se as ferramentas de que precisa estão disponíveis. Assim, lançamentos em commits diferentes no mesmo host não mexem no checkout nem no ambiente de um supervisor em curso. A versão nova foi testada no homelab em modo `probe`, com um processo, e não alterou o checkout do run. A cópia `~/launch-x3x7.sh` do homelab passou a ser a versão nova, e a anterior ficou em `~/launch-x3x7-c8e4861f.sh`. O run em curso continua usando o clone `~/Documents/github/research-workbench-v4x` em `c8e4861f`, onde cada worker inicia X7 depois de X5, e por isso esse clone não pode mudar de commit até X7 terminar.

## X5: resultado

X5 rodou no homelab das 03h09 às 08h36 UTC de 29/09, com 12 processos, no commit `c8e4861f`. Consumiu 5 h 27 min de relógio e 58,5 horas de CPU. As 72 células terminaram sem erro, e o agregado está em [`results/x5.json`](results/x5.json) (SHA-256 `88e78a38…`). Pela declaração, X5 não é selado.

Em cada célula, o braço de dados tem a = 0, sem nenhuma influência, e é observado por um canal diferente do que a nula B assume. A nula B, corretamente especificada, é reajustada pelo pipeline congelado, e a AUC mede o quanto a má especificação sozinha separa os braços. As leituras seguem a regra declarada, com intervalos pela fórmula congelada da banda a 1,96: "cruza o alvo principal" quando o limite inferior passa de 0,70, "cruza o secundário" quando passa de 0,60 e "abaixo dos alvos" quando o superior fica abaixo de 0,60.

| Condição | Células com estimativa | AUC (mín.–máx.) | Leituras | Portão nulo congelado dispararia |
| --- | ---: | --- | --- | ---: |
| Tendência linear em r, A = 0,03 | 9 | 0,680–0,710 | 9 cruzam o secundário | 9 |
| Tendência linear em r, A = 0,08 | 9 | 0,884–0,907 | 9 cruzam o principal | 9 |
| Degrau na onda 5, A = 0,03 | 0 | — | 9 falhas de ajuste | 0 |
| Degrau na onda 5, A = 0,08 | 0 | — | 9 falhas de ajuste | 0 |
| Condicionamento de permanência, δ = 0,10 | 0 | — | 9 falhas de ajuste | 0 |
| Condicionamento de permanência, δ = 0,20 | 0 | — | 9 falhas de ajuste | 0 |
| Atrito dependente da confiança, RC 1,5 | 9 | 0,540–0,640 | 1 cruza o secundário, 4 intermediárias, 4 abaixo dos alvos | 9 |
| Atrito dependente da confiança, RC 2 | 9 | 0,578–0,820 | 5 cruzam o principal, 2 o secundário, 1 intermediária, 1 abaixo | 9 |

Sem nenhuma influência, uma tendência lenta na parcela de sinal ao longo das onze ondas basta para uma AUC perto de 0,70, com A = 0,03, ou perto de 0,90, com A = 0,08. O atrito dependente da confiança também produz AUCs acima de 0,70 nas confiabilidades baixas; com RC 2, a AUC cai de 0,82 em r = 0,5 para 0,58 em r = 0,9. Com o degrau na onda 5 e com o condicionamento de permanência, o ajuste congelado de B não encontra solução interior, fica na fronteira ou mal condicionado, e a célula vira lacuna em todos os r. Nas quatro condições com estimativa, o portão nulo congelado em a = 0, com o intervalo a 2,7729, excluiria 0,5 e invalidaria a comparação.

A leitura, apenas exploratória, é que a fronteira confirmatória vale para um canal de medida corretamente especificado. Numa aplicação a dados reais, em que não há braço conhecido com a = 0, má especificações dessas magnitudes separariam as trajetórias da nula tanto quanto uma influência perto do alvo. Depois da liberação, cada condição será posta sobre a curva a*(r) como uma "força equivalente", como a declaração prevê.

## X6: pré-condição do T_pop

Estado em 29/09/2026: X6 está implementado e ainda não rodou. O código está em `src/ic_study/simulation/v4_exploratory_x6.py`, com testes em `tests/unit/test_v4_exploratory_x6.py`, no commit `0443b91e` (SHA-256 do módulo `5c0e230a…`). As repetições de X6a e X6b e os pipelines de T_D1 usam o executor congelado sem mudança, e só o ajuste de T_pop recombina partes congeladas, por isso só ele tem pré-condição. X6 fica selado até a liberação, e esta nota traz apenas o resultado da pré-condição e os hashes.

A pré-condição passou no homelab às 03h03 UTC de 29/09/2026. No commit `0443b91e`, com árvore limpa e N = 10.626, dois processos separados rodaram cada uma das células declaradas, (0,03; 0,70) e (0,30; 0,70), com as sementes `x6-pop`: um com `fit_cell` congelado e outro com o invólucro de ajuste de T_pop em M = 1.024. Cada lado gravou os arrays da primeira tentativa (parâmetros, diferenças, resíduos, EP e tolerâncias) e a entrada congelada de `fit_record` sem a validação. Os sete arquivos de cada célula coincidiram byte a byte, assim como a sequência de ações e chaves de `access.jsonl` e a proveniência da unidade, e as duas células chegaram a resultado.

| a | r | Ajuste | Arquivos | SHA-256 de `seal.json` | SHA-256 de `result.json` | Idênticos |
|---:|---:|---|---:|---|---|---|
| 0,03 | 0,7 | interior | 7 | `35d274a3…` | `e3989231…` | sim |
| 0,3 | 0,7 | interior | 7 | `ab417f5f…` | `adf9b1c7…` | sim |

O registro de verificação fica no homelab, em `~/.local/state/research-workbench/sealed-v4-exploratory-x3-x7/x6-0443b91e/x6-pop-precondition.json` (SHA-256 `41763ffd…`), com a classe de host (Intel Core i5-1335U, Linux, ambiente `c9766467…`) e os 80 arquivos Python congelados conferidos contra `freeze-v4.json`, todos iguais. A aprovação vale para esse commit e essa classe de host. Cada PC do laboratório repete a pré-condição no commit de lançamento antes de rodar qualquer unidade de X6.
