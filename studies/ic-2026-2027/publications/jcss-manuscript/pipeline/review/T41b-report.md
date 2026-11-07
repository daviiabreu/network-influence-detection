# T41b — montador nos shells integrados

Worktree `research/shell-assembler`, HEAD inicial `127d02d0`, com T41 `6285dbbf` e merge `6b959187`. Sem commit ou push. Somente o escopo autorizado foi alterado; shells, seções, exportadores, figuras, tabelas e arquivos congelados permanecem intactos.

A cobertura passa de 264/264 regras expressáveis da T41 para 267/267. As 264 identidades anteriores permanecem. Os dois blocos novos T36 e a exigência geral non-PASS têm regras próprias, cada uma com linha do shell. Nenhuma dependência unsupported.

Repinagem: 5 trechos visíveis aceitos por ID, 7 comentários revisados, 204 deslocamentos e 48 trechos intactos. A abertura A.design fica somente em 13:13; o diff também incluía a nota editorial 15. O recibo separa o resultado da repinagem mecânica das adaptações semânticas finais.

O comando reutilizável está em [repin_v4_manuscript_assembly.py](repin_v4_manuscript_assembly.py); uso em [ASSEMBLY.md](../ASSEMBLY.md). [Recibo por ID](t41b-shell-repin-receipt.json). Testes cobrem inserção antes do trecho, comentário interno, mudança visível com/sem aceite, remoção inteira e de fragmento, digest antigo incorreto, ID desconhecido e limite explícito para excluir nota editorial.

A auditoria completou os 24 casos, sem recusas, mantendo as 24 fontes manuais e os catálogos registrados com os mesmos hashes da T41. Foram 591 divergências de composição: 386 fragmentos omitidos/parafraseados, 141 trechos fixos de Discussion, 24 de Conclusion, 24 resumos e 16 ordens de exibição. Há 150 novas, 8 desaparecidas e 49 com texto alterado. Toda divergência atual segue o shell no lado do montador; isso não transforma toda paráfrase em incompatibilidade científica. As oito desaparecidas eram D-X5-POST sem X5 fornecido. [JSON completo](v4-manuscript-assembly-audit-2026-09-30.json) registra cada caso, linha, lado e explicação.

Os textos fixos integrados DS01, DS02, DS06, DS10 e CN01 foram preservados. DS01 separa largura e região; DS02 exige permissão global e leitura estrita; DS06 distingue limites de matching/cobertura/inventário; DS10 remove RC28; CN01 restringe novas sementes a PASS e usa every-stage nos demais gates. Nenhuma seção foi corrigida nesta tarefa.

Prova anterior aos digests: worktree limpo `6fce4b508b193177ef726ff7a3dd02efae089b13`; Python do worktree autorizado, com imports isolados das duas fontes. Os três digests anteriores reproduziram exatamente seus valores esperados. Em cada catálogo, as únicas adições são os 15 IDs `v4.gate.<estágio>.verdict.*`; ao retirá-los, a serialização JSON inteira é byte a byte igual à anterior. [Prova e capturas](t41b-verdict-catalog-proof.json). Apenas esses três digests foram substituídos.

| Caso | IDs antigos | SHA-256 anterior = projetado | SHA-256 atual |
| --- | ---: | --- | --- |
| gate | 99 | `31f322512701c66129b544bdbc1e84384eadcad275f4a9db089360b67bb44aeb` | `265e6f0ca927c985d3e3ff6c7be081cca12f0f2ef7ad4348509fc3274f300842` |
| gate+exploratory | 10956 | `82b9b7cd8ee6f9dd79fd3cd0467b803b5d7e9bbc73d539d66132bf8006905ae8` | `953086e7bca477898bde9cbc064df84749ef2ae63f35efd61c2b1b3594c67531` |
| gate+exploratory-x1b | 11116 | `62c80d588c27d0dc7213f98d32d1e96ee5d76548044ce72144bb33b075131b48` | `ec617a5fb3afe85921253d6ab92371eee92e06e434a196fc47ac40451b90cb25` |

Portões em um supervisor, filhos sequenciais, OMP/OPENBLAS/MKL/VECLIB = 1: ruff check e format --check dos sete Python tocados; mypy dos mesmos sete; pytest em quatro processos distintos. 141 testes do montador, 52 exploratórios, 80 do exportador e 1 check de arquivos congelados: 274 passaram. `git diff --check` passou. Dependências já presentes; não foi necessário uv sync nem download. Logs: `/private/tmp/t41b-gates-i8key6sm/results.json`.

