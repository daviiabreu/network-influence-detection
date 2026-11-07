# Registro de execução da v4

Preparação em 2026-09-30, para o item R08 da revisão de pendências. Este registro cobre os fatos disponíveis até o item 102 do log de decisões, registrado aproximadamente às 11:00 UTC desse dia. Nesse recorte, G0, G1b, G1c e G2 estão aprovados, G2c está em curso e os resultados confirmatórios e de X3, X4, X6 e X7 continuam selados. As seções posteriores à liberação identificam evidências a incorporar, sem atribuir valores ou declarar conclusão. Fontes: log do owner [L], itens 46 e 102; revisão de pendências [R], item R08.

O ramo documental é `docs/v4-run-record-20260930`, com base em `00c8dc3d113545bcbaaa807041f316373a4acbbc`. Ele não é um checkout de execução. O caminho segue a convenção dos [registros de aquisição][C1] e de [produção da literatura][C2]: preparação, proveniência, execução, incidentes e limites ficam num relato separado dos artefatos canônicos. A pasta `report/` é adequada porque seu [README][P] e o [roteiro de liberação][B] já concentram a proveniência do relato da v4; os registros em `research/literature/run-records/` pertencem à literatura. Fonte da base: commit `00c8dc3d`; fontes da convenção: [C1], [C2] e [P].

Todos os horários abaixo são UTC. Horários aproximados do log continuam aproximados; os originalmente anotados em BRT foram convertidos somando três horas. A data de um commit identifica o registro em Git, não um horário de execução ausente da fonte. `coord/` designa `/Users/davi/.local/state/research-workbench/coord-20260925/`. Os caminhos de evidências futuras são apenas ponteiros: nenhum conteúdo selado, log privado de gate ou tier, saída de liberação ou diretório restrito foi aberto para preparar este arquivo.

## Freeze, host e pré-voo

O primeiro pré-registro congelado está vinculado ao commit `fd65d2a` e ao SHA-256 `fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706`. A falha do gate v1 levou à emenda sucessora v4.3, com exposição prévia declarada e sementes novas. O freeze da v4 foi registrado no commit `37513841`, cuja data de commit é `2026-09-25T15:01:55Z`. O SHA-256 de `freeze-v4.json` é `99c4277235d4f2303b6f009d6ead8287a5d71372744dd6781e1e2d1847710837`, coerente com o identificador abreviado da emenda de liberação. Fontes: [L], itens 18 e 19; [freeze][F]; [emenda de liberação][A]; commit `37513841`.

O ambiente congelado é `macOS-27.0-arm64-arm-64bit`, Python `3.12.13` compilado com Clang `21.1.4`, NumPy `2.5.3`, oito workers, oito shards e uma thread de BLAS. O freeze registra `OPENBLAS_NUM_THREADS=1` e `VECLIB_MAXIMUM_THREADS=1`; o hash do ambiente é `218a26db2a28d94727b0cc5693b242152c5ea9916ddcf2fe39a9767fbc514439` e o do código é `db9d6eadb5019d691a8c73703d511d0337dc49834bb219d168a27693df0e0acd`. Esses dados vêm do [F], não de uma nova sondagem do Mac.

O pré-voo exige igualdade da coleção de código e do ambiente com o freeze, os artefatos vinculados e a sonda numérica dentro da tolerância declarada. A segunda vinculação, `coord/v4-allocation.json`, é produzida depois de G0 e antes de G2: prende o digest dos estados de G0, as células concretas de G2 e o hash dos critérios ao freeze. G2c, retomadas e agregações reutilizam essa mesma vinculação. Não se escolhem substituições por AUC. Fontes: [README da execução][D], seção “Execução futura”; [F].

A avaliação do homelab como segundo host confirmatório não satisfez o critério discreto pré-declarado de equivalência, por divergência de `seed_material_sha256`. A decisão 41 manteve gate e tiers no Mac, sob `caffeinate`, na tomada. A equivalência contínua relatada naquela avaliação não substitui a equivalência em bytes exigida. A integração acrescentou dependências depois do freeze; seu `pyproject.toml` e `uv.lock` não identificam o ambiente confirmatório. O executor continua no checkout `37513841`. Fontes: [L], item 41, de 2026-09-27 aproximadamente às 23:35Z, e item 45; [P], “Known constraints”.

## Gate G0 a G2c

A sequência de execução é G0 → G1b → G1c → G2 → G2c. G1a é a bateria de identidades unitárias, não uma etapa adicional do driver com contagem de tarefas de gate. Este registro não transforma a existência dessa bateria em uma nova aprovação observada. Fonte: [D], “Execução futura”.

