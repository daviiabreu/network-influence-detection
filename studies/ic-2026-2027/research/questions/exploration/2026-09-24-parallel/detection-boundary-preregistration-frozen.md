# Pré-registro congelado — curva de separabilidade de painéis

Versão 1, 25/09/2026. **Congelado pelo agente coordenador sob delegação explícita
de Davi, pendente de ratificação.** Executa as decisões 16 e 17 e substitui o
[rascunho cb457af](detection-boundary-preregistration-draft.md). Não autoriza
experimento confirmatório nesta sessão. Congelamento fixa escolhas; não declara
que os gates de execução, cobertura ou validade empírica já passaram.

Código científico: `9fe4264ce0dbf9774ada0eed306b9f95f89d8fb8`, branch
`research/question-consolidation`. O SHA-256 destes bytes e a revisão do código
estão no [registro de congelamento](detection-boundary-freeze.json), separado
para evitar autorreferência do hash. Alteração futura exige sucessor com motivo,
novo hash e exposição acumulada; nunca substituir silenciosamente esta versão.

## Autoridade, evidência e exposição

O log `owner-decisions-20260924-session-log.md` foi lido até o item 17; SHA-256
`5022725290007b6a8a0d7e6b16fd60e74fa521655619ac38c137f7e3d936a5bf`.
A decisão 16 adotou as correções estatísticas A–G. A 17 tornou a grade inteira
de confiabilidade primária, incluiu nulos/sensibilidades e delimitou os antecedentes.
O pedido de Davi nesta sessão autoriza congelar com um gate de cobertura em a=0
antes de qualquer confirmatório, caso a validação paralela ainda esteja pendente.

Parecer adversarial: SHA-256
`cb55a4763605e270dcfaabf09569e71d5cabff1ea1baaa682670e5530dacdc40`, em
`/Users/davi/.local/state/research-workbench/adversarial-novelty-20260925/`.
Diagnóstico da segunda revisão: `prereg-review2-20260925/diag.py`, SHA-256
`d7be1eacd1eb1f2675ceae0094a17ca26a54685b0dea0e70a312c46491760dc0`.
Referências foram verificadas em fontes primárias na [nota bibliográfica](decision17-reference-verification.md).
Não se alega novidade nem completude do screening bibliográfico.

Exposição anterior: gates de BA em r=0,65 e 0,70 foram vistos; seleção antiga
usou BA em r=0,80. Foi visto o bit de interioridade de a*(0,70) sob a versão
cb457af. Nenhum desses resultados valida a versão atual: mudaram matching,
características, mecanismo principal e inferência. Não haverá novos gates
primários ou contrastes divulgados na calibração. Testes de código e cálculo
de poder com verdades artificiais conhecidas não são contrastes do estudo.

## Pergunta e estimandos

A pergunta é quanto de inovação direcionada por interação torna painéis
sintéticos distinguíveis de uma família sem interação, com o mesmo formato
observacional. O resultado primário é **toda a curva a*(r)** para
`R={0,50;0,55;0,60;0,65;0,70;0,75;0,80;0,85;0,90}`. r=0,70 é somente ponto
destacado. A decisão 17 substitui a prioridade exclusiva desse ponto na 16.
Não escolher r depois dos resultados nem resumir a curva pelo melhor valor.

Na grade fixa `G={0;0,001;0,003;0,01;0,03;0,10;0,30;0,60;0,90}`:
`a*(r)=min{a∈G: AUC(a,r)≥0,70}`. Reportar também a fronteira sustentada
`a_s*(r)=min{a∈G: AUC(a',r)≥0,70 para todo a'∈G, a'≥a}`. Alvos 0,60 e 0,80
são secundários. Não interpolar forças nem impor monotonicidade à AUC. Sinalizar
qualquer diminuição entre limites inferiores ou superiores consecutivos da banda.
Uma lacuna por célula inviável ou não pareada impede declarar a fronteira global
através dessa lacuna; reportar domínio elegível e censura, sem pular a lacuna
para chamar o próximo ponto de força mínima.

