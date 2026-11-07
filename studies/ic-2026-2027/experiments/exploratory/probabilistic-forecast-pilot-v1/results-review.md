# Revisão isolada dos resultados do piloto de previsão

12/09/2026. Nenhum bloqueante encontrado para a entrega das sete afirmações
candidatas com o alcance exploratório declarado. Nenhuma célula satisfaz o
contraste central em nenhum lote. Encerrar este piloto delimitado segue a
regra congelada; não demonstra ausência geral do efeito nem constitui
aceitação científica do Research Owner.

## Isolamento e escopo real

A revisão seguiu Independent challenge do charter e recebeu somente os nove
arquivos candidatos identificados abaixo, as fontes/lock do manifesto, os
cinco objetos JSONL em CAS e as normas aplicáveis. Não acessou o memo de
origem, rankings, propostas anteriores, conversação de autoria, outros
relatórios finais ou decisões de aceitação. Não delegou trabalho. A comunicação
com a coordenação tratou de escopo e achados, sem incorporar sua validação
externa ao parecer.

Não executou matriz completa, novos lotes, busca bibliográfica ou aquisição de
dados. As dez regenerações foram verificações pontuais em memória de
trajetórias registradas. Apenas este relatório foi criado pelo revisor no
pacote. As URLs bibliográficas não foram reabertas: a parte bibliográfica
foi avaliada a partir de `source-check.md` e `implementation-review.md`,
não como uma nova validação primária de toda a literatura.

## Integridade, completude e custo

Os cinco objetos CAS têm SHA256 e tamanho iguais ao manifesto. Cada um contém
um cabeçalho, todas as trajetórias esperadas e um único rodapé `completed`,
terminando com nova linha. São 16 trajetórias por benchmark e 480 por lote
analítico: 16 células completas, com réplicas únicas 0 a 29 nos lotes
analíticos. Todas têm quatro ondas, duas de treino e duas de teste, cinco
candidatos por onda e R membros por candidato. Cada histograma tem onze
inteiros não negativos somando n. Os estados observados encadeiam exatamente
os desfechos anteriores a partir do histograma uniforme.

Cabeçalhos, rodapés e manifesto concordam em fase, R, tempos, ambiente,
revisão Git, especificação e fontes. Foram feitas 70 comparações dos 14
hashes de fontes/lock de cada lote aos bytes de
`git show <revisão>:<arquivo>`. Os benchmarks usam
`333938ecddf7f97eec4544d0fda40a0952e54183`; os três lotes analíticos,
`71ae80cf313b6c467abad5eeedfa6a266e5daaa0`. As fontes são iguais entre
essas revisões e o checkout conferido. Especificação, protocolo, nota de
fontes, revisão da implementação e autorização coincidem com os bytes nos
commits de execução. Também conferiram as referências de hash da análise
ao manifesto, da autorização à revisão e do orçamento à especificação.
Os testes citados na autorização não foram relidos ou executados.

A projeção refeita é 278,88545917725423 s para R=128 e
143,09232777130092 s para R=64. A escolha de R=128 cabe no teto de
1.200 s com a margem de 50% já incorporada e seu registro precede o
principal. Os tempos dos três lotes somam 179,1775705839973 s. A conferência
atesta aritmética e ordem temporal; não permite verificar se alguém
inspecionou os sinais dos benchmarks.

## Reconstrução e reprodução

Foram recalculados todos os 147.200 scores: 1.472 registros de trajetória ×
quatro ondas × cinco candidatos × cinco scores. A validação percorreu
2.795.520 histogramas de ensemble. Nenhum membro ou score foi amostrado.
Os benchmarks foram conferidos, mas ficaram fora dos contrastes analíticos.

A rotina independente não chamou `score_ensemble`, `summarize` ou
`interval` do estudo. W1 foi calculado por somas cumulativas das contagens,
normalizadas ao fim por `10*n`; W1 do centro, por somas das contagens dos R
membros e denominador `10*R*n`. L2 foi calculada no espaço de contagens e
dividida por n. ES subtraiu da média L2 a soma de distâncias dos pares não
ordenados dividida por `R*(R-1)*n`. A implementação registrada normaliza
os vetores antes das distâncias. A maior discrepância entre as duas rotinas
foi `4.440892098500626e-16`, abaixo da tolerância `1e-12`.
O menor ES foi zero; nenhum valor ficou abaixo de `-1e-12`.

Todas as escolhas foram refeitas somente com as duas ondas de treino,
respeitando o desempate congelado, e coincidiram. As duas perdas de teste
foram agregadas antes de calcular diferenças pareadas por trajetória.
Para 30 diferenças, o erro padrão independente foi
`sqrt(sum((d-mean(d))²)/(30*29))` e o IC foi
`mean(d) ± 2.04523*SE`. A unidade é a trajetória, não a onda ou entrevistado.

