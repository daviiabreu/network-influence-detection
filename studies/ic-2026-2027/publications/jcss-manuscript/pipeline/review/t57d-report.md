# T57d — manchete só de B sem as contagens que Results já imprime

Data: 02/10/2026. Base: integração `5d66440a`. Autoridade: decisão delegada do coordenador (decisão 161), estendendo o item 3 da T57c à manchete só de B. Tudo foi aplicado antes da liberação de qualquer resultado dos tiers; nenhum dado selado, log de tier, diretório restricted ou dado SHP foi aberto, e nada do fechamento congelado nem do texto fixo mudou.

## O que mudou

O mesmo princípio da T57c vale agora para a manchete só de B: as contagens ficam em Results, e a Discussão e a Conclusão dão a leitura uma vez cada, remetendo a Results.

- **D-H-B (Discussão).** A frase com as quatro contagens de região virou "Results classify the first boundaries of the complete valid B units by the frozen interval-based regions." A ressalva fica, sem o "These counts" que dependia dos números: "An early point estimate alone does not establish a small region, and an unavailable boundary is not evidence of non-attainment."
- **C-H-B (Conclusão).** A frase com as contagens virou "The first-boundary regions against B, for the complete valid B units, are reported in Results." O fragmento da fronteira atingida, selecionado só com `v4.t1.n_attained > 0`, não mudou.
- **D-B03 (Discussão, manchete só de B sem atingimento pontual).** O pedido nomeia D-H-B e C-H-B. Incluí também D-B03 porque é a mesma manchete no ramo B03 e repetia dois números que o bloco B03 de Results já imprime: a contagem `v4.t1.n_interval_lower_finite` e a faixa `v4.t1.upper_a090_min`–`max`. As duas ressalvas ficam, agora remetendo a Results:
  - onde a banda superior alcançou o alvo, a ausência de atingimento pontual não exclui atingimento dentro da grade;
  - a faixa da banda superior na força máxima trata de limites de banda, não de fronteiras atingidas nem de uma fração de sinal escolhida.

  A frase de leitura (AUC pontual abaixo do alvo até a = 0,90, com constantes de protocolo) e a limitação final não mudaram. C-B03 não imprimia contagens e ficou como estava.

- **Invalidação da curva principal.** D-B02 e C-B02 não mudaram e continuam imprimindo `v4.t1.n_not_valid` e as causas da invalidação.

## Verificação por ramo

Cada variante foi montada e composta a partir das fixtures sintéticas. As variantes com sufixo foram derivadas por alteração de valores: "pares vazios" com `v4.bd.n_eligible = 0`; "B03" com `n_not_attained = 9` e contagens de persistência zeradas.

| Variante                                        | Blocos selecionados                | Contagens só de B em Results             | Contagens só de B na Discussão e na Conclusão   | Frases órfãs |
| ----------------------------------------------- | ---------------------------------- | ---------------------------------------- | ----------------------------------------------- | ------------ |
| H-B sem permissão (`incomplete-tier2`)          | D-H-B, C-H-B, P5-a.1               | as quatro de região (P5-a.1)             | nenhuma                                         | nenhuma      |
| B02 + H-B (`invalid-main`)                      | D-B02, C-B02, D-H-B, C-H-B, P5-a.1 | as quatro de região                      | nenhuma; D-B02 e C-B02 mantêm as da invalidação | nenhuma      |
| H-B com permissão e pares vazios (`passed-shp`) | D-H-B, C-H-B, P5-a.1               | as quatro de região                      | nenhuma                                         | nenhuma      |
| B03 + D-after-B03 (`passed-shp`)                | D-B03, C-B03, B03                  | contagem e faixa da banda superior (B03) | nenhuma                                         | nenhuma      |
| B03 sem permissão (`incomplete-tier2`)          | D-B03, C-B03, B03                  | contagem e faixa da banda superior       | nenhuma                                         | nenhuma      |
| Falha de gate G0 e G2c                          | nenhum destes                      | não se aplica                            | nenhuma                                         | nenhuma      |

O shell de Results não mudou, então nenhum binding saiu de Results. P5-a.1 é selecionado sempre que D-H-B é (PASS e não B03), e o bloco B03 de Results sempre que D-B03 é, com a mesma condição. Nenhum ramo de falha de gate seleciona D-H-B, C-H-B ou D-B03.

A busca por frases que dependem de números ausentes ("These counts", "of them", "those shares", "that share") não achou nada na Discussão nem na Conclusão de nenhuma variante.

## Registros

- `t57d-shell-repin-receipt.json`: repinagem do shell de Discussão e Conclusão contra `5d66440a`, com aceite explícito de D-H-B, C-H-B e D-B03, 241 regras inalteradas, condições e fragmentos preservados.
- Teste novo `test_b_only_headline_counts_stay_in_results`, com cinco casos. Ele confere que Results imprime cada contagem do bloco de Results correspondente e que a Discussão e a Conclusão não imprimem nenhuma das sete contagens só de B. No caso B02, confere também que C-B02 mantém a contagem de invalidação.

## Verificação

Testes com `nice -n 15` e BLAS em uma thread: 648 aprovados e nenhuma falha.

| Conjunto                                             | Aprovados |
| ---------------------------------------------------- | --------- |
| Montador (inclui os 5 casos novos)                   | 194       |
| Derivação                                            | 84        |
| Exportador                                           | 80        |
| Relatório (inclui `test_frozen_files_are_untouched`) | 95        |
| Exploratório                                         | 58        |
| Projeção pública                                     | 93        |
| Gate-only                                            | 15        |
| Propagation                                          | 24        |
| Sucessor v4.4                                        | 5         |

Ruff (check e format) e mypy passam no teste tocado, e `scripts/check_repository.py` passa nas 7 checagens.

Montagem sintética só de B (`invalid-main`: D-B02, D-H-B, C-B02, C-H-B) compilada com `tectonic --only-cached` e a classe Springer de `review-20261001/passed-shp` (SHA-256 `36d0c327…`): exit 0, sem erro LaTeX, sem overfull e sem referência indefinida.

## Alerta operacional

Em 02/10, por volta das 11:00 UTC, o cache do Tectonic (`~/Library/Caches/TectonicProject.Tectonic`) estava vazio de novo; o diretório tinha sido apagado por fora desde a recarga de 01/10. A compilação `--only-cached` falhou ao gerar o formato LaTeX. Uma compilação online da montagem sintética recarregou o cache (45 MB), e a compilação offline passou em seguida.

A cadeia pós-liberação compila offline. Convém conferir o cache no dia da liberação, ou deixar a cadeia recarregá-lo antes da compilação.