Regiões operacionais: pequena, `0<a*≤0,03`; grande, `0,03<a*≤0,90`; não atingida
na grade elegível completa; censurada/indeterminada por borda, lacuna ou IC amplo.
0,03 é convenção interna, não efeito empiricamente relevante demonstrado.
Não-atingimento é resultado registrado, não licença para ampliar a grade ou
promover um secundário. Fronteira em a=0 sem passar o gate nulo invalida a análise.

A unidade da AUC é **um painel completo**, não uma pessoa. O escore usa
estatísticas agregadas de trajetórias em onze ondas. Pessoas, ondas e pares
anuais não são réplicas independentes de classificação. O tamanho N altera a
separabilidade e fica fixo. AUC populacional de um escore da LDA declarada é **limite inferior** da AUC
Bayes-ótima nos mesmos dados e sob as mesmas leis; a estimativa amostral tem
erro e não satisfaz necessariamente essa desigualdade em cada realização; a fronteira dessa família
pode ser maior que a ótima. Não-atingimento pela LDA não prova indistinguibilidade
por qualquer procedimento. Trata-se de limiar operacional finito, não fronteira
minimax assintótica no sentido de Ingster/Donoho–Jin.

O estudo distingue padrões dinâmicos. Sem exposição/rede observada não identifica
influência social causal (Manski 1993, DOI 10.2307/2298123; Shalizi–Thomas 2011,
10.1177/0049124111404820). Misfit de um nulo não identifica o gerador verdadeiro.

## Painel e canal de observação

N=10.626, onze ondas anuais, domicílios de duas pessoas: 7.084 entradas em t=0,
3.542 em t=5, retenção domiciliar anual 0,89, saída definitiva independente da
opinião. Gestefeld–Lorenz (2023, DOI 10.18564/jasss.5204) reportam 10.627 pessoas
e 50.008 transições de confiança no governo federal; arredondar N para divisibilidade
por seis permite a geometria sintética. Entrada e atrito são aproximações,
não máscara reconstruída dos microdados. O mesmo item P$$P04 aparece anualmente
em 1999–2009, com administração telefônica/CATI. Não se presume acesso atual aos
microdados nem se inventa uma ACF empírica. [Fontes e códigos](empirical-data-access-and-reproduction.md).

Canal principal contínuo: `w_it=√r z_it+√(1−r)e_it`, e iid normal independente
de estados, rede e máscara. **Erro** significa variação transitória de resposta
que não é atitude verdadeira. Inovações/choques verdadeiros pertencem a z, mesmo
que específicos de uma ocasião; não são reclassificados automaticamente como
erro. r é fração de sinal desse canal contínuo padronizado, antes de discretizar.
Não é confiabilidade ordinal estimada nem parâmetro ajustado aos contrastes.

Por onda, transportar postos dos respondentes para 0…10 equiprováveis com
quantis `(j+0,5)/n_t`; com mesma máscara, os braços têm marginais observadas
idênticas. O transporte usa a onda inteira e é artificial. Retira informação
marginal e não reproduz necessariamente as frequências reais do SHP.

As âncoras não medem o mesmo objeto/estimando/modo: ESS/Poses et al. 2021
(10.18148/srm/2021.v15i3.7816) e GSS/Hout–Hastings 2016 (10.15195/v3.a43) são
presenciais; MTMM qualidade r²×validade não é a mesma quantidade que erro de
resposta independente. Lucas–Donnellan 2012 (10.1007/s11205-011-9783-z) estimam
0,62/0,68 para **satisfação com a vida** no SHP em modelos univariado/bivariado,
não P$$P04. Quasi-simplex pode classificar estado verdadeiro transitório como
erro. A faixa inteira é primária justamente porque transportar um centro único
a um item telefônico não está validado. Manter o [dossiê](reliability-and-prior-art.md)
como antecedente, com estas qualificações.

Sensibilidades observacionais separadas, sem selecionar resultados:

- Estilo persistente: `e_it=√c u_i+√(1−c)v_it`, c=0,25 e 0,50; u e v normais
  independentes do processo. Conserva variância marginal 1 e corr(e_t,e_s)=c.
  Motivo: Aichholzer 2013 (10.1016/j.ssresearch.2013.01.002); c é cenário, não
  estimativa transportada daquele artigo.
