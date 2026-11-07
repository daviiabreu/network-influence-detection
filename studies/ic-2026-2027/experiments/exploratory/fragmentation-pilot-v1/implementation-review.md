# Revisão adversarial da implementação do piloto

Data: 12/09/2026. Estado: dois achados reproduzidos e corrigidos; nenhum achado
acionável permanece aberto no escopo e nos hashes finais abaixo. Esta é evidência
de revisão por agente, não aprovação científica do Research Owner nem validação
dos resultados de uma campanha.

## Escopo e isolamento

A revisão recebeu os três módulos candidatos, testes científicos, especificação
e desenho experimental do protocolo. Seguiu os AGENTS da raiz e do estudo,
`docs/process/research-lifecycle.md`, `docs/process/engineering-validation.md` e a
seção Independent challenge do charter. Não consultou histórico da conversa,
memórias, ranking de propostas, README de recomendações ou justificativa dos
autores. O teste de integração foi acrescentado ao escopo durante a correção.
O coordenador alterou implementação e testes; este revisor escreveu somente este
relatório. Não houve execução de benchmark ou campanha por este revisor.

Foram examinadas correção, fidelidade dos observadores, amostragem, pareamento,
censura e proveniência. A revisão não avalia novidade, prioridade da pergunta,
poder estatístico confirmatório ou reprodução das figuras publicadas.

## Achados e resolução

### R1 — P2: a serialização da especificação mudava as sementes

Local original: `src/ic_study/analysis/fragmentation_pilot.py:56`, em conjunto
com a serialização com `sort_keys=True` na linha 162. A geração usava a posição
do perfil nas chaves de `spec["profiles"]`. O cabeçalho persistido ordenava essas
chaves, mudando a geração ao recarregar sua própria especificação.

Caso reproduzido no candidato original:

```python
spec = json.loads(spec_path.read_text())
roundtrip = json.loads(json.dumps(spec, sort_keys=True))
original = trial_inputs(spec, "pilot")
reloaded = trial_inputs(roundtrip, "pilot")
assert sum(a != b for a, b in zip(original, reloaded)) == 32
```

O perfil `er200` passava de `graph_seed=2027121200` para `2027131200`; os streams
de opiniões e eventos também mudavam. `er100_dense` sofria a troca inversa.
Os inputs completos por linha ainda permitiam repetir uma trajetória, mas
regenerar os inputs a partir de `header["spec"]` já não reproduzia o lote.

Resolução verificada: cada perfil declara `seed_index`, usado explicitamente
na linha 56. Todas as fases produzem inputs idênticos após a serialização
ordenada. O teste
`tests/integration/test_fragmentation_pilot.py:16` cobre esse contrato, as
contagens, o pareamento entre modelos e a reutilização pela sensibilidade.

### R2 — P3: arredondamento podia selecionar uma folha vazia

Local original: `src/ic_study/models/deffuant.py:57–67`. O residual era limitado
à soma da raiz, mas uma subtração podia arredondá-lo para exatamente a soma de
uma subárvore. A comparação estrita seguinte então descia ao preenchimento
vazio, produzindo falha numérica sem peso inválido ou underflow.

Caso reproduzido no candidato original:

```python
sampler = WeightedEdges(6, 0.5)
for i, exponent in enumerate([54, 51, 43, 53, 21, 1]):
    sampler.replace(i, 2.0**-exponent)
sampler.select(math.nextafter(1.0, 0.0))
# ArithmeticError: Weighted selection reached an empty leaf
```

São pesos positivos alcançáveis por decaimento a partir de 0,5. O residual na
subárvore direita era `0.5000004768371582`, igual à soma dela; o algoritmo
chegava à folha de índice 7 para apenas seis arestas. O uniforme extremo torna
esse evento raro; não há evidência de ocorrência em uma campanha. A consequência
era uma interrupção espúria, registrada como `numerical_failure`.

Resolução verificada: a linha 68 limita o residual também na subárvore escolhida.
O caso retorna a aresta 5 e está protegido pelo teste
`tests/scientific/test_fragmentation.py:93`. Uma sondagem adicional percorreu
50.276 uniformes em fronteiras e seus vizinhos representáveis, para 2 a 33
arestas e pesos entre `2**0` e `2**-59`, sem seleção de folha vazia.

## Verificações e limites

O [código primário fixado](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py)
foi conferido diretamente: atualização com as duas opiniões anteriores,
confiança estrita, reforço/decaimento do peso, agenda adaptativa e retenção dos
dois primeiros testes de parada correspondem à implementação local. A árvore
usa outra ordem de soma; não foi alegada igualdade de trajetória com a fonte.