Conferiram integralmente os resumos das 80 células-lote, os cinco scores,
perdas dos cinco candidatos e do selecionado, diferenças e frequências;
nos benchmarks, os IC são ausentes. Nos lotes analíticos, todos os campos
de `all_cell_summaries`, `oracle_contrasts`, `controls`,
`precision_sensitivity`, critérios e mínimo de ES coincidiram.
O maior erro nos resumos/contrastes foi `3.3306690738754696e-16`.

Os 40 resumos de sensibilidade, oito células × cinco scores, foram refeitos
por `(oracle-constant)_precision - (oracle-constant)_primary` na mesma
trajetória. Essa comparação muda R e o ensemble conjuntamente. Em
`dw-a25-n55`, por exemplo, a mudança do contraste de média W1 foi
-0,0028726325757575735, IC [-0,005497801536211105;
-0,0002474636153040424]. O sinal pontual do principal não deve ser
interpretado sem essa sensibilidade.

Todas as sementes registradas de dados e modelo/onda foram refeitas por
SHA256. Não houve duplicatas dentro de cada lote nem colisão entre dados e
previsões. Principal e precisão têm os mesmos 480 registros de dados,
incluindo as 1.920 transições e sementes, com sementes de previsões
distintas. Confirmação tem sementes novas de dados e previsões; nenhum dos
seus 1.920 desfechos coincide com o desfecho alinhado do principal.
Os benchmarks compartilham seu próprio grupo de dados e sementes-base,
separados dos lotes analíticos. Há 960 trajetórias de dados novas entre
principal e confirmação; precisão não eleva esse número a 1.440.
A separação de sementes sustenta a independência operacional dos subfluxos,
não uma demonstração matemática de independência do pseudoaleatório.

Dez trajetórias completas foram regeneradas com igualdade exata de
observações, ensembles, scores, sementes e escolhas, normalizando somente
tupla/lista por JSON. Os caminhos de importação dos três módulos
científicos efetivamente carregados foram conferidos e seus hashes
coincidem com os commits. A regeneração usa o código congelado; a rotina
de scores acima é independente. Não houve segunda implementação integral
do kernel nesta revisão.

Os hashes abaixo são de `json.dumps(row, sort_keys=True)` em UTF-8, sem
nova linha. Réplicas são os índices registrados, a partir de zero.

| Lote | R | Célula | Réplica | SHA256 da trajetória regenerada |
| --- | ---: | --- | ---: | --- |
| Principal | 32 | `constant-a25-n55` | 0 | `21c7ee0152c64cf1521b9cfcb3d8eb4b7c35d52d53dcbfecbcac0b237b0b9fc0` |
| Principal | 32 | `dw-a150-n550` | 0 | `17e861fb60a72acdc0482dde1216349a6beb724a53247c0a4935bbab5cea7f8c` |
| Principal | 32 | `pulsed_dw-a150-n55` | 0 | `69bfd961527f5b1c655b9781e84aa7a2ecd5ee74bb659bd54106404d36ebe826` |
| Principal | 32 | `drift_plus-a25-n550` | 0 | `21b14efb796d83fcda4bde571d411aa70b899c014fe0f602d56d6e3475cb2001` |
| Precisão | 128 | `dw-a150-n55` | 15 | `cc19a14e58a01ee3c6b1c95e1448654e9eebe7b5d297fc86f30e8f364dcac311` |
| Precisão | 128 | `pulsed_dw-a25-n550` | 15 | `884aebd4f8ce1ccabb91e32fd1298b3bd23b81683ea9dca2c4f347478e71b637` |
| Confirmação | 128 | `constant-a150-n550` | 29 | `4fcceab904a80bfc878627a0084bab7367922009e0d0ff653e1930fca05c675d` |
| Confirmação | 128 | `dw-a25-n55` | 29 | `b8c736d20fad01cb69fe6f6a2d4ee3a2af164e4da420af570feade35cc499fb3` |
| Confirmação | 128 | `pulsed_dw-a150-n550` | 29 | `1e514ec8a60ef25b1acfb415ab53f4a412cfed88ff0bf185676ecdf8dae38e8d` |
| Confirmação | 128 | `drift_plus-a150-n55` | 29 | `108fb70cc4948208d29025925d7348bab25cde2b2291d79539b692aebe4cf669` |

## Afirmações atômicas e julgamento científico