- Condicionamento: `r_it=min(0,95; r0+δ tenure_it/10)`, δ=0,10 e 0,20; tenure=0
  na primeira entrevista de cada coorte. Kraemer et al. 2025
  (10.1177/00491241251372503) motivam a direção; seu efeito também inclui
  estabilidade verdadeira e não é reproduzido integralmente por esta sensibilidade.
- Os dois tipos variam um de cada vez no cruzamento R×G; combinação c=0,50,
  δ=0,20 é análise exploratória identificada, sem nova hipótese principal.

## Viabilidade anterior à discriminação

No canal contínuo iid, `corr(w_t,w_s)=√(r_t r_s)corr(z_t,z_s)`, portanto
`|corr(w_t,w_s)|≤√(r_t r_s)` e, com r constante, ≤r. Essa é uma condição
necessária, não suficiente. Antes de treinar classificador, publicar a máscara
de elegibilidade derivada dos alvos de matching da calibração: no principal,
excluir `(r,a)` quando `|media L1 observado alvo|>r`. É regra conservadora
**operacional** na escala ordinal; o teorema contínuo não é automaticamente
universal depois do transporte não linear e de copulas não gaussianas.
Registrar separadamente falha de alcance numérico do gerador ordinal.

Com estilo persistente o limite contínuo passa a
`√(r_t r_s)+c√((1−r_t)(1−r_s))`; não aplicar o teto iid nessa sensibilidade.
Com deriva usar o máximo desse limite entre pares como condição necessária
mais fraca; no runner isso corresponde ao maior r possível no intervalo.
Os controles latente e ordinal r=1 têm limite 1. Igualdade no limite é elegível.
Não converter célula inviável em “não atingiu AUC” nem ajustar r para salvá-la.

Os alvos deste estudo são sintéticos e dependem da célula, por isso a regra
fica congelada agora e a lista numérica é materializada com sementes de
calibração antes de qualquer treino/teste. Não há lista numérica empírica de
P$$P04 verificada nesta entrega. Uma extensão empírica exige calcular a ACF de
P$$P04 com licença e máscara auditadas antes de fixar seu próprio domínio.

## Mecanismos e significado de a

Principal: bounded confidence **com repulsão b=0,25**, sem retorno à opinião
inicial. Oito permutações independentes definem a rede dirigida fixa, oito
entradas/saídas contando multiplicidade; autoarestas e repetição são permitidas.
Uma etapa síncrona por onda: cada pessoa recebe oito termos de vizinhança e faz
uma atualização. Sensibilidade: 24 etapas por onda, observação somente ao final,
com os mesmos coeficientes por etapa. É cenário de resolução temporal motivado
pelo ajuste de aproximadamente 24 passos/ano de Gestefeld–Lorenz, não 24 contatos
humanos identificados. Fixar a resolução; não ajustá-la pela AUC.

`D_i=media_j f(z_j−z_i)`, com `f(g)=g` se |g|≤1 e `f(g)=−b g` fora.
Centralizar D e dividir pelo seu DP transversal: d. Para ρ=0,85 por etapa:
`u=ρz+√(1−ρ²)[√a d+√(1−a)ε]`, `z'=R_N(u)`.
R_N preserva postos e atribui quantis normais de variância 1. Inicialização
normal por postos, sem burn-in; reorganização após a rede sorteada faz parte
do alvo. DP(D)=0 com a>0 é falha, não substituição silenciosa do kernel.

a é a **parcela nominal do orçamento de inovação pré-transporte** dada a d.
É âncora **interna ao simulador**, independente do discriminador, não parcela
empírica da variância total de mudança latente. D se correlaciona com z e R_N
altera a escala. O diagnóstico da revisão, para b=0, reportou R² parcial
realizado de aproximadamente `0,77a–0,96a`; o script disponibilizado calcula
`1−SSE(z'~1+z+d)/SSE(z'~1+z)`. Essa faixa não é identidade nem calibração de
P$$P04 e não deve ser transferida automaticamente ao principal b=0,25.
Reportar o mesmo mapeamento R² por a/etapa/b no futuro estudo, sem redefinir a.