G0 e G1b estão aprovados conforme o item 46, registrado em 2026-09-28 aproximadamente às 07:20Z. Esse item não fornece os horários originais das aprovações nem suas contagens completas; eles não são reconstruídos aqui. G1c está aprovado, com 150/150 tarefas seladas; o defeito de serialização do agregado e seu registro sucessor são descritos abaixo. Fonte: [L], item 46. Não se reproduzem estimativas ou diagnósticos desses estágios.

G2 está aprovado: o agregado foi gravado em `2026-09-30T10:01:43Z`, com 700/700 tarefas e zero falhas. G2c começou automaticamente em seguida e está em curso no recorte do item 102; ainda não há aprovação ou reprovação a registrar. Fonte: [L], item 102, que declara critérios, contagens e aprovação públicos por desenho. A aprovação de G2 não autoriza tiers ou abertura de resultados enquanto faltar a aprovação de G2c.

O driver dos tiers espera a continuação do gate e exige o marcador `GATE_SEQUENCE_DONE`, escrito somente após G2 e G2c passarem. O executor congelado ainda reconfere todos os agregados antes de executar uma curva. Fontes: [L], itens 45, 46 e 94; [D]. O desfecho e as contagens públicas de G2c serão acrescentados a partir de um novo item do log do owner, com horário UTC; não se abrirá seu diagnóstico para preencher esta seção.

## Incidentes e recuperações

Em `2026-09-28T07:14Z`, o `run_gate` saiu com código 2 depois de selar as 150 tarefas de G1c. O agregado congelado devolvia `pass` como `numpy.bool`, que o serializador JSON congelado não aceitava. O diagnóstico registrado encontrou o estágio completo e aprovado. Um script externo chamou o pré-voo e o agregador congelados e converteu apenas escalares NumPy, produzindo o registro sucessor de G1c, SHA-256 com prefixo `a945e848`. A continuação de G2 e G2c começou às 07:19Z com a configuração original; o driver dos tiers passou a esperar essa continuação. Não houve alteração de código, critério, tarefa ou arquivo selado. Fonte: [L], item 46. O sucessor é identificado pelo [P] como `coord/v4-gate-logs/G1c-aggregate-successor.json`; esse arquivo não foi lido aqui.

Em 2026-09-29 aproximadamente às 12:40Z, a revisão de `67d7789c` vetou o lançamento de X3/X4/X6 no laboratório. O bloqueante permitia que a comparação dos stores sobrescrevesse a verificação de proveniência. Os demais problemas atingiam solver, denominadores e mínimos de X6, retomada entre versões, persistência de erro em X7, prioridade, corte, leitura de X4 e censura de X7. O lançamento foi condicionado às correções e a novas pré-condições por classe de host. X5 e X7 conservaram seu produtor `c8e4861f`; a compatibilidade de leitura passou a exigir os registros originais e o código corrigido. Fontes: [L], itens 69, 80 e 81; commits `30c10dc8` e `3334ac0f`.

Antes de lançar `3334ac0f`, o coordenador substituiu a barreira entre análises por ordem fixa em cada worker e acrescentou agregação da união de diretórios. A barreira exigia recibos de X5/X7 que não existiam nos shards novos; os diretórios isolados por host também não continham a união necessária a X6. A reconfirmação dos registros originais de X5 e X7 usou seus booleanos e vínculos, sem sobrescrever as pré-condições. Os testes focados sobre o próprio commit de lançamento terminaram sem falha, e os supervisores prosseguiram. Fontes: [L], itens 80, 81 e 84. São verificações técnicas registradas, não resultados científicos.

Em 2026-09-30 aproximadamente às 00:27Z, a revisão do lançamento encontrou manifestos de estágios que só nasceriam quando um worker chegasse a eles. O coordenador criou os manifestos ausentes nos três hosts por chamadas do próprio CLI sem unidades elegíveis, com o ambiente de BLAS do lançador. O mesmo item prescreve recuperação de queda ou reboot: confirmar que não há worker vivo, mover arquivos parciais órfãos para quarentena fora dos stores e retomar o mesmo lançamento. Essa recuperação é uma regra preparada; não há queda posterior registrada neste recorte. Fonte: [L], item 90.

O Mac sofreu disputa de CPU com a matriz da venue run 20 e testes de outras sessões. Em 2026-09-30 aproximadamente às 02:20Z, o coordenador pausou o container e aplicou QoS de fundo às sessões; depois de uma retomada do container, a venue run 20 foi cancelada e o container parado, aproximadamente às 04:35Z. Ela não era necessária ao caminho crítico da IC. O mesmo registro aponta o risco de uma atualização de macOS mudar o ambiente congelado e registra o pedido para desativar a instalação automática; não comprova que Davi o tenha executado. Fontes: [L], itens 95 e 98.

