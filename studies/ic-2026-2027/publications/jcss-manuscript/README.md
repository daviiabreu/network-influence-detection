# Manuscrito IC — preparação para JCSS

**Status: rascunho; pergunta escolhida pelo agente coordenador sob delegação, pendente de ratificação humana. A v1 está congelada; a emenda sucessora v4 foi congelada em `37513841` e está passando pelos gates, sem resultado confirmatório.** O artigo trata da fronteira de detecção $a^*(r)$ entre trajetórias de reorganização semelhantes às de influência e nulos de persistência/atualização em painel sintético de 11 ondas. Não há resultado confirmatório. A revisão focada de antecedentes está em consolidação e o mapa sistemático v4 continua como entrega separada. O texto não atribui à escolha do agente a aprovação científica do Research Owner.

O plano de venue é tentar primeiro o *Journal of Computational Social Science* (JCSS), com o *Journal of Artificial Societies and Social Simulation* (JASSS) como alternativa especializada. É uma estratégia de trabalho, condicionada ao encaixe da contribuição que vier a ser demonstrada, às regras vigentes na submissão e à decisão científica posterior. Os requisitos consultados em 24/09/2026 estão em [author-guidelines.md](author-guidelines.md).

O [pipeline de redação e revisão](pipeline/README.md) reúne checklist de venues verificado em 27/09/2026, briefs para seções independentes do tema, revisão adversarial, modelo ODD e checagens mecânicas para o PDF compilado. Ele prepara a escrita sem antecipar a escolha da pergunta ou fechar os resultados.

| Parte | Entrada necessária antes de fechar o texto |
| --- | --- |
| Título, resumo e palavras-chave | O título e as palavras-chave são provisórios; o resumo depende de resultados validados. |
| Introdução | A pergunta e as diferenças específicas frente aos antecedentes estão redigidas; conferir após a consolidação e segunda leitura da revisão focada. |
| Referencial teórico | O texto inclui confiabilidade de painéis e validação longitudinal; revisar a seleção das famílias de modelos contra a síntese consolidada. |
| Materiais e métodos | Descrevem a v4 sucessora, sua exposição de calibração, os gates e a janela operacional; conferência final contra emenda congelada e saídas validadas ainda pendente. |
| Resultados | Cinco entradas `generated/*.tex` aguardam tabelas e figuras geradas de manifests validados, com inventário completo e resultados negativos ou inconclusivos. |
| Discussão e conclusão | Regras de interpretação e rascunho com campos explícitos aguardam resultados validados e síntese aceita. |
| Agradecimentos e declarações | Autoria, apoio, ética, disponibilidade de dados/código e interesses apurados para o trabalho efetivo. |
| Referências | Somente obras citadas, com metadados e suporte de afirmações conferidos. |

Este rascunho usa agentes de IA na preparação e na redação. A declaração factual atual está em [methods.tex](sections/methods.tex). A revisão e ratificação humana do texto final ainda são necessárias antes da submissão, conforme a [regra da JCSS](author-guidelines.md).

## Regras de escrita

Escrever o artigo em inglês claro para leitores interdisciplinares. Vincular cada afirmação factual a uma fonte primária ou ao artefato científico aceito, com localização em [claim-evidence.md](claim-evidence.md). Não inferir novidade de uma busca curta nem citar a venue por quota. Não inventar dados, medidas, achados, aprovação ou acesso público a materiais restritos. Separar hipótese, proposta, execução e inferência. Atualizar as instruções editoriais imediatamente antes de submeter. Um pacote de submissão, se houver, será exportado dos registros canônicos; este rascunho não é uma cópia da evidência privada.

O [main.tex](main.tex) usa a estrutura solicitada por Henrique. Parte de [background.tex](sections/background.tex) veio da leitura exploratória das candidatas e ainda depende da síntese focada. A pasta `publications/README.md` descreve o pacote final com `manuscript/`, `claim-evidence/`, `figures/`, `tables/` e `submission/`; esta pasta permanece um rascunho até haver protocolo congelado e resultados validados.
