# Verificação delimitada das correções A1 e A2

Registro de 12/09/2026 por `/root/proposal_review`, o mesmo revisor do parecer inicial. Objeto exclusivo desta verificação: `review-response.md`, SHA-256 `e8fc9b76dd0790ec41c012d4c62c91a596147035015793c3e66a43b927dc6b58`.

Os dois achados foram resolvidos no nível de proposta pré-piloto pelo conteúdo desta resposta. Não há pendência remanescente de A1 ou A2 nesse escopo.

## A1 — Resolvido na especificação apresentada

As linhas 12–24 definem a lei do histograma observado, seu condicionamento, categorias e discretização, horizonte de um passo, inicialização e camada de observação. As alternativas recebem a mesma informação observada e o mesmo tamanho amostral futuro; o controle com parâmetros conhecidos não recebe o estado latente verdadeiro. O comparador sem mudança preserva a mesma camada de amostragem.

As linhas 26–35 fixam energy score euclidiano com expoente 1 e `R>=2`. O denominador `2*R*(R-1)` está correto para a soma sobre pares ordenados `r!=s` de réplicas independentes. A resposta distingue a média de W1 entre realizações de W1 aplicado à média dos vetores, mantém o alvo observado comum e compara resultados dentro de cada score. Também evita atribuir propriedade estrita à alternativa baseada em W1.

Essas definições resolvem a lacuna de verificabilidade apontada no parecer. A declaração de que parâmetros, réplicas e partições serão fixados antes da execução é compatível com a preparação pré-piloto; não equivale a uma especificação de execução já congelada. Esta conclusão não estabelece vantagem preditiva, identificação de parâmetros ou validade da observação empírica.

## A2 — Resolvido na descrição apresentada

As linhas 44–47 incluem explicitamente as duas hipóteses relevantes: grafo completo e `tol<c`. A garantia não é estendida aos outros grafos, e o microcaso conserva `0,01<0,1`. Isso corrige integralmente a omissão identificada em A2.

As linhas 51–55 também registram a escolha da atualização simétrica convexa do código fixado e distinguem a inconsistência de sinal no texto do artigo de uma eventual execução incorreta. A resposta preserva, assim, a convenção empregada no contraexemplo revisado.

## Escopo e preservação

Li somente `review-response.md` neste acompanhamento e comparei seu conteúdo aos dois achados já conhecidos. Não li `README.md`, `empirical-evidence.md`, o memo mecanístico ou outros memorandos; portanto, não atesto a propagação das correções para os documentos mencionados pela resposta. Não realizei nova auditoria bibliográfica, checagem de políticas de venues, execução de modelos ou revisão científica ampliada.

Os arquivos originais mantêm os mesmos hashes verificados ao encerrar o parecer inicial:

| Arquivo preservado | SHA-256 |
| --- | --- |
| `review-input.md` | `a7d37c2ae60b93f8d57d7eda391e35ee0b638d6b517c2ed448443d194315d939` |
| `independent-review.md` | `832d4d79b2c8bd701164abd95a93f3687a0e14842930d8ef243e750382c51c36` |

Este acompanhamento produz apenas `review-followup.md`. Resolver A1/A2 é evidência de revisão de agente sobre a proposta; não constitui aceite científico, autorização de execução ou seleção de pergunta/venue.
