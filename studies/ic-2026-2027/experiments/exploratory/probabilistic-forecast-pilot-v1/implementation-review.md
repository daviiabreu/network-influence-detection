# Revisão independente da implementação do piloto

Data: 12/09/2026. Estado: achados corrigidos; nenhum bloqueio remanescente para o piloto sintético exploratório delimitado. Esta é evidência de revisão por agente em contexto separado, não aprovação do Research Owner, aceitação científica, demonstração de novidade ou autorização de avanço para ESS.

A revisão recebeu apenas o pacote candidato indicado abaixo, a rubrica e as normas do repositório. Foram lidos os AGENTS aplicáveis, a arquitetura, o ciclo de pesquisa, as regras de validação, o contexto do estudo e a seção Independent challenge do charter. Não foram abertos o memo de origem, o ranking de propostas, a conversação de autoria ou decisões anteriores de aceitação. Houve comunicação com o implementador exclusivamente sobre achados e correções; nenhum outro agente foi delegado pelo revisor. As afirmações bibliográficas foram confrontadas com fontes primárias públicas.

## Achados e resolução

| Achado | Evidência inicial e consequência | Correção verificada |
| --- | --- | --- |
| P2 — empates do DW podiam cair na categoria inferior; bloqueava os lotes | O núcleo inicial produzia `0.44999999999999996` para o par `[0.3, 0.6]`, entrando na categoria 4, embora o ponto médio exato 0.45 pertencesse à 5. O par `[0.6, 0.7]` entrava na 6 em vez da 7. Esses pares têm probabilidade positiva desde a inicialização; o erro alterava contagens, não apenas sua apresentação. Os nove testes iniciais passavam porque construíam fronteiras diretamente. | `histogram_forecast.py:52–66,85–101` usa unidades inteiras de `1/(10*2^A)`, médias exatas, confiança racional e discretização inteira. Depois de no máximo A eventos, há precisão suficiente: cada média pode consumir no máximo um fator 2 da divisibilidade inicial. As regressões dos dois pares e dos valores um tick abaixo passaram. O kernel completo coincidiu com uma referência independente em `Fraction` nos 60 casos descritos abaixo. |
| P3 — afirmação incorreta sobre ES negativo | O protocolo inicial dizia que o ES U euclidiano com expoente 1 poderia ser negativo em aritmética exata. Entretanto, a desigualdade triangular dá `sum(r<s) d(Xr,Xs) <= (R-1)*sum(r) d(Xr,y)`, garantindo a não negatividade do estimador implementado. Essa afirmação poderia normalizar resultados numericamente inválidos. | `protocol.md:53–57` agora distingue não negatividade exata e arredondamento, sem truncamento silencioso, e manda investigar resultados abaixo de `-1e-12`. O denominador U já estava correto e foi preservado. |

A redação sobre a comparação de precisão também foi ajustada: ela mede sensibilidade ao aumento de R e a um novo ensemble. Como as sementes mudam entre principal e precisão, não é uma diferença determinística causada somente por R.

## Rubrica aplicada

O gerador e o candidato correspondente à verdade chamam o mesmo `draw_histogram`, recebem o mesmo histograma observado e os mesmos parâmetros de população, amostra e tentativas. O oracle conhece o mecanismo condicional; não recebe a população latente realizada nem os sorteios de verificação. O reinício a cada onda é parte explícita da lei geradora. Há duas camadas de amostragem também no controle sem atualização. A variância analítica desse controle inclui ambas e seu teste passou.

As sementes distinguem dados e previsões, fase, célula, trajetória, onda, modelo e membro; inicialização, eventos e observação usam subfluxos separados. Principal e precisão reutilizam os dados declaradamente, com previsões novas; confirmação usa outro grupo de dados e outra fase de previsões. A escolha de modelo acessa apenas as duas ondas de treino, respeita a ordem prévia para desempate e é reutilizada no teste. A dependência temporal entre ondas permanece dentro da trajetória; não se exige que as ondas sejam observações independentes.

