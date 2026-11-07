# Revisão independente das proposições exploratórias

Revisão de 12/09/2026, concluída em contexto isolado por `/root/proposal_review`. Objeto: `review-input.md`, SHA-256 `a7d37c2ae60b93f8d57d7eda391e35ee0b638d6b517c2ed448443d194315d939`, no checkout cujo HEAD era `623704c4a7aa3db4fcf4e44f445bbaf6f8e4b34a`. As linhas abaixo referem-se a esse arquivo. Esta é evidência de revisão de agente sobre a prontidão das propostas; não constitui aceite científico, revisão canônica de síntese da RSL ou decisão de venue.

## Escopo e isolamento

Li apenas o pacote de revisão, as instruções raiz e do estudo, `CONTEXT-MAP.md`, `docs/agents/domain.md`, `studies/ic-2026-2027/CONTEXT.md` e os documentos de arquitetura, ciclo de pesquisa, validação de engenharia e processo de venues exigidos pelas instruções. A busca por protocolo/README/AGENTS sob `research/questions/` não encontrou arquivo adicional com esses nomes. Não li outros memorandos exploratórios, justificativas dos autores das propostas, rankings, memórias de sessões ou histórico da conversa. Consultei diretamente as fontes primárias relacionadas abaixo e duas referências metodológicas sobre scores. Não executei modelos ou experimentos publicados; os cálculos foram determinísticos, com a biblioteca padrão do Python 3.9.6 em macOS arm64.

## Defeitos acionáveis

### A1 — O alvo probabilístico ainda não permite verificar a comparação proposta