A [equação 31 da versão 2 do artigo](https://arxiv.org/html/2605.20418v2#S5.SS2)
usa diâmetros dos componentes efetivos correntes. A reconstrução local e seu
pré-filtro de diferenças nas arestas são equivalentes a essa condição nos
instantes de observação declarados. Os três critérios compartilham a mesma
trajetória e agenda. A primeira interação receptiva entre grupos declarados é
registrada antes da próxima verificação, preservando eventos transitórios.

Para o certificado, até uma suposta primeira interação externa, cada grupo só
realiza atualizações convexas internas e fica no seu intervalo anterior. Exigir
distância de pelo menos a confiança em cada aresta-base entre intervalos impede
essa primeira interação. O diâmetro abaixo da tolerância, menor que a confiança,
também mantém receptivas as arestas internas. Isso sustenta a lógica do critério
sob as hipóteses declaradas; a margem em float não é prova por aritmética
intervalar de toda a trajetória.

As contagens verificadas foram 10 benchmark, 112 principais, 16 sensibilidade
e 10 controles. Os modelos compartilham grafo, opiniões e stream de uniformes;
pesos diferentes podem selecionar arestas diferentes. A sensibilidade reutiliza
exatamente o subconjunto declarado de inputs principais. As redes ER e modulares
usam as probabilidades de aresta correspondentes aos graus esperados descritos.
O executor preserva inputs completos e usa criação exclusiva; o teste de
integração verificou persistência e recusa de sobrescrita. O resumo distingue
certificação, censura e falha numérica, incluindo paradas sem cruzamento observado
que terminam sem certificação.

Comando executado no escopo final, com resultado **17 testes aprovados**:

```sh
uv run --project studies/ic-2026-2027 --frozen pytest \
  studies/ic-2026-2027/tests/scientific/test_fragmentation.py \
  studies/ic-2026-2027/tests/integration/test_fragmentation_pilot.py -q
```

O candidato original tinha 14 testes científicos aprovados, antes das duas
regressões serem corrigidas. A sondagem adicional usou `random.Random(913)`,
30 vetores por tamanho, expoentes `rng.randrange(0, 60)`, e, para cada soma
acumulada dividida pela raiz, o uniforme e seus dois vizinhos via `nextafter`,
além de 0 e `nextafter(1, 0)`.

Hipóteses não avaliadas: frequência de cruzamentos fora do microcaso, custo do
lote, adequação dos controles observados e utilidade científica do contraste.
Dependem de execução e análise posteriores. A revisão também não transforma
ausência de achados em prova de inexistência de outros defeitos. A agenda só
verifica após eventos receptivos e não observa t=0, conforme especificado; um
estado sem qualquer evento receptivo pode terminar censurado mesmo já separado.

## Vinculação por conteúdo

Base Git observada: `623704c4a7aa3db4fcf4e44f445bbaf6f8e4b34a`, branch `main`.
Os candidatos estavam ainda não versionados durante a revisão; os hashes,
portanto, identificam os bytes revistos, não uma implementação presente nessa
base. Ambiente: Python 3.12.13, Clang 21.1.4,
`macOS-26.6.2-arm64-arm-64bit`, ambiente existente via `uv --frozen`.
Nenhuma dependência foi acrescentada.

Hashes SHA-256 iniciais, relativos a `studies/ic-2026-2027/`:

| Arquivo | SHA-256 inicial |
| --- | --- |
| `src/ic_study/models/deffuant.py` | `a078a916631ee101da949bbb84c98de1a6a40f8bd19b5aa71fbbc55c3c398734` |
| `src/ic_study/simulation/fragmentation.py` | `b299a53dad35f8c00f5ba4d8dd080ca45d591546c180425912bf2dee6e8d5acb` |
| `src/ic_study/analysis/fragmentation_pilot.py` | `0f6e0f2e37aaaf14af733993becd70b1724f9559def7e99649070273ac6bc5dd` |
| `tests/scientific/test_fragmentation.py` | `c6539de2dcbe854b7293d40f5a777254e907fb629f04e0e752f1e3c1736a957a` |
| `experiments/exploratory/fragmentation-pilot-v1/spec.json` | `f18ed55d57a64f8d98056439191333992dc68fb9bb00201384501c65e69ca1e3` |
| `experiments/exploratory/fragmentation-pilot-v1/protocol.md` | `5811b352c68c9ebb57d6072c1a1100f4d14f11831a861b603ae5aaf47b541278` |

Hashes SHA-256 finais revistos:

| Arquivo | SHA-256 final |
| --- | --- |
| `src/ic_study/models/deffuant.py` | `ca2f276645c61cfecbf0ce52ca8a894a98154fe65b24429c0692d3dd2a8e7f4d` |
| `src/ic_study/simulation/fragmentation.py` | `b299a53dad35f8c00f5ba4d8dd080ca45d591546c180425912bf2dee6e8d5acb` |
| `src/ic_study/analysis/fragmentation_pilot.py` | `bd14158e491180f9dc0e8de8a93c0431835e9eb808d33caf5e576468b33beeeb` |
| `tests/scientific/test_fragmentation.py` | `4f952d360dfe1b722675af0dccebac3c1d3d8cd2a01a49c9e6c52dbd3443fc8c` |
| `tests/integration/test_fragmentation_pilot.py` | `4ff53bf93815c0befd8eb86de9a7baf05d7dcd3074ee068d936855491c4a8220` |
| `experiments/exploratory/fragmentation-pilot-v1/spec.json` | `4fc30997b27ee759e69e39e4a922a8c79f2342367cb29a664639bafcb37efe8c` |
| `experiments/exploratory/fragmentation-pilot-v1/protocol.md` | `5811b352c68c9ebb57d6072c1a1100f4d14f11831a861b603ae5aaf47b541278` |
| `pyproject.toml` | `9f4394ce1733048a86d6ce3b1c3d1889ce50fce6b8952b7a0788c5b1b5490007` |
| `uv.lock` | `b68ff2485ea124d94ef5e4df33ae15f1118e0530266bdd1b38221bc6f1835e7c` |

O arquivo primário `EdgeWeightedDW.py` na revisão externa
`5e33664982bda6b7576074ff47772791459ea22c` tem SHA-256
`a2b352c590825a8b4c4491af661ed18772bb8f461f0b5fd54ea3cf0c1db64cae`,
conferido sobre os bytes obtidos diretamente de `raw.githubusercontent.com`.
