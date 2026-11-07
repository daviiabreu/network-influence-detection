# Análises exploratórias sucessoras da v4: gêmeo de campo médio e mapa de R² da deriva

Declaração de 28/09/2026. Registrada antes da implementação e da execução, e antes de qualquer resultado confirmatório: o gate v4 está em execução e nenhum tier começou. As duas análises são exploratórias e rotuladas assim. Não mudam o protocolo congelado (`../detection-boundary-v4/freeze-v4.json`, commit `37513841`), a grade, os alvos, os nulos, o discriminador, as bandas, a censura, os gates ou a ordem dos tiers, e nenhum resultado delas pode ser promovido a evidência confirmatória. O [JSON](declaration.json) traz a mesma especificação em forma legível por máquina.

## Motivo

O parecer adversarial interno de 28/09/2026 (`publications/jcss-manuscript/pipeline/review/referee-report-2026-09-28.md`, itens R1-M1, R1-M3 e mudanças 4 e 5 da lista ordenada) aponta que, com oito parceiros sorteados por permutação uniforme e transporte por postos a cada passo, a deriva de interação é, em primeira ordem, uma função não linear do próprio estado da pessoa mais ruído. O discriminador fixo pode então separar o braço de interação de B por persistência não gaussiana, e não por algo especificamente social. O parecer também nota que o mapa de R² parcial da deriva, prometido na v1 ("Mecanismos e significado de a"), não existe no código congelado.

## X1: gêmeo de campo médio

Pergunta: a estrutura da rede acrescenta algo que o discriminador fixo enxerga, além do componente de campo médio da deriva?

O gêmeo é idêntico ao braço de interação congelado (`models/detection_panel_v4.py:influence` com `models/detection_panel.py:influence_update`) em tudo, exceto na deriva. Ficam iguais a geometria, o AR com ρ = 0,85, a mistura da inovação pela fração nominal `a`, o kernel `f(g) = g` se `|g| ≤ 1` e `f(g) = −b·g` fora disso (b = 0,25), a padronização da deriva a cada passo, o transporte por postos, os passos por onda e a ancoragem. A deriva da rede, `D_i = (1/8) Σ_k f(z_{π_k(i)} − z_i)` com parceiros fixos por painel, é trocada por `D_i^MF = m(z_i) + ξ_i √(v(z_i)/8)`.

Os termos do gêmeo são estes:

- `m(z) = (1/N) Σ_j f(z_j − z)`, calculado exatamente sobre o estado corrente da população, com somas acumuladas sobre os estados ordenados;
- `v(z) = (1/N) Σ_j f(z_j − z)² − m(z)²`;
- `ξ_i` é normal padrão, independente entre pessoas e renovada a cada passo.

Depois disso, `D^MF` passa pela mesma padronização e entra na mesma atualização.

O contraste entre o braço e o gêmeo junta dois efeitos da rede: a autocorrelação temporal do desvio da deriva, que vem dos parceiros persistentes, e as covariâncias entre pessoas ligadas.

**X1a (principal).** Em cada célula `(a, r)` com `a ∈ G \ {0}` e `r ∈ R`, que são 72 células:

- geram-se painéis do braço e do gêmeo com a geometria SHP e o canal observado da camada 1;
- extraem-se as features congeladas (defasagens 3 a 5, as colunas 2:5 do perfil);
- treina-se a LDA congelada (`analysis/redesign.py:fit_discriminant`) com 2.000 painéis de treino por braço;
- calcula-se a AUC congelada (`analysis/detection_boundary.py:auc`, empates pela metade) numa referência de 2.000 redes com dois eventos por braço, os tamanhos da D1.

O intervalo é um bootstrap percentil de 95% com 1.000 reamostragens das redes de referência. Relatar também, por célula, as médias de L1 a L5 de cada braço e suas diferenças.

Leitura declarada: uma célula cujo intervalo exclui 0,5 indica que a rede acrescenta informação separável para a LDA fixa naquela célula. Um intervalo que contém 0,5 não prova ausência de efeito da rede. Não há correção para multiplicidade nem afirmação sobre a curva inteira.

**X1b (segundo estágio, opcional).** Estima a fronteira do gêmeo contra B, `a*_MF(r)`, pelas regras congeladas de ajuste, validação, discriminação, bandas e inversão. Condições:

- um pipeline sucessor que reutiliza os componentes congelados e troca só o gerador social;
- esse pipeline precisa reproduzir bit a bit, com o gerador original, as saídas do pipeline congelado em pelo menos duas células antes de qualquer uso.

Se essa verificação falhar, X1b não roda e a falha fica registrada. A comparação com a curva confirmatória `a*(r)` só é feita depois da liberação dela, lado a lado e rotulada como exploratória.

## X2: mapa de R² da deriva

Em cada condição, simulam-se trajetórias latentes, sem canal de observação nem máscara, com N = 10.626 e 11 ondas. A implementação expõe a deriva padronizada `D̃_t` e precisa reproduzir bit a bit a trajetória de estados da função congelada `influence` para as mesmas sementes. Com mínimos quadrados agrupados sobre pessoas e passos, em cada réplica:

- **X2a:** R² parcial de `D̃_t` na regressão de `z_{t+1}` sobre `[1, z_t, D̃_t]`, contra `[1, z_t]`. É o diagnóstico prometido na v1.
- **X2b:** R² incremental de `D̃_t` além de uma spline cúbica natural de `z_t`, com nós nos quantis 0,05; 0,275; 0,5; 0,725 e 0,95 da réplica. Mede a parte da deriva que uma função não linear do próprio estado não explica.

As condições são `a ∈ G` (incluindo 0 como linha de base, com a deriva calculada de uma rede sorteada pelo mesmo esquema e sem efeito na trajetória), `b ∈ {0,25; 0}`, passos por onda `∈ {1; 24}` e ancoragem ω = 0, com 10 réplicas por condição. Relatar média, desvio-padrão, mínimo e máximo entre réplicas.

## Sementes, host e saídas

As sementes derivam da raiz `20260928` no namespace `v4-exploratory-x1-x2`, distinto de todos os namespaces confirmatórios congelados e do namespace `shp-crosswalk-v1`. Nenhuma semente confirmatória é derivada ou consumida, e nenhum resultado de gate, tier ou `a*(r)` é lido. A execução roda num host de exploração, fora do Mac que executa o gate e os tiers; a equivalência numérica entre hosts não é exigida para análise exploratória, e o host fica registrado. As saídas são agregados em JSON nesta pasta, com o commit de código, as sementes derivadas e o host, e um relatório curto em PT-BR.

## Relato no artigo

X1 e X2 entram no artigo e no suplemento como análises exploratórias pré-declaradas nesta data, com o resultado que tiverem, inclusive nulo ou falha. A frase de manchete continua sendo a da curva confirmatória.
