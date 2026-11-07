Tabela de seleção T41c para registro pelo coordenador. Base: `83aecd3c`.
Os IDs e os guards externos dos blocos são preservados; os fragmentos abaixo
não constituem regras novas. O registro estruturado com linhas, antes e depois
está em [t41c-selection-changes.json](t41c-selection-changes.json).

| ID / trecho | Antes | Depois |
| --- | --- | --- |
| A.B11 | B11 selecionado | B11 e `n_channel_dependent > 0` |
| B11: inventário | Todo B11 selecionado | Todo B11 selecionado; sem alteração |
| B11: contagem de excedência | Todo B11 selecionado | B11 e `n_pairs_compared > 0` |
| B11: interpretação de sensibilidade | Todo B11 selecionado | B11 e `n_obs_exceeds > 0` |
| B11: rótulo channel-dependent | Todo B11 selecionado | B11 e `n_channel_dependent > 0` |
| B11: não avaliação | Todo B11 selecionado | B11 e `n_channel_not_assessed > 0` |
| B11: frase sobre mobilidade | Todo B11 selecionado | B11 e `n_pairs_compared > 0` |
| A.B05 | B05 selecionado | B05 e `n_dip > 0` |
| B05: queda pontual e seus dois registros | Todo B05 selecionado | B05 e `n_dip > 0` |
| B05: diagnóstico da banda | Todo B05 selecionado | B05 e `n_nonmonotone_band > 0` |
| C-H-B / C-H-BD: nova implicação de fronteira atingida | Frase ausente; guard da classe já existente | Mesmo guard, mais `v4.t1.n_attained > 0` para a nova frase; contagens existentes mantidas |
| C-B02 / C-B03 / C-BD-PERSISTENCE: novas implicações | Frases ausentes; guards das classes já existentes | Mesmos guards; nenhuma condição de seleção relaxada |

Com zero comparações, P7-c1 continua selecionado pelo guard já existente e
B11 conserva o inventário e a não avaliação. A admissibilidade também recusa
`n_obs_exceeds` ou `n_channel_dependent` maiores que `n_pairs_compared`.

Os requisitos de disponibilidade abaixo produzem recusa quando falta evidência;
não transformam ausência em um resultado nem alteram o predicado externo.

| ID | Antes | Depois |
| --- | --- | --- |
| D-X1B | Contagens globais vinculadas; sem requisito explícito de estados por r | Mesmos guards, exigindo os nove IDs públicos `by_r.<r>.x1b.state` |
| E.twin-and-expanded-feature-boundaries | Seleção pelas contagens disponível/indisponível | Mesmo predicado, exigindo os nove estados públicos; sem fallback para a execução histórica |

P1.1, C-EVALUATION-PASS e E.tables mudam texto ou inclusão, com condição
inalterada. Nenhum limiar, destino de output ou leitura primária registrada muda.
As correções numéricas são somente de sucessores artificiais, documentados em
[t41c-synthetic-successors.json](t41c-synthetic-successors.json); os ensaios
históricos e seus catálogos continuam intactos.