Durante o ajuste, a primeira auditoria recusou o resumo por incluir a nota editorial no hunk da abertura. A primeira rodada de testes encontrou etiquetas X5 omitidas pelo recorte histórico; foram repostas a partir dos catálogos públicos com fonte e hash. Uma execução intermediária falhou porque a fixture ainda não havia sido gravada após a tentativa de ler catalog.json no caso gate-only; corrigida para a-catalog.json. Nenhuma regressão foi removida, xfailada ou suprimida. A rodada final acima passou integralmente.

Regras originais tocadas — decisão individual:

| ID | Tipo | Linhas antigas → atuais | Decisão |
| --- | --- | --- | --- |
| `B1a` | comment-only | 117-134 → 117-135 | T38b: comentário INCLUDES adia T3/F4 até depois da resposta F1/F2B/T1. Condição e slot P2 corretos; montador ajusta exibição sem mover P2. |
| `B1b-G0` | displacement | 138-155 → 139-156 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1b-G1b` | displacement | 159-176 → 160-177 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1b-G1c` | displacement | 180-197 → 181-198 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1c` | displacement | 201-214 → 202-215 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1b-G2` | displacement | 218-246 → 219-247 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1b-G2c` | displacement | 250-269 → 251-270 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1d` | displacement | 273-284 → 274-285 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1-END` | displacement | 288-295 → 289-296 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B1-SHP` | displacement | 299-322 → 300-323 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B02` | comment-only | 326-345 → 327-347 | T38b: comentário INCLUDES ordena F1/F2B/T1 antes de inventário e gate. Predicado de invalidação e substituição P4 mantidos; exibição ajustada. |
| `B02.lead` | displacement | 338-338 → 340-340 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B02.gate` | displacement | 340-340 → 342-342 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B02.a0gap` | displacement | 341-341 → 343-343 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B02.clock` | displacement | 342-342 → 344-344 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B02.limits.1` | displacement | 343-343 → 345-345 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B02.limits.2` | displacement | 344-344 → 346-346 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B03` | displacement | 349-363 → 351-365 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04` | displacement | 367-387 → 369-389 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04.low.1` | displacement | 376-376 → 378-378 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04.low.2` | displacement | 377-377 → 379-379 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04.low.3` | displacement | 378-378 → 380-380 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04.low.4` | displacement | 379-379 → 381-381 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04.low.5` | displacement | 380-380 → 382-382 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04.low.6` | displacement | 384-384 → 386-386 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B04.zero` | displacement | 386-386 → 388-388 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B05` | displacement | 391-405 → 393-407 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B06` | displacement | 409-423 → 411-425 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B07` | displacement | 427-438 → 429-440 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B08` | displacement | 442-464 → 444-466 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B08.main.1` | displacement | 457-457 → 459-459 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B08.main.2` | displacement | 458-458 → 460-460 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B08.main.3` | displacement | 459-459 → 461-461 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B08.main.4` | displacement | 460-460 → 462-462 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B08.main.5` | displacement | 461-461 → 463-463 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B08.dependency` | displacement | 463-463 → 465-465 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B09` | displacement | 468-478 → 470-480 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B10` | displacement | 482-500 → 484-502 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B10.bd.1` | displacement | 493-493 → 495-495 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B10.bd.2` | displacement | 494-494 → 496-496 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B10.bd.3` | displacement | 495-495 → 497-497 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B10.be` | displacement | 498-498 → 500-500 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B10.bc` | displacement | 499-499 → 501-501 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B11` | displacement | 504-521 → 506-523 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B12` | displacement | 525-539 → 527-541 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B12.inventory` | displacement | 532-532 → 534-534 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B12.region.1` | displacement | 534-534 → 536-536 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B12.region.2` | displacement | 535-535 → 537-537 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B12.scope.1` | displacement | 536-536 → 538-538 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B12.scope.2` | displacement | 537-537 → 539-539 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B12.scope.3` | displacement | 538-538 → 540-540 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B13` | displacement | 543-558 → 545-560 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B14` | displacement | 562-584 → 564-586 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B15` | displacement | 588-598 → 590-600 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B16` | displacement | 602-614 → 604-616 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B17` | displacement | 618-627 → 620-629 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `B00` | comment-only | 631-719 → 633-773 | T38b: comentários INCLUDES estabelecem prioridade de exibição, destinos e legendas. Texto P1–P10 e predicados preservados; montador emite F1/F2B/T1, T4/F5, T3/F4, F6. Legendas já pertencem aos exportadores integrados e são preservadas. |
| `SECONDARY-SUPPLEMENT` | displacement | 722-728 → 776-782 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P1.1` | displacement | 646-646 → 700-700 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P1.2` | displacement | 647-647 → 701-701 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P1.3` | displacement | 648-648 → 702-702 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P3.1` | displacement | 653-653 → 707-707 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P3.2` | displacement | 654-654 → 708-708 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P3.3` | displacement | 655-655 → 709-709 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P4` | displacement | 658-658 → 712-712 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P5-a.1` | displacement | 662-662 → 716-716 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P5-a.2` | displacement | 663-663 → 717-717 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P5-b.range` | displacement | 666-666 → 720-720 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P5-b.crossing` | displacement | 667-667 → 721-721 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P5-c` | displacement | 669-669 → 723-723 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P6-a` | displacement | 673-673 → 727-727 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P6.lead` | displacement | 675-675 → 729-729 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P6.counts` | displacement | 677-677 → 731-731 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P6-c` | displacement | 680-680 → 734-734 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P6-d` | displacement | 683-683 → 737-737 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P6-e` | displacement | 685-685 → 739-739 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P6-f` | displacement | 687-687 → 741-741 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P7-a` | displacement | 691-691 → 745-745 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P7-b` | displacement | 693-693 → 747-747 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P7.offset` | displacement | 695-695 → 749-749 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P7-c` | displacement | 697-697 → 751-751 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P7-c1` | displacement | 699-699 → 753-753 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P7-c2` | displacement | 701-701 → 755-755 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P7-d` | displacement | 705-705 → 759-759 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P8.1` | displacement | 708-708 → 762-762 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P8.2` | displacement | 709-709 → 763-763 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P8.3` | displacement | 710-710 → 764-764 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P8.4` | displacement | 711-711 → 765-765 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P9` | displacement | 714-714 → 768-768 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P9.diagnostics` | displacement | 715-715 → 769-769 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `P10` | displacement | 718-718 → 772-772 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-H-BD` | displacement | 41-47 → 51-57 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-H-BD` | displacement | 49-54 → 59-64 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-H-B` | displacement | 56-62 → 66-72 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-H-B` | displacement | 64-69 → 74-79 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-B03` | displacement | 71-79 → 81-89 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-B03` | displacement | 81-86 → 91-96 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-D-AFTER-B03` | displacement | 88-94 → 98-104 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-D-AFTER-B03` | displacement | 96-101 → 106-111 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-B02` | displacement | 103-109 → 113-119 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-B02` | displacement | 111-116 → 121-126 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-NO-PERMISSION` | displacement | 118-124 → 128-134 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-NO-PERMISSION` | displacement | 126-131 → 136-141 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-T2-INCOMPLETE` | displacement | 133-139 → 143-149 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-T2-INCOMPLETE` | displacement | 141-146 → 151-156 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-PERMISSION` | displacement | 148-154 → 158-164 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-PERMISSION` | displacement | 156-161 → 166-171 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-EMPTY-PAIRS` | displacement | 163-168 → 173-178 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-EMPTY-PAIRS` | displacement | 170-175 → 180-185 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BD-PERSISTENCE` | displacement | 177-183 → 187-193 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-BD-PERSISTENCE` | displacement | 185-190 → 195-200 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BD-INCONCLUSIVE` | displacement | 192-197 → 202-207 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BD-BOTH` | displacement | 199-205 → 209-215 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BD-NO-CROSSING` | displacement | 207-212 → 217-222 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BE-PERSISTENCE` | displacement | 214-219 → 224-229 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BC-PERSISTENCE` | displacement | 221-226 → 231-236 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BOUNDARIES-DIFFER` | displacement | 228-234 → 238-244 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-BOUNDARIES-DIFFER` | displacement | 236-241 → 246-251 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BOUNDARIES-SAME` | displacement | 243-248 → 253-258 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-BOUNDARIES-SAME` | displacement | 250-255 → 260-265 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-BOUNDARIES-NO-VALID` | displacement | 257-262 → 267-272 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-BOUNDARIES-NO-VALID` | displacement | 264-269 → 274-279 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-PRECISION` | displacement | 271-277 → 288-294 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-IMPLICATION` | displacement | 279-284 → 296-301 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X5` | displacement | 286-291 → 303-308 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-X5` | displacement | 293-298 → 310-315 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X5-POST` | visible-text | 300-308 → 317-325 | T36: crossings vira attainments; SELECT exige X5 fornecido. Acrescentado fato com fonte de proveniência e todas as nove etiquetas disponíveis. Ação DS11 mantida. |
| `D-X6-DENOMINATORS` | displacement | 310-320 → 335-345 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-INTERVAL` | displacement | 322-327 → 347-352 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-FAILURE` | displacement | 329-335 → 354-360 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-SUBNOMINAL` | displacement | 337-343 → 362-368 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-INCONCLUSIVE` | displacement | 345-351 → 370-376 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-NO-READING` | displacement | 353-359 → 378-384 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-ABSENT` | displacement | 361-367 → 386-392 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-ADEQUATE` | displacement | 369-375 → 394-400 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X6-CONSERVATIVE` | displacement | 377-382 → 402-407 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-X6-UNDERCOVERAGE` | displacement | 384-389 → 409-414 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-X6-NOT-ESTABLISHED` | displacement | 391-396 → 416-421 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-X6-RESTRICTED` | displacement | 398-403 → 423-428 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X1B` | displacement | 405-413 → 430-438 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X1B-NO-RELEASE` | displacement | 415-420 → 440-445 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-SCOPE` | displacement | 422-429 → 447-454 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-READINGS` | displacement | 431-438 → 456-463 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-GAPS` | displacement | 440-447 → 465-472 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOST` | displacement | 449-455 → 474-480 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-DOMAIN` | displacement | 457-462 → 482-487 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X4-SCOPE` | displacement | 464-470 → 489-495 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X4-NORMAL` | displacement | 472-478 → 497-503 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X4-PAIRED` | displacement | 480-486 → 505-511 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X4-SIZE` | displacement | 488-494 → 513-519 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X4-DOMAIN` | displacement | 496-501 → 521-526 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-POST-AVAILABILITY` | displacement | 503-510 → 528-535 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X7-SCOPE` | displacement | 512-520 → 537-545 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X7-GAIN` | displacement | 522-528 → 547-553 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X7-CLOSE` | displacement | 530-536 → 555-561 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X7-OTHER-STATES` | displacement | 538-544 → 563-569 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-SHP-ADMISSIBLE` | displacement | 546-552 → 571-577 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-B13-OUT` | displacement | 554-560 → 579-585 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-B13-PART` | displacement | 562-567 → 587-592 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-B14` | displacement | 569-576 → 594-601 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-B14-ENVELOPE` | displacement | 578-583 → 603-608 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-B15` | displacement | 585-591 → 610-616 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-GATE-SHP` | comment-only | 593-599 → 618-624 | T36: parênteses no comentário tornam explícita a precedência já implementada; SHP admissível exclui B14. Condição e ação mantidas. |
| `D-SHP-NOT-RUN` | comment-only | 601-606 → 626-631 | T36: comentário SELECT explicita not B14; condição agora explicita a exclusão, redundante nos estados fechados. Slot e texto mantidos. |
| `C-SHP-ADMISSIBLE` | displacement | 608-613 → 633-638 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-B13` | displacement | 615-620 → 640-645 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-B14` | visible-text | 622-627 → 647-652 | T36: retira pressuposição de resultado simulado; colocação empírica passa a referir-se à análise. Predicado B14 e slot C3 continuam corretos. |
| `C-B15` | displacement | 629-634 → 654-659 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-GATE-SHP` | comment-only | 636-641 → 661-666 | T36: parênteses no comentário tornam explícita a precedência já implementada; SHP admissível exclui B14. Condição e ação mantidas. |
| `C-SHP-NOT-RUN` | comment-only | 643-648 → 668-673 | T36: comentário SELECT explicita not B14; condição agora explicita a exclusão, redundante nos estados fechados. Slot e texto mantidos. |
| `D-G2C` | displacement | 650-658 → 675-683 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-G2C` | visible-text | 660-667 → 685-693 | T36: acrescenta requisito de aprovação de todos os estágios antes de novas sementes. Condição G2c completo falho e ação C1 permanecem corretas. |
| `D-CLOSE` | displacement | 669-675 → 695-701 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `C-CLOSE` | visible-text | 677-682 → 703-709 | T36: acrescenta requisito de todos os estágios antes de novas sementes. Condição encerramento sem gate completo e ação C1 permanecem corretas. |
| `C-GATE-IMPLICATION` | displacement | 684-689 → 711-716 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R050` | displacement | 693-702 → 720-729 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R055` | displacement | 704-713 → 731-740 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R060` | displacement | 715-724 → 742-751 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R065` | displacement | 726-735 → 753-762 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R070` | displacement | 737-746 → 764-773 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R075` | displacement | 748-757 → 775-784 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R080` | displacement | 759-768 → 786-795 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R085` | displacement | 770-779 → 797-806 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `D-X3-LOCAL-R090` | displacement | 781-790 → 808-817 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.design` | visible-text | 13-13 → 13-13 | T38a: nova abertura pela pergunta, AUC por painel e corte convencional 0.03; condição universal e posição inicial preservadas. Oráculo atual separado do ensaio histórico. Limite explicitamente corrigido para a citação 13:13; nota editorial 15 não pertence ao resumo. |
| `A.new-seeds` | displacement | 17-17 → 19-19 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.every-stage` | displacement | 21-21 → 23-23 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.limitation` | displacement | 25-25 → 27-27 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.G` | displacement | 31-31 → 33-33 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B02` | displacement | 35-35 → 37-37 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.H-BD` | displacement | 39-39 → 41-41 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.H-B` | displacement | 43-43 → 45-45 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.P6-a` | displacement | 47-47 → 49-49 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.P6-empty` | displacement | 51-51 → 53-53 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B03` | displacement | 55-55 → 57-57 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.D-after-B03` | displacement | 59-59 → 61-61 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B10` | displacement | 63-63 → 65-65 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B06` | displacement | 67-67 → 69-69 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.X6` | displacement | 73-73 → 75-75 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B09.1` | displacement | 85-85 → 87-87 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B09.2` | displacement | 87-87 → 89-89 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B09.3` | displacement | 89-89 → 91-91 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B04` | displacement | 93-93 → 95-95 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B05` | displacement | 97-97 → 99-99 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B08` | displacement | 101-101 → 103-103 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B11` | displacement | 105-105 → 107-107 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B14` | displacement | 109-109 → 111-111 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B1b-G0` | displacement | 119-119 → 121-121 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B1b-G1b` | displacement | 123-123 → 125-125 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B1b-G1c` | displacement | 127-127 → 129-129 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B1c` | displacement | 131-131 → 133-133 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B1b-G2` | displacement | 135-135 → 137-137 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B1b-G2c` | displacement | 139-139 → 141-141 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.B1d` | displacement | 143-143 → 145-145 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `A.X` | displacement | 147-147 → 149-149 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |
| `X6-READING-LABEL` | displacement | 34-36 → 44-46 | Somente remapeamento de linhas e fragmentos; texto visível, condição e ação correspondem ao mesmo bloco. |

Regras acrescentadas para o shell integrado:

| ID | Linha(s) | Decisão |
| --- | --- | --- |
| `C-EVALUATION-PASS` | 281-286 | Novo bloco T36, incorporado com condição e slot literais do shell. |
| `D-X5-POST-UNAVAILABLE` | 327-333 | Novo bloco T36, incorporado com condição e slot literais do shell. |
| `C-EVALUATION-REQUIRED` | 692-692 | T36 linha 28 exige requisito de todos os estágios em toda conclusão non-PASS. Usa a sentença literal 692 nos demais gates, sem duplicá-la em G2c ou close. |

Divergências novas, desaparecidas ou com texto alterado — explicação por ocorrência:

| Ensaio | Caso | Mudança | Tipo / bloco | Explicação |
| --- | --- | --- | --- | --- |
| dress | failed-G0 | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | failed-G0 | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | failed-G0 | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | failed-G0 | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | failed-G0 | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | failed-G0 | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | failed-G0 | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-REQUIRED | A instrução geral T36 para non-PASS exige todos os estágios antes de novas sementes; este gate anterior a G2c recebe a sentença literal, sem afirmar avaliação realizada. Lado atual: montador. |
| dress | i-comparison-failed | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | i-comparison-failed | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | i-comparison-failed | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | i-comparison-failed | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | i-comparison-failed | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | i-comparison-failed | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | i-comparison-failed | new | selected-shell-fragment-missing-or-paraphrased / C-G2C | T36 acrescenta à conclusão da falha em G2c a exigência de todos os estágios antes de qualquer avaliação em sementes reservadas; o ensaio omite ou desloca a sentença. Lado atual: montador. |
| dress | ii-comparison-no-ratio | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | ii-comparison-no-ratio | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | ii-comparison-no-ratio | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | ii-comparison-no-ratio | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | ii-comparison-no-ratio | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | ii-comparison-no-ratio | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | ii-comparison-no-ratio | new | selected-shell-fragment-missing-or-paraphrased / C-G2C | T36 acrescenta à conclusão da falha em G2c a exigência de todos os estágios antes de qualquer avaliação em sementes reservadas; o ensaio omite ou desloca a sentença. Lado atual: montador. |
| dress | iii-comparisons-absent | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | iii-comparisons-absent | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | iii-comparisons-absent | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | iii-comparisons-absent | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | iii-comparisons-absent | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | iii-comparisons-absent | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | iii-comparisons-absent | new | selected-shell-fragment-missing-or-paraphrased / C-G2C | T36 acrescenta à conclusão da falha em G2c a exigência de todos os estágios antes de qualquer avaliação em sementes reservadas; o ensaio omite ou desloca a sentença. Lado atual: montador. |
| dress | incomplete-tier2 | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | incomplete-tier2 | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | incomplete-tier2 | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | incomplete-tier2 | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | incomplete-tier2 | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | incomplete-tier2 | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | incomplete-tier2 | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | incomplete-tier2 | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | incomplete-tier2 | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| dress | invalid-main | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | invalid-main | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | invalid-main | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | invalid-main | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | invalid-main | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | invalid-main | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | invalid-main | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | invalid-main | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | invalid-main | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| dress | passed-shp | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | passed-shp | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | passed-shp | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | passed-shp | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | passed-shp | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | passed-shp | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | passed-shp | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | passed-shp | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | passed-shp | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| dress | unavailable | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | unavailable | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | unavailable | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | unavailable | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | unavailable | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | unavailable | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | unavailable | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | unavailable | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | unavailable | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| dress | x6-failure | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | x6-failure | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | x6-failure | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | x6-failure | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | x6-failure | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | x6-failure | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | x6-failure | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | x6-failure | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | x6-failure | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| dress | x6-inconclusive | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | x6-inconclusive | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | x6-inconclusive | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | x6-inconclusive | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | x6-inconclusive | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | x6-inconclusive | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | x6-inconclusive | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | x6-inconclusive | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | x6-inconclusive | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| dress | x6-no-reading | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | x6-no-reading | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | x6-no-reading | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | x6-no-reading | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | x6-no-reading | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | x6-no-reading | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | x6-no-reading | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | x6-no-reading | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | x6-no-reading | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| dress | x6-subnominal | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| dress | x6-subnominal | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| dress | x6-subnominal | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| dress | x6-subnominal | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| dress | x6-subnominal | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| dress | x6-subnominal | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| dress | x6-subnominal | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| dress | x6-subnominal | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| dress | x6-subnominal | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| g2c-failure | i-comparison-failed | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| g2c-failure | i-comparison-failed | new | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| g2c-failure | i-comparison-failed | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| g2c-failure | i-comparison-failed | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| g2c-failure | i-comparison-failed | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| g2c-failure | i-comparison-failed | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| g2c-failure | i-comparison-failed | changed-text | selected-shell-fragment-missing-or-paraphrased / C-G2C | T36 acrescenta à conclusão da falha em G2c a exigência de todos os estágios antes de qualquer avaliação em sementes reservadas; o ensaio omite ou desloca a sentença. Lado atual: montador. |
| g2c-failure | ii-comparison-no-ratio | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| g2c-failure | ii-comparison-no-ratio | new | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| g2c-failure | ii-comparison-no-ratio | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| g2c-failure | ii-comparison-no-ratio | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| g2c-failure | ii-comparison-no-ratio | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| g2c-failure | ii-comparison-no-ratio | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| g2c-failure | ii-comparison-no-ratio | changed-text | selected-shell-fragment-missing-or-paraphrased / C-G2C | T36 acrescenta à conclusão da falha em G2c a exigência de todos os estágios antes de qualquer avaliação em sementes reservadas; o ensaio omite ou desloca a sentença. Lado atual: montador. |
| g2c-failure | iii-comparisons-absent | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| g2c-failure | iii-comparisons-absent | new | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| g2c-failure | iii-comparisons-absent | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| g2c-failure | iii-comparisons-absent | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| g2c-failure | iii-comparisons-absent | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| g2c-failure | iii-comparisons-absent | new | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| g2c-failure | iii-comparisons-absent | changed-text | selected-shell-fragment-missing-or-paraphrased / C-G2C | T36 acrescenta à conclusão da falha em G2c a exigência de todos os estágios antes de qualquer avaliação em sementes reservadas; o ensaio omite ou desloca a sentença. Lado atual: montador. |
| release-day | failed-G0 | new | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | failed-G0 | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | failed-G0 | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | failed-G0 | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | failed-G0 | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | failed-G0 | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | incomplete-tier2 | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | incomplete-tier2 | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | incomplete-tier2 | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | incomplete-tier2 | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | incomplete-tier2 | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | incomplete-tier2 | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | incomplete-tier2 | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | incomplete-tier2 | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | incomplete-tier2 | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | incomplete-tier2 | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| release-day | invalid-main | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | invalid-main | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | invalid-main | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | invalid-main | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | invalid-main | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | invalid-main | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | invalid-main | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | invalid-main | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | invalid-main | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | invalid-main | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| release-day | passed-shp | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | passed-shp | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | passed-shp | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | passed-shp | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | passed-shp | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | passed-shp | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | passed-shp | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | passed-shp | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | passed-shp | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | passed-shp | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| release-day | unavailable | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | unavailable | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | unavailable | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | unavailable | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | unavailable | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | unavailable | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | unavailable | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | unavailable | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | unavailable | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | unavailable | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| release-day | x6-failure | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | x6-failure | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | x6-failure | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | x6-failure | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | x6-failure | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | x6-failure | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | x6-failure | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | x6-failure | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | x6-failure | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | x6-failure | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| release-day | x6-inconclusive | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | x6-inconclusive | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | x6-inconclusive | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | x6-inconclusive | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | x6-inconclusive | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | x6-inconclusive | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | x6-inconclusive | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | x6-inconclusive | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | x6-inconclusive | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | x6-inconclusive | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| release-day | x6-no-reading | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | x6-no-reading | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | x6-no-reading | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | x6-no-reading | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | x6-no-reading | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | x6-no-reading | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | x6-no-reading | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | x6-no-reading | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | x6-no-reading | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | x6-no-reading | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |
| release-day | x6-subnominal | changed-text | abstract-first-fit /  | T38a substitui a abertura de 84 por 88 palavras visíveis, define AUC por painel e explicita o corte convencional 0.03. O ensaio mantém a abertura anterior; a composição usa first-fit 101 e preserva consequências obrigatórias. Lado atual: montador. |
| release-day | x6-subnominal | changed-text | fixed-conclusion-changed /  | T36 corrige CN01: mantém condicionamento e exposição parcial, retira avaliação em novas sementes do texto fixo universal e a fornece só com PASS. O ensaio conserva formulação anterior. Lado atual: montador. |
| release-day | x6-subnominal | new | fixed-discussion-changed / DS01 | T36 separa a largura do intervalo da classificação regional; intervalos largos não mudam por si a região. O ensaio conserva a sentença fixa anterior. Lado atual: montador. |
| release-day | x6-subnominal | new | fixed-discussion-changed / DS02 | T36 exige B válido, tier 2 inteiramente completo válido e leitura estrita B/D na grade comum sem gaps; o ensaio conserva a formulação anterior. Lado atual: montador. |
| release-day | x6-subnominal | new | fixed-discussion-changed / DS06 | O texto fixo integrado distingue limites de matching, cobertura e validade de inventário; resíduo empírico não é limite de viés populacional. O ensaio conserva a versão anterior. Lado atual: montador. |
| release-day | x6-subnominal | changed-text | fixed-discussion-changed / DS10 | T36 remove a sentença RC28 sobre status de rascunho em toda montagem; o ensaio ainda contém essa sentença. Lado atual: montador. |
| release-day | x6-subnominal | new | results-display-order / B00 | T38b muda prioridade de exibição para F1/F2B/T1, T4/F5, T3/F4 e F6 quando aplicável. O ensaio usa a ordem anterior; P1-P10 continuam na ordem textual. Lado atual: montador. |
| release-day | x6-subnominal | new | selected-shell-fragment-missing-or-paraphrased / C-EVALUATION-PASS | Novo bloco T36: avaliação em novas sementes aparece apenas em PASS, após C2. O ensaio usa outra formulação no antigo texto fixo CN01. Lado atual: montador. |
| release-day | x6-subnominal | disappeared | selected-shell-fragment-missing-or-paraphrased / D-X5-POST | A divergência anterior desapareceu porque T36 condiciona as contagens a X5 fornecido. Neste caso a proveniência/etiquetas registram ausência; substituído por D-X5-POST-UNAVAILABLE. Lado atual: montador. |
| release-day | x6-subnominal | new | selected-shell-fragment-missing-or-paraphrased / D-X5-POST-UNAVAILABLE | Novo bloco T36: a proveniência artificial e todas as etiquetas X5 registram agregado não fornecido. O montador declara indisponibilidade e preserva X5 fixo, sem converter ausência em contagens zeradas. Lado atual: montador. |

`git diff --stat` (arquivos novos ainda untracked):

```text
 .../jcss-manuscript/pipeline/ASSEMBLY.md           |    53 +-
 .../review/audit_v4_manuscript_assembly.py         |   199 +-
 .../v4-manuscript-assembly-audit-2026-09-30.json   | 10445 ++++++++++++++++---
 .../ic_study/analysis/v4_manuscript_assembly.py    |    30 +-
 .../analysis/v4_manuscript_assembly_facts.py       |     1 +
 .../v4_manuscript_assembly_facts.schema.json       |    16 +
 .../analysis/v4_manuscript_assembly_rules.json     |   653 +-
 .../dress/incomplete-tier2/assembly-facts.json     |    12 +-
 .../dress/invalid-main/assembly-facts.json         |    12 +-
 .../dress/passed-shp/assembly-facts.json           |    12 +-
 .../dress/unavailable/assembly-facts.json          |    12 +-
 .../dress/x6-failure/assembly-facts.json           |    12 +-
 .../dress/x6-inconclusive/assembly-facts.json      |    12 +-
 .../dress/x6-no-reading/assembly-facts.json        |    12 +-
 .../dress/x6-subnominal/assembly-facts.json        |    12 +-
 .../incomplete-tier2/assembly-facts.json           |    12 +-
 .../release-day/invalid-main/assembly-facts.json   |    12 +-
 .../release-day/passed-shp/assembly-facts.json     |    12 +-
 .../release-day/unavailable/assembly-facts.json    |    12 +-
 .../release-day/x6-failure/assembly-facts.json     |    12 +-
 .../x6-inconclusive/assembly-facts.json            |    12 +-
 .../release-day/x6-no-reading/assembly-facts.json  |    12 +-
 .../release-day/x6-subnominal/assembly-facts.json  |    12 +-
 .../tests/unit/test_v4_exploratory_export.py       |     6 +-
 .../tests/unit/test_v4_manuscript_assembly.py      |   259 +-
 25 files changed, 10149 insertions(+), 1705 deletions(-)
