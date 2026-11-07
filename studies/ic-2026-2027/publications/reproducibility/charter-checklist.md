# Cobertura da carta do estudo

Este checklist mapeia os requisitos da [carta](../../research/charter/study-charter.md),
principalmente “Evidence and reproducibility”, ao pacote preparatório. `[x]` significa
que o mecanismo está documentado ou demonstrado no exemplo; `[ ]` depende da
pergunta e dos resultados futuros. Não constitui aceitação científica.

| Requisito da carta | Onde verificar | Estado |
| --- | --- | --- |
| Procedimento recuperável | `README.md`, `Makefile`, `regenerate_fragmentation.py` | [x] exemplo; [ ] experimento final |
| Respostas brutas e versões de fontes recuperáveis | `future-run-manifest.template.json` (`inputs`), hashes dos pilotos no manifesto original | [x] convenção; [ ] catálogo final e direitos de depósito |
| Exclusões e emendas recuperáveis | `future-run-manifest.template.json` (`lineage`, `protocol_approval_record`), protocolo do experimento futuro | [x] campos; [ ] decisões registradas |
| Revisão de código e fontes | `future-run-manifest.template.json` (`code_revision`, `source_sha256`), recibo offline do exemplo | [x] exemplo; [ ] revisão final |
| Ambiente travado | `README.md`, `.python-version`, `uv.lock`, campos `environment` e `lock_sha256` | [x] convenção; [ ] ambiente final conferido |
| Parâmetros, unidades e sementes | `future-run-manifest.template.json` (`design`, `seed_streams`, `runs`); `spec.json` do piloto | [x] convenção; [ ] grade registrada |
| Saídas imutáveis, correção por sucessor | `README.md`, campos `runs.outputs` e `lineage`; saída nova do exemplo | [x] exemplo; [ ] sucessores futuros |
| Validação distinta da aprovação do pesquisador | `offline-validation.json` gerado pelo exemplo, campos `validation` | [x] integridade offline; [ ] aprovação científica |
| Replay distinto de regeneração | `README.md`, `regenerate_fragmentation.py` | [x] distinção e demonstração |
| Pacote público sem conteúdo restrito | `README.md` e `data-availability.md` | [x] regra; [ ] auditoria do depósito |
| Emenda sucessora e gates recuperáveis | `README.md` (G0, G1b, G1c, G2, G2c), freeze v4 e segundo vínculo R6 | [x] sequência documentada; [ ] freeze, vínculos e recibos reais |
| Inventário, tiers e shards íntegros | `README.md` (seis tiers, hashes e estados), manifestos de fase/shard futuros | [x] contrato descrito; [ ] execução e conferência de hashes |
| Reprodutibilidade entre hosts | `README.md`; `scripts/xhost_probe.py` na branch paralela | [x] condição documentada; [ ] sonda integrada e identidade byte a byte |
| Figuras e tabelas regeneráveis | `README.md`; módulo em `research/v4-reporting` | [x] fluxo documentado; [ ] módulo integrado, arquivos liberados e comparação |
| Dados e depósito | `data-availability.md`, `README.md` | [x] ausência de microdados SHP declarada; [ ] conta/aprovação do Research Owner, DOI e revisão de direitos |
| Manuscrito pronto junto ao pacote até 2026-10-31 | mapa de afirmações e manuscrito na publicação futura | [ ] fora deste esqueleto |