Sensibilidades mecânicas: b=0 (assimilação limitada) e ancoragem inicial
`z'=R_N((1−ω)u+ωz0)`, ω∈{0,25;0,50;0,75;1}; nunca usar a ancoragem no principal.
Não interpretar resets de Gestefeld–Lorenz como evidência de influência pura.

Controle analítico linear: para assimilação global à média,
`x'=(1−α)x+αm_t+η`. Condicional ao caminho da média, ao centrar,
`x'−m_(t+1)=(1−α)(x−m_t)+η'`: AR com coeficiente 1−α. Sob mesmas inovações,
marginais, canal e lag-1, os dois rótulos têm a mesma lei e AUC populacional 0,5.
Pré-declarar não-atingimento dos alvos para essa classe, sem gastar poder para
redescobri-lo. Isso não afirma equivalência de toda rede linear heterogênea.
Manski (1993) e Granger–Morris (1976, DOI 10.2307/2345178) contextualizam os
limites; a equivalência acima é derivação sob estas hipóteses. No principal,
kernel não linear pode produzir copulas e decaimentos não reproduzidos pelo
AR gaussiano, permitindo a* finita; não garante que ela exista contra nulos
mais flexíveis.

## Família nula e matching

Todos os braços usam a mesma geometria/máscara e alvos marginais do canal.
A: AR gaussiano estacionário, “atualização ativa”, secundário.
B: `z=√λ T+√(1−λ)x`, x AR(φ), T normal independente, **confirmatório**.
B inclui estabilidade durável e atualização e contém A em λ=0; sua covariância
é `λ+(1−λ)φ^k`. Não chamar AR puro de disposições estáveis.

C: AR com erro maior no centro, `s(z)=1+2exp(−z²/2)`, normalizado por
E[s²]=1, e 10% de heaping w=0 antes de discretizar; desempate independente.
Ambos os braços da comparação C recebem marginal-alvo com 0,1 extra em 5 e
0,9/11 por categoria. No controle ordinal r=1 desligar erro/heaping e manter
essa marginal comum. C é secundário, não ajuste oportunista do canal principal.

D: persistência sem rede dependente do estado,
`ρ(z)=ρ0+γ(1−ρ0)[1−exp(−z²/2)]`; atualização `R_N(ρ(z)z+√(1−ρ(z)²)ε)`.
Caudas estáveis e centro volátil; γ=0 contém atualização ativa por postos.
E: mover–stayer, proporção π conserva seu estado inicial e os demais seguem AR;
mixture fixa por pessoa, sem rede. É sensibilidade inspirada em Converse (1964)
e Hill–Kriesi (2001, DOI 10.1017/S0003055401002209), não reprodução literal de
seu modelo de três grupos. Covariância de E: `π+(1−π)φ^k`.

Por célula R×G, pelo menos 256 realizações independentes na calibração curta;
plano de produção: 1.024. B ajusta **conjuntamente λ e φ nas médias de L1 e L2
observados**; E ajusta π/φ e D γ/ρ0 do mesmo modo. Nunca usar Pearson latente
para definir λ do alvo observado. φ/ρ0∈[0;0,999], λ/π/γ∈[0;0,8]. Newton
numérico limitado, diferenças finitas 0,005, busca de passos 1;0,5;0,25;0,125,
início (0,8;0,1), até 64 avaliações com números aleatórios comuns.

Lk é Pearson reunindo todos os pares válidos separados por k ondas **dentro de
cada painel**; o alvo é a média entre painéis. Cada momento ajustado deve ter
erro ≤`min(0,0003;0,1 DP_alvo;0,1 DP_nulo)`. Marginais são iguais por transporte.
A/C têm um parâmetro livre, pareiam L1 e relatam L2 residual; não afirmar que
parearam dois momentos. B/D/E só passam se ambos passarem. Bracket impossível,
limite de família ou orçamento esgotado são falhas de matching, não não-atingimento.