W1 opera sobre frequências nos suportes `0,.1,...,1`, pela integral discreta das diferenças entre CDFs. O cálculo de ES usa norma euclidiana e pares não ordenados com denominador `R*(R-1)`, equivalente à soma ordenada com denominador `2*R*(R-1)`. Com membros iid condicionais e independentes da verificação, isso estima o score da lei preditiva, não o score da distribuição empírica finita. Os testes analíticos distinguem a distribuição verdadeira de uma previsão pontual no caso enumerável. O centro é um estimador plug-in. As perdas não têm magnitudes diretamente comparáveis; os controles mean-L2 e central-L2 ajudam a separar a geometria da correção de dispersão.

O resumo primeiro calcula a média de teste de cada trajetória e depois as diferenças pareadas em relação ao controle constante. Portanto, cada intervalo usa 30 unidades independentes por célula, não 60 ondas nem os entrevistados. O valor crítico é compatível com os 29 graus de liberdade declarados. São intervalos pontuais exploratórios; a reprodução em células selecionadas não os converte em intervalos simultâneos ou validação registrada. Tolerância, células, tamanhos, sementes e critérios de continuidade foram declarados antes dos lotes.

A reprodução por sementes e a invariância à ordem de chaves JSON passaram. Os registros mantêm observações, previsões, seleção e scores completos. O cabeçalho contém especificação, revisão Git, hashes de fontes/lock e ambiente; criação exclusiva evita sobrescrever uma saída existente, e o rodapé identifica conclusão. A decisão de orçamento exige os dois benchmarks e o registro da projeção antes dos lotes. A fórmula separa geração linear, scoring quadrático e overhead, com margem; ela não prova antecipadamente o custo real nem autoriza aumentar R em função dos sinais observados.

## Verificação executada

Na versão corrigida, executados no diretório do estudo:

```text
/Users/davi/.local/bin/uv run pytest tests/scientific/test_histogram_forecast.py tests/integration/test_forecast_pilot.py
11 passed in 0.12s

/Users/davi/.local/bin/uv run ruff check src/ic_study/models/histogram_forecast.py src/ic_study/metrics/histogram_scores.py src/ic_study/analysis/forecast_pilot.py tests/scientific/test_histogram_forecast.py tests/integration/test_forecast_pilot.py
All checks passed!

/Users/davi/.local/bin/uv run mypy src/ic_study/models/histogram_forecast.py src/ic_study/metrics/histogram_scores.py src/ic_study/analysis/forecast_pilot.py
Success: no issues found in 3 source files
```

Uma referência temporária independente representou opiniões por `Fraction(k,10)`, comparou confiança racional, calculou médias e drift racionais e categorizou por `floor(10*x+1/2)`. Houve igualdade exata de todos os histogramas para cinco mecanismos, A em {0,25,150}, amostras em {55,550} e sementes {19,773}: 60 casos, sem calcular os contrastes científicos do piloto.

Um smoke temporário mínimo, anterior à correção aritmética, verificou cabeçalho, trajetória e rodapé, regenerou a linha da trajetória a partir da especificação/sementes serializadas e confirmou `FileExistsError` sem mudança de bytes ao tentar repetir o caminho de saída. A correção posterior ficou restrita ao mecanismo e a sua validação; os testes de reprodução JSON foram repetidos na versão final. Nenhum lote empírico, benchmark de orçamento ou matriz completa foi executado por este revisor.

## Fontes e limites remanescentes

