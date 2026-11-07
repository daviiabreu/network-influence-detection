# Ponte sintética entre os estimadores de âncora e o r da simulação (exploratória)

Execução de 28/09/2026 da Adição 2 do [sucessor 1 do pré-registro SHP](../../../research/questions/exploration/2026-09-24-parallel/shp-reliability-successor-1.md), congelado em [shp-reliability-successor-1-freeze.json](../../../research/questions/exploration/2026-09-24-parallel/shp-reliability-successor-1-freeze.json). A análise é exploratória, não lê microdados do SHP e não entra em nenhuma regra confirmatória da v4. Rodou antes de qualquer acesso aos dados do SHP e antes de qualquer resultado confirmatório de `a*(r)`.

## Execução

O código é o commit `17a0dbed`, o mesmo vinculado no congelamento do sucessor (`source_dirty: false`). Os painéis vêm do gerador congelado da v4 (`37513841`), com a geometria SHP do estudo e o canal ordinal de 11 categorias tratado como contínuo, exatamente como a âncora trata o SHP. São 99 células (braço de interação em `G × R`, mais a família B com φ = 0,85 e peso de traço η ∈ {0,25; 0,50} em cada `r`) e 10 réplicas por célula. As sementes vêm da raiz 20260928, no namespace `shp-crosswalk-v1`.

O host de exploração foi o homelab (Linux x86_64, 12 threads), em quatro fragmentos, com 17.512 s de CPU no total. A proveniência completa, com hashes dos módulos, sementes e host, está em [crosswalk.json](crosswalk.json).

## Resultado descritivo

A tabela traz a média, entre as 10 réplicas, do `r` de 2004 estimado pelo quase-simplex principal em cada `r` da simulação, e a média do STARTS em duas colunas de referência. Entre parênteses, o número de réplicas em que o STARTS falhou pelas regras declaradas.

| r da simulação | braço de interação, a = 0 | a = 0,9 | B, η = 0,25 | B, η = 0,5 | STARTS, a = 0 (falhas/10) | STARTS, B η = 0,5 (falhas/10) |
| -------------: | ------------------------: | ------: | ----------: | ---------: | ------------------------: | ----------------------------: |
|           0,50 |                     0,477 |   0,480 |       0,468 |      0,465 |                 0,482 (6) |                     0,477 (0) |
|           0,55 |                     0,522 |   0,528 |       0,513 |      0,510 |                 0,525 (4) |                     0,522 (0) |
|           0,60 |                     0,572 |   0,575 |       0,563 |      0,560 |                 0,575 (6) |                     0,574 (0) |
|           0,65 |                     0,621 |   0,626 |       0,613 |      0,610 |                 0,624 (2) |                     0,625 (0) |
|           0,70 |                     0,672 |   0,677 |       0,663 |      0,659 |                 0,675 (5) |                     0,674 (0) |
|           0,75 |                     0,723 |   0,726 |       0,714 |      0,710 |                 0,725 (4) |                     0,724 (0) |
|           0,80 |                     0,773 |   0,778 |       0,766 |      0,763 |                 0,775 (2) |                     0,776 (0) |
|           0,85 |                     0,825 |   0,827 |       0,818 |      0,815 |                 0,826 (3) |                     0,828 (0) |
|           0,90 |                     0,877 |   0,880 |       0,871 |      0,868 |                 0,881 (2) |                     0,881 (0) |

Nesta geometria, o quase-simplex estima o `r` de 2004 cerca de 0,02 a 0,03 abaixo do `r` da simulação no braço de interação. Nas referências com traço, a diferença sobe para cerca de 0,03 a 0,04. Parte da diferença vem da discretização por postos em 11 categorias, que acrescenta erro à escala tratada como contínua. A parte maior com traço é o viés do modelo sem traço que o parecer interno apontou, mas com φ = 0,85 ele é bem menor que o do exemplo do parecer, que usava φ = 0,5. O STARTS fica mais perto do `r` da simulação quando há traço. Quando não há traço, o que é o caso do braço de interação, ele falha em parte das réplicas pela regra da variância no limite, e falha em todas com a = 0,9. Isso é o esperado para um modelo cujo componente de traço é nulo.

## Uso

Pelo sucessor, a F6 pode mostrar ao lado do posicionamento bruto da âncora, rotulado como "ponte sintética, exploratória", o conjunto de valores de `r` da grade cujos intervalos entre réplicas contêm a estimativa SHP, para `a = 0` e para as duas referências B. O relatório v4 lê este arquivo pela opção `--crosswalk`. A ponte não substitui o posicionamento bruto, não escolhe `r` e não altera a curva.

Para reproduzir, siga o [guia da âncora](../../../research/questions/exploration/2026-09-24-parallel/shp-reliability-guide.md), seção "Ponte sintética", no commit `17a0dbed`.
