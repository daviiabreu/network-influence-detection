# Limits of Detecting Network Influence in Attitude Panels

Compêndio científico do artigo sobre detecção de influência em redes: código,
protocolos, especificações de experimentos, registros de evidência e publicações.
O conteúdo foi extraído do histórico privado de `research-workbench`, no commit
`cbf7d721`, sem reexecutar experimentos ou alterar resultados científicos.

O estudo permanece em [`studies/ic-2026-2027/`](studies/ic-2026-2027/) para
preservar os caminhos usados pelos registros congelados. Ele tem seu próprio
`pyproject.toml`, `uv.lock`, ambiente e pacote `ic_study`. O framework de
orquestração não faz parte deste repositório e não é dependência do pacote.

Leia a [arquitetura](docs/architecture.md), a
[reprodutibilidade e proveniência](docs/reproducibility.md) e a
[política de validação](docs/process/engineering-validation.md).

Com Python 3.12, [uv](https://docs.astral.sh/uv/), `just` e ShellCheck no `PATH`:

```sh
just sync
just quality
```

`just quality` verifica a estrutura, lint, tipos, a suíte hermética e o wheel
instalado em um ambiente descartável. A suíte usa casos reduzidos e fixtures
sintéticas; os gates que dependem de estado externo ou de replay científico
ficam explicitamente fora dela. Os limites estão documentados na política de
validação. Sem `just`, as mesmas operações estão nas receitas do `justfile`.

A versão editorial atual está em
[`publications/jcss-journal/`](studies/ic-2026-2027/publications/jcss-journal/).
As publicações anteriores e as regras congeladas permanecem no estudo com sua
linhagem. A compilação editorial usa dependências externas configuráveis;
consulte [como obter e configurar o toolchain](docs/publication-toolchain.md).
Compilar o texto não constitui submissão, aceite científico ou aprovação ética.

Dados licenciados, textos restritos, estado de execução e credenciais ficam fora
do Git. O escopo público e os limites de licença estão descritos na
[seleção da extração](docs/publication-selection.md).

## Origem e estrutura de pesquisa

O [mapa de origem](provenance/origin-map.json) relaciona os arquivos desta
seleção à revisão original, sem publicar o histórico privado de preparação.
A infraestrutura agêntica reutilizável está no repositório privado
[`research-workflows`](https://github.com/daviiabreu/research-workflows);
ela não é necessária para instalar ou validar este compêndio.
