# Resolução editorial C2 v2 — sucessor parcial

Em 24/09/2026, Davi respondeu “tudo aprovado” à pergunta da coordenação que
incluía as [oito escolhas apresentadas](c2-v2-decision-brief.md). O
`OwnerDecision` privado registra a adoção **desse conjunto exato**, não uma
declaração de leitura pessoal dos recortes restritos. A decisão C2 não abrange
*Africa Today*, identidade entre obras, elegibilidade ou aceitação científica.

| Vínculo imutável | SHA-256 ou valor |
| --- | --- |
| Request aprovado, 4 `title_resolved` + 4 `explicitly_untitled` | `52e450054c46b9a506c399baabc43cf6c327a811d622031433fe494d10d6a509` |
| Ação | `metadata-resolution-v2.52e450054c46b9a506c399ba` |
| `OwnerDecision`, com os 15 hashes exigidos | `7dd27faa55087f44f56e37a3ea05e3b371779adb9314f481a219a9576ca28118` |
| Commit da aprovação do protocolo v5 no contexto C2 | `a952582f47798c80404dbd39ae8b79fe82a02657` |
| Recibo C2 v2 | `ee1822e5101bf7d44208e27c711aa946d0f7aa23ff257a912ac7df7f5efe806a` |
| Projeção C2 v2 | `f8d6d0d0f8aadbd5b48518d48e1b4fc2203ca4969897c687a3d67136500da573` |
| `proposal_basis_v2` | `80f4652d855e299ea938dd2f9f8f485583ddae772cc2717f25a8a32b8e7a39d9` |
| Manifesto das propostas de identidade regeneradas | `9bc03a05b79664a7a7e9cb574415f5370bc88580a24af166cac2ac3befc0555c` |

O [operador versionado](c2-v2-execute.py), commit `539987e`, revalidou em modo
somente leitura o request, a prova, as oito escolhas originais, a cadeia de
aprovação v3 → v4 → v5, fontes, permissões e offsets. Depois publicou o request
e a decisão em um CAS privado novo, executou o runtime C2 v2 uma única vez e
reproduziu o recibo em modo somente leitura, inclusive em processo separado.
O manifesto de execução e o resultado foram publicados em modo create-once;
nenhum recibo anterior foi reescrito.

O sucessor tem `metadata_status=incomplete`, `outcome=incomplete`,
`screening_ready=false` e `scientific_eligibility_assessed=false`. Quatro títulos
foram incorporados apenas à projeção de obras, quatro obras permanecem com
título nulo e estado `explicitly_untitled`, e *Africa Today*
(`metadata.v1.ea8185255c7dc5d57ab30655`) é o único candidato de metadados
não resolvido. Observações adquiridas, result-3 e conflitos originais seguem
preservados.

A base nativa exportada contém 46.400 obras e dois pares adicionais introduzidos
pelos títulos recuperados. O gerador independente de propostas 3.2.0 rodou no
commit `539987e`, com semente `20260917`, os três inputs originais vinculados
por SHA-256 e a base C2 acima. O resultado completo tem 20.966 pares em 10.756
cartões, dois pares/cartões a mais que o pacote v3.1; ambos os novos cartões
ficaram em `T4.contradicting_identifiers`, pendentes de auditoria humana. Nenhuma
fusão ou escolha de identificador foi adotada pelo Owner; nenhuma decisão C3
foi registrada.

Os artefatos restritos estão fora de Git, em
`/Users/davi/.local/state/research-workbench/research-area-20260924-c2-v2-52e45005/`:
`execution/` guarda CAS, journal, manifesto, resultado e base de propostas;
`identity-proposals-v2/` guarda os cartões, amostra, cenários e manifesto.
Diretórios verificados em `0700`, arquivos de manifesto/base em `0400`.
O `execution-result.json` foi publicado antes da exportação e, por isso,
mantém `proposal_basis_sha256=null`; a base e o manifesto posteriores registram
o SHA acima sem reescrever esse primeiro resultado.

Validação local: 46 testes focados do runtime e da recuperação passaram; Ruff
lint e formatação do operador, estrutura do repositório (7 verificações),
publicação atômica e revisão independente dos eixos de contrato e manutenção
passaram. A matriz integrada permanece com a coordenação central. O próximo
gate científico é resolver *Africa Today* por fonte e política adequadas e
auditar as propostas de identidade; este resultado não permite C3 final, C4
ou triagem.
