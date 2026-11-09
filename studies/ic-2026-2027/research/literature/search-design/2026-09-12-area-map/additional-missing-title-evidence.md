# Dois registros adicionais sem título próprio

A consulta OpenAlex q16 acrescentou dois DOIs sem título ao conjunto final.
Esta verificação de 12 de setembro de 2026 complementa a
[checagem dos sete registros anteriores](missing-title-evidence.md), preservada
em seu pacote original. Os localizadores da aquisição constam no
[inventário das dez observações](../../searches/2026-09-12-v3-missing-title-records.json).

| DOI | Evidência primária consultada | Resultado e limite |
| --- | --- | --- |
| `10.2979/africatoday.65.1.08` | [Registro JSTOR](https://www.jstor.org/stable/10.2979/africatoday.65.1.08) | A projeção aberta informa “Review: [Untitled]” no título do documento; o corpo expõe apenas um marcador de imagem. |
| `10.5215/pennmaghistbio.141.1.0092` | [Edição oficial JSTOR](https://www.jstor.org/stable/10.5215/pennmaghistbio.141.issue-1) e [registro individual](https://www.jstor.org/stable/10.5215/pennmaghistbio.141.1.0092) | O índice primário marca a entrada como sem título e como resenha. A abertura da edição confirma o link para o DOI; o registro individual não expõe metadados legíveis. |

No primeiro caso, o [registro institucional CityU](https://scholars.cityu.edu.hk/en/publications/book-review-longman-timothy-2017-memory-and-justice-in-post-genoc/)
apareceu no índice com DOI explícito e descrição de resenha do livro de Timothy
Longman. Sua abertura foi bloqueada pela ferramenta. No segundo, a descrição
do livro de Jessica Choppin Roney pertence à obra resenhada; o vínculo ao DOI
foi conferido no link 24, linha 25 da projeção da edição. O rótulo de resenha
sem título e a autoria da resenha permanecem evidência do índice primário.
Nenhum título próprio verificável foi adotado para preencher os registros.

Foram feitas cinco buscas e cinco aberturas iniciais de URLs distintas,
incluindo um clique na edição. Não houve nova tentativa após bloqueios,
contorno de acesso ou importação de metadados. As evidências são excertos e
metadados da ferramenta, com limitações de extração e de data de rastreamento;
os hashes não representam corpos HTTP originais.

O pacote privado está em
`/Users/davi/.local/state/research-workbench/broad-research-20260911/untitled-additional-two-evidence-20260912/`.
Os 11 arquivos do manifesto tiveram tamanho e SHA-256 conferidos na revisão.
O pacote anterior de sete DOIs permaneceu inalterado.

| Artefato | SHA-256 |
| --- | --- |
| `manifest.json` | `d4544fabd9e18a53fd261b6afad44de3b572e58fe9bf8b61cc058f6c01dd4262` |
| `metadata-resolution.json` | `60e1d58b898381b269b9e68a82a37972f7f23db9b0294345e5a5df8aa29f4bf9` |
| `report.md` | `21a84a3bb440742636a054df9ab52ae1b41eb124b502d31ab89268d316973223` |

Os dois campos `article_title` continuam nulos. A checagem não modifica o
protocolo, a aquisição, identidades ou decisões de elegibilidade.