As esperas de liberação foram substituídas em 2026-09-29 aproximadamente às 22:50Z e novamente em 2026-09-30 aproximadamente às 04:40Z, sem liberação feita. A primeira troca incorporou lock e publicação atômica; a segunda retirou a parada por horário após tentativas antecipadas. O checkout do script de liberação permaneceu fixado em `9669b509`. Fontes: [L], itens 83 e 97.

A cópia de X5/X7 do homelab para o Mac foi concluída e conferida em 2026-09-30 aproximadamente às 05:05Z, preservando manifestos antes, depois e no destino. A tentativa anterior travara numa sessão SSH; a cópia passou a usar timeout de E/S e novas tentativas. O log registra os recibos em `coord/lab-pcs/export-manifests/c8e4861f/` e o manifesto com prefixo `b8c4c922`, sem abertura de X7. Fonte: [L], item 100. Não se refez a cópia nem se inspecionou o destino nesta preparação.

## Alocação dos shards e configuração dos hosts

Gate e tiers confirmatórios ficam no Mac. O freeze declara oito shards e oito workers. Para os tiers, o driver lança um worker por shard, com barreira global entre tiers, na árvore `37513841`, usando o mesmo freeze e a segunda vinculação. Fontes: [F]; [L], itens 41 e 45. A existência desse encadeamento não comprova início ou término de um tier no recorte atual.

X3/X4/X6 usam `SHARD_TOTAL=64` e produtor `3334ac0f`. O icmomat recebeu shards 0–27, 28 processos; o homelab recebeu 52–63, 12 processos. Ambos foram lançados em modo `run`, com `nice 10`, em `2026-09-29T22:37Z`. O icllm recebeu 28–51, 24 processos, em `2026-09-29T23:49Z`, depois de Davi liberar escrita no disco. As faixas são disjuntas e cobrem os 64 shards. Fontes: [L], itens 80, 81, 86 e 87.

As pré-condições de `3334ac0f` passaram no icmomat em `2026-09-29T22:54Z`, no homelab em `2026-09-29T23:28Z` e no icllm em `2026-09-30T00:13Z`: `verify-x3-fit`, `verify-x3-store`, `verify-x4-fit` e `verify-x6-pop`, todos com código de saída zero. O icllm é registrado como Xeon w5-2455X; o homelab como i5-1335U no registro anterior de X6. O resultado da pré-condição vale por commit e classe de host, não como equivalência numérica entre os três hosts. Fontes: [L], itens 65, 85 e 88; [declaração X3–X7][X37].

No icllm, o pacote da CPU foi limitado por RAPL a 140 W de longo prazo e 150 W de curto prazo, com valores originais de 200/240 W registrados para restauração. Essa configuração foi autorizada sob a restrição do nobreak e da carga de GPU já existente, aplicada e lida de volta antes do lançamento. Sua restauração fica ligada ao fim da IC nesse host ou à margem disponível quando a carga de GPU cessar; não há restauração registrada aqui. Fontes: [L], itens 86–88.

X3 e X4 são distribuídos por blocos inteiros de r, para manter a proveniência da unidade ao unir hosts; X6 usa shards globais. Cada worker segue a prioridade declarada, sem barreira entre hosts. A agregação de X3/X4/X6 deve validar cada diretório com a própria classe de host e unir as saídas no checkout `3334ac0f`, no Mac, depois da liberação. X5/X7 mantêm a origem única no homelab, produtor `c8e4861f`. Fontes: [L], itens 66, 80, 81 e 100.

## Espera da liberação e automação por evento

A emenda registrada em `2026-09-28T23:28Z`, commit `428ca7cd`, antecipa a liberação para quando existirem os registros das 414 unidades do inventário e nenhum `run_curve.py` estiver vivo, ou para o fechamento `2026-10-19T02:59:00Z`, o que vier primeiro. Antes da liberação, a completude é verificada apenas pela existência dos arquivos. Não existe liberação parcial. A função congelada continua registrando o fechamento nominal em `inventory.closed_utc`; o horário efetivo vem do registro lateral `release-record.json`. Fontes: [A]; [L], itens 57–60; [B], seções 2 e 3.

O par de liberação é `released-curves.json` mais `release-record.json`, com o SHA-256 dos bytes publicados. A tentativa inteira usa lock; curvas são publicadas antes do recibo, por escrita temporária e rename atômico. Um par íntegro permite retomada idempotente. Recibo isolado ou com digest divergente não comprova sucesso. Fontes: [L], item 83; [B], seções 2 e 3; [script de liberação][RL].