Local: linha 8. A descrição de Moor-Smith e Carpentras é fiel, mas a proposta ainda não define o score, o objeto aleatório avaliado, o condicionamento nem como a camada de amostragem entra em ambos os métodos. Isso impede verificar se uma eventual vantagem compara previsões para a mesma observação. Na fonte, a previsão é de um passo, reiniciada na distribuição observada anterior, e a perda é a média dos erros entre realizações; não é o Wasserstein da distribuição média do ensemble. [Artigo, §§2.1.3, 2.3 e 3.2](https://arxiv.org/html/2602.00876v1).

Reprodução da consequência: represente um histograma de dois bins pela fração `Y` no segundo bin. Se `P(Y=0)=0,8` e `P(Y=1)=0,2`, uma realização independente do gerador correto tem `E|X−Y|=0,32`, enquanto a previsão fixa `X=0` tem erro `0,20`. O primeiro alvo recompensa aqui uma previsão pontual central. Com o termo de dispersão do energy score, `E|X−Y|−½E|X−X′|`, os riscos passam a `0,16` e `0,20`. A inversão ilustra alvos distintos; não revela erro do Wasserstein.

Correção sugerida: escrever antes do piloto uma especificação curta de `Qθ(Ht+1 | informação observada até t)`, com bins, tamanho amostral, operador de observação e horizonte comuns. Explicitar a média de `W1` usada como comparador e escolher um score próprio para a lei dos histogramas, sem comparar diretamente as magnitudes de scores diferentes. Uma opção verificável é o energy score com norma euclidiana no vetor de frequências, expoente `0<β<2` e termo entre duas realizações independentes; fixar também sua estimativa com ensemble finito. [Gneiting e Raftery, 2007, §4.3, eq. 22 e teorema 5](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf).

Não atribuo ao pacote uma escolha de energy score que ele não contém. Contudo, chamar uma futura versão baseada diretamente em `W1` de estritamente própria exigiria prova adicional. Para histogramas nos bins `0,1,2`, as leis equiprováveis `P={(0,1;0,5;0,4),(0,2;0,5;0,3)}` e `Q={(0,1;0,6;0,3),(0,2;0,4;0,4)}` são diferentes, mas têm divergência de energia baseada em `W1` igual a zero. O código abaixo reproduz o empate. A distinção entre tipo negativo e tipo negativo forte está documentada em [Lyons, 2013, introdução e §3](https://rdlyons.pages.iu.edu/pdf/dcov-published.pdf). A alternativa euclidiana evita esse problema específico; ela não garante identificação dos parâmetros do gerador ou da influência humana.

### A2 — Incluir a hipótese `tol<c` na descrição da garantia para completos

Local: linha 9. A descrição omite `tol<c`, hipótese explícita do teorema 4. O contraexemplo respeita essa condição, mas uma referência posterior à garantia pode perdê-la. Correção sugerida: “O teorema 4 identifica os grupos finais em grafo completo sob `tol<c`; o uso numérico em outros grafos não recebe essa garantia.” [Thompsky et al., §V.2, teorema 4](https://arxiv.org/html/2605.20418v2#S5.SS2).

## Fatos verificados sem defeito adicional

O artigo de Thompsky et al. define a parada pela amplitude de opiniões em cada componente efetivo, usa `tol=0,01` e aplica o procedimento a grafos completos e esparsos. O texto também reconhece que componentes finais e grupos de opinião-limite podem diferir fora dos completos. A proposta não estende o teorema a grafos esparsos. [§V.2, eq. 31 e texto após o teorema 4](https://arxiv.org/html/2605.20418v2#S5.SS2).

A linha 10 reproduz um contraexemplo válido de suficiência, com confiança estrita e atualização simétrica. Aritmética racional independente produziu:

| Estado | Opiniões | Componentes efetivos | Amplitudes | Distância da ponte |
| --- | --- | --- | --- | --- |
| Inicial | `(0; 0,009; 0,096; 0,105)` | `{0,1}`, `{2,3}` | `0,009`, `0,009` | `0,105` |
| Após `(0,1)` | `(0,0045; 0,0045; 0,096; 0,105)` | `{0,1}`, `{2,3}` | `0`, `0,009` | `0,1005` |
| Após `(2,3)` | `(0,0045; 0,0045; 0,1005; 0,1005)` | `{0,1,2,3}` | `0,096` | `0,096` |

Os dois primeiros estados satisfazem a parada, e o terceiro reativa a ponte. A sequência prova possibilidade matemática; não mede frequência, viés em estatísticas agregadas ou impacto nos resultados publicados.

O [código fixado em `5e33664982bda6b7576074ff47772791459ea22c`](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py#L259) foi acessado. As linhas 208–211 usam confiança estrita e atualização simétrica. As linhas 264, 280, 304 e 316 fazem verificações sobre arestas e amplitudes; não calculam a separação entre intervalos proposta na linha 11. Esses predicados aceitam o estado inicial do contraexemplo quando avaliados. A rotina efetiva agenda a verificação após atualizações, sob as condições da linha 248: isso não demonstra uma execução do código parando em `t=0`. Não instalei suas dependências nem executei a rotina publicada.

As equações 1 e 3 no HTML e no texto extraído do [PDF v2, pp. 2–3](https://arxiv.org/pdf/2605.20418v2) apresentam `xj + µ(xj−xi)` para a segunda opinião; o código usa `xj + µ(xi−xj)`. A primeira forma não é convexa. O cálculo segue a regra simétrica explicitada na proposta e implementada no código. Registrar essa escolha na futura especificação evita reproduzir a expressão inconsistente do artigo; os números da linha 10 permanecem corretos.

O certificado da linha 11 é suficiente para impedir interações entre os componentes certificados sob as hipóteses declaradas. Formalmente, para cada componente `Ca` no instante da certificação, fixe `Ia=[ma,Ma]`, seu intervalo naquele instante, e imponha

`dist(Ia,Ib)=max(0, mb−Ma, ma−Mb) ≥ c`

para cada par com ao menos uma aresta da topologia-base entre eles. Suponha, por indução, que ainda não houve interação entre componentes: atualizações convexas internas mantêm cada opinião em seu intervalo fixado. Logo, nenhuma aresta entre eles satisfaz `|xi−xj|<c`, fechando a indução. A igualdade é segura para confiança estrita; se a regra permitir interação em `≤c`, a condição deve ser `>c`. Em computação finita, uma margem numérica conservadora deve preservar essa desigualdade. O teste rejeita o contraexemplo porque `0,096−0,009=0,087<c`.

Como complemento a `amplitude<tol<c`, ele também conserva as arestas efetivas internas existentes. Não certifica tempo restante de convergência, necessidade da condição, nem desigualdade entre opiniões-limite de componentes sem aresta-base entre si. Ruído, repulsão, topologia ou confiança variáveis exigem outra análise. Não identifiquei erro lógico na formulação candidata.

Os antecedentes da linha 12 sustentam a afirmação limitada de que partes dessas intervenções já foram estudadas:

| Manifestação consultada | Localizador e conteúdo relevante |
| --- | --- |
| [Ju et al., arXiv v1 de 2024](https://arxiv.org/html/2412.05093v1) | §5, “Sensitivity to prompts”, e apêndice A.4: variações na formulação e formatação dos prompts. |
| [Cisneros-Velarde, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.101.pdf) | §6, p. 7 do PDF: comparação com e sem memória das duas interações anteriores. |
| [Yang, arXiv v1 de 2026](https://arxiv.org/html/2606.22203v1) | Resumo e §5: paráfrases e controles de acoplamento/estrutura; o documento se identifica como preprint. Não validei suas alegações de primazia. |
| [DEBATE, arXiv v6](https://arxiv.org/html/2510.25110v6#A15) | Apêndice O: temperatura e remoção da opinião privada inicial e do primeiro tweet da memória. |
| [Sarangi et al., arXiv v1](https://arxiv.org/pdf/2605.30258v1) | Apêndice C.3, H4, p. 19 do PDF: remoção dos campos explícitos de opinião/crença anterior com observações e memória preservadas. O resumo registra revisão em andamento no NeurIPS 2026. |
| [Mehdizadeh e Hilbert, arXiv v1](https://arxiv.org/abs/2606.04197v1) | Somente resumo: interação entre profundidade de memória e oito topologias em Naming Game. Não fiz auditoria do método ou dos resultados completos. |

Os links arXiv acima identificam manifestações de preprint; apenas a versão de Cisneros-Velarde foi conferida como publicação nos proceedings citados. Esta tabela não estabelece que cada fonte cobre todos os eixos nem que a proposta careça de novidade. A situação bibliográfica interna descrita na linha 7 foi mantida como premissa fornecida, sem auditoria do corpus.

Nas políticas consultadas em 12/09/2026, [CCR](https://journal.computationalcommunication.org/openaccess) declara ausência de APC; [JCSS](https://link.springer.com/journal/42001/how-to-publish-with-us) oferece assinatura sem APC e OA opcional. Para [PLOS](https://plos.org/fees/), confirmei também no navegador a associação do link `journals.plos.org/complexsystems/` ao card “Research Article $3,165”, no mesmo contêiner da árvore de acessibilidade. A extração textual da página não preservava essa associação e a requisição direta via Python recebeu HTTP 403; a página abriu normalmente no navegador.

A divergência informada também permanece: a [política central](https://plos.org/fees/) usa instituição do autor e ausência de financiamento externo, com US$940 para o grupo B nas demais revistas; a [página do periódico](https://journals.plos.org/complexsystems/s/journal-information) usa localização do financiador e US$500. Não apliquei desconto nem converti ausência de APC em ausência de qualquer custo. Não auditei o inventário citado na linha 14.

A linha 13 não afirma participação remota confirmada. Não há base nesta revisão para substituir esse desconhecido por uma nota positiva, e submissão eletrônica de manuscrito não demonstra política de participação/apresentação. Não fiz levantamento exaustivo das políticas das cinco revistas nem das 235 venues; não inferi adequação final, elegibilidade de descontos ou orçamento disponível.

## Reprodução mínima dos cálculos

O bloco usa somente a biblioteca padrão, sem sementes ou aleatoriedade. Foi executado novamente a partir deste relatório; os asserts passaram.

```python
from fractions import Fraction as F
from itertools import product

x = list(map(F, ["0", ".009", ".096", ".105"]))
c, tol = F(".1"), F(".01")
assert x[1] - x[0] < tol and x[3] - x[2] < tol
assert x[3] - x[0] >= c
for i, j in [(0, 1), (2, 3)]:
    assert abs(x[i] - x[j]) < c
    x[i] = x[j] = (x[i] + x[j]) / 2
assert x == list(map(F, [".0045", ".0045", ".1005", ".1005"]))
assert abs(x[0] - x[3]) == F(".096") < c
assert F(".096") - F(".009") == F(".087") < c

truth = [(F(0), F(4, 5)), (F(1), F(1, 5))]
risks = []
for forecast in [truth, [(F(0), F(1))]]:
    loss = sum(py * px * abs(y - z) for y, py in truth for z, px in forecast)
    spread = sum(p * q * abs(a - b) for a, p in forecast for b, q in forecast)
    risks.append((loss, loss - spread / 2))
assert risks == [(F(8, 25), F(4, 25)), (F(1, 5), F(1, 5))]

# Coordenadas CDF nos dois intervalos entre bins: W1 e a norma L1 aqui.
P = [(F(1, 10), F(6, 10)), (F(2, 10), F(7, 10))]
Q = [(F(1, 10), F(7, 10)), (F(2, 10), F(6, 10))]
def cross_distance(A, B):
    return sum(sum(abs(a - b) for a, b in zip(x, y))
               for x, y in product(A, B)) / len(A) / len(B)
assert P != Q
assert 2 * cross_distance(P, Q) - cross_distance(P, P) - cross_distance(Q, Q) == 0
print("Cálculos determinísticos: OK")
```

## Limites de conclusão

Há uma lacuna de especificação experimental (A1) e uma hipótese omitida na descrição do teorema (A2). Nenhuma delas altera a validade do contraexemplo de quatro nós ou da condição suficiente por intervalos. Não se mediram efeito experimental, prevalência bibliográfica, novidade completa ou recuperação de parâmetros. As fontes de artigo, código e dados não receberam uma auditoria de licenças; uma licença do artigo não foi usada para autorizar aquisição ou reutilização de dados/código. O único arquivo produzido por esta revisão é este relatório; não houve commits, mensagens externas ou alteração de estado científico canônico.