| Afirmação | Resultado da revisão |
| --- | --- |
| 1 — lotes, contagens e custo | Confirmada. Principal e confirmação contêm 960 trajetórias de dados independentes por construção; precisão compartilha os dados do principal. Os dois benchmarks também compartilham seu próprio grupo. A soma é 179,18 s contra projeção de 278,89 s. |
| 2 — critério central | Confirmada em todas as oito células dinâmicas: 0/8 no principal, 0/8 na precisão, 0/8 na confirmação e 0/8 na interseção. Foram usados IC absolutos completos contra ±1% da média do baseline, antes de arredondar. |
| 3 — DW com 150 tentativas | Confirmada. Os três scores principais têm IC inteiramente favorável ao oracle, nas duas amostras, nos três lotes. Na confirmação, média W1 cai 16,1428935% e 23,1739074%; ES cai 42,2831391% e 54,5020123%. As escalas não são diretamente comparáveis. |
| 4 — célula episódica A=150, n=550 | Confirmada. Na confirmação: ES -21,3940341%, média W1 +1,5622368%, W1 do centro -11,0438669%. O IC absoluto de média W1 é [-0,00199873; 0,00414172], arredondado a oito casas. Mean-L2 é +8,6373463%, IC relativo [1,7791264%; 15,4955662%]; seus IC nos dois lotes anteriores cruzam zero. Não cumpre o critério central. |
| 5 — controles e seleção | Confirmada em todas as células. Nenhum dos 48 contrastes de candidatos dinâmicos fixos contra o oracle de controle tem IC de ES inteiramente favorável. Também foram conferidos os 24 contrastes do modelo selecionado e as frequências de todos os scores. |
| 6 — fontes e kernel | Reinicialização, N=50, duas camadas multinomiais e ausência de inferência causal conferem no código/protocolo. Os antecedentes constam das notas fornecidas, sem nova consulta primária nesta revisão. A busca dirigida não certifica novidade. |
| 7 — encerrar o piloto | Compatível com a regra congelada e o resultado. É recomendação operacional para este piloto; não rejeita definitivamente uma família de perguntas, elege artigo ou substitui a síntese e a decisão do Research Owner. |

No controle sem atualização, as escolhas de dinâmica por ES se distribuem
assim; cada célula tem 30 trajetórias:

| Célula | Principal | Precisão | Confirmação |
| --- | ---: | ---: | ---: |
| A=25, n=55 | 16 | 15 | 18 |
| A=25, n=550 | 14 | 12 | 14 |
| A=150, n=55 | 6 | 7 | 6 |
| A=150, n=550 | 6 | 2 | 2 |
| Total de escolhas dinâmicas | 42/120 | 36/120 | 40/120 |
| Total de kernel errado, incluindo drift | 44/120 | 39/120 | 41/120 |

No controle de drift positivo, ES escolheu o kernel verdadeiro 120/120 em
cada lote. Escolha errada com duas ondas de treino não equivale a vantagem
esperada indevida nem demonstra vazamento. Também não é uma estimativa
universal de falsos positivos. O acerto no drift construído não demonstra
identificabilidade geral ou recuperação de parâmetros contínuos.

Não há cálculo de poder que permita tratar os 30 casos por célula como
teste de equivalência ou afirmar inexistência do contraste. Os IC t são
pontuais e exploratórios, sem ajuste simultâneo. R=128 não aumenta o número
de trajetórias de dados nem elimina a incerteza de população finita.
O encerramento segue a regra de parada, não uma prova de impossibilidade.

O baseline `constant` ainda aplica as duas amostragens. Ele difere da
cópia determinística do histograma anterior descrita para o baseline do
benchmark na revisão de implementação. O piloto não testa diretamente a
preferência por esse baseline literal, nem explica empiricamente o
“congelamento” publicado. A declaração de não reprodução integral deve
acompanhar qualquer comparação.

ES euclidiano ignora a ordem das categorias, enquanto W1 usa essa ordem;
W1 do centro também muda a agregação. Mean-L2 aproxima a geometria, mas o
contraste ilustrativo não replica seu IC positivo. Esses resultados não
isolam uma contribuição probabilística nova. Os percentuais e IC divididos
pela média observada do baseline são escalas descritivas, não IC de uma
razão que propaguem a incerteza do denominador.

Não há correção numérica exigida para as afirmações recebidas. Generalidade,
equivalência, reprodução integral do benchmark, detecção confiável de
influência ou novidade demonstrada excederiam este parecer.

## Identidade exata dos inputs

Arquivos relativos ao diretório deste relatório:

```text
376fec9728358d1f26ca9f42b5beb3e21afb3395031f6ed5aec19e7326d619cb  analysis-input.json
4cc22c40f449fb9ed2b98775f5a2819457fed039d9242aa6bf083984b9d564ae  authorization.json
a0e3b6659ef9dc07a1a0a095f835e2f04721c722e06e4eecf80afb757fe5503c  budget-decision.json
08a4c89cd9e4c13d5098975bf76f0848142652098943cc7efa77dd680eb0e08b  implementation-review.md
53cda076c6c818792a7331bcde1f631dcabffe72fefaf1b540041b4fbfb72150  protocol.md
3b778e33f20ee1720303431d7800996a2c2caed88837077616abae0fe5cb50fb  recommendation-input.md
0021bcc6c7b433b72bd7c23fe8120e8062e3cd1a703b534d9fb06209895bf60c  run-manifest.json
ddbc3266bd02847fc56a2bcecf0ebf724ae68833b978f103d237c8a1b3218823  source-check.md
7e8e0d4b8d61a2d64e3b9d32102ab905045d4d583fad40f5c71212ac4b3f054b  spec.json
```