Em 2026-09-30 aproximadamente às 02:10Z, Davi determinou que nenhum passo operacional aguardasse horário quando seus insumos já existissem. A decisão 94 substituiu a regra da decisão 59 de parar após três tentativas antecipadas: a espera passa a tentar novamente a cada 30 minutos, com alerta. Os cortes registrados continuam limites, não esperas mínimas: X3–X7 em `2026-10-10T02:59:00Z` e confirmatório em `2026-10-19T02:59:00Z`. Fontes: [L], itens 59 e 94; [B]; [X37].

A automação por evento, `c661809b`, integrada em `c0bfd4e2`, foi ligada conforme o item 97. O vigia de exportação estava em loop desde `2026-09-30T03:21Z`. A cadeia pós-liberação foi ligada sob `caffeinate` no checkout fixo `review/post-release-chain`, em `0083009f`, conforme o item 100; seu estado registrado era `waiting-release`. Ela espera o par íntegro, gera relatório e exportação, espera os recibos de exportação dos hosts, agrega X3–X7 no produtor correto, calcula comparações e compila. O código termina em `awaiting-human-review`; a montagem automática não constitui aceite científico ou submissão. Fontes: [L], itens 97 e 100; [automação rastreada][EV].

## Exploratórias X1 a X7

X1 e X2 foram declarados antes da implementação e dos resultados, no commit `12ef78f1`, em 2026-09-28. X1a compara o braço de interação com o gêmeo de campo médio; X2 registra o mapa da deriva. O host destinado a essas execuções é o homelab, com namespace próprio. O relatório de X1a/X2 foi integrado em `f6028817`, conforme a decisão 51. A pré-condição de X2 exige reprodução em bytes da trajetória congelada ao expor a deriva. Este registro aponta a declaração e a integração sem reproduzir suas estatísticas. Fontes: [L], itens 44 e 51; [declaração X1–X2][X12].

X1b usou produtor `8f6f4cdb` no homelab. Sua pré-condição reproduziu o pipeline congelado em quatro células de tamanho declarado, antes do uso: `(a; r) = (0; 0,90), (0,003; 0,70), (0,03; 0,50), (0,30; 0,60)`, com registro de prefixo `1664d801`. O log registra execução de `2026-09-28T17:15Z` a `2026-09-28T23:23Z`, 81 células sem erro, e relatório integrado em `a3a76a9a`. A comparação com a curva confirmatória permanece pendente da liberação. Fontes: [L], itens 54 e 58; [X12].

As diferenças operacionais de X1b foram registradas: erro de valor preservado por célula com continuação do shard; dependências posteriores ao freeze, com a mesma versão de NumPy; e um erro de aspas que juntou stdout dos processos da verificação, corrigido antes da rodada, sem efeito nos stores. Elas não autorizam tratar X1b como confirmatório. Fonte: [L], item 54.

X3–X7 foram declarados em `85cdb8f2`, conforme o item 61, registrado em `2026-09-29T00:52Z`, antes de implementação, execução e resultado confirmatório. X3 libera a parcela de sinal da nula B; X4a/X4b examinam referências de rejeição de painel único; X5 estressa canal e atrito em força zero; X6a/X6b examinam cobertura interior; X7 compara o discriminador congelado com atributos ampliados. Fontes: [L], item 61; [X37] e seu [JSON][J37]. Os nomes das análises não antecipam suas conclusões.

X3/X4 foram implementados em `cfe15198`; X6 em `0443b91e` e `f7e15b71`. A pré-condição antiga de X6 deixou de valer para o novo lançamento. A execução de X3/X4/X6 fica vinculada a `3334ac0f` e às aprovações por host de 2026-09-29 e 2026-09-30 descritas acima. As verificações cobrem ajuste de X3, stores de X3, ajuste de X4 e o invólucro populacional de X6. Fontes: [L], itens 63, 65, 69, 81, 85 e 88.

X5 e X7 foram implementados em `3915eb9e` e `1ed5ee8a`, com lançador em `c8e4861f`. As pré-condições do homelab reproduziram quatro células por análise, em bytes, com registros de prefixos `6911209e` e `cc01fc6b`. X5 terminou em `2026-09-29T08:36Z`, depois de iniciar às 03:09Z, e seu relatório foi integrado em `4a372a71`. X7 foi registrado como concluído em 2026-09-29 aproximadamente às 17:20Z, com 81/81 registros e saída dos workers sem erro. Fontes: [L], itens 62, 66, 68, 70 e 80. Não se reproduzem AUCs, escores ou leituras de X5/X7 neste registro.