Para latente, ordinal r=1 e latent_rank, manter o segundo parâmetro ajustado ao
observado e reajustar φ/ρ0 para o **L1 do próprio canal**, mesmo critério e
orçamento máximo. Essa escolha mantém o traço/heterogeneidade da célula observada
para a decomposição; não promete igualdade de L2 dos controles. Não reutilizar
φ observado sem rematching. Números aleatórios comuns entre tentativas/canais,
calibração disjunta de treino/teste. Orçamentos são iguais entre famílias;
dimensões paramétricas diferentes são propriedades declaradas dos nulos.

Resíduos em L3…L5 são o sinal estudado; L6…L10, quando computados, são
checagens descritivas sem seleção do discriminador. Diferenças longas significam
inadequação dinâmica do nulo especificado. Parear toda a ACF eliminaria por
construção o sinal do discriminador e constituiria outro estimando.

## Discriminador e interpretação dos canais

LDA fixa: padronização no treino, covariância 0,8S+0,2I, entradas **L3,L4,L5**.
L1/L2 ajustados não entram. Sem busca de hiperparâmetros, mudança de sinal pelo
teste ou corte de classificação. Escores maiores significam reorganização;
AUC usa todos os pares de escores, meio crédito para empate.

Controles: latente mascarado, ordinal r=1, latent_rank (postos médios por onda).
Remover rank observado: categorias equiprováveis o tornam redundante com
Pearson observado, salvo arredondamento. Mobilidade |Δ| nos três terços da posição
é separada, com LDA de três entradas e mesmo orçamento; não reforça a hipótese
principal de decaimento. É sensível ao canal/escala, conforme Carpentras–Quayle
2023 (10.1080/13645579.2022.2137938).

Se AUC observada exceder latente, interpretar como sensibilidade das estatísticas
a transformação/erro e aos pares de geradores rematched; não como informação
criada pelo ruído. A desigualdade de processamento de dados é para o ótimo sob
as mesmas leis, não para duas LDAs de resumos com nuisance reajustado.
Separação somente no observado será rotulada dependente do canal.

Se B ultrapassar o alvo e D, com gate válido, tiver banda superior abaixo dele,
a leitura é “compatível com persistência não gaussiana, sem evidência específica
de interação”. Se a banda D atravessar o alvo, leitura inconclusiva. Ausência
de significância sozinha não prova equivalência. Usar regra análoga para E/C.

## Inferência viável e validade

Por célula/classe: matching 1.024 realizações; treino 1.000 redes × dois eventos;
teste 2.000 redes × dois eventos. Rede é efeito aleatório e unidade de cluster;
evento é aninhado. No nulo, blocos identificadores correspondentes com estados
independentes. Classes independentes no teste; mesmos blocos entre forças/r.
Cada evento produz um painel e um escore. Pesos iguais por rede.

Substituir definitivamente 2.000×201 refits aninhados: **2.000 bootstraps de
clusters sobre escores fixos + 40 refits independentes de matching e treino**.
O bootstrap sorteia redes separadamente nas classes e leva os dois eventos
juntos; mesmos índices em toda G. Os 40 refits usam novos conjuntos matching/treino,
regeneram o nulo sob seus parâmetros e avaliam em população de referência fixa
separada do teste, com 2.000 redes × dois eventos/classe e números aleatórios
comuns entre refits. Não confundir novos testes aleatórios com variação de nuisance.

`SE_total²=SE_scores²+Var(AUC_refit)`; **não dividir Var por 40**. Preservar a
covariância entre células, combinando draws do bootstrap e vetores de desvios
de refit centrados, corrigidos por √(40/39). É aproximação de componentes de
variância condicionais à referência, não bootstrap exato da população inteira.
A referência finita e o acoplamento entre componentes são riscos a avaliar no
gate de cobertura; não proclamar exatidão da quadratura.

