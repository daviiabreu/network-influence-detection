# Reprodução limitada de antecedentes e controles de mecanismo

Execução exploratória em 24/09/2026, no branch `research/mechanism-leads-reproduction`.
O desenho inicial está em `protocol.md`; `protocol-v2.md` corrige a calibração
estática e `protocol-v3.md` torna o par projetado uma soma independente por
arestas. As saídas anteriores permanecem para auditoria. Resultados usados na
interpretação: `antecedents-results-v2.json`, `controls-results-v3.json`,
`thompsky-proxy-results.json`, `thompsky-authors-results.json`,
`thompsky-authors-figure2-results.json` e `summary-v3.json`. Nenhuma execução é
validação registrada ou aprovação do Research Owner.

## Proveniência e ambiente

O [ZIP público de Dong](https://zenodo.org/records/21820152) foi encontrado no
cache privado preexistente `/private/tmp/dong-code.7AcOo5/Code_Public.zip`.
URL de aquisição declarada pelo registro:
`https://zenodo.org/api/records/21820152/files/Code_Public.zip/content`.
SHA-256 conferido antes da extração:
`57afbe543032e2138c23622f81ed48b72b37310e4f4c2ef14594e7cb3c9ad4ae`.
O MD5 `c60491c6c820d9c2890631751988df87` coincide com o anunciado pelo
Zenodo.
O download novo foi tentado e falhou com `Could not resolve host: zenodo.org`.
O ZIP foi extraído apenas em `/private/tmp/ic-mechanism-antecedents-20260924/dong`
com `bsdtar --no-same-owner --no-same-permissions`; não há código dos autores
em Git. A [API do registro](https://zenodo.org/api/records/21820152) informa
`metadata.license.id = cc-by-4.0` (consulta de 24/09/2026; SHA-256 do JSON
recebido `b36aa1337ee76ff49c96dbb64055e537dc5f310a2b9e527c70b2fd9c850e7975`).
O ZIP não contém arquivo `LICENSE` separado. A execução foi local.
Os dados Reddit declarados no depósito não estão no ZIP.

O [commit público de Thompsky](https://github.com/Yolandayx929/adaptive-edge-BCM/tree/5e33664982bda6b7576074ff47772791459ea22c)
falhou inicialmente por DNS e foi obtido depois em
`/private/tmp/ic-thompsky-authors-20260924`, fora de Git. `run_thompsky_proxy.py`
chama apenas o kernel escalar do estudo. `run_thompsky_authors.py` executa a
função `DW` dos autores a partir de `EdgeWeightedDW.py` após conferir o SHA-256
`a2b352c590825a8b4c4491af661ed18772bb8f461f0b5fd54ea3cf0c1db64cae`.
O carregador omite em memória uma única importação de `scipy.io/stats`, não usada
pela função, porque a instalação local de SciPy falha ao carregar `_spropack`.
Nenhum outro trecho da função foi alterado. As verificações de
[Abedinzadeh–Akyol](https://arxiv.org/html/2603.21081)
e [Neuhäuser et al.](https://arxiv.org/html/1910.09226v1) são implementações
independentes de casos pequenos das equações acessíveis.

Host: macOS arm64, Python 3.12.13 para estudo/controles, `uv 0.10.9`; Python
3.10.20, NumPy 2.2.6 e PyTorch 2.13.0 para Dong. O projeto do estudo está
travado pelo seu `uv.lock`, sem dependências científicas adicionais. Neste
worktree isolado, a sandbox impediu escrever no cache uv padrão; os comandos
abaixo usam o ambiente travado já instalado no checkout principal somente para
leitura, `UV_NO_SYNC=1` e um cache novo em `/private/tmp`. `PYTHONPATH=src`
garante que o código científico venha deste worktree. Os dois `uv.lock`
foram comparados byte a byte (`cmp`, saída 0); `UV_NO_SYNC=1` ainda pressupõe
que o ambiente previamente instalado corresponde ao lock.

Para Thompsky, a função dos autores foi executada com Python 3.10.20,
NumPy 2.2.6, python-igraph 0.11.4, pandas 2.3.3, SciPy 1.15.3,
matplotlib 3.10.9 e seaborn 0.13.2. As dependências auxiliares ficaram em
`/private/tmp/ic-thompsky-run-env`; o código dos autores, fora do projeto.
As versões diferem das declaradas no README dos autores e limitam a
reprodução exata.

## Comandos exatos

Executar a partir de `studies/ic-2026-2027/`. Escolher caminhos de saída novos:
os scripts abrem JSON com modo exclusivo e recusam sobrescrever uma execução.

```sh
UV=/Users/davi/.local/bin/uv
export UV_PROJECT_ENVIRONMENT=/Users/davi/Documents/github/research-workbench/studies/ic-2026-2027/.venv
export UV_NO_SYNC=1 UV_CACHE_DIR=/private/tmp/ic-mechanism-uv-cache PYTHONPATH=src
$UV run --locked pytest tests/scientific/test_mechanism_controls.py -q
$UV run --locked ruff check .
$UV run --locked mypy src tests
$UV run --locked python experiments/exploratory/antecedent-reproduction-mechanisms/run_controls.py experiments/exploratory/antecedent-reproduction-mechanisms/controls-results-v3.json
$UV run --locked python experiments/exploratory/antecedent-reproduction-mechanisms/run_thompsky_proxy.py experiments/exploratory/antecedent-reproduction-mechanisms/thompsky-proxy-results.json
PYTHONDONTWRITEBYTECODE=1 /Users/davi/Documents/github/inteli/inteli-projects/m11/g02/src/.venv/bin/python experiments/exploratory/antecedent-reproduction-mechanisms/run_antecedents.py experiments/exploratory/antecedent-reproduction-mechanisms/antecedents-results-v2.json --dong-cache /private/tmp/ic-mechanism-antecedents-20260924/dong
$UV run --locked python experiments/exploratory/antecedent-reproduction-mechanisms/summarize.py experiments/exploratory/antecedent-reproduction-mechanisms experiments/exploratory/antecedent-reproduction-mechanisms/summary-v3.json
```

Execução posterior com a função `DW` dos autores, a partir da raiz do
repositório. O primeiro JSON usa `gamma=delta=0,5`; o segundo seleciona
`gamma=delta=0,1`, correspondente ao painel da Figura 2 do artigo. Para
reexecutar, usar um diretório temporário e nomes de saída novos:

```sh
git clone https://github.com/Yolandayx929/adaptive-edge-BCM.git /private/tmp/ic-thompsky-authors-20260924
git -C /private/tmp/ic-thompsky-authors-20260924 rev-parse HEAD
UV_CACHE_DIR=/private/tmp/ic-thompsky-uv-cache /Users/davi/.local/bin/uv venv --python /Users/davi/Documents/github/inteli/inteli-projects/m11/g02/src/.venv/bin/python --system-site-packages /private/tmp/ic-thompsky-run-env
UV_CACHE_DIR=/private/tmp/ic-thompsky-uv-cache /Users/davi/.local/bin/uv pip install --python /private/tmp/ic-thompsky-run-env/bin/python 'python-igraph==0.11.4' 'pandas==2.3.3' 'seaborn==0.13.2'
PYTHONPATH=/private/tmp/ic-thompsky-run-env/lib/python3.10/site-packages XDG_CACHE_HOME=/private/tmp/ic-thompsky-xdg MPLCONFIGDIR=/private/tmp/ic-thompsky-mpl PYTHONDONTWRITEBYTECODE=1 /Users/davi/Documents/github/inteli/inteli-projects/m11/g02/src/.venv/bin/python studies/ic-2026-2027/experiments/exploratory/antecedent-reproduction-mechanisms/run_thompsky_authors.py studies/ic-2026-2027/experiments/exploratory/antecedent-reproduction-mechanisms/thompsky-authors-figure2-results.json --author-source /private/tmp/ic-thompsky-authors-20260924/EdgeWeightedDW.py --gamma 0.1 --delta 0.1
```

O script recusa SHA diferente e saída já existente. Usa grafo completo de 100
nós, 20 sementes 101–120, opiniões iniciais uniformes em `[0,1]`, mesma
condição inicial e semente de sorteio de arestas por par de braços, `mu=0,3`,
`tol=0,01`, `Tmax=10^8`, `z0=0,1` adaptativo e baseline
`(gamma,delta,z0)=(0,1,0,5)`. Foram comparados `c={0,1; 0,2; 0,3; 0,5}`.
São células exploratórias selecionadas após o acesso ao artigo, não sua grade
integral.

Para preparar o cache privado a partir de um ZIP adquirido legitimamente e
conferido, copiar `Code_Public.zip` ao diretório `dong/` e executar:

```sh
bsdtar --no-same-owner --no-same-permissions -xf /private/tmp/ic-mechanism-antecedents-20260924/dong/Code_Public.zip -C /private/tmp/ic-mechanism-antecedents-20260924/dong
shasum -a 256 /private/tmp/ic-mechanism-antecedents-20260924/dong/Code_Public.zip
```

Sementes e todos os parâmetros estão congelados nos protocolos. `K=1` na
execução válida de Dong; a primeira saída usou o default `K=0,3` e é inválida
para o limiar que havia calculado. `run_antecedents.py` verifica o SHA-256 do
arquivo antes de importar o código externo.

## Saídas e custo medido

| Arquivo | SHA-256 |
| --- | --- |
| `antecedents-results.json` (falha de `K`) | `7c0dc23dc258a67966d9de89f80af76d4c4743ba9e74b379f1c22ac52e8e77ff` |
| `antecedents-results-v2.json` | `aceab733480b90c6f6c23ad00b812ad2644717bb6edd4a53161d8154fc821004` |
| `controls-results.json` (calibração inicial) | `2a1018daf19af1008c129749aa521a14de2987b1378824947073d33272afa91a` |
| `controls-results-v2.json` | `8b483eece31ae97bd80e1eb5904370157178eb6eceb4e180db9b0a07ae4536f7` |
| `controls-results-v3.json` | `881eea1150d37557d8320496396edccc510c708f1dc36f24417cddce2702eeb5` |
| `thompsky-proxy-results.json` | `27c74e08abe50f57bd6b778ba11d0c9abe3a6fd4840f0d60e1bb50b4fa1bdcc4` |
| `thompsky-authors-results.json` (`gamma=delta=0,5`) | `b3b2bb78afd4b1144b15167daf697c42382edcc4afee459ce585ea65d0954853` |
| `thompsky-authors-figure2-results.json` (`gamma=delta=0,1`) | `03d4b9a4a1d69c4d1d9c5350ebf3f6a8dbdfcf6f087e4be436eb9fdb0128cb18` |
| `summary-v3.json` | `021d1713792148e654cd0615e6f4765ed9255fb3aae039c59edcae9e2b21d79e` |

No lote final, mediana por réplica: pares 0,22–0,37 ms, trios 0,14–0,17 ms,
proxy Thompsky 0,40–2,01 ms, Dong 38,7–43,0 ms (apenas chamada `model.run`,
sem importação). `run_antecedents.py` levou 0,99 s no total; todo o lote ficou
amplamente abaixo de 30 min. Esses custos em `N≤40` não projetam o custo
das figuras publicadas (`N=100–1000`, grades, sementes e dados empíricos).
O subconjunto com código dos autores levou 22,26 s nas 160 chamadas `DW`,
sem contar importação; todas terminaram sem bailout. A Figura 2 usa 20
condições iniciais, mas nossa amostra de sementes não coincide com a dos
autores. Não foram reexecutadas as Figuras 3–4 nem a grade completa da Figura 2.

Os resultados numéricos e as discrepâncias frente às fontes primárias estão
no [memo de interpretação](../../../research/questions/exploration/2026-09-24-parallel/mechanism-reproduction-and-controls.md).