X1a, X1b, X2 e X5 têm relato exploratório já registrado. X3, X4, X6 e X7 permanecem selados até a liberação confirmatória efetiva, inclusive X7 já concluído e copiado. O corte computacional de X3–X7 não autoriza por si só sua abertura. Comparações de X1b, X3, X4 e X5 com a curva confirmatória também esperam a liberação. Fontes: [X12]; [X37]; [L], itens 61, 70, 89 e 100.

## Mapa sistemático separado

Ponteiros: [registro de produção v5.1][C2], [protocolo priorizado v5.1][MAP], [síntese versionada de 2026-09-28][SYN] e [L], itens 52, 53 e 92. As evidências, contagens e limitações do mapa permanecem nesses registros próprios.

## Desvios e exposição cumulativa

A seção D8 da [emenda v4.3][V] acrescenta ao histórico da v1 os gates BA em r = 0,65 e 0,70, a seleção antiga em r = 0,80 e o bit de interioridade sob `cb457af`; depois, AUC e refits da lei v1 em r = 0,70, refits e probe da proposta A e quantidades de matching da proposta B. A preparação v4 acrescentou critérios artificiais e custos de matching. Esses tipos de exposição são registrados aqui sem transcrever seus valores estatísticos. A mesma seção determina que os critérios observados de G2/G2c sejam acrescentados ao histórico quando executados. Fontes: [V], “Autoridade, evidência e exposição — D8”; [L], item 19.

r = 0,70 é exposto para calibração, e o método global foi escolhido depois de exposição parcial. A descrição adequada é avaliação em sementes novas de protocolo emendado após exposição parcial. A curva completa continua primária; os outros r não viram um novo primário. As aprovações públicas de gate, as verificações de host e os relatos exploratórios X1/X2/X5 conhecidos entram na cronologia, sem converter exploração em confirmação nem ocultar o histórico anterior. Fontes: [V], D8; [L], itens 41, 44, 54, 58, 68 e 102.

O defeito e o sucessor de G1c, a manutenção do confirmatório no Mac, a antecipação da liberação e as correções de lançamento e leitura das exploratórias são alterações ou incidentes distintos, com a proveniência acima. A antecipação foi declarada antes de qualquer tier; as escolhas de leitura foram registradas antes da exposição confirmatória. Não se soma uma “contagem de exposição” artificial entre critérios, AUCs, estados e revisões. Fontes: [A]; [L], itens 46, 57, 69, 80, 82, 89, 91, 99 e 101.

## Decisões delegadas que afetam a leitura

A delegação do item 20 não é verificação humana dos artefatos. Os itens abaixo foram registrados pelo agente sob delegação e devem permanecer identificados assim; a ratificação e o aceite humano são fronteiras próprias. Fontes: [L], itens 20 e 21; [tabela de interpretação][I].

A decisão 82, de 2026-09-29 aproximadamente às 22:45Z, fixou Q11, Q16 e Q22: a leitura de D requer banda superior abaixo do alvo na grade inteira sem lacuna; largura não muda a região; diferença descritiva de região não vira teste nem “reversão”. Seu Q8 permitia leitura local pareada entre B e D. Esse Q8 foi substituído pela decisão 91 e não é a regra vigente. Fontes: [L], itens 82 e 91; [I].

A decisão 89, de 2026-09-30 aproximadamente às 00:20Z, fixa a curva principal como tier 1, família B, canal observado. A célula selecionada é a primeira fronteira pontual; a sustentada é relatada ao lado. X5 usa a menor força da grade, incluindo zero, cuja AUC pontual confirmatória iguala ou supera a de má especificação; lacuna anterior censura a leitura e ausência de força suficiente fica “acima da grade”. Seu intervalo com crítico congelado é comparado à banda em a*(r) por sobreposição, acima ou abaixo. Sem fronteira disponível, a leitura nessa célula fica indisponível com motivo. X1b fica lado a lado; X3/X4 são lidos na célula selecionada com as restrições de redação. Fontes: [L], item 89; [módulo de comparações][CMP]; [restrições X3–X7][W].

