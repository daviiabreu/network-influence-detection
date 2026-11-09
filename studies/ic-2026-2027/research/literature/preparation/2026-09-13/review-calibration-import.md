# Revisão independente da importação de referências

Revisão do candidato privado congelado, realizada em 13/09/2026 no checkout
`2bfa4ea33b637fa1a3fc61cdffac8ad3ffba4ded`. O resultado é **revisão requerida**:
há um defeito de isolamento do destino HTTP e uma frase que precisa delimitar
o alcance da comparação de identidades. Nenhum candidato foi alterado. Esta
revisão não aprova autoria humana, calibração, promoção ou aceite científico.

## Achados priorizados

### P1 — O destino pode publicar referências no diretório HTTP

O bloqueio em
`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/import_owner_references.py:268`
exclui o CAS e os diretórios do scaffold e do mapeamento. O teste de Git e
permissões em `verify_output_target` também é aplicado, mas o diretório
congelado `owner-form-v3-20260913` não é excluído. Esse diretório tem modo
`0700`, satisfazendo a checagem de diretório privado. O servidor HTTP roda
com o mesmo usuário e consegue ler arquivos `0600` criados nele.

Isso contradiz a garantia de que os arquivos permanecem fora do diretório
HTTP em
`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/calibration-import.md:89`.
O comando documentado, que usa o diretório privado `calibration-import`, não
aciona o problema; a falha ocorre quando `--output` aponta para um novo
subdiretório do formulário servido.

Reprodução: em uma árvore inteiramente sintética, o teste criou um diretório
HTTP `0700`, importou 50 referências artificiais para um subdiretório novo e
consultou `owner-export.json` com `SimpleHTTPRequestHandler`. A importação
passou pela validação nativa e a resposta HTTP foi **200 com os bytes exatos
da exportação sintética**. Separadamente, uma chamada somente de verificação
aceitou um destino inexistente sob o diretório HTTP real; não houve criação
de arquivo nesse diretório. O teste está em
`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/reviewer-20260913-48Mbci/test_independent_import.py`,
caso `test_http_root_is_not_excluded_and_serves_export`.

Antes de usar referências reais, o helper deve restringir a publicação a uma
raiz privada explicitamente permitida ou rejeitar também os diretórios HTTP
congelados e seus descendentes. A regressão deve recusar o destino antes de
ler a exportação e continuar permitindo o destino privado documentado.

### P3 — A frase sobre sementes excede o método de comparação registrado

`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/calibration-import.md:71`
afirma que a amostra não contém as 64 obras de desafio nem as 16 sementes.
A evidência disponível é uma comparação por propostas de obra,
identificadores e títulos normalizados, não uma resolução semântica exaustiva
de versões. A formulação recomendada é: “A comparação registrada não
encontrou sobreposição por proposta de obra, identificador ou título
normalizado com os 64 leads de desafio e as 16 sementes; 25 casos compartilham
páginas bibliográficas com leads de desenvolvimento.”

O histórico de ajuste continua pendente e a seleção não deve ser apresentada
como historicamente inédita. Esta correção é de precisão documental; a
revisão não encontrou evidência de uma nova sobreposição semântica.

## Comportamentos confirmados

Os quatro hashes recebidos conferem. A leitura do helper foi confrontada com
os contratos e os resolvers nativos atuais. `validate_calibration_sources`
é chamado antes da publicação: reproduz as páginas bibliográficas, verifica
os registros fornecidos, resolve a evidência da manifestação correta e
reproduz os locators de texto completo. Os testes usaram esses resolvers,
sem substituí-los por mocks. Excertos alterados foram recusados.

A bijeção exige 50 IDs de caso distintos, obras e pares A/B iguais ao
mapeamento congelado, 101 tarefas únicas e cobertura completa. A mesma
referência de triagem é copiada para os dois agentes; isso não representa
duas avaliações humanas independentes. Os critérios selecionados ficam
integrais no envelope e no recibo, sem virar assertions de modelo.

