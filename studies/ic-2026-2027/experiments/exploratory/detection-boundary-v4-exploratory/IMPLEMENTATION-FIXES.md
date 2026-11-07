# Correções sucessoras de X3–X7

Esta implementação corrige o review de `67d7789c`. A declaração registrada em
`85cdb8f2`, suas sementes, tamanhos e regras científicas permanecem imutáveis.
A execução em tamanho declarado exige novas pré-condições no commit final por
classe de host. Os testes locais usam dados sintéticos e não liberam resultados.

## Proveniência e compatibilidade

Uma execução nova vincula seu diretório a `run-manifest.json` e a um
`manifest-<kind>.json` por análise. O runner confere o manifesto antes de procurar
unidades reutilizáveis; cada registro vincula a identidade, tamanhos, commit,
hashes sucessores, classe de host e digests das verificações. Diretórios antigos
não podem ser retomados pelo runner corrigido. A agregação de uma execução nova
pode ocorrer em outro host, mas exige o mesmo código e valida a classe de host
original dos registros contra o manifesto.

Os agregadores de X5 e X7 reconhecem exclusivamente os registros sem manifesto
produzidos no commit completo `c8e4861fdba24700d3ca802e337f81f103d65c57`.
`compatibility-c8e4861f.json` fixa os hashes extraídos dos blobs Git desse commit,
incluindo declaração, lockfile, freeze e módulos produtores. O diretório de entrada
deve conter também `<kind>-precondition.json` original, cujo digest precisa ser o
registrado nas células. Além de `passed`, todos os campos independentes de
igualdade, proveniência e erros são conferidos; o falso positivo do verificador
antigo não é aceito. Identidades são reconstruídas da grade declarada. Registros
X7 com desfecho rico desconhecido são recusados, sem refazer simulações.

Esse caminho é automático somente nessa combinação exata e exclusivamente na
agregação. Usa-se o comando `aggregate` habitual; X7 continua exigindo liberação.
O agregado inclui `compatibility.mode = aggregate-only`, o commit original e o
código agregador. Não reescreve registros históricos nem gera um manifesto novo
para legitimá-los. X5 e X7 aceitam um único `--out`, inclusive nesse caminho
legado. A existência e validade dos outputs reais serão verificadas pelo
coordenador após a liberação; nenhum deles foi inspecionado nesta correção.

## União de hosts na agregação

X3, X4 e X6 aceitam `--out` repetido. Cada diretório é validado sozinho contra
seus manifestos, verificações e identidades, antes da união dos registros.
Um índice presente em mais de um diretório é recusado, mesmo se algum registro
terminou depois do corte. Commit, lockfile, sucessor, sementes, janela, tamanhos,
total e identidades devem coincidir. Classes de host e digests das verificações
podem diferir; os registros continuam vinculados à proveniência de sua origem.
Diretórios sem manifesto são recusados fora da compatibilidade legada de X5/X7.

Só as unidades ausentes ou tardias da união são incompletas. Isso permite que
X6a alcance o mínimo de 100 repetições completas juntando shards de vários
hosts. O agregado inclui em `sources` o SHA-256 de cada `run-manifest.json`,
a classe de host e a contagem de unidades aceitas daquele diretório, somada
entre os kinds quando houver mais de um. Nenhuma estatística vai para os logs.

## Solver de X3

Após uma secante degenerada, a busca sonda extremos ainda não visitados e depois
bissecta o maior intervalo não examinado, sempre dentro das 12 avaliações.
Resíduos com o mesmo sinal em amostras finitas não demonstram ausência de raiz
sem uma hipótese adicional de monotonicidade. Por isso a ausência de bracket
termina em `budget`; `family-limit` exige um domínio reduzido a um ponto cujo
resíduo exceda a tolerância. Essa decisão evita atribuir ao modelo uma limitação
que a busca numérica não demonstrou.

## Cobertura e retomada

