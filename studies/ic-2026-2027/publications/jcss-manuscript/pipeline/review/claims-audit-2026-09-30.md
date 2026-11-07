# Auditoria de rastreio das afirmações JCSS — M04 — 30/09/2026

A auditoria documental foi concluída com correções mecânicas e redução de frases ao alcance das fontes. Isso não encerra a revisão científica nem constitui ratificação humana. Foram acrescentadas 26 linhas: AB01–AB08, IN04–IN07, CN01 e SUP01–SUP13. Permanecem pendências de fonte primária, pressupostos matemáticos/estatísticos e atestações do Owner.

## Base, limites e procedimento

Worktree `docs/claims-audit`, ramo `docs/claims-audit-20260930`, HEAD `00c8dc3d113545bcbaaa807041f316373a4acbbc`, base `integration/ic-20260928`. A árvore estava limpa na inspeção inicial. M04 foi lido em `/Users/davi/.local/state/research-workbench/coord-20260925/remaining-work-review-20260930.md`; decisões foram consultadas no arquivo permitido `owner-decisions-20260924-session-log.md`, no mesmo diretório. Decisões de agentes sob delegação são registros de coordenação, não atestação humana.

Foram lidos os AGENTS aplicáveis, CONTEXT-MAP/CONTEXT do estudo e arquitetura. O recorte contém o texto efetivamente ligado a `main.tex`, fora de Results e dos gerados. `sections/systematic-map*.tex` são outra entrega, retirada do suplemento conforme seu comentário inicial; não entram no PDF auditado. A base concisa pedida foi lida e tratada só neste relatório. Identificadores, índices algébricos e dimensões tipográficas não foram confundidos com estimativas.

Foram confrontados ledger, protocolo congelado/sucessores públicos, código por leitura, relatórios de docking/equivalência, JSONs exploratórios abertos, revisão focada, posicionamento, `antecedent-search-2026-09-30.md` e Q7. Áreas proibidas e microdados não foram consultados. Não houve modelo, simulação, suíte, instalação, commit ou push. Checagens documentais e fórmulas usaram Python padrão em um processo por vez; compile e checker foram sequenciais, com os quatro limites de threads em 1.

Os 82 caminhos do freeze foram confrontados por hash: somente `pyproject.toml` e `uv.lock` diferem na árvore atual; o código congelado citado conserva os bytes vinculados. Hashes de freeze, V1, emenda, decisões, critérios e inventário foram conferidos sem executar gates. O wrapper foi comparado com o blob histórico, sem abrir conteúdo selado.

## Afirmações sem rastreio suficiente ou com suporte inadequado

Linhas do estado final. “Feito” é correção aplicada; “pendente” não equivale a contradição da fonte nem a leitura integral concluída.

