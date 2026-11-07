# Sonda exploratória de Gestefeld e Lorenz (2023)

Esta é uma reimplementação independente e mínima da regra de atualização de
[JASSS 26(4):9](https://www.jasss.org/26/4/9.html), consultado em 24/09/2026.
Não é a execução do código dos autores nem a reprodução dos ajustes às amostras
ESS e SHP. O artigo aponta para [um depósito no OSF](https://osf.io/fsbda/).
As primeiras tentativas de 24/09/2026 falharam por 403 na ferramenta web e por
DNS no `curl`. Com a rede restaurada, a [API do nó](https://api.osf.io/v2/nodes/fsbda/)
e a [listagem de arquivos](https://api.osf.io/v2/nodes/fsbda/files/osfstorage/)
responderam. O nó é privado (`public: false`), mas o link de visualização publicado no artigo
permite leitura. A listagem contém três CSVs derivados, nenhum arquivo de
código, licença ou microdados individuais identificáveis. Não inferimos uma
licença de redistribuição para os CSVs; eles ficaram fora do Git, em
`/private/tmp/ic-empirical-repro-cache/osf/`.

| Arquivo no OSF | SHA-256 do download |
| --- | --- |
| [ESSdataset+calibrated.csv](https://osf.io/download/jbhgf/) | `6b51c8cd535103e5f20b924ac40443f761885cfe2fd4b0204786a4161035feb7` |
| [SHPdataset+calibrated.csv](https://osf.io/download/ayk2g/) | `521124758cf6da52cbc4c940215abe3fc0edf13cb767351e8678283653b0123f` |
| [Simulations.csv](https://osf.io/download/9hruy/) | `195134f179cc173e172840c766b9114e74767bdea5f5c7a80d5d0c5990a45ab4` |

O [auditor de depósito](deposit_audit.py) confere os três hashes antes de ler
as tabelas e emite só contagens e intervalos agregados. Executar a partir deste
diretório:

```sh
python3 deposit_audit.py --cache-dir /private/tmp/ic-empirical-repro-cache/osf
```

O [log da auditoria](run-2026-09-24-deposit.log) registra a execução. O
SHA-256 do script foi
`9d9697ec5428e704f0422f0a2158eb8d3db0008a84acc714a5fce864415900f6`;
o do log foi
`44d74b54f8351b821ab0003fe530a67dc4b62332098a53daa087a8997a49ccc5`.
O CSV ESS contém 1.235 linhas, mas atribui 161 a `trstprt` (partidos) e 179 a
`trstprl` (parlamento), invertendo as duas contagens da Tabela 1 do artigo. O
CSV SHP contém 14 anos (1999–2009, 2011, 2014, 2017) e uma linha adicional
`Based on Micro Data`; seus valores depositados de R² vão de 0,565 a 0,877,
compatíveis com o intervalo arredondado 0,56–0,88 relatado no artigo. O CSV
de simulações contém 44.788 linhas e 4.498 IDs de parâmetros, enquanto o
artigo relata 41.163 saídas estabilizadas. Sem código original e histórico da
seleção, não é possível explicar as duas divergências. Esta auditoria reproduz
apenas o inventário e estatísticas das tabelas depositadas, não recalcula os
ajustes a partir dos microdados ou executa a simulação dos autores.

## Execução

Ambiente executado: macOS 27.0 arm64, Python 3.12.13 da instalação local do
`uv`; somente biblioteca padrão. A partir deste diretório:

```sh
/Users/davi/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 model_probe.py --seed 20230924
```

O comando portátil equivalente é `python3.12 model_probe.py --seed 20230924`.
O [log final](run-2026-09-24-v3.log) guarda o comando e a saída da execução de
24/09/2026. Naquele computador, o cronômetro interno registrou 0,349 s.
A semente fixa o gerador `random` do Python; o tempo pode variar. O SHA-256 de
`model_probe.py` executado foi
`da8e5fafce6006f065c0ecf4488d9c080742e4d6b9966aa7c05d9d568b9ad1c5`.
O SHA-256 do log foi
`6451879fa1a9c97a56fd09d92c715e6fcd553c33eb3a5b2375e6178df0d0e61f`.
Os [logs inicial](run-2026-09-24.log) e
[intermediário](run-2026-09-24-v2.log) permanecem como tentativas anteriores
à correção de estilo e formatação do script; `v3` é o sucessor executado com
o arquivo atual. A saída científica foi igual nas três tentativas.

## Alcance do resultado

Usamos o conjunto de parâmetros da linha “Best Fit” da tabela 3 do artigo:
α=0,25, ρ=0,5, θ=0,1, σ=2, λ=4 e k=2. O artigo usa 800 agentes, pelo menos
1.000 passos e estima cerca de 24 passos por ano para a comparação micro. Esta
sonda faz 1.000 passos fixos, sem implementar o critério de estabilidade,
seguidos de 24 passos. Amostra a fonte entre os demais agentes, atualiza
receptores em ordem aleatória e limita as opiniões a [-0,5; 10,5].

No log, a distribuição final deslocou-se para valores altos (média categórica
6,68) e 580 dos 800 agentes mudaram de categoria nos 24 passos seguintes;
492 permaneceram na mesma categoria ou mudaram uma posição. Isso verifica que
a implementação publicada em equações pode gerar distribuição agregada
deslocada com mudanças individuais sob esses parâmetros. Uma semente e uma
trajetória não estimam a distribuição estacionária ou a variância entre réplicas.
Não reconstruímos a matriz empírica SHP, os 50.008 pares anuais, as 1.235
distribuições ESS, o varrimento de 48.750 simulações, R², D_micro nem a
comparação com e sem cognição motivada. Os números publicados continuam sendo
afirmações do artigo, sem confirmação independente nesta sonda.
