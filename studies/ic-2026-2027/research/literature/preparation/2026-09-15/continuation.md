# Continuidade após a conferência

As 50 propostas de triagem e os seis campos de extração foram adotados pela
declaração “conferido, pode seguir”. A
[decisão registrada](../../../decisions/2026-09-15-calibration-reference-adoption.md)
preserva a autoria assistida e a confirmação pelo chat. Não é preciso repetir
o formulário. A informação ainda ausente é se esses casos ou suas fontes já
foram usados para ajustar critérios, prompts ou configurações dos revisores.
Se houve ajuste, ou se o histórico não puder ser informado, o lote não será
apresentado como verificação inédita.

A [regra de avaliação](extraction-adjudication-method.md), fundamentada na
[pesquisa de fontes primárias](extraction-evaluation-evidence.md), está expressa
na [política versionada](extraction-evaluation-policy-v1.json). Seu SHA-256
canônico é `207ca2c5a323e3e0e35da1e8ef7fc1a1c305acfc97f8eeea7a931571171c6d1d`;
os hashes da regra e da fundamentação foram calculados dos arquivos presentes.
O método exige adjudicação posterior de cada campo, além das validações
automáticas. Os textos e localizadores adotados permanecem preservados.

O preflight confirmou 101 tarefas e 73 objetos de fonte retidos. A checagem
específica da correção confirmou que os 18 localizadores distintos das
referências de extração estão cobertos pelos 28 blocos originais fornecidos
ao agente. Isso valida a cobertura do material, sem criar uma suíte científica
ou preencher o histórico de ajustes.

O preflight remoto de 15/09/2026 falhou antes de qualquer inferência. A RPC de
limites retornou HTTP 401 com `token_expired` para a credencial dedicada. A
verificação do SDK confirmou a causa, sem alterar a credencial nem iniciar
geração. A existência do arquivo e suas permissões corretas não comprovam um
login válido. É necessário renovar a sessão dedicada com interação do titular.

Para renovar apenas esse login, executar no Terminal:

```bash
env CODEX_HOME=/Users/davi/.config/research-workbench/codex \
  /Users/davi/Documents/github/research-workbench/workbench/.venv/lib/python3.12/site-packages/codex_cli_bin/bin/codex \
  --config 'forced_login_method="chatgpt"' \
  --config 'cli_auth_credentials_store="file"' \
  login --device-auth
```

Seguir a URL e o código exibidos pelo comando na própria sessão. Não enviar
tokens ou o arquivo de autenticação pelo chat. Esse comando faz somente o
login; a disponibilidade da assinatura e do modelo será verificada novamente
pelo preflight nativo antes de iniciar a calibração.

Depois de registrar o histórico real e validar a sessão, a continuação é
compilar o envelope da adoção já feita, importar com
`import-assisted-calibration --extraction-evaluation-policy` e os demais
vínculos privados, validar as fontes, executar os 101 casos e reproduzir os
recibos. A avaliação das respostas reais virá depois, com 20% das obras de
triagem e todos os campos de extração. Os gates podem exigir correções e
uma nova seleção; a implementação não garante aprovação científica.

O corpus nativo e sua ponte para produção v4 continuam incompletos. Os
consumidores de produção também precisam receber explicitamente a adjudicação
de extração para aceitar uma suíte 4. Uma futura aprovação pelo CLI não
habilita esses consumidores silenciosamente. Não houve nova aquisição,
triagem canônica, síntese ou escolha final de venue nesta continuação.

Os registros privados desta etapa ficam fora de Git em
`/Users/davi/.local/state/research-workbench/calibration-adoption-20260915`,
com diretório 0700 e arquivos 0600. A referência de execução e seus limites
constam em `execution-preflight.md`; o diagnóstico de cobertura não é uma
execução de revisores. A validação de engenharia e a entrega são registradas
separadamente de qualquer futura conclusão científica.

A matriz completa de engenharia executou 3.721 testes do workbench: 3.720
passaram e um encontrou uma importação relativa incompatível com a execução
direta do CLI. A correção usa importação absoluta; os 114 testes afetados,
incluindo o caso que falhou e a importação assistida, passaram depois dela.
Também passaram os 34 testes do estudo, `just check` nos dois projetos e a
construção e verificação isolada dos dois wheels. A matriz completa não foi
repetida após essa correção localizada, conforme a política do repositório.
A revisão independente não encontrou bloqueador no método de calibração.