| Arquivo:linha | Afirmação | Problema | Correção feita ou proposta |
| --- | --- | --- | --- |
| `main.tex:32` | Oito frases fixas do resumo; geometria SHP. | V18 marcava ausência de resultados, sem rastrear cada frase; geometria sugeria reprodução do painel. | Feito: AB01–AB08; preservada a ressalva da aproximação de campo médio. O coordenador manteve “Swiss Household Panel geometry”: a geometria do painel vem do SHP e o ODD (P1) a descreve, a sigla ficaria sem definição no resumo e a base dos shells usa a mesma frase. |
| `sections/introduction.tex:2` | Mecanismos e insuficiência de ajuste marginal para explicar trajetórias. | Abertura sem linha própria; inferência marginal/conjunta podia parecer achado de Flache. | Feito: IN04, Introduction/Table 1 de Flache e argumento dos autores identificado como tal. |
| `sections/introduction.tex:5` | Categoria, mudança, estado transitório, erro e decomposição de estabilidade. | Sem linha própria; Heise/Wiley/Achen não têm localizadores primários suficientes. | Feito: IN05 separa argumento do canal de literatura; pendência de fontes originais preservada. |
| `sections/introduction.tex:8` | Três ondas, 183 itens; Lersch e três/cinco/dez ondas. | Sem linha específica para o parágrafo e seus números. | Feito: IN06; Kiley pp. 483–490/504, qualificação na p. 21 do manuscrito dos autores; Lersch pp. 222/228 e suplemento Part B. Leitura anterior registrada, sem nova leitura integral alegada. |
| `sections/introduction.tex:43` | Roteiro e resultados aguardando execução válida. | Fechamento sem rastreio próprio. | Feito: IN07, ligado às seções da emenda congelada; não afirma ausência de gates aprovados. |
| `sections/conclusion.tex:2` | Pergunta e interpretação condicional após exposição. | V18 não rastreava o texto fixo e ficou histórico após os números de X5. | Feito: CN01 e nota sucessora em V18; X5 continua EX14–EX15/RC30–RC31. |
| `sections/supplement.tex:8` | Mecânica, solver, bandas, gates, exposição e busca. | Treze parágrafos sem linhas próprias; conexões dispersas com Methods/ODD. | Feito: SUP01–SUP13 com fontes congeladas e limites; nenhum resultado novo inserido. |
| `sections/supplement.tex:16` | Face inferior do perfil e passo local. | eta=0/0.01 não cobriam o perfil que começa acima de zero; M19/M20 já registravam isso. | Feito: extremo inferior solucionável e passo min(0.8, eta_lower+0.01), conforme DB4:263–310; regra preservada. |
| `sections/background.tex:49` | Testes micro e macro. | C31 usava §3.12 sem localizador reconhecível na consulta atual. | Feito: Abstract/Conclusions na fonte aberta; frase mantida. |
| `sections/background.tex:55` | Experimento e compatibilidade micro/macro. | C34/C35 com §5/§6 pouco informativos. | Feito: seções nomeadas e subseção de comparação, Figs. 12–13; texto conferido e mantido. |
| `sections/background.tex:70` | Confiabilidade por item e hipóteses de mudança. | C39 com DOI/tópico, sem página ou seção. | Feito: pp. 973–974, Quantifying Reliability/Eqs. 1–5, e p. 975, Data and Methods. |
| `sections/background.tex:74` | Qualidade MTMM e diferença do r sintético. | C41 sem localizador; não substituição direta é inferência dos autores. | Feito: p. 236 e §4.1, pp. 238–239; inferência ligada separadamente a M06. |
| `sections/related-work.tex:92` | Exposição observada seria necessária para identificação causal. | R52 excedia a condição sobre grupos de referência do resumo registrado de Manski. | Feito: restringido à dificuldade de inferir efeitos endógenos sem informação prévia sobre composição dos grupos; suporte permanece em nível de resumo. |
| `sections/discussion.tex:11` | Canal, máscara e marginal exatos nos dois braços. | M17 separa acoplamento em matching/validação de classes independentes em treino/teste/referência; C muda o canal do nulo. | Feito: comparação primária; canal/processo de atrito/alvo categorial compartilhados; máscaras acopladas só em matching/validação. DS03 atualizado. |
| `sections/verification.tex:81` | Limites de família viriam só da triagem de viabilidade. | IDA A03b contradiz DB4:294/297/315/338, como M11 já registra. | Feito: mantidos os três contrastes observados e classificação como gaps; generalização retirada e contradição histórica explicitada. |
| `sections/background.tex:44` | Clustering/polarização definiriam os modelos e seriam impossíveis no gerador. | Rank transport fixa a marginal; não exclui toda estrutura de rede/temporal nem sustenta “define these models”. | Feito: A04/M57/ODD08/DS04 limitados à marginal populacional, com código congelado/ODD18. |
| `sections/methods.tex:241` | IA por papel, modelos e responsabilidade humana. | M54/M55 não ligavam o registro Q4 que distingue execução, trailer, família e desconhecido. | Feito: fonte ai-disclosure-evidence.md/Q4-01–Q4-43; nenhum modelo inferido de trailer e nenhuma atestação humana declarada. |
| `sections/background.tex:64` | Decomposições de Heise e Wiley. | C36 sem página/seção primária; DOI específico não deu texto legível. | Pendente: obter originais/localizadores ou aprovar fonte secundária. Hout pp. 973–974 conferido como apoio secundário, sem promover a integral. |
| `sections/background.tex:66` | Erro explica inconsistência; introdução acrescenta questões vagas. | C37/notas não oferecem localizador primário suficiente, especialmente para “vague”. | Pendente: leitura autorizada/localizador ou redução da atribuição; nenhuma página inventada. |
| `sections/background.tex:68` | Pergunta/condições de resposta; idade/coorte. | C38: livro sem página/seção; Alwin–Krosnick apenas resumo registrado e DOI inacessível nesta consulta. | Pendente: locadores separados e leitura delimitada das duas fontes; DOI não comprova toda a frase. |
| `sections/background.tex:72` | 0.69 para political views; coluna adjacente no ledger. | 0.6899 tem coluna identificada; nota registra conflito 0.6634 versus 0.6764 na coluna vizinha. Planilha não relida. | Pendente: conferir coluna adjacente se usada. 0.69 mantido como fato com fonte registrada, sem nova validação da planilha. |
| `sections/methods.tex:47` | m positivo para todo z>0 e crescente em módulo. | M61 tem fórmula/grade finita, sem demonstração do quantificador universal; valores em 0.5/1/2 conferem pela fórmula. | Owner: prova analítica ou limitação ao domínio avaliado. Sem alterar interpretação científica ou executar o processo. |
| `sections/methods.tex:60` | SE de um painel 32 vezes maior. | sqrt(1024)=32 é regra de uma média iid. SE de fitting usa diferenças pareadas com CRN; falta explicitar que a comparação é do alvo médio sob variância comparável. | Owner: distinguir SE do alvo e SE residual; não apresentar como dificuldade de estimação empírica demonstrada. |
| `sections/methods.tex:114` | Viés máximo 0.25 SE salvo piso 1e-6. | Limite vale para raízes que satisfazem tolerância; boundary B/D/E pode ser aceito por sinal de L2 e validação a 4 SE, sem satisfazer esse limite em L2. | Owner: restringir a raízes interiores/equações satisfeitas e distinguir resíduos de soluções restritas. DS06 herda ressalva; não alterado por afetar sentido científico. |
| `main.tex:84` | Licença SHP proíbe redistribuição e âncora será local. | AV01 tem regras do estudo/roteiro público, mas preregistração exige Owner conferir contrato/versão efetivos. | Owner: atestar condições do contrato e plano de agregados; nenhum microdado ou restricted consultado. |
| `sections/methods.tex:217` | Digest do sucessor G1c. | RC39 tem proveniência documental, mas bytes privados não podem ser lidos nesta auditoria. | Feito: acrescentada fonte no log permitido, decisão 83, que registra digest e checagem do predicado. Sem confirmação independente dos bytes. |
| `sections/appendix-odd.tex:369` | Wrapper e hash histórico. | Risco de confundir 1f74e902 com wrapper operacional posterior. | Conferido: blob histórico 9acdfcdd…a0c1; HEAD e7cb9f56…1fb. Localizadores do ledger explicitamente históricos; log do owner, decisão 83, registra sucessor. Hash do manuscrito mantido. |
| `main.tex:98` | Financiamento, conflitos, ética e contribuições. | Campos editoriais não são declarações verificadas; autoria/ratificação pendentes. | Owner: fornecer e atestar declarações. Campos preservados. |
| `sections/introduction.tex:40` | Nenhum resultado confirmatório disponível; ratificação pendente. | Disponibilidade de resultado não se confunde com aprovação técnica de gates. | Estado público do pedido preservado no relatório; sem importar veredictos ao manuscrito ou preencher Results. |
| `pipeline/drafts/2026-09-28/results-shells-abstract.md:13` | Seis frases da base concisa, incluindo geometria. | Sem linhas próprias de desenho; “Swiss Household Panel geometry” repete a extrapolação do resumo ativo. | Rastrear AB01, AB02, M04/M60–M62, AB04, M16, AB05 em ordem. A troca por “SHP-like geometry” não foi adotada, como no resumo ativo. Shell não editado. |

