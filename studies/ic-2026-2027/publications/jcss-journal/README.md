# Versão da revista (JCSS)

Esta pasta guarda a versão do artigo editada para os leitores da JCSS depois da
liberação da v4, em 08/10/2026. Ela sucede, no plano editorial, a tentativa
montada pelas regras congeladas `assembly-xdj406x0` (handoff
`release-handoff-20261008-t58`, relatório e montagem no commit `eb6e9882`, PDF
com SHA-256 `c1a255db…1aee`). Essa tentativa continua sendo o registro
pré-especificado e vai para o depósito sem alteração.

## Por que existe

Em 09/10/2026, quatro pareceres independentes leram o PDF montado: editor,
área, métodos e um parecerista adversarial de outra família de modelo
(decisões 264 a 267 do log). Os quatro consideraram a ciência correta e sem
análise faltando, mas o texto ilegível para a revista: longo, cheio de códigos
internos, com o resultado escondido e sem posicionamento na literatura de
identificação de influência. Em 13/10/2026, Davi delegou a revisão (decisões
268 e 269).

## Regras

1. Todo resultado numérico do texto usa `\resultnum{chave}{valor}`. O valor é
   conferido contra `values/result-values-final.json`, cópia byte a byte do
   arquivo da tentativa (SHA-256 `38ab7ab6…2979`), e contra
   `values/journal-values.json`, que reúne tabulações novas de valores já
   liberados, geradas por código.
2. A leitura feita depois da liberação aparece rotulada como tal no texto.
3. Nada aqui altera o protocolo congelado, os critérios, as sementes ou os
   resultados liberados.
4. O texto montado pelas regras e as regras de leitura pré-escritas ficam
   arquivados no depósito, para que a proteção contra leitura seletiva continue
   verificável.

## Origem dos arquivos

`main.tex`, `sections/`, `generated/` e `references.bib` foram copiados de
`manuscript-assembled/` da tentativa, sem as seções do mapa sistemático, que é
uma entrega separada. `values/result-values-final.json` veio da mesma
tentativa. As alterações seguintes estão no histórico do Git.

## Como compilar e conferir

Na pasta, `python3 build.py` copia as fontes para uma pasta temporária, compila
`esm.tex`, `main.tex` e `esm.tex` de novo com o tectonic fixado e roda `check.py`. O
`check.py` confere cada `\resultnum` contra os três arquivos de valores, as citações, as
referências cruzadas entre os dois PDFs, os rótulos internos e em português proibidos no
artigo e as contagens de palavras. `python3 build.py --submission` também falha com
marcadores `[AT SUBMISSION …]` abertos.

## Onde está cada coisa

- `main.tex` e `sections/`: o artigo, que termina nas referências.
- `esm.tex` e `esm/`: o Online Resource 1, com seções S1 a S12, tabelas S… e figuras S….
- `generated/journal-*.tex` e `generated/J*.pdf`: tabelas e figuras geradas por
  `ic_study.analysis.v4_journal_export` a partir dos artefatos liberados. Os demais
  `generated/*.tex` são cópias das exportações da tentativa, com rótulos traduzidos para
  o inglês e valores inalterados. `check.py` confere as amarrações.
- `generated/online-resource-2-units.csv`: o Online Resource 2, a tabela das 414
  unidades com rótulos de status em inglês. O CSV original, com os rótulos em português,
  é `generated/T1s_a_star_all_units.csv`.
- `values/`: os valores da tentativa, os valores gerados para a revista e os transcritos
  de registros exploratórios, cada um com sua fonte.
- `literature-verification.md`: a conferência de cada referência nova ou alterada.
- `cover-letter.md`: a carta ao editor.
