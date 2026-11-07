# Checagem de fontes do piloto de fragmentação

Consulta: 12/09/2026; corte bibliográfico pretendido: 11/09/2026. Registro exploratório preparado no âmbito da continuação autorizada por Davi (“pode ir”), a partir do [memo de mecanismo](../../../research/questions/exploration/2026-09-12/mechanism-evidence.md). Esta leitura não seleciona a pergunta da IC, não aceita síntese e não altera o protocolo. Foram inspecionadas fontes primárias abertas e código como texto; nenhum código externo foi executado.

A busca encontrou um antecedente direto para combinar separação entre grupos e pequena amplitude interna. Portanto, a ideia genérica de usar intervalos separados não sustenta uma reivindicação de novidade. A variante que verifica somente pares de componentes ligados pela rede-base continua sendo uma condição suficiente candidata, cuja prioridade não foi estabelecida. O valor do piloto depende de consequência empírica além do microcaso construído.

## Antecedentes e alcance da leitura

| Fonte primária e trecho inspecionado | Achado e relação com o certificado |
| --- | --- |
| Meng, Van Gorder e Porter, [artigo publicado, PRE 97, 022312 (2018)](https://www.math.ucla.edu/~mason/papers/flora-published-2018.pdf), seção III.B, p. 022312-6; [preprint de 2017](https://ww3.math.ucla.edu/camreport/cam17-06.pdf), seção III, p. 6. DOI `10.1103/PhysRevE.97.022312`. | A regra publicada exige grupos consecutivos separados por pelo menos `c` e diferenças internas de no máximo `0.02`; o preprint escreve amplitude inferior a `0.02`. O estudo inclui diversas redes. É antecedente direto de parada por separação e amplitude. O enunciado é global no espaço de opiniões; não foi verificado um algoritmo que aplique exatamente a checagem apenas aos pares de componentes ligados por aresta-base. Não equiparar automaticamente seus grupos aos componentes efetivos do piloto. |
| Lorenz, [A stabilization theorem for dynamics of continuous opinions](https://arxiv.org/pdf/0708.2981), Physica A 355, 217–223 (2005), manifestação arXiv de 2007; Teorema 2, discussão e apêndice A.3, pp. 2–4 e 7. | Estabelece estabilização sob condições de auto-influência positiva, reciprocidade e limite inferior das entradas positivas; o apêndice usa contração do diâmetro para médias estocásticas. É fundamento anterior para convergência por médias, não uma identificação, nesta leitura, do certificado operacional específico para o grafo-base esparso. Não foi refeita a prova completa. |
| [When network bridges foster consensus. Bounded confidence models in networked societies](https://academic.schawe.me/pdf/2021_hknet_PRR.pdf), artigo de 2021, seção II.A e apêndice D, pp. 3 e 16. | Já investiga pontes, redes esparsas e uma extensão DW. Usa soma das mudanças de opinião inferior a `10^-3`; o apêndice declara manter esse critério e relata trajetórias DW que não terminaram. É antecedente do problema empírico de pontes e convergência lenta, sem constituir a condição de separação por intervalos procurada. |
| Li, Luo e Porter, [preprint v3 de Bounded-Confidence Models of Opinion Dynamics with Adaptive Confidence Bounds](https://arxiv.org/html/2303.07563v3#S4.SS2), seção 4.2, equação 24. | Usa diâmetro por componente efetivo, tolerância DW `0.02`, e reconhece que os componentes finais aproximados podem diferir dos grupos limite. Também distingue componentes separados que convergem à mesma opinião. O modelo adapta confiança: a garantia candidata de confiança fixa não se transfere diretamente. Leitura dirigida dessa seção, não auditoria integral dos teoremas. |

Como inferência desta comparação, o piloto deve apresentar a checagem por arestas-base como uma especialização a confrontar com esses antecedentes, sem anunciar um método inteiramente novo. Convergência assintótica, ausência de interação futura entre blocos e igualdade de opiniões limite são propriedades diferentes.

## Preprint de 2026: parâmetros verificados

Fonte: [Thompsky et al., arXiv 2605.20418v2](https://arxiv.org/html/2605.20418v2#S5.SS2), tabelas 1 e 3, equação 31 e Teorema 4. A identidade usada aqui é a manifestação v2, não uma publicação editorial presumida.

| Item | Especificação |
| --- | --- |
| Pesos | `gamma, delta, z0 ∈ {0.1, 0.5, 0.9}`; baseline `(gamma,delta)=(0,1)` |
| Opiniões | `mu ∈ {0.1,0.3,0.5}`; `c ∈ {0.1,0.2,…,0.9}` |
| Grafos completos | `N ∈ {100,200,1000}` |
| ER nos resultados, seção VI.2 | `(N,p) ∈ {(1000,0.1),(1000,0.01),(100,0.1)}` |
| Repetições | Cinco grafos ER por configuração; vinte conjuntos iniciais por grafo sintético |
| Parada textual | Todos os diâmetros dos componentes efetivos `<0.01`; bailout `10^8` eventos, exceto ciclo de grau 10: `10^10` |

O Teorema 4 garante a identificação dos grupos para grafo completo e `tol<c`; sua prova já usa mínimo não decrescente e máximo não crescente dentro de cada grupo. As equações 1 e 3 exibem sinal inconsistente na segunda opinião; a própria prova do Lema 2 usa a atualização simétrica. O HTML consultado não especifica a distribuição inicial nem a agenda de checagens. Esses dois detalhes não devem ser inferidos da tabela de parâmetros. [Modelo e prova](https://arxiv.org/html/2605.20418v2#S3), [garantia](https://arxiv.org/html/2605.20418v2#S5.SS2).

## Código fixado: contrato operacional

Fonte: [`EdgeWeightedDW.py`, commit `5e33664982bda6b7576074ff47772791459ea22c`](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py). Mapeamento: `d=c`, `z=z0`. Inspeção estática da função `DW`, sem importar o módulo.

| Trecho | Comportamento observado |
| --- | --- |
| [L21–63](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py#L21) | Default executável `tol=1e-5`; docstring `0.02`; `Tmax=1e8`, `Tmin=0`, `T_acc=None`, `sigfigs=3`. |
| [L111–143](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py#L111) | Recebe opiniões no grafo; preserva ordem das arestas; usa `random.seed`; inicializa pesos em `z` ou aceita `z_start`. |
| [L187–232](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py#L187) | Seleção proporcional aos pesos via cumulativa e `random.uniform`. Para opiniões anteriores `a,b`: se `abs(a-b)<d`, atualiza `(a+mu*(b-a), b+mu*(a-b))` e `z←z+gamma*(1-z)`; senão `z←delta*z`. Somente a aresta sorteada muda de peso. |
| [L217–253](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py#L217) | `T_changed` conta eventos receptivos, inclusive diferença zero. Checa após evento receptivo desde última checagem, `step_counter>=T_acc` e `t>Tmin`; não checa em `t=0`. Adaptativo começa em zero; depois `T_acc=10**(floor(log10(t))-sigfigs)`. |
| [L259–322](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py#L259) | Primeiro: nenhuma aresta com `tol<=gap<d`. Segundo: componentes efetivos com diâmetro `<d`. Ambos permanecem aprovados. Após segundo, partição fixa; testa diâmetros `<tol`, sem reconstruí-la nem verificar separação dos intervalos. |

A leitura determina escolhas diferentes para três observadores: regra textual com componentes atuais; comportamento do código com partição memorizada; certificado por intervalos do memo. Compará-los na mesma trajetória permite atribuir diferenças ao critério, sem confundi-las com novas condições iniciais. A reprodução do código deve preservar a agenda e essa memória; a implementação de componentes recalculados deve receber outro nome. O contraexemplo avaliado em `t=0` demonstra insuficiência lógica da condição, mas sozinho não demonstra que a função pública pararia naquele instante.

Para o certificado candidato, adotar explicitamente atualização simétrica convexa, confiança e rede-base fixas. Com intervalos `I_C=[min(x_C),max(x_C)]`, exigir `diam(I_C)<tol<c` e `dist(I_C,I_D)>=c` para cada par de componentes ligado por alguma aresta-base. A distância relevante é entre intervalos completos, não apenas as opiniões atuais das extremidades da ponte. A separação impede a primeira interação externa; a recorrência interna precisa de probabilidades positivas e controle de arredondamento. Não atribuir a esse teste garantia de tempo finito de parada ou igualdade de opinião limite entre componentes socialmente separados. Essas são condições e limites analíticos do piloto, não resultados de execução desta checagem.

## Controle pequeno e fronteira de reprodução

Uma comparação pequena pode fixar `N=100`, `mu=0.5`, `z0=0.1`, `(gamma,delta)=(0.5,0.1)`, `c∈{0.1,0.2,0.5}`, completo e `G(100,0.1)`, com baseline `(0,1)` e `tol=0.01`. São valores contidos nas especificações verificadas. Quantidade menor de sementes e orçamento medido localmente tornam isso um **ensaio reduzido**, cuja finalidade é verificar implementação, censura e viabilidade. Essa sugestão não substitui a especificação do coordenador nem afirma que o contraste publicado aparecerá.

Se o piloto usar opiniões IID `U[0,1]`, registrar essa distribuição como escolha explícita: a função inspecionada apenas recebe os valores. Reprodução exata da campanha exige localizar os chamadores originais, confirmar geração e sementes de grafos/opiniões, argumentos efetivos, ambiente, ordem de arestas e agenda. Um novo gerador aleatório ou amostrador pode preservar a lei do modelo sem reproduzir sua trajetória bit a bit. Compartilhar a mesma semente entre braços tampouco mantém as arestas sorteadas iguais quando os pesos mudam.

A continuação de cada trajetória deve manter opiniões, pesos e estado do gerador; não reiniciar pesos após a primeira parada. `T_changed` não substitui uma contagem própria de mudanças estritamente não nulas. Censura deve permanecer explícita, e uma diferença observada neste ensaio não é reprodução de uma figura nem validação do levantamento completo.

## Registro das oito consultas e limites

Consultas literais, busca web geral, em 12/09/2026, sem filtro temporal automático; verificações bibliográficas e leitura feitas nos originais encontrados. Ordem dentro dos três lotes de busca:

```text
1. Deffuant stopping criterion convex hull connected components fixed graph
2. "bounded confidence" "intervals" "stopping"
3. "Deffuant" "convergence criterion" network
4. "Deffuant" "convex hull" "separated"
5. "Deffuant" "stopping criterion" "components"
6. "Lorenz" "A stabilization theorem" 2005 pdf
7. "Meng" "Van Gorder" "Porter" "Opinion formation" separation clusters
8. "Deffuant" "stopping" "separated" "interval"
```

O primeiro lote localizou Meng e o estudo de pontes; o segundo permitiu seguir Lorenz; o terceiro confirmou identidade e manifestação publicada de Meng. Houve numerosos resultados irrelevantes sobre intervalos estatísticos e geometria. Agregadores e snippets foram apenas pistas, sem sustentar os achados. Li e Thompsky foram abertos pelos identificadores já presentes no memo. Leituras e buscas locais nas páginas, navegação para originais e inspeção do arquivo fixado não foram novas consultas ao motor de busca.

O limite de oito consultas foi atingido. Não houve snowballing completo, consulta exaustiva a bases bibliográficas, auditoria dos códigos antecedentes ou prova de ausência de equivalentes. A árvore GitHub fixada falhou no navegador com mensagem de URL restrita; o arquivo Python específico permaneceu legível pela página e pelo endpoint raw público. Não foi contornado o bloqueio da árvore. Não foram adquiridos dados Facebook100 nem textos autenticados. Estas notas são paráfrases e metadados; manuscritos e código externo não foram adicionados ao repositório.