## Cobertura do texto restante

Cada conjunto foi conferido seguindo as cadeias de fonte e a profundidade de leitura registrada. Resolver um marcador não comprova sozinho o conteúdo.

| Parte | Ledger e fontes | Resultado e limite |
| --- | --- | --- |
| Resumo | AB01–AB08; AMD/V1, M04/M16/M22/M60–M62/M65 | Rastreio acrescentado; pergunta/estimando não afirmam sucesso observado. Aproximação de campo médio continua uma aproximação. |
| Introdução | IN01–IN07, IP01–IP09; revisão focada/dossier/AMD | Abertura rastreada; página de manuscrito de autor distinguida da publicação. Ausência no recorte não foi convertida em inexistência na literatura. |
| Background | C01–C07/C16–C19/C22–C23/C31–C41; A01/A02/A04/A06/A07 | Regras/equações têm locadores nas notas existentes; C36–C38 pendentes de primários. Abstract/preview não promovidos a integral. |
| Trabalhos relacionados | R21–R71; dossier, busca complementar e Q7 | Contrastes limitados aos estudos lidos: marginais/trajetórias, redes/eventos/canal ordinal, influência/persistência. R52 estreitado; limites de R60/R61 preservados. |
| Métodos | M01–M86; AMD/SPEC/DRD/V1 e código em 37513841 | Canal, fitting, inferência, gates, inventário/exposição rastreáveis. M61/M66/M69 pendentes de alcance. Não presumida cobertura interior ou transferência de âncora. |
| Verificação | VER01–VER16; MD/ID/HE e reconstruções | Verificações históricas delimitadas; não substituem cobertura científica ou veredictos atuais. VER10 corrigido com o código congelado. |
| Discussão/conclusão | DS01–DS11/CN01/EX14–EX15/RC18–RC31 | Regras condicionais preservadas; X5 exploratório com 36 estimativas/36 gaps. Campos de resultados mantidos em aberto. |
| Suplemento | SUP01–SUP13/EX01–EX15/RC01–RC31; congelados e JSONs abertos | Fontes próprias acrescentadas; números abertos de X1a/X1b/X2/X5 conferidos. Nenhum resultado X3/X4/X6/X7 consultado. |
| ODD | ODD01–ODD40; V1/AMD/SPEC/DRD, código e sucessores | Constantes/fluxos com cadeia; ODD08 limitado à marginal; ODD39 separa âncora/STARTS/compatibilidade; ODD40 histórico, recibo privado não lido. |
| Declarações | AV01–AV10/M54–M55; FRZ/HE/MD/Q4 | Ambiente e verificações históricas com fonte; licença aceita, autoria, ratificação, interesses e divulgação final exigem Owner. Arquivo/publicação ainda placeholders. |

