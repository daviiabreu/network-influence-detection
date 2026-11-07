# Reconstrução local

Esta pasta foi produzida pela sessão em nuvem `session_01T8azMG3bEkG2LmE3aeT85H`
(RT5), sobre a base `37513841`. O sandbox não tinha credencial de push, e os
quatro commits originais existiram só lá: `de3457ce` (fase 1), `7382bfa9`
(pré-declaração), `554bcab8` (comparação) e `51a36c4a` (relatório e
ambiguidades da fase 2). São esses os hashes citados em `REPORT.md`. A
reconstrução refez a mesma sequência a partir da transcrição teleportada, com as
mesmas mensagens e o trailer `Reconstructed-From`, nos commits locais
`76fecc20`, `55d027b5`, `ac5576ac` e no commit que adiciona este arquivo.

Código e textos foram reaplicados byte a byte, na ordem da transcrição,
incluindo as edições por heredoc Python e o `cat >>` que ampliou
`AMBIGUITIES.md`. Os resultados não foram copiados da saída das ferramentas.
`comparison-results.json` e `explain-results.json` foram regenerados em macOS
arm64 (Darwin 27.0.0, CPython 3.12.13, numpy 2.5.3 com Accelerate e BLAS em um
thread), na mesma ordem da sessão: primeiro `compare_v4.py` na versão anterior à
correção do stub de retry, depois `explain_v4.py`, por fim a correção do stub e
o script inline que reexecuta `compare_retry()` e atualiza a seção
`3_validation`. A sessão rodou em Linux com CPython 3.12.3, porque o 3.12.13
fixado pelo estudo não existia no sandbox, e com o mesmo numpy 2.5.3 do
lockfile.

Diante dos valores que a sessão imprimiu, os resultados locais coincidem em
todos os status, decisões, sinalizadores, contagens de avaliações e
probabilidades de Monte Carlo. Dos 153 números impressos, 23 diferem apenas nos
últimos dígitos: o θ do solver em S01, S19 e S20 (2,8e-17 sobre valores da ordem
de 7e-14), os críticos da banda e as variantes de `explain_v4.py` (até 6,0e-14,
relativo 9e-15) e a quadratura determinística da regra de parada (até 4,9e-13,
relativo 5,8e-13). Todas ficam abaixo do critério pré-declarado
`1e-12 + 1e-9·|x|`. Pela grafia desses floats, os dois arquivos regenerados
diferem em 4 bytes dos tamanhos que a sessão listou (32.155 contra 32.159 antes
da atualização do retry, e 3.176 contra 3.172).

Duas observações não mudaram nenhum arquivo da sessão, que foram mantidos como
estavam. `REPORT.md` diz que o status do solver coincide em 17 dos 22 casos e
fala em cinco divergências, mas lista seis (S05, S06, S09, S10, S17 e S21).
Tanto os dados da nuvem quanto os regenerados dão 16 dos 22, e em S09 a decisão
também muda, porque o projeto aceita a raiz interior e a docking declara lacuna
por perfil não monótono. Além disso, a sessão não rodou o ruff, e o código desta
pasta não passa em `ruff check` nem em `ruff format --check` com a configuração
do estudo.