Studentização em logit, com `epsilon=1/(2n)` e n=2.000 redes independentes/classe:
recortar probabilidades para [epsilon,1−epsilon] apenas na transformação e
usar `max(SE,epsilon)/(p(1−p))`. EP zero não aborta o IC. Para estimativas 0/1,
conservar o respectivo endpoint 0/1 na banda de saída. Usar máximo |t| sobre
nove forças, separadamente por r; crítico=max(quantil bootstrap 0,95,
`z_(1−0,05/18)=2,7729`). SE plug-in total é transportado aos draws, sem bootstrap
interno. O piso normal impede intervalo colapsado em draws idênticos.

Bandas são simultâneas **em G para cada r**, não uma banda simultânea de 95%
sobre os 81 pontos. Toda R é resultado primário, com todas as bandas e estados
de validade publicados; não escolher r nem fazer afirmação global “existe algum
r significativo” a partir dessas bandas. Qualquer afirmação simultânea da curva
inteira exige banda adicional de 81 células, explicitamente identificada. A
prioridade da curva não transforma cobertura por r em cobertura conjunta.

Uma regra unilateral: ultrapassagem sustentada pelo teste onde limite inferior
>0,70. Inverter bandas para IC de a*: primeiro ponto da banda superior ≥alvo é
limite inferior; primeiro da inferior ≥alvo é superior. Aplicar a mesma inversão
à fronteira sustentada. Preservar None como censura à direita, não remover
realizações sem cruzamento. Relatar não monotonicidade, sem consertá-la por PAVA.

**Gate nulo:** a banda em a=0 deve conter 0,5. Caso contrário, a corrida dessa
comparação/r é inválida e suas fronteiras são suprimidas, não tratadas como
resultados positivos. Falha no B principal em qualquer r elegível impede
aceitar a curva principal como validada. Nulos secundários rígidos, como C,
podem falhar esse gate: publicar invalidade, sem promover/demover famílias.
A0 inviável ou matching ausente também impede esse gate e a inferência válida.

## Poder para resolução da fronteira e custo

O alvo de precisão é IC cobrindo a fronteira discreta verdadeira e largura de
**no máximo um passo da grade**, com gate nulo válido. Planejamento por curvas
monótonas assumidas, erros normais independentes de AUC e SE
`√[1/(2×2.000)+σ_nuisance²]`. Não é poder empírico nem promessa para qualquer
inclinação. O [cálculo reproduzível](../../../../experiments/exploratory/decision16-validation/precision_planning.py)
usa 100.000 draws por cenário e bandas logit com crítico 2,7729:

| AUC nos dois pontos que cercam a fronteira | σ nuisance=0,01 | σ nuisance=0,02 |
| --- | ---: | ---: |
| 0,66 / 0,74 | 43,9% | 19,2% |
| 0,62 / 0,78 | 99,0% | 84,3% |
| 0,58 / 0,82 | 99,5% | 99,4% |

Demais pontos são os declarados no script; não derivam de contrastes piloto.
SEs 0,01871/0,02550. A banda bootstrap efetiva pode ser mais larga; dependência
entre células, viés e referência finita podem mudar essas probabilidades.
Não aumentar N, redes ou grade conforme a AUC confirmatória.

O diagnóstico de custo da revisão estimou ~3 CPU-h por refit completo: 40
representam ordem de 120 CPU-h, não 1,2 milhão. Matching em dois momentos e
controles adicionais podem aumentar esse valor. Antes do confirmatório medir
custo por operações cegas à discriminação e provisionar o plano fixo; se não
couber, parar por inviabilidade operacional e registrar emenda antes de novos
dados confirmatórios. Não reduzir silenciosamente refits, células ou amostra.

## Sementes, execução e gate de cobertura

Namespace desta implementação: `ic-detection-boundary-v3-calibration`; material
`namespace|bloco|fase|papel|indice`, SHA-256, primeiros oito bytes big-endian.
Fases permitidas no runner: match, train, check, reference. Bloco=0 para
baseline, 1…40 para refits; reference usa sempre bloco=0. Papéis state,
null-state, network, mask, error, heap. a e r compartilham números aleatórios.
Em matching, cada realização i usa índice 2i+1 e rede própria. Em treino/teste,
índice 2i+classe, rede floor(indice/(2×eventos_por_rede)); estados/erros/máscaras
por evento. Controlar colisões numéricas antes de executar qualquer nova fase.