O ledger tem 436 IDs únicos, incluindo linhas retiradas e de outra entrega; todos os marcadores ativos de claims no recorte resolvem. R1/R2 em comentários identificam pareceristas. A primeira checagem lexical sinalizou R1 como falso positivo; a exclusão explícita desses identificadores resolveu a checagem sem alterar texto científico.

## Números sem fonte e números com suporte limitado

Após as adições, não ficou número literal sem alguma fonte identificada no texto ativo auditado. Isso não significa validação integral de cada fonte: abaixo constam os números rastreáveis cujo suporte exige ressalva. Fatos exploratórios abertos podem usar fonte explícita; resultados confirmatórios futuros continuam dependentes de resultnum/exportação validada.

| Local / números | Tipo e fonte | Situação |
| --- | --- | --- |
| Resumo: onze ondas, 0.70, seis estágios | Constantes: AB04–AB06; AMD painel/estimandos/gate, 37513841 | Linha explícita acrescentada. |
| Introdução: três ondas, 183 itens, três/cinco/dez ondas | Literatura: IN06; Kiley pp. 483–490/504, Lersch suplemento Part B | Linha própria acrescentada; leitura anterior identificada. |
| Background/related/introdução: 11 ondas, 1,235 distribuições, seis painéis, 10%/duas ondas/30 atores, datas de busca | Fatos: C33/IP01/R23–R24/R35/R41/R64/R56–R58/R63 | Fontes/notas com página/seção ou contagens reconstruídas; não prova de ausência de antecedente. |
| 0.69/sete categorias de political views | Fato: C40, Sheet1/polviews/Alwin-Heise = 0.6899 | Planilha não relida. Coluna vizinha conflitante 0.6634/0.6764 permanece fora do valor publicado. |
| N=10,626; 7,084/3,542; ondas 0/5/10; duas pessoas; 0.89; onze categorias | Constantes: M02/M06, ODD03–ODD06/ODD22–ODD23, SUP01 | Desenho sintético, não estatísticas de microdados. |
| Oito slots; distância 1; b=0.25; 0.85; um/24 passos; caixas, grids e coeficientes de canais | Constantes: M04–M08/M14/M18–M20/M58, ODD18–ODD23, SUP01–SUP03 | AMD/V1/código congelado; 0.85^24≈0.02 é derivação, não persistência SHP medida. |
| r=0.50…0.90/nove valores; forças 0/0.001/0.003/0.01/0.03/0.10/0.30/0.60/0.90; alvos 0.60/0.70/0.80 | Constantes: M07/M23/M31/M71 e V1/AMD | Grade e convenções internas preservadas. |
| Matching 1,024/4,096; validação 2,048; orçamento 96; tolerâncias 5e-5/1e-6/0.25 SE; 4 SE; ratios 0.71/1.41; diagnóstico 2.2414/0.0003 | Constantes/derivações: M18–M21/SUP03–SUP04; DB4:43/87/393–418 | Fonte identificada; alcance de 0.25 SE em boundary pendente. Razões de SE supõem variância pareada comparável. |
| 2,000 redes/dois eventos/4,000 painéis; bootstrap/nuisance; passos 0.01/0.005; 2.7729/0.95/floors | Constantes: M22/M26–M30/M35, ODD29–ODD33/SUP05–SUP06 | Regras congeladas, não cobertura observada. |
| Gates: oito grids; G1b 5×1,000/935; G1c 3×50/150/3; G2 7×100/50 pares/5 e 14 falhas; G2c 100/40 e 3/2; ratios 0.8–2.0; stop 0.80/54 fits/0.445 | Constantes ou exemplo histórico: M36–M41/M72–M78, ODD34, SUP07–SUP09, critérios v43 | Critérios, não resultados atuais. 0.445 é exemplo do stop no docking, não resultado de G0. |
| Inventário, tiers, close/liberação, hashes, versões, projeções 256–726h | Constantes/fatos documentais: M42/M44/M48/M51/M80–M86, AV02–AV10/ODD40/RC32–RC50 | Inventário: 3,726 linhas/414 unidades. Prazo original distinto da liberação; projeção não é tempo concluído. Hash privado G1c só documental. |
| Docking/equivalência: seeds/células/endpoints/tolerâncias; AUCs reduzidas; 538/3 testes; 82 hashes; 1,331,544 valores/4,448 divergências | Fatos históricos: VER06–VER13/AV06–AV08; MD/ID/HE | Relatórios, não testes reexecutados. Hipótese de plataforma permanece hipótese. |
| Exposições v1/A/B/docking e seus valores/contagens | Fatos: M48–M53/M84/ODD36/SUP10; AMD/COV/MD | Cumulativas; não novas estimativas confirmatórias nem motivo para selecionar faixa. |
| m(0.5)≈0.013/m(1)≈0.085/m(2)≈0.40; 0.52 no bound | Derivações: M60–M62, fórmula em M61 | Valores conferidos em fórmula fechada. Sinal/crescimento universal permanece pendência. |
| 32; AUC 0.60/0.70/0.80 → delta 0.36/0.74/1.19 e power 0.10/0.18/0.32; exemplo Heise 0.63 | Derivações: M66/M70/DS05 | Power normal conferido: 0.0991/0.1832/0.3246. Fator 32 depende das hipóteses; 0.63 é exemplo sintético, não âncora SHP. |
| X1a/X1b/X2/X5: AUCs, intervalos, lags, R², tabelas, denominadores/falhas | Fatos: EX01–EX15/RC01–RC31; results/x1a.json/x1b.json/x2.json/x5.json | Fontes abertas; X1b completo válido não elimina quatro lacunas. X1a sem correção múltipla/variância de treino; X2 não se converte em AUC; X5 não calibra SHP. |
| Busca: 10 queries/20 hits/40 runs; 399/391/5/3; 200/24 DOIs ausentes; split 16/8; truncamento 100–115 | Fatos: R56–R58/R63/SUP12–SUP13; search-log.json/dossier | Reconstrução limitada, não exportação original íntegra ou busca nova. |
| Shell conciso e ramificações: onze ondas/0.70; 414/nove/935 de 1,000/54/0.80, IDs resultnum | Constantes ou vínculos esperados: AB04–AB06/M38/M40/M42/M46 e decisões 82/91 | Apenas relatório; estimativas variáveis são campos de exportação futura. Contagens editoriais de orçamento são ensaios anteriores, sem nova composição aqui. |

