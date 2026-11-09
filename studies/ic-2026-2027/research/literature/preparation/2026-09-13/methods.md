# Método para concluir a preparação do corpus

Consulta em 2026-09-13. Esta nota orienta a preparação autorizada por Davi;
não altera o protocolo v3 nem registra decisões humanas.

A melhor sequência é conferir identidades e fontes, apresentar os conflitos
sem repetições e preparar referências humanas ligadas à aquisição atual.
Depois vêm calibração medida, triagem, texto completo, extração e síntese.
Repetir a busca já encerrada não resolve esses gargalos.

## O que as fontes sustentam

O capítulo 4 do Cochrane Handbook distingue registros repetidos de um mesmo
relato e relatos diferentes de um mesmo estudo. Recomenda conservar os relatos
secundários, documentar decisões e ser inclusivo na triagem inicial. Aplicamos
essa distinção à organização bibliográfica; as exigências clínicas do manual
não se tornam critérios desta revisão de dinâmica de opiniões. Fonte:
[capítulo 4, seções 4.6.1–4.6.4](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04).

A Crossref explica que metadados parecidos podem indicar tanto duplicatas como
itens diferentes. Um alias registrado tem significado distinto de uma simples
coincidência de título. Portanto, DOI plural ou destino editorial comum pede
verificação da relação, não eliminação arbitrária de um identificador. Fonte:
[Conflict report, cenários e aliases](https://www.crossref.org/documentation/reports/conflict-report/).

O próprio arXiv documenta a correspondência entre `arXiv:ID` e
`10.48550/arXiv.ID`, distinguindo esse DOI do DOI editorial informado pelo
autor. A correspondência permite investigar uma equivalência de identificadores;
não torna preprint e publicação editorial intercambiáveis para extrair resultados.
Fonte: [comunicado oficial do arXiv, regra e FAQ](https://blog.arxiv.org/2022/02/17/new-arxiv-articles-are-now-automatically-assigned-dois/).

PRISMA 2020 pede relato dos revisores, da independência, das discordâncias e do
uso e validação de automação. Dois modelos não equivalem a dois revisores
humanos. A descrição final deve identificar exatamente quem decidiu e o que
foi automatizado. Fonte:
[checklist expandido, itens 8 e 9](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf).

PRISMA-S pede estratégias completas, fontes, datas e método de deduplicação.
Isso favorece manter consultas e observações por fonte, distinguindo o total
recebido do número de obras após decisões de identidade. Fonte:
[PRISMA-S, itens 8, 13, 15 e 16](https://link.springer.com/article/10.1186/s13643-020-01542-z).

## Aplicação neste corpus

| Operação | Decisão operacional e limite |
| --- | --- |
| Identificadores exatos | Reproduzir a política 2 aprovada. Relações entre tipos e aliases entram como propostas com fontes, sem alterar o agrupamento histórico. |
| Coincidências de título | Organizar candidatos para análise; nunca fundir só pelo título. Autores, ano e local de publicação ajudam a conferir, mas não substituem a decisão prevista no protocolo. |
| Pares repetidos | Um cartão por par de obras propostas, conservando todos os pares de observações e seus identificadores. O componente do grafo é contexto, não uma obra aceita. |
| Títulos ausentes | Preservar a ausência na observação original. Separar título editorial comprovado, resenha sem título próprio e acesso bloqueado. Não usar o título do livro como título autoral da resenha. |
| Calibração | Vincular os casos a páginas v3 retidas; separar ajuste e verificação por obra e por página. Referências, justificativas e extrações são de autoria humana. |
| Amostra | Declarar seleção, diversidade e limitações. Cinquenta obras são o mínimo do protocolo por etapa medida, não uma estimativa de cobertura do campo. |
| Texto completo | Distinguir URL disponível, bytes recebidos, permissão registrada, ingestão validada e referência de extração completa. |
| Cobertura suplementar | Registrar buscas adicionais e rastreamento de citações como sucessores. Os 64 desafios usados para expandir consultas são regressão de cobertura, não avaliação independente de recall. |

Adotamos a compactação da apresentação porque reduz trabalho repetido sem
mudar uma única decisão de identidade. Uma fusão automática por similaridade
reduziria mais a fila, mas falta a evidência que a política exige. Trocar de
software de revisão tampouco resolve os conflitos de fontes ou produz
referências humanas; não há necessidade demonstrada de outra dependência.

Os limiares de 50 obras, recall mínimo de 0,95, zero falsas exclusões e auditoria
humana vêm do [protocolo do estudo](../../protocol/opinion-dynamics-systematic-map-v3.json)
e do [processo de calibração](../../../../../../docs/process/systematic-review-calibration.md),
não de uma imposição numérica de PRISMA. A fila v3 continua incompleta até uma
transição registrada de resolução. A preparação de casos não autoriza executar
a triagem do corpus.

## Verificação necessária para encerrar esta entrega

Conferir hashes e contagens diretamente nos artefatos; verificar cada proposta
de metadados contra sua fonte; reproduzir a seleção dos casos; confirmar que
nenhuma resposta humana foi criada; testar acesso ao formulário sem alterar
respostas existentes; submeter este pacote a revisão independente. Resultados
e limitações ficam no registro de integração desta mesma pasta.
