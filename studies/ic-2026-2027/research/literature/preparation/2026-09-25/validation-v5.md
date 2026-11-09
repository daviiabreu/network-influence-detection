# Validação e revisão independente do v5

Em 25/09/2026, a implementação passou por revisão independente nos eixos
Spec e Standards, separada da autoria. Os achados foram corrigidos antes do
commit: parada antiga por rendimento, cobertura vazia de categorias, pares
ambíguos não adjacentes, verificação incompleta do plano de lote, evidência de
extração sem vínculo à obra, contagem de registros projetados como originais,
e incorporação do adendo de duas famílias. Os revisores não encontraram novos
defeitos acionáveis no escopo reexaminado. Isso não é auditoria humana nem
adoção de referências de elegibilidade.

| Verificação | Resultado observado |
|---|---|
| Testes v5, protocolo e manifests do repositório | 33 passaram; exit 0 |
| Regressões de calibração, proveniência de referências e protocolo histórico | 153 passaram; exit 0 |
| Suíte completa do estudo IC | 167 passaram; exit 0 |
| `just check`, ambos os projetos | Passou; estrutura, Ruff e mypy, exit 0 |
| `just build`, ambos os projetos | Wheels e smoke tests passaram; exit 0 |
| JSON v5 e projeção de contexto | Parser nativo e integração dos manifests passaram |
| `OwnerDecision` e envelope | Validados nativamente; SHA-256 dos bytes conferido |
| Replay do driver | Plano do lote 1 idêntico, 500 obras, zero chamadas de modelo |
| Artefatos privados v2 | Dez hashes conferidos na revisão independente; 200 IDs idênticos no pacote/coorte, 20 por decil, 20 marcados para auditoria adicional; zero sobreposição com exposições/sementes registradas |
| Permissões | Diretório de preparação `0700`; pacote e artefatos `0600` |
| `git diff --check` | Sem erro |

O `just quality` completo **não passou**. A tentativa encontrou quatro falhas
nos novos manifests (registro de papéis, fixtures, documentação e orçamento
de contexto), todas corrigidas e reexecutadas com sucesso no conjunto focado.
A execução foi interrompida em `tests/recovery/test_focused_attempts_backup.py`
após 433 segundos, com 1.208 testes passados e aquelas quatro falhas no
snapshot anterior. O resultado dessa tentativa não é um gate verde para o
snapshot final. O teste de recuperação já tinha histórico de paralisação;
não foi removido, ignorado ou marcado xfail. Nenhuma conclusão de regressão
resolvida ou de matriz completa foi derivada desse bloqueio.

Logs locais: `/private/tmp/broad-map-v5-quality.log`,
`/private/tmp/broad-map-v5-check-final.log`,
`/private/tmp/broad-map-v5-build.log` e
`/private/tmp/broad-map-v5-study-tests.log`. O cache uv usado foi
`/private/tmp/uv-broad-map-v5`. Antes do commit, `check_repository.py` é
executado novamente conforme as regras de delegação.

Continuam abertos os gates científicos: inventário histórico de exposição,
referências duais, acordo/adjudicação, calibração A/B, camada 0 codificada,
identidade dos pares efetivamente triados, extrações e saturação. O executor
Claude ainda é requisito de produção; o driver entregue é offline.