Reserva futura **não executável pelo runner atual**:
`ic-detection-boundary-v3-confirmatory`, mesmo esquema, check substituído por
test. Índices i: matching 0…1023; treino 0…1999; teste e referência 0…3999 por
classe. Bootstrap: namespace separado `ic-detection-boundary-v3-bootstrap-calibration`
para validação, e sufixo `-confirmatory` somente depois da liberação. Nenhuma
semente/trajetória confirmatória foi gerada nesta entrega. Reservas e resultados
v1 não serão reaproveitados como confirmatórios.

Antes de executar o confirmatório, a validação **do procedimento corrente** em
a=0 é obrigatória: 200 repetições independentes de calibração, na geometria/canal
principal, com matching e treino novos e a mesma regra de inferência; exigir
cobertura de 0,5 em pelo menos 190/200 repetições em cada r elegível e registrar
intervalos binomiais e invalidade numérica. O gate individual continua ativo
mesmo que o gate agregado passe. Não ajustar a regra usando contrastes a>0.
Falha exige emenda, nova validação e novo hash antes do confirmatório.

A branch `research/boundary-bootstrap-validation` é a frente responsável;
conclusões commitadas aplicáveis serão vinculadas na evidência da entrega.
Resultados de um surrogate gaussiano ou do bootstrap aninhado antigo não
certificam a cobertura deste pipeline ordinal corrigido. Na ausência de
resultado aplicável, **o protocolo está congelado e a execução confirmatória
permanece bloqueada por esse gate**, conforme autorização explícita de Davi.
Não duplicar a rodada da frente paralela. A [evidência desta entrega](../../../../experiments/exploratory/decision16-validation/README.md)
registra a revisão paralela consultada e delimita os checks já concluídos.

## Antecedentes e contribuição delimitada

A [verificação bibliográfica](decision17-reference-verification.md) resolve
identificadores e separa leitura de texto, suplemento e metadados:

- Moor-Smith–Carpentras 2026, 10.1007/978-3-032-31712-4_30, arXiv:2602.00876,
  §§3.1/3.3: limiar de drift contra no-change e falha sob ruído já são precedentes.
  Aqui: painel individual, erro somente de resposta, nulos AR/mistos e AUC.
- Lersch 2023, 10.1177/00031224231156456, suplemento Parte B: detectabilidade
  com 3/5/10 ondas e SHP já estudadas; acréscimo pretendido é a curva condicionada
  ao canal e ao matching observado, não usar painel longo.
- Mulder 2023, 10.1080/10705511.2022.2122467, e Dang–Ma 2026,
  10.48550/arXiv.2608.09951: poder depende de confiabilidade, ICC, ondas e N;
  alvo aqui é discriminação de geradores, não coeficiente cross-lag. Dang–Ma
  é preprint; nenhum DOI de periódico foi confirmado.
- Stadtfeld, Snijders, Steglich e van Duijn 2020, 10.1177/0049124118769113:
  poder para seleção/influência em SAOM com rede observada; aqui não há exposição.
- Lucas 2023, 10.1177/25152459231158378: traço/estado/erro podem induzir
  caminhos espúrios; fundamenta B, não demonstra identificação causal aqui.
- CoDiNG v3, 10.48550/arXiv.2406.19204: reconhecer baseline random-empirical
  e limiar determinístico de verbalização. Não são canal de resposta com r
  externo; a diferença não apaga o precedente de comparação contra nulos.
- Kiley–Vaisey 2020, 10.1177/0003122420921538: atualização ativa pode parecer
  disposição estável com erro alto. A ambiguidade não é descoberta deste estudo.

A contribuição pretendida é a conjunção específica de controles e curva finita,
sem declarar prioridade. P4 continua abandonada pela decisão 15; a função morta
log_dose_ratio foi removida. Pendências bibliográficas mais amplas não são
resolvidas por este congelamento e devem constar de eventual publicação.