A decisão 91, de 2026-09-30 aproximadamente às 01:05Z, commit `44b722dd`, exige tier 2 completo e válido e curva principal válida para qualquer frase entre mecanismos, inclusive local. As contagens pareadas usam o mesmo conjunto de r. Os controles incluem `latent_rank`; “dependente do canal” exige que nenhum dos três controles válidos e sem lacuna atinja. Os alvos secundários ficam sempre no suplemento. X6 com falha ou subnominal na banda primária contra D1 entra no resumo; X5 entra sempre na discussão e conclusão; X3/X4/X7 ficam na discussão e suplemento. X3 em força zero e X4b fora dos r declarados têm estado próprio de fora do domínio. Fontes: [L], item 91; [I]; [W]; commit `99c59590` para aplicação nos shells e exportadores, registrado no item 96.

A decisão 99, de 2026-09-30 aproximadamente às 05:00Z, commit `0083009f` registrado às 04:52Z, fecha os ramos de falha do gate: artigo com forma completa, Métodos preservados, Results pelo ramo do gate e B1-END; resumo conforme o shell; estado de B1d fixado no fechamento. Gate que termine depois pode apoiar somente um sucessor e não deriva semente confirmatória para esse relato. Sem resultado confirmatório, os registros selados de G2/G2c não abrem sob esse freeze; uma emenda sucessora deve declarar a abertura e somá-la à exposição antes de ler. A âncora SHP em ramo de falha fica em subseção exploratória textual, contra a grade de r, sem curva, fronteira ou F6. Fontes: [L], itens 99 e 102; [I]. Nenhum dado SHP foi usado nesta preparação.

A decisão 101 corrigiu a 99 antes do desfecho de G2, em 2026-09-30 aproximadamente às 05:25Z; o commit `00c8dc3d` é registrado às 05:10Z. Q7 passou ao bloco B1-SHP dos shells, com as constantes vinculadas. A extensão do exportador só do gate para aceitar esse agregado continua pendente se esse ramo for selecionado. Q17 segue a composição obrigatória da decisão 91 e acrescenta opcionais na ordem fixada, sem remover anteriores. Q18 distingue B03, sobre todas as grades, de P5-b, sobre fronteiras atingidas, sem estender faixas a r censurado ou não atingido. Fontes: [L], itens 101 e 102; [I]; commit `00c8dc3d`. As decisões 99 e 101 antecederam o agregado de G2.

## Evidências a incorporar depois da liberação

Esta seção é uma lista de proveniência, sem resultados. Os diretórios de tentativa da automação têm nomes variáveis. Para localizar as saídas exatas, o responsável usará o campo `root` de `coord/v4-release/confirmatory-checkpoint.json` e de `coord/v4-release/exploratory-checkpoint.json`. Abaixo, `C` e `E` designam respectivamente essas duas raízes, depois de verificar os recibos e os manifestos. Os nomes e campos vêm do código rastreado [EV]; os arquivos reais não foram inspecionados.

### Liberação efetiva

Registrar data UTC e condição disparadora de `coord/v4-release/release-record.json`, campos `released_utc` e `condition`; conferir os bytes de `released-curves.json` contra `released_curves_sha256`, o commit da emenda e o hash do script presentes no recibo. Registrar separadamente `inventory.closed_utc` de `released-curves.json`. Os IDs textuais exportados são `v4.release.effective_utc` e `v4.release.condition`; o fechamento nominal continua sendo o do protocolo. Nenhum desses valores foi preenchido. Fontes do contrato: [RL], [B] e [exportador confirmatório][EX].

### Tiers e inventário final

Registrar estados finais por unidade de `released-curves.json`, em `inventory.units`, e a validade principal em `inventory.main_curve_valid`. Conferir `C/report/T4_inventory.csv` e `C/report/manifest.json`. As contagens totais vêm de `C/result-catalog.json`, chaves `v4.inv.n_not_started`, `v4.inv.n_partial`, `v4.inv.n_invalid`, `v4.inv.n_valid` e `v4.inv.n_incomplete`; por tier, vêm das mesmas terminações sob `v4.inv.t1` até `v4.inv.t6`. O total de curvas vem de `v4.all.n_curves`. São quantidades finais, ainda sem valor. Fontes dos contratos: [P], [EX] e [EV].

Horários de início, término e retomada de cada tier precisarão de novos itens públicos do log do owner, com commit, host e shard. O inventário final não fornece por si só essa cronologia; não se deduzirão tempos dos resultados nem se abrirão logs privados para este registro. A lista concreta de unidades e o plano são os arquivos rastreados [inventário planejado][INV] e [plano congelado][PLAN]. Eles são denominadores de planejamento, não prova de execução.

### Relatório confirmatório e gate encerrado