Em X6a, a unidade inteira define a elegibilidade pontual e conjunta. Contagens
por célula continuam disponíveis como descrição. Lacunas entram como misses na
leitura secundária, mas não no mínimo de 100 completos. O mesmo mínimo condiciona
a classificação de viés. Quando a sensibilidade de `T_D1 ± 2 EP` muda a conclusão,
a leitura efetiva fica inconclusiva e a classificação nominal permanece explícita;
a regra vale também para misses secundários, a classificação conservadora e viés
padronizado.
Quando o EP de T_D1 não é estimável, as leituras de cobertura e viés ficam
inconclusivas; as médias descritivas permanecem disponíveis, e EP desconhecido
não vira zero nas estatísticas do componente de matching.

Em X7, `outcome.json` torna durável o erro terminal rico antes do resultado
congelado. A retomada repara selos pendentes e preserva o erro, sem uma nova
tentativa oportunista. Um resultado rico antigo completo permite reconstruir
um desfecho conhecido; ausência de resultado e de desfecho não permite supor
sucesso. Os agregados conferem os selos dos stores usados contra os registros.

## Corte operacional

Os comandos CLI `run` e `precondition` executam em um grupo de processos filho,
supervisionado até `2026-10-10T02:59:00Z`. No corte, o supervisor termina o grupo,
preserva checkpoints já publicados e grava um recibo `operational/cutoff-*.json`,
com status incompleto e `scientific_failure = false`; retorna 124. Isso também
cobre os treinos de `T_pop` e não depende do alarme usado pelo executor congelado.
O flag interno `--deadline-worker` pertence ao supervisor e não deve ser usado
em lançamentos manuais. Chamadas Python diretas são infraestrutura interna;
execuções declaradas usam o CLI supervisionado. O filtro temporal dos agregados
continua excluindo unidades concluídas fora da janela.

## Ordem e barreiras de execução

Cada worker percorre os estágios selecionados na ordem fixa
`X5 → X7 → X3 → X4a → X4b → X6a → X6b`, independentemente da ordem dos módulos
fornecidos ou de `STAGES`. Só executa estágios dos módulos passados ao launcher.
`ONLY` filtra unidades com ou sem shards. Se um estágio falhar, aquele worker
registra o código em `logs/worker-<k>.status` e para; os demais continuam.
O script espera todos e devolve o primeiro código não zero na ordem dos workers.

Não há barreira local nem entre hosts. Com shards globais estáticos, a unidade
`i` só pode ser executada pelo worker do shard `i mod SHARD_TOTAL`. Uma barreira
não transfere computação para análises anteriores: apenas deixa threads ociosas.
Sem barreira, cada estágio termina no mesmo instante ou antes do que terminaria
com barreira, por indução sobre os estágios. A prioridade registrada vale se a
capacidade faltar e é preservada pela sequência fixa de cada worker. Sem shards,
a fila compartilhada do host aproveita a capacidade disponível e não começa
uma unidade posterior enquanto houver unidade anterior ainda não reivindicada.

Uma barreira entre hosts exigiria um coordenador vivo por dias transportando
recibos por um túnel frágil. Também impediria o launch-2 de X3 em hosts divididos:
o desenho anterior exigia recibos de X5 e X7 nos 64 shards, mas ambas as análises
já terminaram em `c8e4861f`, sem esses recibos. Os comandos e os arquivos de
recibos de estágio foram removidos; `STAGES` seleciona um subconjunto e nunca
reordena os estágios.

## Leituras de X4 e X7

Em X4b, calibração liberal ou ausente suspende a classificação e a contagem de
perda de poder. Taxas e diferenças permanecem no agregado; `quantity` identifica
taxa de rejeição, poder ou limite inferior de poder quando conservador.

Em X7, cada regra consulta somente as quantidades necessárias: o contraste por
intervalo usa o ponto congelado e o intervalo rico; o contraste por diferenças
e a equivalência usam os dois pontos e seus deltas. Censura da fronteira
sustentada continua registrada separadamente, sem censurar a primeira travessia.
