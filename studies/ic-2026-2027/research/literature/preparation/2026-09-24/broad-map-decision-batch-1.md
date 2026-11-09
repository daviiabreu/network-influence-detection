# Lote 1 de decisão para o mapa amplo

Este pacote prepara a primeira decisão humana necessária para continuar o
corpus amplo. Ele não registra uma decisão do Research Owner e não autoriza
triagem, inclusão, exclusão ou síntese.

Atualização posterior: Davi [aprovou somente a política v5 exata](../../../decisions/2026-09-24-editorial-metadata-policy-v5.md).
Este texto preserva a pergunta como foi apresentada; a próxima decisão é sobre
o [request C2 v2 preparado](c2-v2-result.md), não sobre aprovar novamente a
policy. Nenhuma das oito escolhas recebeu decisão por essa resposta.

## Decisão solicitada

Decidir se deve ser adotada a proposta editorial
[`opinion-dynamics-systematic-map-v5-editorial-refresh-proposal.json`](../../protocol/opinion-dynamics-systematic-map-v5-editorial-refresh-proposal.json),
hash canônico e SHA-256 do arquivo
`4c4eda364e780acd86ce367b1d7b7bd5854f4c3352f6f15a01b735a649a568e5`,
como sucessora da v4 somente para identificação bibliográfica.

A proposta mantém as buscas, fontes de aquisição, critérios de elegibilidade,
limiares e conclusão do mapa amplo. A mudança acrescenta uma política de
resolução de metadados com oito fontes de identificação e representação
explícita de obra editorialmente sem título. A
[revisão da proposta](../../protocol/opinion-dynamics-systematic-map-v5-editorial-refresh-review.md)
explica as duas fontes acrescentadas na reconferência de 16/09.

## Evidência disponível

O lote privado de metadados foi reaberto em 24/09. Seus hashes publicados
coincidem com os arquivos presentes e privados:

| Artefato | SHA-256 |
| --- | --- |
| `choices.json` | `eeff79017bbf1bd25a7f886128e87916713a3e383eca249422d151ef48264553` |
| `evidence-index.json` | `45ce841344d801810b2b42379853c52b9744eb1842afb789e5f9261ebf756f75` |
| `validation.json` | `f761b2585ff24fa993e1bcdd8e1859d586fc294eb82bc5aaea9bd800f6a9e589` |
| `REVIEW.md` | `7889b851b202d611e508a72f54deba11d23e7872ba1355f995cba39260cde42e` |

A validação registra nove propostas: quatro `title_resolved`, quatro
`explicitly_untitled` e uma `defer`. Os checks de contrato, identificador,
fonte, DOI e recortes exatos passaram; 30 arquivos originais ficaram
inalterados. O próprio registro mantém `policy_chain_missing=true`,
`request_published=false`, `owner_decision_recorded=false` e
`scientific_acceptance=false`.

Africa Today permanece fora da decisão. A evidência posterior de `[Untitled]`
não tem ainda uma captura source-bound coberta pela política proposta. O caso
continua `defer`; nem o título do livro nem a projeção posterior devem ser
promovidos por inferência.

## Recomendação

Recomendo adotar esta proposta v5. Ela é a menor emenda que representa os
oito casos já sustentados sem alterar o escopo amplo nem decidir elegibilidade.
O aceite deve ficar limitado à política e aos bytes exatos acima; não deve ser
registrado como aprovação das nove escolhas de metadados. Essa escolha permite
progresso parcial, não o fechamento do corpus: Africa Today continuará impedindo
`identity_ready` e C4 até uma captura source-bound e uma policy sucessora
específica.

Se aprovada, a próxima transição é registrar a aprovação Git-bound, preparar
somente em leitura o request C2 v2 sobre as oito escolhas sustentadas e apresentar
esse request exato para uma segunda decisão. Depois do sucessor parcial C2, a base
nativa pode ser exportada para regenerar e auditar as propostas amplas de
identidade. Não se deve solicitar a decisão C3 final enquanto Africa Today e os
novos pares eventualmente abertos pelos títulos continuarem pendentes.

Se não for aprovada, C2 v2 não pode usar essas fontes nem representar os quatro
estados sem título. O corpus permanece incompleto até uma política sucessora ou
outra evidência versionada resolver a mesma lacuna.

## Formulação curta para o responsável

> Recomendo adotar a proposta editorial v5 de hash
> `4c4eda364e780acd86ce367b1d7b7bd5854f4c3352f6f15a01b735a649a568e5`
> somente para permitir fontes de identificação e a representação explícita
> de obras sem título no mapa amplo. Isso não aprova os metadados individuais,
> não muda critérios e não decide elegibilidade. Você aprova essa emenda?
