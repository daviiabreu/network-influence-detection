# Continuidade com autenticação validada

Este registro sucede a [continuidade após a conferência](continuation.md),
preservada como histórico. Em 15/09/2026, Davi informou “fiz login”. O preflight
nativo às 22:20:46 UTC confirmou autenticação ChatGPT, assinatura Pro e
disponibilidade de `gpt-5.6-sol`, com runtime e SDK 0.147.0. Não houve geração.
O impedimento anterior de sessão expirada foi resolvido nessa consulta.

Davi também determinou “nao depende do CI remoto, ele ta off” e “vamos continuar
sem”. Esta entrega usa as verificações locais exigidas pelo projeto, sem esperar
o CI hospedado. A dispensa não converte o estado remoto em teste aprovado nem
substitui os critérios científicos.

## Referências e histórico de ajustes

A conferência anterior permanece válida: as 50 referências de triagem e os
seis campos de extração foram adotados pelo chat, com autoria assistida
preservada. Não há motivo para repetir o formulário. Foi preparado um envelope
privado com essas confirmações e histórico de ajustes ainda desconhecido; ele
não é uma suíte importada nem uma declaração de ausência de ajustes.

A auditoria delimitada do Git e dos registros privados encontrou prompts e
configurações dos revisores anteriores à seleção dos casos, sem ajuste posterior
com esses casos nos registros examinados. A preparação e a correção das
referências por IA estão identificadas separadamente. As 25 coocorrências em
páginas bibliográficas não coincidem com obras, identificadores ou títulos dos
leads de desenvolvimento; compartilhar uma página não comprova uso do caso no
ajuste do revisor.

Permanece aberta a pergunta factual sobre ajustes fora do repositório. Ausência
de registro não prova ausência de atividade externa. A resposta poderá
complementar a auditoria; se o histórico continuar desconhecido, o lote não será
apresentado como verificação inédita. Não se alterou o importador para declarar
ausência de ajustes automaticamente.

## Integração da avaliação

Os consumidores passam a receber explicitamente a revisão posterior de cada
campo de extração. O plano versão 2 fixa o arquivo privado e seu hash; a
autorização de execução e o recibo de consumo vinculam a revisão, a decisão do
responsável e o relatório avaliado. A reabertura sem escrita exige os mesmos
bytes já retidos no armazenamento. Os formatos anteriores mantêm sua
serialização. Ver [contrato operacional](../../../../../../docs/process/ic-study-review-runtime.md).

Essa integração permite consumir uma calibração 4 aprovada quando ela existir.
Não preenche julgamentos posteriores em nome do responsável e não transforma
avaliação incompleta ou reprovada em autorização de execução. A revisão
independente identificou a necessidade de distinguir o commit aprovado do
protocolo do commit do código da calibração; são vínculos separados.

Ainda não houve execução dos 101 casos, triagem canônica, extração do corpus ou
síntese aceita. O corpus e sua passagem ao protocolo v4 também permanecem
incompletos. A [atualização das venues](../../../questions/exploration/2026-09-15/venue-priority.md)
recomenda JCSS e JASSS como referências de planejamento, sem escolher o alvo
definitivo ou avaliar a adequação de um manuscrito inexistente.

## Evidência privada

Os arquivos abaixo permanecem em
`/Users/davi/.local/state/research-workbench/research-completion-20260915`,
com diretório 0700 e arquivos 0600. Os hashes identificam os bytes examinados;
nenhuma credencial foi copiada para esses registros.

| Registro | SHA-256 |
| --- | --- |
| `auth-check-20260915T222046Z.json` | `2ff5abc20ae33c4e69144c0fc957ab28dffb5bd48a7df155627728678b6b6810` |
| `tuning-history-audit.md` | `a45db0fca984c567a7b578598dbd43d1d656f544f1ce3f159d316dfe72aed54d` |
| `owner-review-pending-tuning.json` | `9f5597edc55fa67fecb096085bc5ba8e203910b2d10a5023c797d2fba097a693` |

## Validação local da integração

O comando `UV=/Users/davi/.local/bin/uv just quality` passou na revisão
`1e9c87b6717ac845702f544bf1a6c64c36495d4d`, em macOS arm64 com Python 3.12.13:
3.734 testes do workbench e 34 do estudo, estrutura, formatação, lint, tipos e
construção e instalação isolada dos dois wheels. Os testes do workbench levaram
1.113,63 segundos. O único aviso veio da criação deliberada de um ZIP com entrada
duplicada no teste de rejeição de arquivos hostis; o teste passou.

O log privado `quality-calibration-consumers-20260915-path-fixed.log` tem SHA-256
`b82092c57eefa2786d5f76e51550481cda54fb4171d55842cf250ed5939b42e8`.
O recibo `local-validation.json`, SHA-256
`5765518a564c1127bc0e9ed98cfc0204de4525604d93652777378f4a4714fd60`,
registra também a tentativa inicial que parou antes das verificações por não
encontrar `uv` no shell da receita. A execução concluída usou o caminho explícito.

A revisão independente de requisitos encontrou a confusão entre o commit do
protocolo e o da execução. A correção passou por nova inspeção e por uma regressão
que usa o controlador real com commits distintos. A revisão de organização do
código não encontrou problema acionável. Nenhuma dessas verificações executou
a calibração científica ou substituiu a resposta sobre seu histórico.
