# Texto completo para preparar um caso de extração

Em 13/09/2026, foi adquirido e ingerido um texto completo entre os 50 casos
novos de calibração: V3-29, obra proposta `work.v2.e618414ee47714dd46aca671`.
Isso prepara uma tarefa de extração; não fornece uma referência humana nem
estabelece elegibilidade ou fidelidade de extração.

A versão fixa é [arXiv:2508.17711v3](https://arxiv.org/abs/2508.17711v3),
*Enhancing LLM-Based Social Bot via an Adversarial Learning Framework*, de
Fanqi Kong, Xiaoyuan Zhang, Xinyu Chen, Yaodong Yang, Song-Chun Zhu e Xue Feng
(2025). A página dessa versão declara
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Sua entrada Atom
retida na aquisição v3 identifica exatamente a versão 3, atualizada em
16/09/2025, antes do corte do protocolo. Não foi usada uma versão posterior
à adquirida na busca.

A captura conservou a página da versão, a declaração de licença e o PDF
original, fora do Git. A representação textual derivada registra a atribuição,
a licença e o fato de ser uma transformação do PDF. Nenhum texto foi alterado
no original.

| Artefato | SHA-256 | Bytes |
| --- | --- | ---: |
| Página arXiv da versão 3 | `2a8a21d7b1452fde03e00d0a102fd4c36ba62d0685112bb5b7b05086dcd51cf9` | 43055 |
| Declaração CC BY 4.0 | `231a5dac65bbf135ba27145969a63cd289faadc172f1512c4810a6c60ba91036` | 32178 |
| PDF original | `a7eea3ee9fbdaf40403b2a0fc5de2c2fd780021aa853fef0aecff01c2c986f0c` | 11640818 |
| Projeção textual nativa | `bb25c8ac262e16494419451688283308cd23baba82226de7dbac44b45d878713` | 105413 |
| `FullTextRecord` | `ac9adff69ca7c58bee0882a38b2b9df1aa54a014ca707dc9baac2e57e4c07396` | 2047 |

Foi usada a API existente `ingest_full_text`, em código da revisão
`b1f8bea6574137ce176ddfd5aecab5d158e93c1f`, com a política v3 e os limites
nativos. O parser `pypdf-6.17.0-plain-strict-v1` produziu 26 páginas com texto,
estado `available`. O título da primeira página corresponde ao registro e um
locator estrutural foi reproduzido diretamente do PDF. Esse teste não escolheu
evidência para uma resposta humana.

Os recibos, o script de aquisição e as fontes estão em
`/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/fulltext-v3/`.
PDF, projeção e registro também foram acrescentados ao CAS
`broad-research-20260911/acquisition-v3/artifacts`, sem reescrever os artefatos
anteriores. O protocolo permanece com SHA-256
`fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f`.

O [processo de ingestão](../../../../../../docs/process/systematic-review-full-text.md)
distingue uma projeção disponível da leitura científica correta de fórmulas,
tabelas e figuras. Essa leitura ainda cabe à autoria da referência. Um único
texto não equivale aos 50 casos exigidos para calibrar uma etapa de triagem
por texto completo. O caso preparado mede apenas extração, se suas referências
forem efetivamente preenchidas e os demais requisitos passarem.
