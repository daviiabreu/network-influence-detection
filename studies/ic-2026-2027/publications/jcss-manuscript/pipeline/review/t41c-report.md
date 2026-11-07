T41c concluída para revisão do coordenador, sem commit. O ramo research/shell-assembler já estava em 83aecd3c, igual à integração; não foi necessário merge. As dependências estavam presentes; não houve sync nem download de pacotes. Foram lidos T43a, T43b e os itens P4/P9 de T46.

1. Admissibilidade: plan/audit-only e a cópia final verificam a expansão dos inputs e a unicidade de labels, recusando com arquivo, linha e cadeia de inclusão. E.tables deixa X7 a cargo da inclusão única já existente em main.tex; o display completo permanece. main.tex, seções fixas, exportador confirmatório, figuras e fechamento de código ficaram intactos. AV03 e Other declarations continuam com o Owner.

2. Entradas: X6 valida limites da interseção dos conjuntos marginais, subconjunto coberto do conjunto completo e preservação do numerador em gaps-as-misses. Fronteiras exploratórias válidas, finitas e sem censura exigem intervalo finito que contenha o ponto, incluindo X7 e as projeções X1b. Ausência explicitamente censurada continua distinta de incoerência. As correções de origem são sucessores artificiais: 16 casos, 120 IDs exploratórios alterados. O registro primário X6 e as etiquetas registradas X7 foram preservados; nenhum ensaio histórico foi sobrescrito. As fixtures X6 de teste agora são produzidas a partir das flags de cobertura sintéticas, e a fixture de ponto zero traz o intervalo correspondente.

3. Seleção: A.B11 exige dependência positiva, e B11 separa contagens, sensibilidade, dependência e não avaliação. Com zero comparações permanecem P7-c1 e o inventário/não avaliação. Contagens positivas incompatíveis com zero comparações recusam a entrada. F02 também restringe A.B05 e separa a queda pontual do diagnóstico da banda.

A tabela para registro da decisão está separada em [t41c-selection-conditions.md](t41c-selection-conditions.md); [t41c-selection-changes.json](t41c-selection-changes.json) contém antes/depois e os localizadores. Nenhum guard externo de classe foi relaxado.

4. Texto: P1.1/B00 recebe o roteiro de P4 sem antecipar os displays à validação. As implicações de P9 entram nos blocos existentes; a frase de fronteira atingida exige contagem positiva. C-EVALUATION-PASS passa a “Evaluation used new seeds.”, conservando a exposição parcial no texto fixo CN01. Os achados maiores de T43a foram aplicados: canal sem evidência, banda distinta de queda, inclusão X7 única e distinção entre a fonte X1b arquivada e a projeção fornecida, sem presumir identidade ou independência das execuções. D-X1B e E.twin exigem os estados públicos de todos os nove r, sem fallback histórico.

5. Repinagem: [t41c-shell-repin-receipt-final.json](t41c-shell-repin-receipt-final.json) registra 12 IDs com aceite de texto visível, um caso de comentário, 145 deslocamentos e 109 regras intactas. Os 267 IDs continuam presentes. O recibo distingue a repinagem mecânica da revisão posterior de fragments/requires e registra o SHA final das regras. A cobertura continua 267/267 expressável (T41b e T41c); a base original tinha 78/264.

A [auditoria](v4-manuscript-assembly-audit-2026-09-30.json) concluiu 24/24 casos admissíveis: 661 divergências contra os ensaios históricos, antes 591; 70 novas, 74 com texto alterado e nenhuma desaparecida. Cada observação nova indica o montador como o lado que segue o shell revisado ou o sucessor sintético coerente. As montagens manuais permanecem como oráculos históricos. As causas das novas divergências são:

| Bloco | Novas | Causa |
| --- | --- | --- |
| `B05` | 1 | F02: queda pontual e extremos da banda têm guards separados. |
| `C-B02` | 1 | P9: ausência de resposta validada é distinta de fronteiras locais. |
| `C-BD-PERSISTENCE` | 6 | P9: implicação conserva o critério registrado B10. |
| `C-H-B` | 2 | P9: implicação de fronteira atingida exige contagem positiva. |
| `C-H-BD` | 6 | P9: implicação de fronteira conserva o guard do conjunto B/D. |
| `D-X1B` | 8 | F04: fonte arquivada e projeção fornecida são distinguidas. |
| `D-X6-DENOMINATORS` | 2 | X6R-02: gaps-as-misses conserva o numerador. |
| `E.twin-and-expanded-feature-boundaries` | 16 | F04: síntese conserva todos os r e estados da fonte fornecida. |
| `E.x6-below-nominal-reference` | 2 | X6R-02: contagens e leituras marginais do sucessor sintético respeitam a interseção conjunta; a leitura primária registrada permanece igual. |
| `E.x6-coverage-denominators.joint` | 4 | X6R-02: contagens e leituras marginais do sucessor sintético respeitam a interseção conjunta; a leitura primária registrada permanece igual. |
| `E.x6-failure-criterion` | 2 | X6R-02: contagens e leituras marginais do sucessor sintético respeitam a interseção conjunta; a leitura primária registrada permanece igual. |
| `E.x6-no-undercoverage-detected` | 4 | X6R-02: contagens e leituras marginais do sucessor sintético respeitam a interseção conjunta; a leitura primária registrada permanece igual. |
| `P1.1` | 16 | P4: roteiro F1/F2B/T1 após validação; ordem dos displays mantida. |

Cada caso e seu antes/depois estão no JSON de auditoria. As alterações de texto já divergente estão explicadas pelas respectivas classes, frases de nova execução e guards de B05/B11. [t41c-synthetic-successors.json](t41c-synthetic-successors.json) registra hashes, localizadores de cada campo artificial corrigido, diferenças de catálogo e arquivos ausentes no export histórico que a cópia atual precisa fornecer. Isso não constitui aceitação científica.

6. Igualdade: nas 24 provas confirmatórias, todos os IDs antigos possuem projeções serializadas byte a byte iguais; o único acréscimo são os 15 IDs de veredito já integrados. O exportador confirmatório não foi editado. Nenhum digest fixado do teste exploratório foi alterado: a projeção que desfaz somente os dois pontos X7 corrigidos na fixture reproduz os digests antigos; qualquer outra diferença continua falhando o teste. Nenhum número de resultado real, limiar, leitura primária registrada ou destino de output foi alterado.

Portões finais: ruff check, ruff format --check e mypy passaram nos sete Python tocados. Pytest passou em processos separados: montador 148; derivação 84; exploratório 58; freeze 1; total 291. As quatro variáveis de threads ficaram em 1, sem pytest concorrente e sem compilação LaTeX. nice 15 foi solicitado em cada comando, mas o ambiente recusou setpriority; os comandos executaram e seus resultados estão registrados no JSON. O teste de congelamento passou antes deste relatório.

Git diff --stat, apenas arquivos rastreados:

```text
.../jcss-manuscript/pipeline/ASSEMBLY.md           |    36 +-
 .../drafts/2026-09-28/results-shells-abstract.md   |     2 +
 .../pipeline/drafts/2026-09-28/results-shells.tex  |     9 +-
 .../2026-09-30/discussion-conclusion-shells.tex    |    11 +-
 .../2026-09-30/exploratory-results-shells.tex      |     4 +-
 .../review/audit_v4_manuscript_assembly.py         |   126 +-
 .../v4-manuscript-assembly-audit-2026-09-30.json   | 12627 +++++++++++--------
 .../src/ic_study/analysis/v4_exploratory_export.py |   107 +-
 .../ic_study/analysis/v4_manuscript_assembly.py    |   111 +-
 .../analysis/v4_manuscript_assembly_rules.json     |   322 +-
 .../current_shell_oracles.json                     |   328 +-
 .../tests/unit/test_v4_exploratory_export.py       |   100 +-
 .../tests/unit/test_v4_manuscript_assembly.py      |   152 +-
 .../unit/test_v4_manuscript_assembly_derive.py     |    17 +-
 14 files changed, 8546 insertions(+), 5406 deletions(-)
```

Os arquivos novos incluem o recibo, a tabela e o registro estruturado de condições, o construtor/recibos de sucessores, este relatório e 24 tabelas sintéticas com manifesto para a fixture de admissibilidade. Permanecem fora do index para revisão do coordenador.
