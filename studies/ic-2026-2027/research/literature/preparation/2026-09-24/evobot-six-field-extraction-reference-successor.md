# EvoBot v3: vínculos privados para seis valores adotados

Atualização de 24/09/2026: Davi aceitou explicitamente o conteúdo das seis
referências como está e aprovou os 24 vínculos afirmação→trecho. A
[decisão do responsável](../../../decisions/2026-09-24-evobot-extraction-owner-decisions.md)
registra o alcance; o envelope e o manifesto originais abaixo permanecem
imutáveis. A execução histórica continua `fail`, sem aceitação científica da
revisão.

Em 24/09/2026, foi preparado um envelope `ExtractionReferenceSuccessor`
**opt-in e não adotado** para o caso de desenvolvimento
`verification.extractor.work.v2.e618414ee47714dd46aca671`. O contrato usado é
o da Engenharia em `485a9b0` (`calibration_extraction_reference_successor.py`,
SHA-256 `20f50418331a7c4c5ccdf8e900e381484f31c6e6fd40925d56e5164e293009f6`),
importado somente para construir e validar; aquele checkout não foi alterado.

O pacote privado, criado uma vez fora do Git, está em
`/Users/davi/.local/state/research-workbench/autonomous-review-20260915/evobot-extraction-reference-successor-20260924/`.
O diretório tem permissão `0700` e os dois arquivos, `0400`:

| Arquivo | SHA-256 | Função |
| --- | --- | --- |
| `successor.json` | `50504f951f29d9441f45247074d43526117d6bc547daba41eea7deac604476f6` | Envelope nativo, com os seis valores e status literais já adotados. |
| `manifest.json` | `544d6503589c03b2bb6f633dbd5ac917ac9ed8b9298695d844f24e3d4ff20a9f` | Linhagem, intervalos precisos da projeção, hashes e estados Owner vazios. |

A entrada é a suíte original SHA-256
`efaf237f3ab0b028bd82ca5a92c43bde25d350cf7ad2d308a4808b9ef5ae7f81`,
partição `development`, com o pacote de decisão SHA-256
`7ac338a31a7299acf59564c27de420caa9f9b8fb0c905cbbf1b84e0bcf677b60`.
O [mapa anterior dos seis campos](evobot-six-field-adopted-evidence-audit.md)
tem pacote privado de suporte SHA-256
`f620c803d8e20cb731f28d471f40ad9e9519c032f6f22ebffdbf0b8f328e0d7d`,
vincula o PDF EvoBot v3 SHA-256
`a7eea3ee9fbdaf40403b2a0fc5de2c2fd780021aa853fef0aecff01c2c986f0c`
à projeção SHA-256
`bb25c8ac262e16494419451688283308cd23baba82226de7dbac44b45d878713`.
O envelope vincula 24 trechos **literais** desses valores a 12 dos 28
`EvidenceLocator` exatos da tarefa original. O manifesto conserva 33
intervalos de linha mais estreitos para a conferência humana. Nenhum número,
cadência, fórmula ou métrica derivados da [nota exploratória anterior](evobot-two-field-reference-successors.md)
foi incorporado como nova exigência.

O builder e o validator nativos passaram no objeto e na releitura do JSON
persistido; o round-trip preservou valores, status, IDs, partições de campos e
os digests canônicos da tarefa
`b05e14cdb99ed62943b1b676b9eca85ae8220b821f60568cdfade2b13734eb72`
e da referência anterior
`32d7e40958451929291ec1833d0596f6b7ad73203655a474ce25a241798ccda4`.
A revisão independente conferiu os 24 vínculos contra a projeção. Ela pediu um
localizador adicional para que a afirmação sobre escores de sentimento tivesse
suporte próprio; o ajuste foi feito e reconferido antes da publicação.

Esta é uma proposta de evidência, não um `ExtractionResult` de agente nem
uma referência sucessora aprovada. `owner_assessment` e `adoption` continuam
`null`; `scientific_acceptance=false`. Não houve extração por provider,
experimento, replay, nova aquisição, alteração da suíte/configuração ou da
matriz congelada `ec3de5d`. O resultado da execução de desenvolvimento
`3044d04` permanece `fail`. Avaliação de suporte/completude científica e
eventual adoção cabem ao Research Owner.
