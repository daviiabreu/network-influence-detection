# T41d — emenda de seleção e ordem (decisões 91/101)

Autorização: consolidação do coordenador fornecida no pedido T41d, antes da exposição de resultados. As mudanças são exclusivas da composição do resumo. SELECT WHEN, ACTION e INCLUDES dos outros shells foram preservados byte a byte.

| ID | Antes | Depois | Motivo |
| --- | --- | --- | --- |
| A.new-seeds (order) | `16` | `950` | Após resultados, incluindo opcionais, antes da limitação. O first-fit respeita esse sufixo. |
| A.B06 (condition) | `{"ref": "B06"}` | `{"all": [{"ref": "B06"}, {"gt": ["v4.t1.n_first_ne_sustained", "0"]}]}` | Toda contagem exibida deve ser positiva; não muda a condição do bloco em Results. |
| A.B04 (condition) | `{"ref": "B04"}` | `{"all": [{"ref": "B04"}, {"gt": ["v4.t1.n_first_low", "0"]}]}` | Toda contagem exibida deve ser positiva; não muda a condição do bloco em Results. |
| A.B08 (condition) | `{"ref": "B08"}` | `{"all": [{"ref": "B08"}, {"gt": ["v4.t1.n_first_gap", "0"]}, {"gt": ["v4.t1.n_sustained_gap", "0"]}]}` | Toda contagem exibida deve ser positiva; não muda a condição do bloco em Results. |
| A.B05 | B05 e n_dip > 0 | Igual | Guard positivo já integrado na T41c; conferido. |
| A.B11 | B11 e n_channel_dependent > 0 | Igual | Guard positivo já integrado na T41c; conferido. |

A.B08 imprime duas contagens; a frase só entra quando ambas são positivas. A.new-seeds conserva condição, ação, slot e opcionalidade; só seu order mudou no registro. A prioridade dos oito opcionais continua B09.1/B09.2/B09.3/B04/B05/B08/B11/B14. O ajuste do compositor deixa esses resultados antes do novo sufixo obrigatório, sem trocar a prioridade de seleção.
