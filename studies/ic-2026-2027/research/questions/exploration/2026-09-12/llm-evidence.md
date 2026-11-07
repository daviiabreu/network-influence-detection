# Evidências sobre propostas com agentes de linguagem

Esta leitura exploratória foi verificada em 12 de setembro de 2026, considerando trabalhos publicados ou depositados até 11 de setembro. Ela serve à preparação de propostas e não representa triagem, extração aceita ou síntese da revisão sistemática. A recomendação é manter esta linha como alternativa: os recortes mais imediatos encontrados já têm concorrentes muito próximos, e a reprodução exige recursos ainda não medidos.

## Resultados que delimitam uma possível contribuição

| Trabalho | Evidência consultada e localização | Consequência para a proposta |
| --- | --- | --- |
| Cisneros-Velarde, 2025 [1] | Página editorial; PDF, conclusão, seção 6 e limitações, pp. 7–8 do arquivo. Compara respostas livres e escolhas fechadas e discute memória de posições anteriores na tarefa de financiamento. | Variar formato ou acrescentar memória, por si só, já tem precedente direto. Não encontrei um repositório de reprodução identificado nas partes consultadas; isso não demonstra sua inexistência. |
| Ju et al., 2024 [2] | Resumo e texto HTML com organização das seções 3–5. Avalia simulações em relação a modelos de referência e reporta sensibilidade a pequenas alterações de instrução. | Uma proposta genérica de sensibilidade a prompts precisaria explicar o que acrescenta a essa avaliação. A conferência de equações e implementação permanece leitura posterior. |
| Cau et al., 2025 [3] | Texto editorial, seção 2.1, discussão e disponibilidade de dados. Compara enquadramentos e distribuições iniciais, analisando dispersão e entropia; identifica código e dados no repositório dos autores. | Repetir consenso sob enquadramento positivo/negativo também não delimita contribuição nova. O repositório público foi aberto, mas uma licença não foi localizada na página consultada. |
| Ashery et al., 2025 [4] | Trechos do original indexado no PMC, incluindo resultados, métodos e disponibilidade; a abertura direta posterior devolveu verificação de navegador. | Convenções linguísticas e opiniões sobre proposições precisam permanecer distintas. O artigo declara estudar populações artificiais, e não substituir participantes humanos. Há ponte para código e depósito, mas esta nota não certifica a reprodução. |
| Chuang et al., DEBATE, versão 6 de maio de 2026 [5] | Resumo, seções 1 e 5 e apêndices A, I, J, N e O em HTML. Inclui comparação com participantes, referências escalares, separação treino/teste e verificações de anotação e convergência. | Comparar consenso de LLMs com humanos ou acrescentar um modelo DeGroot já está contemplado. O apêndice A informa acesso de revisores via sistema de submissão; não estabelece acesso público utilizável aos dados. |
| Yang, junho de 2026 [6] | Texto HTML, seções 3, 5.4 e 6, e repositório do autor. Mede sensibilidade à opinião apresentada e testa transferência entre formas de interação. A própria análise limita o uso de um coeficiente obtido em pares para prever grupos. | Medir influência local e confrontar consenso coletivo já tem concorrente direto. Trata-se de preprint; suas afirmações precisam de reprodução e não constituem uma lei estabelecida. |
| Mehdizadeh e Hilbert, junho de 2026 [7] | Resumo e histórico do arXiv. Já combina memória e topologia no naming game e distingue estabilização de consenso. | Uma varredura de memória por topologia seria insuficiente como recorte. O comentário informa submissão ao JASSS, não aceitação ou publicação naquele periódico. |
| Hashimoto et al., julho de 2026 [8] | Página editorial e resumo da manifestação publicada em Findings ACL. Incorpora retorno de um ambiente econômico à dinâmica. | Acrescentar experiências econômicas a agentes também tem precedente. Não houve leitura integral ou verificação de código para esta nota. |
| Sarangi et al., maio de 2026 [9] | PDF, apêndice C.3, especialmente H3–H5, pp. 18–19 do arquivo. Já remove lembretes do estado anterior mantendo observações e memória, e compara interfaces de exposição. | A hipótese de que registrar a posição passada altera a dinâmica já tem teste próximo. Não promover uma proposta de “efeito da medição” sem uma comparação que esse desenho não responda. |

Estas observações não excluem nenhum trabalho do mapa sistemático. São razões para não apresentar ideias amplas como lacunas comprovadas. As análises de mecanismos artificiais também exigem verificar o enquadramento no critério de domínio humano do protocolo v3.

## Acesso e viabilidade

O repositório de Yang [10] exibe licença MIT e separa a análise dos logs retidos das chamadas ao provedor. A reprodução das análises pode, em princípio, começar sem novas inferências, mas nenhum script foi executado nesta exploração. A licença do código não autoriza automaticamente o uso de todos os modelos ou dados citados. O endereço do artigo consta no próprio texto, mesmo que o README ainda preserve um identificador bibliográfico a preencher.

O repositório de Cau [11] foi acessível; a ausência de licença identificada nessa consulta deve ser resolvida antes de reutilizar seus arquivos. No DEBATE, acesso reservado a revisores não foi convertido em disponibilidade pública. Não houve aquisição de dados de participantes, contratação de API, instalação de modelos ou execução de simulações.

A máquina local informou Apple M5, dez CPUs lógicas e 16 GiB de memória por `sysctl`. Isso não é um benchmark de inferência nem prova de que caiba a reprodução de um artigo. GPU e limites do VPS continuam sem inventário. Por essas razões, a avaliação de LLMs permanece abaixo das duas propostas que podem começar com modelos numéricos pequenos. Uma reanálise dos logs de [10] é uma alternativa de familiarização, sujeita a revisão do código e do escopo, não uma contribuição já escolhida.