Os rótulos, justificativas e evidências de triagem conservaram igualdade
integral em todos os 50 casos. A ausência de uma comparação explícita
`model_dump == entrada` para triagem, existente para extração, não produziu
defeito com o contrato atual: os cinco campos de `EvidenceLocator` são
obrigatórios, textuais e sem defaults. Dez verificações independentes
removendo cada campo ou substituindo-o por número foram recusadas; o
contrato não normaliza os textos válidos. A extração conserva a checagem
explícita contra defaults e a validação nativa de campos e vínculos.

O histórico é argumento obrigatório, sem default. O scaffold fixo só permite
`no_prior_tuning`; `declared_in_suite` exige um sucessor. O helper não obtém
essa declaração de respostas estáticas nem a infere. A CLI recusou a
ausência do argumento. Autenticidade da declaração continua sendo uma
condição do uso autorizado, não algo demonstrado por esse teste.

As leituras recusam symlinks em qualquer componente, FIFO, arquivos não
regulares, permissões abertas, tamanho excedente e alterações detectadas
durante a leitura. `read_private` aceita hardlinks e caminhos dentro de uma
árvore Git quando as permissões satisfazem o contrato; isso foi reproduzido
sem modificar a entrada. Não se classificou essa aceitação como defeito:
a documentação exige leitura privada e recusa de links simbólicos, não
`st_nlink == 1` nem rejeição de toda entrada já situada no Git. A publicação
no Git, por sua vez, foi recusada. A distinção não elimina o achado HTTP.

A publicação cria exclusivamente um destino novo, com diretório `0700` e
arquivos `0600`, após validar o conteúdo. Destinos preexistentes permanecem
intactos. O teste de falha ao criar o recibo confirmou rollback dos arquivos
novos. Não foi demonstrada atomicidade contra encerramento abrupto do
processo ou falha do sistema de arquivos durante o próprio rollback, e ela
não é atribuída a essa implementação. Em uma falha de evidência acionada
pela CLI, o código de erro foi curto e não revelou o marcador sintético
inserido na referência.

## Exportação JavaScript, CLI e limites

As funções exatas `extractionState`, `meaningful`, `buildExtraction` e o
handler de exportação foram retirados do HTML de hash
`3861d7e5d7698e394583f3b5454ac974eb39ac9cc91705a1431657faec849a2f`.
O pacote bibliográfico real foi descartado; a VM recebeu somente vínculos,
fontes e respostas sintéticos. A exportação gerada contém 50 triagens e seis
campos de extração. O teste executou `main()` do helper em subprocesso,
substituindo apenas `PRODUCTION_INPUTS` por `FrozenInputs` sintéticos, pois
a CLI pública deliberadamente não oferece override de fontes. Isso testa
a função CLI congelada com seus argumentos e tratamento de erros, sem
importar respostas contra o corpus real.

O resultado passou por cópia exata das referências, validação nativa das
fontes durante a importação e, depois, pela CLI real
`systematic-review validate-calibration-suite`, que retornou código 0 e
`schema_valid` para 101 tarefas de uma suíte `material_kind=synthetic`.
O digest da suíte sintética foi
`0e78f6e459e0625112689946c110cf96e6a6d925f3cacc2a5cd4fe9338d03289`.
O teste de excerto adulterado retornou código 2 sem criar o destino.

Não foram abertos perfis de navegador, `localStorage`, respostas humanas ou
fontes restritas. A VM verifica geração de JSON e integração com a importação;
não testa interação visual, persistência do navegador ou download pelo
sistema operacional. Não houve inferência, matriz completa, execução de
calibração ou criação de suíte científica. A única rede do ensaio independente
foi HTTP em loopback para reproduzir o achado com conteúdo sintético.

## Evidências e reprodução

