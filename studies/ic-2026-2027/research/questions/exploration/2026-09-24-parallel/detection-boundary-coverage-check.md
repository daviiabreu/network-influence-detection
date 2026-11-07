# Checagem bloqueante de cobertura da fronteira de detecção

25/09/2026. Protocolo congelado em `fd65d2a`, SHA-256
`fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706`,
conferido antes de qualquer simulação. Código desta medição: `618cb05` no branch
`research/frozen-coverage-check`; o teste de regressão de N completo foi
commitado em `0f3a018`. Esta é evidência de calibração; não executou
nenhum namespace confirmatório nem libera o experimento confirmatório.

## Escopo e critério

O [protocolo](detection-boundary-preregistration-frozen.md) exige, antes do
confirmatório, 200 repetições independentes em a=0, cobertura de 0,5 em pelo
menos 190/200 bandas em **cada r elegível**, e registro de intervalos binomiais
e falhas numéricas. A decisão do coordenador nesta sessão fixou teto de 24 h
de parede, até oito dos dez núcleos, e meta operacional R=100, ou o maior R
inteiro que caiba nesse teto. Em R=100, o EP de Monte Carlo junto de cobertura
verdadeira 0,95 seria 2,18 pontos percentuais; para EP ≤2,5 pontos junto de
0,95, bastam 76 repetições. Isso não substitui o critério congelado de 200.

A banda congelada toma o máximo |t| das **nove forças G para cada r**. A
cobertura em a=0 é só a estatística relatada, mas seu valor crítico depende das
nove células. Rodar apenas a=0, ou a=0 mais um ponto interior, produziria outro
intervalo. O domínio completo do teste inferencial é, portanto, até 81 células
por repetição, com exclusões de viabilidade registradas antes do treino.

## Custo observado antes da rodada de cobertura

Medições em a=0, r=0,70, família B, N=10.626, onze ondas, máscara e canal
principais, 1.024 realizações de matching, 1.000 redes/classe × dois eventos
para treino, 2.000 redes/classe × dois eventos para referência. O matching usa
L1/L2 observados e alcançou o mesmo ajuste (`ρ=0,8502023151`, `λ=0`) antes e
depois da otimização, em 15 avaliações e 16.384 painéis.

| Componente | Tempo medido | Observação |
| --- | ---: | --- |
| Matching anterior, características completas | 871,28 s | Mesmos seeds e ajuste |
| Matching com só perfil observado | 189,53 s | Ganho 4,60× neste ponto |
| Treino de 4.000 eventos e ajuste da LDA | 72,46 s | LDA propriamente dita <0,001 s |
| Referência de 8.000 eventos | 140,82 s | Duas classes; classe social pode ser compartilhada entre refits |
| Bootstrap em escores fixos | 15,70 s | 2.000 draws, nove forças, 2.000 redes/classe; escores sintéticos só para custo |
| Banda logit | 0,006 s | Sobre os mesmos draws sintéticos |
| 40 refits científicos, oito processos | 1.651,63 s de parede | 26 completos; 14 falharam no matching L1/L2 |

No probe de 40 refits em `refit-cost-r070/`, cada bloco tentou novo matching e
treino em sementes próprias e gerou novamente o nulo na referência fixa. Gerar
uma vez a classe social dessa referência levou 99,78 s. Nos 26 blocos válidos,
as médias por processo foram 187,37 s de matching, 90,73 s de treino e 52,69 s
de avaliação da referência nula. **14/40 falharam** com
`Joint observed matching cannot meet both tolerances` (blocos 1, 6, 13, 14,
15, 20, 26, 27, 28, 32, 35, 36, 39 e 40). Não se completou a variância de
nuisance de 40 refits. Os tempos dos blocos falhos não foram cronometrados
individualmente; estão incluídos no tempo de parede do conjunto.
O intervalo de Wilson de 95% para a proporção de falhas deste probe é
22,1%–50,5%; não é uma taxa estimada para toda a grade.

## Ponto interior pré-escolhido

Em a=0,30 e r=0,70, uma corrida independente de calibração usou 1.024 painéis
para matching, 2.000 eventos/classe para treino e **20.000 redes/classe × dois
eventos** para uma referência separada. O ajuste B foi `ρ=0,8405660` e
`λ=0,3482420`. A AUC de referência do discriminador treinado nessa corrida
foi **0,943912**, com EP de Monte Carlo **0,000724** por 199 reamostragens de
redes e percentis 95% `0,942385–0,945276`. É uma aproximação de alta precisão
à AUC condicionada a esse ajuste/treino, não a verdade média sobre novos
ajustes. Matching levou 85,23 s, treino 50,74 s e referência 986,72 s; total
1.123,70 s (18,73 min), 95.264 painéis. Como não houve repetições completas da
inferência congelada nessa célula, a cobertura fora do nulo segue não estimada.

## Projeção e decisão operacional

Multiplicar os 1.651,63 s medidos deste ponto por 81 células dá 37,16 h de
parede para os refits de **uma** repetição da banda da família B, antes do
ajuste/treino/teste basais e bootstrap. R=100 exigiria aproximadamente 3.716 h
(155 dias), se cada célula custasse o mesmo. A variabilidade entre células e
novos ganhos de cache alterariam a conta; esta não é uma medição da grade. Sob
o teto atual, R completo concluído é 0 e o R máximo projetado é 0. O próprio
probe teve 14 falhas: mesmo com mais CPU não produziria a banda congelada.