```

`git status --short`:

```text
 M publications/jcss-manuscript/pipeline/ASSEMBLY.md
 M publications/jcss-manuscript/pipeline/review/audit_v4_manuscript_assembly.py
 M publications/jcss-manuscript/pipeline/review/v4-manuscript-assembly-audit-2026-09-30.json
 M src/ic_study/analysis/v4_manuscript_assembly.py
 M src/ic_study/analysis/v4_manuscript_assembly_facts.py
 M src/ic_study/analysis/v4_manuscript_assembly_facts.schema.json
 M src/ic_study/analysis/v4_manuscript_assembly_rules.json
 M tests/fixtures/v4_manuscript_assembly/dress/incomplete-tier2/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/dress/invalid-main/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/dress/passed-shp/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/dress/unavailable/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/dress/x6-failure/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/dress/x6-inconclusive/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/dress/x6-no-reading/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/dress/x6-subnominal/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/incomplete-tier2/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/invalid-main/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/passed-shp/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/unavailable/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/x6-failure/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/x6-inconclusive/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/x6-no-reading/assembly-facts.json
 M tests/fixtures/v4_manuscript_assembly/release-day/x6-subnominal/assembly-facts.json
 M tests/unit/test_v4_exploratory_export.py
 M tests/unit/test_v4_manuscript_assembly.py
?? publications/jcss-manuscript/pipeline/review/T41b-report.md
?? publications/jcss-manuscript/pipeline/review/prove_v4_verdict_catalogs.py
?? publications/jcss-manuscript/pipeline/review/repin_v4_manuscript_assembly.py
?? publications/jcss-manuscript/pipeline/review/t41b-shell-repin-receipt.json
?? publications/jcss-manuscript/pipeline/review/t41b-verdict-catalog-proof.json
?? tests/fixtures/v4_manuscript_assembly/current_shell_oracles.json
```