O preprint do benchmark confirma previsão de um passo reiniciada na observação e ajuste por erro médio entre repetições. Seu baseline da Eq. (2) copia diretamente o histograma anterior; o controle constante deste piloto passa pelas duas amostragens. A interpretação deve preservar essa diferença e a declaração de que não há reprodução integral do benchmark. [Moor-Smith–Carpentras, §§2.1–2.3, 3.1.1 e 3.2](https://arxiv.org/html/2602.00876v1).

A definição de ES, a propriedade estrita na classe com momento finito e a limitação do expoente 2 estão apoiadas na fonte. A distinção entre distribuição empírica e ensemble amostrado também é explícita na literatura; o denominador usado no piloto decorre da sua derivação, sem tratar a fórmula escalar de CRPS como demonstração multivariada. [Gneiting–Raftery, §4.3](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf), [Ferro, §§2–3](https://empslocal.ex.ac.uk/people/staff/ferro/Publications/ferro2013.pdf), [Fricker–Ferro–Stephenson, §4](https://empslocal.ex.ac.uk/people/staff/dbs202/publications/2013/fricker2013.pdf).

A checagem dirigida confirmou os antecedentes que impedem alegações genéricas de novidade: MSE entre momentos simulados na comparação com verossimilhança; MAE e Brier na previsão de interações; Brier e acurácia na agregação com HK modificado; e componente logarítmico na avaliação de especialistas. A orientação da figura SI8 de Kolic continua descrita como ambígua, sem reinterpretar seus números. Essa checagem não estabelece ausência de trabalhos sobre o contraste exato. [Lenti et al., §5](https://arxiv.org/html/2310.02766v2), [Kolic et al., §2.2 e apêndice A.2](https://arxiv.org/html/2509.17625v1), [Douven et al., Dynamic aggregation e Study](https://journals.sagepub.com/doi/full/10.1177/26339137261435121), [Gonzalez-Hernandez et al., Prediction accuracy](https://jasss.soc.surrey.ac.uk/27/4/3.html).

Antes de usar resultados para uma afirmação, a entrega ainda precisa congelar os arquivos revisados, registrar a escolha de R por tempo, preservar os lotes concluídos e conferir todas as células e controles. O resumo exportado compara modelos com o baseline constante; as comparações com o oracle de drift e as diferenças pareadas entre lotes devem ser reconstruídas dos registros completos. O contraste central, os controles de geometria, as reversões e o cumprimento das regras de parada ainda não foram avaliados. A equivalência condicional do oracle e a propriedade do ES não garantem sua vitória em cada amostra, seleção correta com treino curto, validade para população persistente ou contribuição publicável.

## Identidade do pacote revisado

Base Git observada: `34a9b43ce96c5b991f07819ced167f3440c7c641`. Os oito arquivos candidatos ainda estavam fora do índice; por isso a identidade desta revisão é dada pelos hashes abaixo, relativos à raiz do estudo. O commit de congelamento deve conter exatamente esses bytes. O próprio relatório não integra sua lista de hashes, para evitar autorreferência.

```text
7e8e0d4b8d61a2d64e3b9d32102ab905045d4d583fad40f5c71212ac4b3f054b  experiments/exploratory/probabilistic-forecast-pilot-v1/spec.json
53cda076c6c818792a7331bcde1f631dcabffe72fefaf1b540041b4fbfb72150  experiments/exploratory/probabilistic-forecast-pilot-v1/protocol.md
ddbc3266bd02847fc56a2bcecf0ebf724ae68833b978f103d237c8a1b3218823  experiments/exploratory/probabilistic-forecast-pilot-v1/source-check.md
8d1b49197e30d0d8ed1fe892f2095bf41b6107109462168a36c8f0ef50e174ed  src/ic_study/models/histogram_forecast.py
32c8ca36267deb7332ba8af56a37a39f01c15c0b90cab83d30265c10b01cf662  src/ic_study/metrics/histogram_scores.py
26ea4f5e6c3754a4cd1344154c72e533dc4004a3b6183c9704b87c3886698436  src/ic_study/analysis/forecast_pilot.py
b157eaffe999dcd89903dba7ae34a276b29fe346aeb5f6f2627e582c013f6adb  tests/scientific/test_histogram_forecast.py
3c7c9b0ec4e25f36c57eaf43940e781238d8ec8fa0ccebadf07bb8ed97f15f80  tests/integration/test_forecast_pilot.py
```