Foram executados **29 testes existentes e 15 verificações independentes:
44 passaram em 3,30 s**. O teste do defeito HTTP passa porque verifica a
aceitação indevida observada no candidato, não porque a considera correta.
Todo material novo fica em `SYNTHETIC/reviewer-20260913-48Mbci/`; tentativas
anteriores do autor foram preservadas.

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/davi/Documents/github/research-workbench/workbench/src \
/Users/davi/Documents/github/research-workbench/workbench/.venv/bin/python \
  -m pytest -q -p no:cacheprovider --override-ini addopts= \
  /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/test_import_owner_references.py \
  /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/reviewer-20260913-48Mbci/test_independent_import.py \
  --basetemp /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/reviewer-20260913-48Mbci/run-1 \
  --junitxml /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/reviewer-20260913-48Mbci/results-1.xml
```

Esse é o comando já executado. Uma repetição deve usar nomes novos para
`basetemp` e JUnit, sem sobrescrever os recibos preservados.

| Artefato | SHA-256 |
| --- | --- |
| Helper congelado | `7df411cffd123e82b9aa9e59ab82efcce801a486f8484e16c5f670e6161e6e9b` |
| Testes do autor | `5eec93343c89d1955747cc570dfc093c937bd350bc50faa4b59b56f1938515a8` |
| Instrução privada | `f65f7312666fe24bb11e207e53c142fd2f47d84c24b89c19797b0c4867172b89` |
| Recibo de implementação do autor | `05bd2091fa2b1f99b0ba7233f4aabcfd4c2f13482351b3749499911371cb9cdc` |
| Testes independentes | `9f5f07f57e09c9b6008c108d532b95169d080c6dea39d0eaa00949c7ac2b0c79` |
| JUnit da revisão | `a458ebb9cdf4029dc379003df9d300832aa7d68279ab8f6bd43baa15e90a6682` |
| Manifesto de 64 arquivos sintéticos da revisão | `a100bfc06062fed05a937ea2ab231e87f2ea6d1ef30ad6759621b482fb115299` |

O manifesto está em
`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/reviewer-20260913-48Mbci/review-evidence.json`.
O adendo anterior sobre identidade e formulário permanece inalterado; esta
revisão é específica do conversor e não reavalia o relatório de metadados.


## Adendo — reteste do sucessor `fef95d1`

O texto anterior foi preservado integralmente, com digest predecessor
`aa9e3655d7521cd7d005b1e5ffb96b04b060bc2cd069292124be43ad11abc3d8`.
O candidato inicial está preservado em `calibration-import/candidates/7df411c/`;
as referências de linha da revisão inicial descrevem seus bytes, não eventuais
sucessores do caminho operacional. Este reteste examinou exclusivamente o
sucessor de hash abaixo, no checkout `1b4b1ae7716b656762dcce3023940b29707ef83e`.

**P1 permanece aberto; P3 foi corrigido.** O novo campo obrigatório
`FrozenInputs.protected_output_roots` inclui explicitamente `owner-material`,
`owner-form-20260913` e `owner-form-v3-20260913` na produção. O destino escrito
com a mesma caixa do root protegido e seus descendentes é recusado antes da
leitura de respostas; no ensaio independente, a rota sintética retornou 404.
A instrução agora delimita corretamente a ausência de sobreposição por obra
proposta, identificadores e título normalizado, preservando os 25 casos com
páginas compartilhadas e a ausência de resolução semântica exaustiva.

### P1 — O alias de caixa ainda contorna a proteção HTTP

A condição de destinos proibidos em `import_owner_references.py:274` usa
`Path.is_relative_to`, que compara componentes lexicais. Neste filesystem,
`owner-form-v3-20260913` e `OWNER-FORM-V3-20260913` resolvem para o mesmo par
`st_dev`/`st_ino`, mas o segundo caminho não é lexicalmente relativo ao primeiro.
A consulta de metadados desses caminhos reais foi somente de leitura.

Na fixture independente, `protected_output_roots` continha explicitamente o
root HTTP sintético verdadeiro. O teste trocou somente a caixa do nome desse
root, confirmou `samefile == True` e `is_relative_to == False`, e importou a
exportação artificial por esse alias. A validação nativa passou e o servidor
HTTP do root protegido retornou **200 com os bytes exatos de
`owner-export.json`**. Não se removeu nem esvaziou a lista de proteção para
produzir o resultado. Nenhuma fonte ou resposta real foi lida ou publicada.

A correção deve comparar também a identidade de filesystem dos roots
protegidos com a dos ancestrais existentes do destino, mantendo a proteção
lexical para caminhos ainda inexistentes. A proteção precisa ocorrer antes
da leitura da exportação. A hipótese de outros aliases físicos não foi
necessária à conclusão: a equivalência por caixa foi observada no host e a
publicação correspondente foi reproduzida com dados sintéticos.

### Fluxo válido e evidências do reteste

A importação para um destino privado permitido continua funcionando. O código
exato de exportação JavaScript foi executado com vínculos e respostas
sintéticos; `main()` recebeu `FrozenInputs` sintéticos completos, incluindo os
roots protegidos, e a CLI nativa validou o sucessor de 101 tarefas e seis
campos de extração com código 0. Rótulos, justificativas, locators e extração
conservaram igualdade exata. O digest da suíte sintética permaneceu
`0e78f6e459e0625112689946c110cf96e6a6d925f3cacc2a5cd4fe9338d03289`.
O histórico ausente e o excerto adulterado continuaram sendo recusados.

Foram executados **31 testes do sucessor e 16 verificações independentes:
47 passaram em 4,72 s**. Como na revisão inicial, o teste do bypass passa
porque afirma o defeito observado; ele não é evidência de proteção correta.
Os hashes do candidato foram conferidos antes e depois da execução.
Não foram executados modelos, matriz completa, perfis de navegador ou
calibração científica. Os limites da QA JavaScript e CLI da revisão inicial
continuam aplicáveis.

Os novos testes e recibos estão exclusivamente em
`calibration-import/SYNTHETIC/reviewer-successor-20260913-LJefVT/`.
O comando manteve `PYTHONDONTWRITEBYTECODE=1`, o `PYTHONPATH` do workbench,
`pytest -q -p no:cacheprovider --override-ini addopts=`, usando o arquivo
atual `SYNTHETIC/test_import_owner_references.py` e o novo
`test_independent_successor.py`, com `--basetemp` apontando para `run-1`
e `--junitxml` para `results-1.xml` dentro dessa nova árvore. Os testes
anteriores e seus recibos foram preservados.

| Artefato do reteste | SHA-256 |
| --- | --- |
| Helper sucessor | `fef95d1b48e940305c41e451bd7bc24987bb07580c5d16880c6778f26103b27b` |
| Testes do sucessor | `1b5720af6ae567ba532db49b18f60a5a8180e5db9a47532e893c01392940c92d` |
| Instrução corrigida | `af5b1c4f7faf22790aa29e05f8e84d35d98a558e185ed8e9ae421c5d930fa661` |
| Testes independentes do reteste | `6a5bc65d07310a441b74c3e5b11d6a071a937d10febb5fd41b53753814707cb0` |
| JUnit do reteste | `b77970856eeb211d1099dbe2efc699ff700de3db32aeb1d3e5705abdb1a85e7e` |
| Manifesto de 65 arquivos sintéticos | `566dea4df7679a05eb1fab54b3a70d86f8c413b444067c78eb9a310fdfe0dda6` |

O manifesto está em
`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/reviewer-successor-20260913-LJefVT/review-evidence.json`.


## Adendo final — reteste do sucessor `b2e9a83`

**Estado atual: P1 e P3 resolvidos no candidato examinado; sem novos achados
no escopo desta revisão.** O histórico anterior permanece integralmente
preservado, com digest predecessor
`4a199be3367ac1c2cf2bd7fa6f4fee4c6c297052d36b03ec9db67e299283bb3a`.
O candidato intermediário está em `calibration-import/candidates/fef95d1/`.
Este fechamento refere-se somente ao helper de hash `b2e9a83` abaixo e não
transforma os testes de preparação em aprovação ou execução científica.

A diferença de código foi conferida contra o snapshot intermediário. A nova
função `overlaps_protected_root` preserva a comparação lexical e acrescenta a
comparação de `st_dev`/`st_ino` dos roots protegidos com todos os ancestrais
existentes do destino. O guard é chamado antes da leitura da exportação e da
publicação. A proteção de caminhos sem diretórios ainda criados continua
coberta pela comparação lexical. A instrução mantém os três roots conhecidos
explicitamente proibidos e a formulação qualificada da comparação de sementes.

O ensaio independente configurou explicitamente o root HTTP sintético em
`FrozenInputs.protected_output_roots`. Tanto o caminho original quanto o alias
de caixa para o mesmo inode foram recusados com
`output_must_not_change_frozen_roots`. Em ambos, `read_private` foi substituído
por uma função que falharia caso fosse chamada, demonstrando que a recusa
ocorreu antes de qualquer leitura das respostas. Nenhum destino foi criado e
as duas consultas HTTP sintéticas retornaram **404**. O ensaio não removeu os
roots protegidos nem contornou o guard para fazer a importação passar.

O fluxo permitido continua íntegro: exportação produzida pelo JavaScript
congelado, execução de `main()` com vínculos completos de fontes sintéticas,
resolução nativa das fontes durante a importação e validação pela CLI nativa.
Foram preservadas 50 referências, 101 tarefas e seis campos de extração, com
igualdade exata dos rótulos, justificativas, evidências e extração. A CLI
retornou código 0 e `schema_valid`, com suíte `material_kind=synthetic` de
digest `0e78f6e459e0625112689946c110cf96e6a6d925f3cacc2a5cd4fe9338d03289`.
Histórico ausente e excerto adulterado continuaram produzindo recusa sem
publicação nem exposição do conteúdo de referência no erro.

Foram executados **32 testes do sucessor e quatro retestes independentes:
36 passaram em 4,79 s, sem skips**. Os quatro casos independentes foram
`test_protected_http_root_rejects_before_read_and_returns_404`,
`test_case_alias_of_protected_root_refuses_before_read_and_returns_404`,
`test_js_export_to_helper_cli_and_native_cli` e
`test_cli_missing_history_and_tampered_reference_are_safe`.
Não houve novos probes além da fronteira demonstrada e do fluxo autorizado.

Os testes e recibos novos estão em
`calibration-import/SYNTHETIC/reviewer-final-20260913-V87g88/`. A execução
manteve `PYTHONDONTWRITEBYTECODE=1`, o `PYTHONPATH` do workbench e
`pytest -q -p no:cacheprovider --override-ini addopts=`, com os testes atuais
do autor e os quatro node IDs acima em `test_independent_final.py`.
O `--basetemp` foi `run-1` e o JUnit foi `results-1.xml` nessa nova árvore,
sem sobrescrever ensaios anteriores. Os hashes congelados do helper,
testes e instrução foram reconferidos depois da execução.

| Artefato do reteste final | SHA-256 |
| --- | --- |
| Helper final examinado | `b2e9a83cc02edc373321e1c53c7e416abca86665d95c7718e0374c9404079eee` |
| Testes do sucessor | `1c5c5cf29d28292ec05c6c8b6a5af078c2748975b46ce2d0b674b6841c54a8de` |
| Instrução privada | `c0ab7579f8cf8dfaf2aae3bba54d51d5ab582f7d4b6f278b46d603745d655b3d` |
| Retestes independentes | `cbf081803c32b78a88bce660abb506e8b02fd150b5ea54fe7f4b3842df48fb75` |
| JUnit final da revisão | `e75ebdce65eebc1375990cc0da819f8b2cb95fc69c10627fe7bc10ed665c7994` |
| Manifesto de 61 arquivos sintéticos | `208a9fa9dbb3c8277755cd2d78d409d59dbedad44e57eb55ea5ef9f7e93b0be5` |

O manifesto final está em
`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/SYNTHETIC/reviewer-final-20260913-V87g88/review-evidence.json`.
Não foram lidas respostas humanas, perfis de navegador, `localStorage` ou
fontes restritas. Nenhum modelo, matriz completa ou calibração científica foi
executado. A QA continua limitada à geração JavaScript em VM, importação e
validação com material sintético; não demonstra uso visual ou persistência
real do navegador, autoria do Research Owner ou aceite científico.