Uma passada confirmatória B na grade primária, sem repetição de cobertura,
tem o mesmo termo dominante, aproximadamente 37,16 h em oito processos neste
regime medido.
As famílias B, D e E têm matching de dois momentos, treino e refits separados;
escalar proporcionalmente esse termo para as três dá aproximadamente 111,5 h
(4,6 dias), antes de A, C, controles e sensibilidades. É projeção, não
tempo medido das outras famílias. A execução confirmatória completa excede a
ordem de três dias nesta máquina sob esse plano; não foi iniciada.

Reduções sem mudar o desenho congelado: o caminho NumPy que calcula somente o
perfil observado reduziu o tempo de painel social de 0,0600 para 0,0174 s
(3,45×) e nulo de 0,0392 para 0,0105 s (3,74×), preservando os bytes testados
em sementes de calibração. Em a=0, o gerador agora evita construir a rede e
calcular o drift que é multiplicado por zero; o SHA-256 do painel de teste
permaneceu idêntico. Reutilizar as características sociais da referência entre
os 40 refits economiza aproximadamente metade desta etapa (até 1,21× no refit
inteiro pela conta acima). Oito processos dão no máximo 8× no tempo de parede;
o probe mede a perda por contenção. Vetorização em lotes de painéis, mantendo
RNG, ordenação e arredondamento idênticos, pode ser estudada, mas ainda não há
speedup verificado. Um host Linux alcançável por SSH expôs quatro CPUs em
consulta somente de leitura; um shard adicional desse porte elevaria o teto
ideal de oito para doze núcleos (até 1,5×), sem fechar nem R=1 em 24 h na
projeção: o termo de 37,16 h cairia só para 24,77 h antes do basal. Nenhum
shard remoto foi executado.

## Resultado e próximo passo

**FAILED como gate operacional e numérico; cobertura estatística não estimada.**
R completo executado foi 0; sob o teto de 24 h, R completo projetado é 0.
Cobertura de 0,5, EP de
Monte Carlo, taxa de falso positivo do gate, largura das bandas e cobertura no
ponto interior são indefinidos, e não zero. Não houve corrida confirmatória.
Mesmo R=100 concluído não atenderia literalmente a exigência congelada de
190/200 sem emenda.

Há uma segunda ressalva à hipótese de verdade 0,5: em a=0 o gerador de
reorganização transporta postos normais a cada onda, enquanto B gera AR
gaussiano estacionário e só ajusta L1/L2. Essas leis se aproximam, mas o código
não prova igualdade exata para N finito. Isso é uma inferência da implementação,
não uma estimativa da AUC populacional; os AUCs dos 26 refits válidos não
substituem uma referência independente nem permitem estimar cobertura após a
seleção por sucesso numérico.

**Emenda sucessora proposta, não adotada:** antes de novos contrastes, fixar uma
referência independente grande para a AUC nula de B em a=0 e testar separadamente
um nulo de lei exatamente igual em ambos os rótulos para validar a mecânica da
banda. Corrigir de forma pré-declarada o problema de matching na borda λ=0
(por exemplo, nova família nula com o mesmo transporte de postos e um ajuste
constrangido auditável), mantendo falhas de alcance explícitas, e validar esse
sucessor com novas sementes. Para custo, provisionar shards suficientes para
200 repetições da inferência corrigida ou definir outra inferência viável com
novo hash e gate de cobertura próprio. Qualquer alteração exige medir novamente
o custo e a cobertura antes do confirmatório. Uma banda pontual de a=0, a
exclusão dos 14 refits falhos ou a redução silenciosa dos 40 refits não
certificam a banda congelada. A versão congelada permanece intacta.

Saídas brutas e tempos: diretório privado
`/Users/davi/.local/state/research-workbench/coverage-check-20260925/`.
O manifesto SHA-256 nesse diretório vincula os JSON e JSONL da medição. Sementes
usadas: `ic-detection-boundary-v3-calibration` para os benchmarks e
`ic-detection-boundary-v3-coverage-r0000-calibration` para o probe de refits;
`ic-detection-boundary-v3-coverage-r9999-calibration` para a referência interior;
o bloco de referência permanece 0 e os refits usam blocos 1…40. Não houve uso
de sementes `-confirmatory`. Uma auditoria de 4.031.616 materiais de semente desses
dois namespaces encontrou zero colisões de 64 bits.

O arquivo privado `manifest.sha256` lista os 12 arquivos brutos e passou em
`shasum -a 256 -c manifest.sha256`; SHA-256 do próprio manifesto:
`0ef2347944a09b0364936eedd5c23d209a8f37c2ff62e7659a3e0c2fa8b25eff`.
Diretórios e arquivos do pacote privado estão em modos `0700` e `0600`.

Verificação: TDD para o caminho observado e para o probe; 37 testes focados
passaram, Ruff e mypy passaram em 24 arquivos do pacote, e
`scripts/check_repository.py` passou nos sete checks com
`UV_CACHE_DIR=/private/tmp/uv-cache-cov` antes dos commits. O painel a=0 com
N=10.626 conservou SHA-256
`0bd67064acd8f37153373d67f69952f7f6ebd9f6cbeac05048761112e3900602`
antes e depois da otimização.
