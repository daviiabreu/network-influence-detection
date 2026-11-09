# Candidatos disjuntos para nova calibração de título/resumo

Em 24/09/2026, uma seleção sem rótulos foi reproduzida dos artefatos retidos da
aquisição v3. São **50 obras propostas**, suficientes para preparar 50 tarefas
por revisor de título/resumo. Isto ainda não é uma coorte de verificação
cientificamente aceita: faltam conferência de identidade e elegibilidade,
referências, histórico de ajustes e auditoria do responsável.

## Fonte e saída privada

O gerador reproduzível é [verification-cohort-select.py](verification-cohort-select.py).
Ele confere SHA-256 antes de ler os três objetos CAS de deduplicação
(`41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53`),
observações projetadas
(`93c8086aa6b0231fd019291f9bb3984e5e436e629c4424e95ae499729957cc85`)
e relatório de páginas
(`edfa48474097d7c81e441fdbe5089a924d514deabbb6baf3bbaf60e0df220a11`).
Também confere a suíte de desenvolvimento
`efaf237f3ab0b028bd82ca5a92c43bde25d350cf7ad2d308a4808b9ef5ae7f81`,
além de registrar os hashes da seleção v3 anterior, da auditoria do legado,
dos 64 desafios e das 16 sementes no manifesto.

Os dois arquivos foram criados com modo 0600 no diretório 0700
`/private/tmp/verification-cohort-20260924-v2/`:

| Arquivo | Bytes | SHA-256 |
| --- | ---: | --- |
| `candidate-manifest.json` | 50.464 | `ada4fa6347c287269b35953660452629d5c7470db7ece1679ac7a36bdc02a717` |
| `corpus-selection.json` | 9.463.057 | `b76c67837d9f5d230f04f1732e6b8c6e732c4a27c5f0cc627ba64cf17196cdc4` |

O manifesto identifica, por obra, os IDs das manifestações e das observações,
o SHA-256 das requisições e páginas originais, a fonte e a família da consulta.
O segundo arquivo é uma entrada `calibration-corpus-selection-2` para a etapa
nativa de scaffold. Nenhum contém julgamento de inclusão, referência ou resposta
do responsável. `/private/tmp` é efêmero e **não é retenção científica durável**;
estes arquivos são candidatos reproduzíveis, não um registro canônico. Antes de
autoria ou execução, copiar por uma transição create-once para um repositório
privado durável autorizado, preservando modo, bytes e hashes, e revalidar as
fontes. Esta tarefa não teve permissão para gravar nessa raiz durável.

## Política e contagem

O gerador lê 46.391 obras propostas com título. Reserva as 50 obras da suite de
desenvolvimento e as 50 do material legado v3 (100 IDs distintos), suas 146
páginas bibliográficas e os respectivos IDs de observação, identificadores e
títulos normalizados. Exclui ainda observações na fila de identidade e colisões
de DOI/identificador ou título com os 64 desafios e as 16 sementes. Uma obra
entra como candidata só se todas as suas manifestações preservadas passarem
esses filtros e houver ao menos um representante em Q01–Q16. Resultaram 26.288
obras propostas elegíveis **para sorteio**, sem julgamento científico.

A semente textual fixa `20260924-verification-candidates-v1` ordena por SHA-256.
O algoritmo tenta três obras distintas por família Q01–Q16, com preferência
OpenAlex, arXiv e DBLP; onde a fonte/família se esgota, mantém as disponíveis.
Acrescenta até duas obras anteriores a 1995, mas dentro do recorte a partir de
1970, e completa os 50 lugares por uma ordenação SHA-256 global dos candidatos
restantes. Não é amostra aleatória de prevalência do corpus.

| Medida da seleção | Resultado |
| --- | ---: |
| Obras / observações de suas manifestações | 50 / 64 |
| Requisições / páginas bibliográficas | 59 / 59 |
| Representantes OpenAlex / arXiv / DBLP | 23 / 10 / 17 |
| Representantes sem resumo | 21 |
| Famílias presentes | 15 de 16 |
| Família sem representante após filtros | Q07 |
| Texto completo / referência do responsável | 0 / 0 |