Para fronteiras por família e r, usar `C/report/T1_a_star_grid.csv`; para todos os tiers, `C/report/T1s_a_star_all_units.csv`. Esses arquivos fornecem fronteira primeira, sustentada, intervalos, regiões, lacunas e censuras, preservando indisponibilidades. Sua proveniência vem de `C/report/manifest.json` e seu vínculo ao manuscrito de `C/result-catalog.json` e `C/result-values.json`. Para qualquer frase entre mecanismos, conferir primeiro `v4.mechanisms.allowed`. Nenhuma fronteira, intervalo, região observada ou comparação foi preenchida. Fontes dos contratos: [P], [EX] e [EV].

A aprovação ou reprovação final e as contagens públicas de G2c virão do novo item do log do owner. Depois da liberação legítima, a conferência do relato usará `C/report/T3_gate_summary.csv` e seu manifesto, incluindo a identificação do sucessor de G1c. Esta preparação não autoriza abrir os arquivos de origem do gate. Se não houver resultado confirmatório, aplica-se a decisão 99(v), sem abrir G2/G2c sob esse freeze. Fontes: [L], item 99; [P]; [I].

### Agregação de X3 a X7

Registrar exportações dos três hosts por `coord/lab-pcs/export-manifests/3334ac0f/{icmomat,icllm,homelab}.verified.json` e pelos respectivos arquivos `.sha256.json`; os recibos vinculam host, produtor, destino e manifesto. Para a origem de X5/X7, usar os recibos em `coord/lab-pcs/export-manifests/c8e4861f/`, registrados no item 100. Conferir o produtor `3334ac0f`, a união sem perda ou duplicação e os vínculos das pré-condições. Os arquivos da agregação serão `E/aggregates/x3.json`, `x4.json`, `x5.json`, `x6.json` e `x7.json`, vinculados por `exploratory-checkpoint.json`. Fontes dos contratos e da cópia anterior: [EV]; [L], itens 80, 81, 90 e 100.

Contagens de execução vêm de `E/catalog.json`, exportado por [exportador exploratório][XX]: as terminações `recorded`, `incomplete`, `errors`, `gaps` e `successful` sob `v4x.x3`, `v4x.x4a`, `v4x.x4b` e `v4x.x7.inventory`. Suas origens são `x3.json/cells`, `x4.json/x4a`, `x4.json/x4b` e `x7.json/cells`, com as listas próprias de incompletos. Leituras por célula de X3 e por unidade de X7 vêm de `v4x.x3.count.*` e `v4x.x7.count.*`; X4 usa `v4x.x4a.count.*` e `v4x.x4b.count.*`, preservando o recorte de AUC declarado e a referência em força zero. X5 conserva as células e condições em `E/aggregates/x5.json`. Nenhum desses valores foi preenchido. Fontes dos contratos: [XX] e [EV].

Para a banda primária de X6a contra D1, os IDs exatos em `E/catalog.json` são `v4x.x6.x6a.band.vs_d1.primary.covered` e `v4x.x6.x6a.band.vs_d1.primary.total`; a referência separada com lacunas como não cobertura usa `v4x.x6.x6a.band.vs_d1.gaps_as_misses.covered` e `.total`. Eles correspondem a `E/aggregates/x6.json`, seção `x6a.band.vs_d1`. As contagens de incompletos vêm de `v4x.x6.x6a.incomplete` e `v4x.x6.x6b.incomplete`; repetições sem curva, de `v4x.x6.x6a.without_curve`. Coberturas por força, verdades, precisão e denominadores ficam nas seções `x6a.strengths` e `x6b.cells` desse agregado, com os campos preservados pelo exportador. Nenhuma cobertura, verdade, AUC ou leitura foi preenchida. Fontes dos contratos: [XX] e [shells exploratórios][XS].

### Comparações e revisão final

Usar `E/comparisons.json`, esquema `ic-study.v4-exploratory-comparisons.v1`, seção `by_r`, vinculada aos hashes de curvas, recibo e agregados. Por r, a comparação preserva `main_curve`, `x1b`, `x3`, `x4` e as entradas de `x5`, incluindo fronteiras, disponibilidade, força equivalente e relação do intervalo com a banda. X1b vem do arquivo indicado por `X1B_JSON` no lançamento registrado no item 100; seu produtor é `8f6f4cdb`. Os outros insumos são os agregados indicados acima. Fontes: [CMP], [EV]; [L], itens 58, 89 e 100.

As contagens de disponibilidade vêm de `E/catalog.json`, IDs `v4x.comparisons.count.{main_curve,x1b,x3,x4}.{available,unavailable,partial}`. Para X5, os IDs são `v4x.comparisons.count.x5.equivalent.{available,censored,above-grid,unavailable}` e `v4x.comparisons.count.x5.interval.{overlap,above,below,unavailable}`. Os valores por r permanecem sob `v4x.comparisons.by_r.*`, com o ponto decimal de r substituído por hífen no ID. Conferir `E/manuscript/generated/exploratory-boundary-comparisons.tex`, `E/manuscript/generated/exploratory-selected-comparisons.tex` e `E/manuscript/generated/exploratory-stress-comparisons.tex`. Fontes: [XX]; [XS]. Nenhuma comparação foi preenchida.

