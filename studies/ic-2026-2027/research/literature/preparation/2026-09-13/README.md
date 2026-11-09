# Preparação da revisão sistemática — 13/09/2026

Este pacote reúne a auditoria integral das identidades, a conferência dos
metadados pendentes e o material atualizado para autoria da calibração.

A busca v3 permanece preservada: 1.027 consultas, 54.570 observações e
46.400 obras propostas. Essas obras ainda não são um conjunto de estudos
incluídos. O pacote não encerra a revisão sistemática.

## Entregas verificáveis

| Entrega | Resultado |
| --- | --- |
| [Auditoria de identidades](identity-audit.md) | Reprodução integral da deduplicação e 10.754 cartões que conservam os 20.964 pares originais. Nenhuma fusão aplicada. |
| [Subfila nativa de identidade](identity-transition.md) | Transição implementada e aplicada ao corpus real, com replay exato, seis novos objetos e 11.821 arquivos anteriores preservados. Aguarda decisões; o agregado permanece incompleto. |
| [Metadados e fontes](metadata-sources.md) | Nove títulos pendentes e dez conflitos de DOI conferidos; três títulos editoriais e um alias confirmados. Propostas vinculadas a 60 projeções de fontes e falhas de acesso. |
| [Calibração](calibration-readiness.md) | Formulário v3 com 50 trabalhos, 100 tarefas de título/resumo e uma extração de seis campos. Fontes reproduzidas e legado preservado; referências e histórico de ajuste permanecem de autoria humana. |
| [Importação das referências](calibration-import.md) | Conversão determinística da exportação para suíte nativa, testada com dados sintéticos e revisada após correções de proteção dos destinos HTTP. |
| [Texto completo](fulltext-preparation.md) | Uma versão fixa com CC BY 4.0, 26 páginas e ingestão nativa, para preparar a referência de extração. |
| [Método](methods.md) | Escolhas operacionais fundamentadas em Cochrane, Crossref, arXiv, PRISMA e no protocolo do estudo. |
| [Verificação](validation.md) | Comandos, revisão de código, fontes, reprodução local e limites de cada resultado. |

Os cartões se dividem em 442 pares com conflito de identificador exato,
1.951 com ponte sintática entre arXiv e DOI arXiv, e 8.361 sinalizados apenas
por título. Essa organização reduz repetição na apresentação; não reduz por
si só o número científico de obras. Os 4.990 componentes são agrupamentos
para análise, e não decisões de que todos os seus membros sejam a mesma obra.

## Revisão independente e correções

O autor da auditoria de identidade revisou o pacote de metadados e método;
o autor dos metadados revisou identidade e calibração. Nenhum aprovou o
próprio resultado. A coordenação também refez a contagem com uma implementação
independente em JSON e busca em grafo, e reconferiu os três títulos Springer
diretamente nas páginas editoriais.

A [revisão de metadados](review-metadata-methods.md) encontrou uma afirmação
sem suporte suficiente: tratar uma entrada institucional no campo de autoria
como erro confirmado. O relatório e o JSON foram corrigidos para registrar
apenas a suspeita, preservando a entrada. Os snapshots anteriores permanecem
inalterados. A [revisão de identidade e calibração](review-identity-calibration.md)
delimita exatamente os materiais e verificações cobertos.

A [revisão do limite da CLI](review-calibration-input-limit.md) conferiu a
correção que permite ler a seleção e a suíte reais, ambas maiores que 10 MB.
O teto específico passou a 20 MB, preservando a leitura privada e a recusa dos
campos humanos pendentes. A CLI nativa gerou 101 tarefas a partir da seleção
real; a validação da suíte preparada chegou aos sentinelas e a recusou pelo
motivo esperado. Nenhum modelo foi executado nesse teste.

O [formulário revisado](http://127.0.0.1:8768/) está disponível neste computador.
Ele permite registrar decisões, trechos e justificativas, consultar o PDF e
exportar as respostas. A autoria precisa registrar também o histórico real de
ajustes dos agentes, que ainda não foi informado.

## O que ainda impede a revisão completa

Há duas dependências distintas. A primeira é resolver as propostas de
identidade e metadados com decisões registradas. A
[transição compatível](identity-transition.md) foi implementada e aplicada:
54.561 registros reproduzem exatamente as 46.391 obras tituladas e todos os
20.964 candidatos, agora em uma subfila nativa com linhagem. Os nove registros
restantes permanecem vinculados ao pai e ao recibo agregado, sem exclusão.
O replay confirmou o resultado sem escrita e os arquivos anteriores continuam
inalterados.

A subfila aguarda decisões de identidade. Ela não resolve títulos, aliases ou
os dez conflitos de prontidão. A promoção das propostas de metadados ainda
exige uma operação própria com fontes e disposições registradas. Os casos
verdadeiramente sem título e as relações entre manifestações precisam de uma
disposição explícita; o corpus agregado continua incompleto.

A segunda é a autoria humana das referências de calibração. O formulário
preparado não foi preenchido pelos agentes. Depois de referências válidas,
histórico de ajuste e configuração congelados, a calibração deve ser executada
e auditada. Só então vêm a triagem do corpus, decisões de exclusão, textos
completos, extração, avaliação e síntese. A adequação ao artigo e a escolha
final da venue continuam posteriores à definição da contribuição.

O trabalho atual não executou inferências de triagem ou extração, não escolheu
uma pergunta científica e não registrou aceitação em nome de Davi. O
[estado geral](../../READINESS.md) mantém essas fronteiras.