Q07 sem candidato sob esta reserva de páginas é uma limitação da seleção, não
evidência de ausência de trabalhos na área. Os 21 casos sem resumo exigem
atenção na autoria das referências. A distribuição de julgamentos positivos,
negativos e incertos ainda é desconhecida; os limiares do protocolo não podem
ser avaliados com esta seleção sem a autoria e conferência correspondentes.

## Prova mecânica e limite científico

O manifesto registra interseções vazias entre os 50 selecionados e o conjunto
reservado nos seis eixos verificados: `work_id`, ID de observação, SHA-256 de
página, identificador bibliográfico, título normalizado e observações na fila
de identidade. A execução exige cardinalidade 50 e essas seis interseções
vazias antes de publicar os arquivos. O gerador pode ser repetido com uma nova
diretoria vazia sob `/private/tmp`; entradas inalteradas devem produzir os
mesmos dois hashes. Isso foi conferido numa segunda execução independente em
`/private/tmp/verification-cohort-20260924-v3/`: `cmp` confirmou igualdade de
ambos os arquivos, byte a byte. Para reproduzir com outra diretoria vazia:

Após a revisão independente, as garantias foram convertidas de `assert` para
checagens explícitas. Uma nova execução com `python -O` em
`/private/tmp/verification-cohort-20260924-v4/` reproduziu os mesmos dois
SHA-256 e as seis interseções vazias; otimização do interpretador não remove
mais o gate.

```sh
PYTHONDONTWRITEBYTECODE=1 workbench/.venv/bin/python \
  studies/ic-2026-2027/research/literature/preparation/2026-09-24/verification-cohort-select.py \
  --repository-root /Users/davi/.codex/worktrees/18d2/research-workbench \
  --private-root /Users/davi/.local/state/research-workbench/broad-research-20260911 \
  --output /private/tmp/verification-cohort-replay-new
```

A checagem nativa adicional carregou a seleção pelo contrato
`CalibrationCorpusSelectionV2` e reproduziu as 59 fontes a partir dos bytes
CAS por `build_calibration_scaffold_v2`: 50 entradas, 100 casos cegos de
triagem, 100 julgamentos e justificativas ainda com `OWNER_TODO_SENTINEL`,
zero casos de extração. Nenhum modelo foi chamado.

Essa prova cobre igualdade exata e títulos normalizados no estado proposto do
corpus; não resolve possíveis aliases bibliográficos ainda não adjudicados,
exposição histórica fora dos conjuntos examinados ou acerto científico das
referências. O corpus v3 segue incompleto. O histórico de ajuste da configuração
de execução é desconhecido. Logo, a fase `verification` não pode ser declarada
pela existência desta seleção. O mesmo vale para a extração: não há texto
completo novo nem referência de seis campos aqui.

## Próxima transição nativa

Depois de reter duravelmente os dois JSON e conferir as 50 identidades,
executar `systematic-review scaffold-calibration` com o protocolo **v3** de
origem, `--phase verification`, esta `corpus-selection.json`, o CAS original
e uma saída privada create-once. A função nativa já reproduziu as fontes sem
escrever o scaffold. O scaffold ainda trará sentinelas; sua construção não
estabelece que a fase de verificação é válida. A API do scaffold preenche
`tuning_history=no_prior_tuning` como valor inicial técnico; esse campo deve ser
substituído por pendência até haver declaração real, como feito na preparação
anterior, e jamais aceito como prova histórica. A adoção assistida sob o protocolo
v4 precisa de proposta, revisão e importação nativas com proveniência; o
histórico de tuning deve ser declarado a partir de evidência real. Se houve
ajuste com estas obras ou seu material, deve-se selecionar outro conjunto.
Só depois de referências completas e validação cabem execução, auditoria de
20% das obras e decisão do Research Owner. A triagem de texto completo e a
extração exigem materiais próprios.
