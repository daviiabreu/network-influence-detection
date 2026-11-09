# Revisão independente de metadados e métodos

Data local: 13/09/2026, America/Sao_Paulo. Revisão somente de `metadata-sources.md`, `metadata-proposals.json` e `methods.md`; nenhum candidato foi editado. Os artefatos de identidade e calibração não foram usados como evidência desta revisão.

| Candidato revisado | SHA-256 |
| --- | --- |
| `metadata-sources.md` | `f887d7ccaa556aa5dd2836510c78d9db85788d7942ffd258f4edd244c2e7165f` |
| `metadata-proposals.json` | `a930282da2a9f3b4cb520fd75877a77f77f7b0e5355631b3f03dc9c5cb5b31a3` |
| `methods.md` | `c3e66edef39b666efb056e87b9b0cc2dd30f8b1bd2f2e5254b187b6720ce2839` |

## Achado acionável

### P2 — Qualificar como suspeita a alegação de erro de autoria em MarriottC14

Local: [metadata-sources.md](metadata-sources.md), linha 36; [metadata-proposals.json](metadata-proposals.json), linha 1063, `identifier_proposals[8].evidence_note`, obra `work.v2.ee09e0e8fc8e6120b1198a84`.

O relatório afirma que os dois depósitos apresentam “indevidamente” o nome de uma universidade como autor; o JSON repete `Both incorrectly expose a university string as an author entry` e orienta uma correção posterior. As projeções `crossref-de6ad4b3f407a154.json` e `crossref-bfd8293ea6e6e572.json` realmente preservam uma entrada `author.name` com University of Washington, endereço e CEP, além de Chris Marriott e Jobran Chebib. Isso demonstra a entrada institucional, mas não estabelece por si só que seja autoria incorreta. A [documentação de contribuidores do Crossref](https://www.crossref.org/documentation/schema-library/markup-guide-metadata-segments/contributors) admite pessoas e organizações como autores. A consulta DBLP retida não seleciona autoria, e `editorial-mit-ch118.json` registra HTTP 403 sem metadados editoriais; as fontes citadas no candidato não fornecem uma lista de autoria independente que descarte a participação institucional.

O problema é a passagem de observação a erro confirmado. Isso pode orientar uma futura limpeza a remover um contribuinte sem evidência suficiente. Qualificar nos dois arquivos como possível afiliação depositada no campo de autoria, mantendo a correção pendente até confrontar uma lista editorial ou uma manifestação primária permitida. Alternativamente, vincular uma fonte específica que confirme o erro antes de manter a afirmação categórica. Não é necessário alterar os registros originais nem concluir nesta etapa se a instituição é ou não autora.

Evidência privada, no diretório `~/.local/state/research-workbench/corpus-preparation-20260913/metadata-sources`:

| Projeção | SHA-256 | Campo conferido |
| --- | --- | --- |
| `crossref-de6ad4b3f407a154.json` | `4bf75b1b49a4ac838c256fb74bb3d441c4578693aa2b0480530c380a2fa98646` | `metadata.author` do DOI `10.1162/978-0-262-32621-6-ch118` |
| `crossref-bfd8293ea6e6e572.json` | `86c8628e254413d8e7d056dfab5e66e8e4b48a43599e8baf5fe4b7cedad58e3a` | `metadata.author` do DOI `10.7551/978-0-262-32621-6-ch118` |
| `editorial-mit-ch118.json` | `f04bb0ac22281a131769b5404367a9747076ff603f3a66986a4a8ec3618e1675` | HTTP 403, sem metadados |
| `dblp-nine-records.json` | `76119feed94afc1dcd1effd6cf9204db8881eec75fd6802455379f5373c79e4d` | Consulta de título, ano, veículo e DOI; autoria não selecionada |

## Verificações realizadas

O manifesto `13943c008cbdb783140418dc8d81d67f204ff3fd6f1579d0c3e9acb6ba1bcd1f` corresponde exatamente ao registro de 60 fontes do JSON. Todos os 60 arquivos existem, são JSON legível e coincidem com seus hashes e tamanhos. Os horários do registro de fontes, convertidos para America/Sao_Paulo, caem em 13/09/2026. O hash do inventário original foi conferido; a deduplicação CAS de entrada também foi conferida pelo hash antes de consultar apenas os metadados das propostas.

As nove propostas de título cobrem exatamente os nove `candidate_id`, `work_id` e conjuntos de observações originais; os títulos originais continuam nulos e os DOI coincidem. As dez propostas de identificadores cobrem exatamente os dez conflitos e preservam os conjuntos DOI e IDs DBLP originais. Foram reconciliados nove pares DOI distintos, 27 DOI do inventário, dois DOI adicionais ligados pelos depósitos consultados, nove publicações DBLP e 18 bindings DOI. Todos os `source_id` citados pelos candidatos resolvem no registro. Não há candidato promovido ou elegibilidade atribuída nesses registros.

Os nove depósitos Crossref têm arrays de título vazios ou contendo somente string vazia. Os três títulos Springer propostos coincidem literalmente com `citation_title`, e o `citation_doi` corresponde ao DOI do candidato nas projeções HTTP 200. JOIA continua explicitamente baseado em projeção indexada; a tentativa independente de abertura nesta revisão também não forneceu metadados e não foi repetida. Não foi elevado a verificação editorial direta.

As projeções atuais dos três sumários JSTOR confirmam a marcação sem título e distinguem o livro resenhado: [SEER 91(4)](https://www.jstor.org/stable/10.5699/slaveasteurorev2.91.issue-4), [SEER 93(3)](https://www.jstor.org/stable/10.5699/slaveasteurorev2.93.issue-3) e [Pennsylvania Magazine 141(1)](https://www.jstor.org/stable/10.5215/pennmaghistbio.141.issue-1). No [sumário OUP](https://academic.oup.com/jah/issue/89/4), o DOI da resenha está sob Book Reviews e o resenhista é James O. Farmer. O candidato preserva o cabeçalho editorial em campo separado. Africa Today mantém a limitação da evidência atual e a divergência de data; a nota histórica não é apresentada como metadado novamente recuperado.

O alias `10.2200/...` → `10.1007/...` é sustentado pelo redirecionamento REST 301 explicitamente retido, DOI de resposta e metadados concordantes. A [comunicação da Crossref](https://community.crossref.org/t/adding-redirects-for-aliased-dois-in-the-rest-api/13138) confirma essa semântica. As relações `is-identical-to` de Lucas76 e MukhopadhyayMR16 estão nos campos `relation` dos depósitos. A relação adicional ACM de ChienK92 não foi estendida ao DOI IEEE. Para os capítulos ALIFE, os recursos editoriais convergem, mas as consultas conservam seus DOI e relações vazias; os candidatos não transformam isso em alias formal. Os itens Bandits têm páginas 29–30 nos dois depósitos e não foram apresentados como versão integral em periódico.

Em `methods.md`, não foi encontrado achado acionável dentro do escopo. A distinção entre registros, relatos e estudos e a preservação de relatos secundários têm suporte no [Cochrane Handbook, 4.6.1–4.6.4](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04). Os [itens 8 e 9 de PRISMA 2020](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf) pedem descrição de revisores e automação; a nota não lhes atribui os limiares numéricos locais. O [PRISMA-S](https://link.springer.com/article/10.1186/s13643-020-01542-z) sustenta o relato de estratégias, datas, totais e deduplicação. A exigência local de 50 obras, recall 0,95 e zero falsas exclusões está atribuída ao protocolo/processo, e a separação de páginas entre ajuste e verificação é coerente com o processo local de calibração. Os 64 desafios também constam da revisão do protocolo v3; não são apresentados como recall independente. As referências locais dos dois Markdown resolvem.

## Limites

Esta revisão verifica os bytes das projeções, não os corpos HTTP transitórios cujo hash foi registrado sem preservação. As consultas web são projeções de páginas primárias, podem refletir rastreamento anterior e não estabelecem HTTP 200 direto. Não foram repetidas as 60 aquisições, baixados textos integrais, contornados bloqueios, executados modelos ou testes completos. Não foi demonstrada alteração dos candidatos; os três hashes foram reconferidos ao final da análise. O achado acima requer qualificação textual ou evidência de autoria adicional; o restante continua sendo proposta de preparação, sem aceitação de corpus ou decisão humana.

## Adendo — resolução do P2 de autoria

Conferência focada em 13/09/2026, America/Sao_Paulo. O achado e os hashes da revisão original acima são preservados; a conclusão deste adendo aplica-se às versões corrigidas abaixo.

| Candidato corrigido | SHA-256 | Bytes |
| --- | --- | ---: |
| `metadata-sources.md` | `69049842f1be5d212217ca11554e334547205daabae81a5a953a18f53ebb9444` | 27305 |
| `metadata-proposals.json` | `daf9a89d8572d1fb06d925c0fa770cf9c73865fb87c6f42bb218f7dfb13b6096` | 55156 |

P2 resolvido. A linha 36 do Markdown e `identifier_proposals[8].evidence_note` do JSON agora descrevem uma possível afiliação no campo de autoria, explicitamente como suspeita pendente de uma lista editorial independente ou outra manifestação primária permitida. O JSON determina preservar todas as entradas de origem; `proposed_action` continua preservando as manifestações e não orienta remover um contribuinte. Essa redação corresponde ao limite das projeções já verificadas e resolve a passagem indevida de observação a erro confirmado. Não foi produzida nova prova de autoria, removido contribuinte ou promovido candidato. `methods.md` permanece com o hash da revisão original. Esta checagem foi delimitada aos dois trechos corrigidos, sem repetir a aquisição das 60 fontes.