Não devem ser considerados encerrados o fator 32, o alcance de 0.25 SE na fronteira, a coluna adjacente C40 e a verificação independente do digest privado. São problemas de alcance/proveniência, não números sem fonte. O comentário antigo de 248 tokens por espaços no resumo foi atualizado para 245; o checker conta 248 palavras por outra regra.

## Literatura e consultas abertas pontuais

Não houve busca ampla. Localizadores específicos de citações existentes foram conferidos nos textos abertos: [Flache et al.](https://www.jasss.org/20/4/2.html), Abstract/Introduction/Table 1/Conclusions; [Banisch e Shamon](https://www.jasss.org/27/1/17.html), seção empírica e comparação micro/macro; [Hout e Hastings](https://sociologicalscience.com/download/vol-3/november/SocSci_v3_971to1002.pdf), pp. 973–975; [Poses et al.](https://ojs.ub.uni-konstanz.de/srm/article/view/7816/7014), p. 236 e §4.1, pp. 238–239. Tentativas nos DOIs de Heise/Wiley/Achen/Alwin–Krosnick não deram texto legível; isso não é evidência contra as obras.

A busca complementar existente sustenta as sobreposições delimitadas em R64–R71: confiança em painéis (Devine), erro/innovations intrapessoais (Schuurman), rede/eventos/testes (Soni) e baseline preditivo de painel (Settle). Não foi promovida a revisão completa nem a prova de prioridade. Q7 sustenta R60 por Kenny–Zautra 1995 p. 53 e R61 pelos resumos Cole/Lüdtke. O capítulo de 2001 continua inacessível. Em DS03, dificuldade de estimação não foi convertida em obrigação universal de trocar traço por erro.

## O que permanece para o Owner

1. Obter locadores primários de Heise/Wiley/Achen/Alwin ou aprovar apoio secundário/atribuições estreitas; conferir a coluna adjacente C40 caso usada.
2. Revisar prova/alcance de M61, a aproximação M60–M62/AB03/DS02, SE em M66 e viés de M69/DS06 em soluções restritas. Compile/checker não encerram esses pontos.
3. Confirmar contrato/versão SHP, política de agregados, autoria, ratificação, financiamento, conflitos, ética e divulgação final de IA. Q4 é evidência para atestação, não atestação.
4. Revisar a base concisa no shell fora deste escopo e a composição final após liberação; consequência X6 somente sob o predicado da decisão 91, preservando demais restrições.
5. Atualizar campos de resultados e afirmações temporais só após liberação e inventário validados. Estado público usado: G0/G1b/G1c/G2 aprovados (G2 em 30/09 às 10:01Z, 700/700, zero falhas), G2c em curso; nenhum resultado confirmatório ou X3/X4/X6/X7 fora do selo para esta auditoria. Não houve inspeção dos logs proibidos.

## Compilação e checker

Uma única invocação de Tectonic no binário solicitado, em cópia temporária: `--only-cached --keep-logs main.tex`. Foram copiados classe/estilo do template indicado e todo o cache existente para `tectonic-cache`; `TECTONIC_CACHE_DIR` aponta para essa cópia. Não houve download. TeX/Bib conferidos contra a cópia compilada; depois do compile, só ledger/relatório foram editados.

Diretório: `/private/tmp/jcss-claims-audit-20260930-h5gl8g7g`. Compile: exit 0; PDF com 42 páginas. Avisos underfull, nenhum overfull na saída. SHA-256 do PDF: `c063c81841a5cba9aa7a69df54d07ff163ec06848f6e71b711b5ac7fe89ab08d`. Saída/log: `compile-output.txt` e `main.log` nesse diretório.

Checker normal, sem `--submission`, depois do compile:

```text
venue: jcss; PDF: 42 pages, 26368 extracted words
abstract: 248 words; keywords: 5
citations: 58 used keys; 77 bibliography entries
placeholders: 24
PASS
```

Binário usado: `/nix/store/l8af77awr5a678gmrbcg94pqhihd5mhs-tectonic-0.17.0/bin/tectonic`. Python usado: `/Users/davi/Documents/github/worktrees/research-workbench/integration/ic-20260928/studies/ic-2026-2027/.venv/bin/python`; `pipeline/paper_check.py --venue jcss --pdf <diretório-temporário>/main.pdf`, com OMP/OPENBLAS/MKL/VECLIB em 1 e `PYTHONDONTWRITEBYTECODE=1`; exit 0. Os 24 marcadores continuam esperados. Não foi executado `--submission`, gate de projeto, teste ou validação científica de cobertura. `git diff --check` passou.

## Estado do Git

`git diff --stat` (arquivos rastreados; relatório novo separado no status):

```text
 .../publications/jcss-manuscript/claim-evidence.md | 88 +++++++++++++++-------
 .../publications/jcss-manuscript/main.tex          |  7 +-
 .../jcss-manuscript/sections/appendix-odd.tex      |  2 +-
 .../jcss-manuscript/sections/background.tex        |  2 +-
 .../jcss-manuscript/sections/conclusion.tex        |  1 +
 .../jcss-manuscript/sections/discussion.tex        |  4 +-
 .../jcss-manuscript/sections/introduction.tex      |  4 +
 .../jcss-manuscript/sections/methods.tex           |  2 +-
 .../jcss-manuscript/sections/related-work.tex      |  2 +-
 .../jcss-manuscript/sections/supplement.tex        | 15 +++-
 .../jcss-manuscript/sections/verification.tex      |  2 +-
 11 files changed, 91 insertions(+), 38 deletions(-)
```

`git status --short`:

```text
 M studies/ic-2026-2027/publications/jcss-manuscript/claim-evidence.md
 M studies/ic-2026-2027/publications/jcss-manuscript/main.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/appendix-odd.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/background.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/conclusion.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/discussion.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/introduction.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/methods.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/related-work.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/supplement.tex
 M studies/ic-2026-2027/publications/jcss-manuscript/sections/verification.tex
?? studies/ic-2026-2027/publications/jcss-manuscript/pipeline/review/claims-audit-2026-09-30.md
```

O relatório novo não entra no diff --stat enquanto não for adicionado ao índice. Nada foi staged; não houve commit/push. Todos os caminhos modificados foram conferidos contra o escopo autorizado. Todos os bytes TeX/Bib finais coincidem com a única cópia compilada. As 72 células numéricas da tabela X2 conferem na precisão impressa.