Registrar ainda os hashes dos módulos produtores e exportadores, os manifestos de saída, `E/result-values.json`, `E/paper-check-status.json` e o caminho do PDF final indicado por `coord/v4-release/chain-status.json`. A passagem para `awaiting-human-review` e os códigos de saída serão evidência técnica; a conferência do PDF contra as fontes, a seleção de ramos, a ratificação e o aceite de Davi deverão ter registros próprios. Fonte: [EV]. Este arquivo ainda não declara que esses eventos ocorreram.

## Limites

Este é um registro documental preparado antes da liberação, não uma reprodução da execução nem uma auditoria dos stores. Usa fatos já registrados no log do owner, commits e arquivos rastreados. As contagens operacionais informam conclusão de tarefas quando a fonte assim as registra; não substituem validade da curva, cobertura, poder ou resultado confirmatório. Nenhuma suíte, simulação, instalação, agregação ou liberação foi executada para prepará-lo.

A reprodução em bytes entre macOS e Linux não foi demonstrada para o confirmatório. As exploratórias têm pré-condições por classe de host e resultados próprios, sem equivalência confirmatória entre hosts. As restrições de [W] continuam obrigatórias: X3 não demonstra impossibilidade por falha de busca; X4 não certifica poder de um analista; X6 não certifica cobertura nominal por ausência de subcobertura detectada; X7 não demonstra teto de informação. Fontes: [L], item 41; [X37]; [W].

A exposição anterior e as decisões delegadas permanecem declaradas. Não houve verificação humana dos artefatos por efeito da delegação. Nenhum microdado SHP foi lido, usado ou citado; eventual âncora depende de evidência agregada permitida e de execução pelo owner, em fluxo separado. A documentação preparada, os testes técnicos históricos e a automação armada não fecham a IC nem autorizam submissão. Fontes: [L], itens 20, 21, 37, 99 e 101; [EV].

## Fontes e ponteiros

[L] e [R] ficam fora do repositório, na pasta de coordenação: [L] é `coord/owner-decisions-20260924-session-log.md` e [R] é `coord/remaining-work-review-20260930.md`.

O log do owner [L] identifica cada evento por item; a revisão de pendências [R] identifica o escopo R08. As demais referências resolvem para arquivos rastreados deste checkout. Os caminhos de saídas futuras são definidos pelos contratos e não constituem evidência já incorporada.

[C1]: ../../../../research/literature/run-records/2026-09-09-primary-acquisition-v2.md
[C2]: ../../../../research/literature/run-records/2026-09-28-broad-map-v5-1-production.md
[P]: README.md
[B]: RELEASE-RUNBOOK.md
[F]: ../freeze-v4.json
[D]: ../README.md
[A]: ../../../../research/questions/exploration/2026-09-24-parallel/detection-boundary-v4-release-amendment.md
[V]: ../../../../research/questions/exploration/2026-09-24-parallel/detection-boundary-amendment-v4.md
[RL]: ../release_on_completion.py
[X12]: ../../detection-boundary-v4-exploratory/README.md
[X37]: ../../detection-boundary-v4-exploratory/README-x3-x7.md
[J37]: ../../detection-boundary-v4-exploratory/declaration-x3-x7.json
[EV]: ../../detection-boundary-v4-exploratory/automation/v4_event_automation.py
[MAP]: ../../../../research/literature/protocol/opinion-dynamics-systematic-map-v5-1-prioritized.md
[SYN]: ../../../../research/literature/synthesis/map-v5-1-2026-09-28/README.md
[I]: ../../../../publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-interpretation-decisions-2026-09-29.md
[W]: ../../../../publications/jcss-manuscript/pipeline/review/x3-x7-reading-restrictions-2026-09-29.md
[XS]: ../../../../publications/jcss-manuscript/pipeline/drafts/2026-09-30/exploratory-results-shells.tex
[CMP]: ../../../../src/ic_study/analysis/v4_exploratory_comparisons.py
[EX]: ../../../../src/ic_study/analysis/v4_report_export.py
[XX]: ../../../../src/ic_study/analysis/v4_exploratory_export.py
[INV]: ../inventory.json
[PLAN]: ../../../../src/ic_study/simulation/v4_plan.py
