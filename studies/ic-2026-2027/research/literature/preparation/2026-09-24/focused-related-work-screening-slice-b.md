# Triagem individual — revisão focada, fatia B

Data: 24/09/2026. Escopo: as 510 identidades pendentes da metade B, ordenadas pelo identificador da obra; primeira `doi:10.1515/9783110475562-006`, última `id:https://openalex.org/W943909467`. Esta é uma triagem individual provisória, sem segunda leitura independente nem consolidação com a fatia A.

Foram triadas **510** identidades: **476 excluídas**, **27 retidas** para texto integral e **7 incertas**. Das 89 que vinham sem resumo, OpenAlex/Crossref forneceram 38; as demais mantêm a profundidade de evidência indicada no registro privado. Em 23 retidas foi obtido PDF e em outras duas se consultou texto integral HTML, com inspeção das seções pertinentes; duas ficaram em título/resumo e metadados por falta de texto integral acessível. Os resultados por identidade e suas fontes, localizadores e profundidade estão em `screening-slice-b.jsonl` no pacote privado; o manifesto sucessor registra os hashes. O relatório principal e o manifesto da aquisição não foram alterados.

## Novas retenções

| Direção | Obra |
| --- | --- |
| Principal | [Efeitos de pares com grupos de referência](https://doi.org/10.2139/ssrn.3097792) |
| Principal | [Estabilidade de atitudes sobre imigração](https://doi.org/10.2139/ssrn.3322121) |
| Principal | [Estabilidade e confiabilidade de eficácia política](https://doi.org/10.2307/1978345) |
| Principal | [Preferências simbólicas e não simbólicas](https://doi.org/10.2307/2111553) |
| Principal | [Crítica ao RI-CLPM](https://doi.org/10.31234/osf.io/6f85c) |
| Principal | [Persistência de pistas partidárias](https://doi.org/10.31234/osf.io/v8tfn) |
| Principal | [Sistemas de crenças dentro/entre pessoas](https://doi.org/10.31234/osf.io/xhs9g) |
| Principal | [Atitudes sobre welfare ao longo da vida](https://doi.org/10.4337/9781800887411.00014) |
| Principal | [CoDiNG: opiniões latentes e expressas](https://doi.org/10.48550/arxiv.2406.19204) |
| Principal | [Posts versus respostas de survey](https://arxiv.org/abs/2109.01762) |
| Principal | [Cinco modelos de opinião e eco-feedback](https://arxiv.org/abs/2112.12063) |
| Principal | [Validação de modelo baseado em argumentos](https://arxiv.org/abs/2212.10143) |
| Principal | [Instabilidade e erro em cinco ondas](https://arxiv.org/abs/2306.17311) |
| Principal | [Inferência de parâmetros de modelos de opinião](https://arxiv.org/abs/2403.05358) |
| Principal | [Mistura de opinião na deliberação](https://arxiv.org/abs/2601.14221) |
| Principal | [D-MODD em dados longitudinais](https://arxiv.org/abs/2601.16226) |
| Principal | [Ising com influência e persistência](https://arxiv.org/abs/2609.23690) |
| Principal | [Mudança política e matrizes de confiabilidade](https://kb.osu.edu/items/984b48b0-b9f1-5189-9296-a0ee9dc0d341) |
| P4 | [Maioria contrária e propaganda oscilante](https://doi.org/10.3390/e25101402) |
| P4 | [Consenso em hipergrafos](https://doi.org/10.48550/arxiv.2105.01369) |
| P4 | [Friedkin–Johnsen em hipergrafos](https://doi.org/10.48550/arxiv.2310.05689) |
| P4 | [Mídia no q-voter em rede Barabási–Albert](https://doi.org/10.48550/arxiv.2407.10035) |
| P4 | [q-voter sob viés externo aleatório](https://doi.org/10.48550/arxiv.2506.05669) |
| P4 | [Grupos versus projeção em comentários Reddit](https://arxiv.org/abs/2505.02989) |
| P4 | [Mediana ponderada com ordem superior](https://arxiv.org/abs/2601.06515) |
| P4 | [Voto majoritário com agentes teimosos](https://arxiv.org/abs/2003.02885) |
| P4 | [Tese sobre opinião privada/expressa e controle](https://spectrum.library.concordia.ca/id/eprint/996231/) |

## Sobreposições que exigem atenção

- **Principal — CoDiNG**, [DOI 10.48550/arxiv.2406.19204](https://doi.org/10.48550/arxiv.2406.19204): **P1, P3 e P4 = sim**. Compara mecanismos de influência com o baseline `Keep`, usa respostas dos mesmos indivíduos nas ondas S4–S6 e distingue ajuste de distribuições, transições e indivíduos (pp. 8–11, Tabela 2, Figuras 3–4). **P2 = não**: não isola erro aplicado apenas à resposta observada. É uma sobreposição forte, mas não o contraste completo do protocolo.

- **P4 — maioria e propaganda oscilante**, [DOI 10.3390/e25101402](https://doi.org/10.3390/e25101402): **F1 e F2 = sim**; quatro agentes por interação e campo de propaganda (preprint arXiv:2309.05765, pp. 2–3). **F3 = parcial**: o limiar varrido é temperatura/ressonância, não dose crítica para reduzir erro persistente (Fig. 4).

- **P4 — mídia em q-voter na rede Barabási–Albert**, [DOI 10.48550/arxiv.2407.10035](https://doi.org/10.48550/arxiv.2407.10035): **F1, F2 e F3 = sim**. Grupo `q`, probabilidade de adesão à mídia e limiar `p_t` para consenso (pp. 2–5, Figuras 1–3). Não compara o mesmo hipergrafo à projeção por pares com normalização controlada; o desfecho é consenso, não erro em relação a uma verdade externa.

- **P4 — q-voter sob campo aleatório**, [DOI 10.48550/arxiv.2506.05669](https://doi.org/10.48550/arxiv.2506.05669): **F1, F2 e F3 = sim**. Painel `q`, atualização por pista externa com probabilidade `p` e transição `p_c` entre ordem e desordem (pp. 2–3, Apêndice B). Não mede redução de erro persistente nem contrafactual hipergrafo/projeção normalizado.

- **P4 — mediana ponderada em complexo simplicial**, [arXiv:2601.06515](https://arxiv.org/abs/2601.06515): **F1 e F2 = sim**. Grupos como simplexes e opinião ambiental externa (pp. 2–5); analisa convergência, sem dose crítica. **Voto majoritário com agentes teimosos**, [arXiv:2003.02885](https://arxiv.org/abs/2003.02885): **F1 e F2 = sim**; grupo e agentes com opinião fixa, sem estimar dose crítica de sinal.

Os sete casos incertos são títulos sem resumo recuperável que não permitem exclusão fundamentada; permanecem identificados no JSONL privado. Nenhuma das retenções examinadas demonstra os quatro itens primários ou o contraste P4 completo. Esta fatia, isoladamente, não sustenta alegação de novidade nem encerra a revisão.
