# Proveniência desta pasta

O docking foi executado na sessão Claude na nuvem `session_01X3rvK54qMDBn2ZnVCs1dty`, com claude-opus-5-5, em 27/09/2026 entre 22:39 e 23:05 UTC. A máquina era Linux x86-64 com Python 3.12.3 e numpy 2.5.3. O sandbox não tinha credencial de push. Por isso o código, o registro de ambiguidades, a pré-declaração e o relatório foram reconstruídos, na ordem original, a partir da transcrição trazida por `claude --teleport`:

- escritas e edições exatas;
- as substituições feitas com `sed` e Python;
- as mesmas passagens de `ruff`.

Os três commits repetem as mensagens originais. Os hashes originais eram `fe32097d` (fase 1) e `09819848` (pré-declaração); o terceiro não foi publicado.

`results/` foi regenerado em macOS arm64 (Python 3.12.13, numpy 2.5.3) com os scripts reconstruídos, e não copiado. O objetivo é conferir a reconstrução e a portabilidade:

- Contagens idênticas às da nuvem: 150/150 desfechos primários equivalentes; 0/2334 testes secundários rejeitados após Holm; AUC equivalente por TOST em C1, C2 e C3; espelho bit a bit nas 25 células; latentes bit a bit nas 7 famílias.
- Diferença máxima de AUC com as mesmas features, local: C1 8.4e-05, C2 8.8e-05, C3 6.0e-05. Na nuvem, C1 foi 8,4e-5. As diferenças vêm da aritmética de ponto flutuante entre plataformas.
- O ajuste de pareamento C3 coincidiu até ~1e-15 em φ e η, com 30 avaliações nas duas máquinas.

As tabelas do REPORT.md trazem os números da execução na nuvem. Os arquivos em `results/` trazem a reexecução local. As conclusões não mudam.