Objetos externos; os caminhos CAS completos constam do manifesto. Foram
lidos os objetos CAS, sem depender dos aliases `original_location`.

```text
5da4db6753c93ae1fa1c906b813bb7300279835c5761e3af68b77cab8b3847cd  benchmark-r32
4c3f73fe0093b1949a1cdd3b8f24730feb4b98911ab3bda3db41b3cea79a3559  benchmark-r64
f24f66d0764f31ed8375888b92bf186778e78db129d7e97c6799e5ab0cf21607  primary-r32
de4129d0bfbd9ca7763870500ea1f83d43c54e9414268222fb64d18f1bb15cee  precision-r128
8e6ebe12291ec73ccb665394eb267b535ef738da07562913829b19ecc01b94de  confirmation-r128
```

Fontes/lock relativos à raiz do estudo, iguais nas duas revisões de execução
e no checkout conferido:

```text
9f4394ce1733048a86d6ce3b1c3d1889ce50fce6b8952b7a0788c5b1b5490007  pyproject.toml
3879b68770a7605b52e54c3a28ce4e113057d5a54def62c2a96d1c5aba03ced8  src/ic_study/__init__.py
97a40cfcc9682427daf8b1323db8d793db3a4a97845c4e39b5e47a2aed1e048e  src/ic_study/analysis/__init__.py
26ea4f5e6c3754a4cd1344154c72e533dc4004a3b6183c9704b87c3886698436  src/ic_study/analysis/forecast_pilot.py
bd14158e491180f9dc0e8de8a93c0431835e9eb808d33caf5e576468b33beeeb  src/ic_study/analysis/fragmentation_pilot.py
2300f6e8d2927c22fc200b49130eb2048364205e0e12b4c0044196525d720c4d  src/ic_study/metrics/__init__.py
32c8ca36267deb7332ba8af56a37a39f01c15c0b90cab83d30265c10b01cf662  src/ic_study/metrics/histogram_scores.py
58a8ea908aaede77aa1b342f9bb6ad24134fa3573e05fb2d198b2177cdc92e27  src/ic_study/models/__init__.py
ca2f276645c61cfecbf0ce52ca8a894a98154fe65b24429c0692d3dd2a8e7f4d  src/ic_study/models/deffuant.py
8d1b49197e30d0d8ed1fe892f2095bf41b6107109462168a36c8f0ef50e174ed  src/ic_study/models/histogram_forecast.py
87f904b9ac14527a325b2821319c3de859ea01887626b017e46644d7218dd178  src/ic_study/simulation/__init__.py
b299a53dad35f8c00f5ba4d8dd080ca45d591546c180425912bf2dee6e8d5acb  src/ic_study/simulation/fragmentation.py
02e9b5c598335b5d95562a56c63397df70b8552359912fe2edea88754a749424  src/ic_study/validation/__init__.py
b68ff2485ea124d94ef5e4df33ae15f1118e0530266bdd1b38221bc6f1835e7c  uv.lock
```

Normas e contexto, relativos à raiz do repositório:

```text
1ac29f75b1e622cf3f94b9deaf3b3654b25036d51334ca1af0c7cbf587c16b72  AGENTS.md
0eeb631b39bd219b8933b033b44a1fb69d4f76c658ba0055628236e0bee7c0b4  studies/ic-2026-2027/AGENTS.md
4c2f31719d5ffee246dfacaa4a33bbfcc318719bb890172baa2b9e63840e3fcc  CONTEXT-MAP.md
cb5cb5313611c2e41c211e38f9efff6ddcfe8907c19ff53b62d2ae087d2a625e  docs/architecture.md
d98bc6e4d80e58d0d879774cc52ec2c38bd694b70368bab97ca089b5452bc245  studies/ic-2026-2027/CONTEXT.md
984fe755b549f07b64dfe92dc8f5dee397dbf5b41b0a33574728c255d1358f05  docs/process/research-lifecycle.md
4712812766c79d507cee8911973817a3d7172743fcc2db30b6a91914fdebcb68  docs/process/engineering-validation.md
5a5da254a85e9f11b0c453e7b5492bdf652f62b5aa452b0b62693d630f29af8f  studies/ic-2026-2027/research/charter/study-charter.md
```

O relatório não integra sua própria lista de hashes. Revisão por agente
isolado e reprodução numérica não são aprovação científica do Research Owner.
