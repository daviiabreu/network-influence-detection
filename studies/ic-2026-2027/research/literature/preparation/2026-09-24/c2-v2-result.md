# Preparação C2 v2 — 24/09/2026

A preparação nativa terminou em modo somente leitura sobre o commit
`a952582f47798c80404dbd39ae8b79fe82a02657`. O runtime reproduziu a aquisição,
a preparação e o recibo original de metadados e validou a cadeia Git-bound
v3 → v4 → v5, incluindo a aprovação editorial v5 registrada em 24/09.

O request contém oito escolhas preexistentes: quatro `title_resolved` e quatro
`explicitly_untitled`, com as evidências, identificadores e recortes originais.
Africa Today (`metadata.v1.ea8185255c7dc5d57ab30655`) foi omitido do request e
continua adiado. Nenhuma escolha individual foi aprovada, nenhum `OwnerDecision`
foi criado e C2 não foi executado. Não há conclusão de elegibilidade ou corpus
pronto para triagem.

As recomendações assistidas no request, a confirmar caso a caso contra a fonte
e o recorte exato preservados, são:

| Candidato | Disposição proposta | Fonte de identificação aprovada |
| --- | --- | --- |
| `metadata.v1.0e18d44d37cf2642f10b72ae` | `explicitly_untitled` | `web-jstor-seer-2013` |
| `metadata.v1.2549f65cfc14c6b88e8f661f` | `title_resolved` | `springer-learning` |
| `metadata.v1.2b16f287360d30fbd72386e5` | `explicitly_untitled` | `web-jstor-seer-2015` |
| `metadata.v1.8a79703d6ac027039213a5f9` | `title_resolved` | `joia-publisher` |
| `metadata.v1.8b2b44dc633a7d71814adc05` | `explicitly_untitled` | `web-jstor-penn` |
| `metadata.v1.b1a486199ea6c6fee2c9a177` | `explicitly_untitled` | `web-jstor-jah-2003` |
| `metadata.v1.c6b942a2d4575be4a7f3f3b0` | `title_resolved` | `springer-settlement` |
| `metadata.v1.d42cd08313775db8cb6ed4cc` | `title_resolved` | `springer-policy` |

| Vínculo | Valor |
| --- | --- |
| Recibo original | `6b16e1cb9954ee505a592121d697fb58c56b444e3c430c8360301625ceb4dd82` |
| Escolhas privadas de 16/09 | `eeff79017bbf1bd25a7f886128e87916713a3e383eca249422d151ef48264553` |
| Request C2 v2 | `52e450054c46b9a506c399baabc43cf6c327a811d622031433fe494d10d6a509` |
| Ação | `metadata-resolution-v2.52e450054c46b9a506c399ba` |
| Preparado em UTC | `2026-09-24T13:18:09.987379+00:00` |

Os bytes exatos estão retidos em
`/Users/davi/.local/state/research-workbench/research-area-20260924-c2-v2-52e45005/request.json`,
acompanhados de `preparation-proof.json` (SHA-256
`816bc7c5076b9d558239e1462c949381072a2d73dbafd72e7c9b67a757821e24`)
e do CAS `policy-artifacts/`. A saída original foi criada em
`/private/tmp/c2-v2-20260924-qrr4wtfb/`; a cópia create-once para a nova pasta
privada foi comparada recursivamente, byte a byte, com a origem. O diretório
durável tem modo `0700`, request e prova modo `0400`, e os hashes foram
reconferidos após a cópia. O request e os recortes restritos não foram copiados
para Git.

O [script de preparação](c2-v2-prepare.py) usa os três runtimes predecessores e
`ReviewCorpusMetadataResolutionV2Runtime` com `read_only=True`. A união de CAS
somente permite leitura dos artefatos existentes; os novos bytes de aprovação e
protocolo ficam exclusivamente no CAS temporário. A validação nativa conferiu
fontes, permissões, registros, identificadores completos e offsets dos oito
casos. Os 11.840 arquivos existentes inventariados mantiveram tamanho e mtime;
o diretório operacional C2 permaneceu vazio. Essa comparação de inventário não
é uma nova declaração de hash sobre todos os arquivos privados.

Ruff lint e formatação passaram para o script; `git diff --check` passou. O teste
funcional foi a preparação nativa sobre os dados reais. A próxima decisão deve
referenciar o request exato e seus 15 hashes de evidência exigidos, preservados
na prova privada. A aprovação da política não substitui essa decisão.

Após revisão, as garantias do script passaram de `assert` a checagens explícitas.
Uma segunda preparação com `python -O`, no mesmo `prepared_at`, reproduziu o
request e o SHA-256 exatos em `/private/tmp/c2-v2-20260924-lf_djgjn/`; nenhuma
decisão ou operação C2 foi gravada.

A [apresentação curta dos oito casos](c2-v2-decision-brief.md) traduz os IDs
para DOI, obra, título proposto, fonte e justificativa, sem copiar os recortes
restritos para Git.

Após a aprovação separada dessas oito escolhas, o
[sucessor C2 v2 parcial](c2-v2-execution-result.md) foi registrado e
reproduzido. Esta nota permanece como histórico da etapa de preparação, não
como estado atual do corpus.
