# Reprodutibilidade e proveniência

Esta é uma extração do compêndio em `studies/ic-2026-2027/` no commit
`cbf7d721` do histórico privado de `research-workbench`. O repositório novo
começa uma história de manutenção própria. Os commits, assinaturas, aprovações
e hashes históricos continuam identificando seus objetos originais; não foram
reassinados nem convertidos em evidência sobre o novo repositório.

Os caminhos do estudo foram preservados para que protocolos, especificações,
registros congelados e fontes editoriais conservem seus identificadores.
O mapa de extração do proprietário registra os arquivos selecionados, omitidos
e adaptados. A cópia privada do histórico original e seus backups continuam
sendo necessários para verificações que dependem de objetos Git antigos.

## O que pode ser reproduzido sem dados externos

`uv sync --locked --group dev`, executado em `studies/ic-2026-2027/`, instala
o pacote científico com Python 3.12. `just quality` verifica estrutura, lint,
tipos, testes herméticos com casos reduzidos e fixtures sintéticas e a
instalação do wheel fora do checkout. Os comandos não executam workflows de
agentes, providers, experimentos completos ou replay dos resultados reais.

As fontes de `publications/jcss-journal/` podem ser compiladas e conferidas com
um toolchain editorial externo. O [guia do toolchain](publication-toolchain.md)
define os requisitos. Compilação e testes de empacotamento verificam a entrega
editorial; não refazem a análise que originou os números publicados.

## O que continua externo

Os microdados SHP dependem de acesso e licença próprios. Bytes de raw,
interim, processed, conteúdo protegido, holdouts privados, sealed runs,
credenciais e coordenação privada não são distribuídos. Os manifests e hashes
registrados no estudo indicam a identidade esperada; eles não fornecem acesso
aos bytes e não demonstram que um replay tenha sido executado nesta extração.

As instalações históricas sob `.local/state/research-workbench/` e os caminhos
Nix citados em fontes congeladas descrevem o ambiente de origem. Não são uma
dependência do wheel nem autorização para ler ou modificar esses locais.
Código científico antigo continua aceitando entradas explícitas nas interfaces
que as oferecem; alterações futuras de portabilidade devem preservar as fontes
congeladas ou criar um sucessor documentado.

Os coordenadores e contratos históricos específicos do IC, as aprovações
privadas e o histórico de agentes permanecem apenas na preservação privada do
monorepo original. Não são dependências deste compêndio público. Sua reprodução
exige o checkout original, a versão correspondente do framework e as
autorizações e entradas originais. Não foram executados nesta extração.

## Evidência e licenças

Resultados e afirmações numéricas continuam vinculados às fontes e recibos
históricos apontados pelas publicações. Uma validação de engenharia atual não
substitui os gates científicos, a licença de um dado, uma decisão ética ou uma
aprovação de submissão. Uma nova execução precisa gerar seu próprio manifesto
com código, ambiente, entradas, parâmetros, sementes e estado de validação.

As licenças MIT e CC BY 4.0 declaradas em bundles anteriores valem para o
escopo declarado nesses bundles. A extração não concede uma licença geral a
textos de terceiros, templates Springer, dados SHP ou snapshots de fontes.
Consulte a [seleção de divulgação](publication-selection.md) antes de publicar.