## Busca direcionada e limites

Partimos do mapa exploratório retido e da navegação por títulos das propostas bibliográficas. As buscas externas foram direcionadas a trabalhos próximos que pudessem contradizer a novidade. Usaram pesquisa web e, nas consultas indicadas, restrição a `arxiv.org` e `aclanthology.org`. Foram seguidos links para fontes originais, código e versões; resultados secundários serviram somente como pistas.

Consultas literais relevantes:

```text
opinion dynamics LLM "output" "format" 2025 2026
"Cisneros-Velarde" opinion dynamics 2025 code
LLM opinion dynamics measurement robustness prompts 2026 2025
Ashery collective biases spontaneous emergence conventions LLM populations 2025 code
"Cisneros-Velarde" "opinion" "2025" [arxiv.org, aclanthology.org]
"opinion dynamics" "measurement" LLM [arxiv.org, aclanthology.org]
"opinion dynamics" "robustness" LLM 2026 [arxiv.org, aclanthology.org]
"LLM" "opinion dynamics" "format" site:arxiv.org
"LLM" "opinion dynamics" "measurement" "consensus"
"Emergent social conventions and collective bias in LLM populations" code data
LLM opinion dynamics "measurement" "observer" effect
LLM opinion dynamics "elicitation" "measurement" intervention
LLM social simulation opinion "probe" "memory" measurement
LLM simulation "measurement reactivity"
"EASE Configuration Facilitates" arxiv
"opinion dynamics" "probe" "measurement" site:arxiv.org/html
"opinion" "elicitation" "memory" "LLM" simulation site:aclanthology.org
```

Uma abertura incidental de arXiv:2410.08968 retornou um trabalho de alinhamento de segurança; não foi usada como evidência deste tema. BeliefShift, arXiv:2603.23848, foi lido apenas no resumo como pista sobre memória longitudinal. O registro arXiv:2605.27752 retornou o título corrente *Same Answer, Different Confidence* e permaneceu uma pista adjacente, sem importar resultados de calibração de confiança para dinâmica de opiniões. A versão 2 de DEBATE foi aberta antes de verificar a versão 6; os argumentos desta nota se referem à versão 6. O HTML de EASE falhou; o PDF original forneceu a passagem usada.

A busca foi encerrada para esta entrega quando os recortes imediatos tinham antecedentes identificáveis e as principais limitações de reprodução estavam explícitas. Isso não comprova saturação da literatura de LLMs, nem impede uma proposta posterior mais específica.

## Fontes

1. Pedro Cisneros-Velarde. *Biases in Opinion Dynamics in Multi-Agent Systems of Large Language Models: A Case Study on Funding Allocation*. Findings NAACL, 2025. [Página editorial](https://aclanthology.org/2025.findings-naacl.101/); [PDF](https://aclanthology.org/2025.findings-naacl.101.pdf). DOI 10.18653/v1/2025.findings-naacl.101.
2. Da Ju, Adina Williams, Brian Karrer e Maximilian Nickel. *Sense and Sensitivity: Evaluating the simulation of social dynamics via Large Language Models*. Preprint, 2024. [Texto, v1](https://arxiv.org/html/2412.05093v1).
3. Erica Cau, Valentina Pansanella, Dino Pedreschi e Giulio Rossetti. *Selective agreement, not sycophancy: investigating opinion dynamics in LLM interactions*. EPJ Data Science 14, 59, 2025. [Artigo](https://link.springer.com/article/10.1140/epjds/s13688-025-00579-1).
4. Ariel Flint Ashery, Luca Maria Aiello e Andrea Baronchelli. *Emergent social conventions and collective bias in LLM populations*. Science Advances, 2025. [Original no PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12077490/); [registro institucional](https://openaccess.city.ac.uk/id/eprint/35211/). DOI 10.1126/sciadv.adu9368.
5. Yun-Shiuan Chuang et al. *DEBATE: A Large-Scale Benchmark for Evaluating Opinion Dynamics in Role-Playing LLM Agents*. Preprint, 2025, versão 6 de 28/05/2026. [Texto](https://arxiv.org/html/2510.25110v6).
6. Dongxu Yang. *When Is Emergent Consensus Real? A Measured Coupling Gain and a Validity Diagnostic for LLM Agent Societies*. Preprint, 20/06/2026. [Texto, v1](https://arxiv.org/html/2606.22203v1).
7. Aliakbar Mehdizadeh e Martin Hilbert. *Exploring the Topology and Memory of Consensus: How LLM Agents Agree, Fragment, or Settle When Forming Conventions*. Preprint, 02/06/2026. [Resumo e histórico](https://arxiv.org/abs/2606.04197v1).
8. Ryuji Hashimoto et al. *From Heard to Lived Opinions: Simulating Opinion Dynamics with Grounded LLM Agents in Economic Environments*. Findings ACL, julho de 2026. [Página editorial](https://aclanthology.org/2026.findings-acl.580/).
9. Sneheel Sarangi et al. *EASE Configuration Facilitates A Reproducible Science of LLM Social Simulations*. Preprint, maio de 2026. [PDF](https://arxiv.org/pdf/2605.30258); [histórico](https://arxiv.org/abs/2605.30258).
10. Dongxu Yang. [llm-coupling-gain: código e logs](https://github.com/deeplethe/llm-coupling-gain), consulta em 12/09/2026. A árvore não foi congelada ou executada nesta entrega.
11. Erica Cau. [LLM-Opinion-Dynamics](https://github.com/ericacau/LLM-Opinion-Dynamics), consulta em 12/09/2026. Acesso ao repositório não equivale a licença verificada ou reprodução.
