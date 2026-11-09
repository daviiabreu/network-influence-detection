# Preparação da calibração — 2026-09-13

O [formulário v3](http://127.0.0.1:8768/) oferece 50 referências de triagem de
título/resumo e uma referência de extração com seis campos. Todas as respostas
começam vazias. O [formulário anterior](http://127.0.0.1:8767/) permanece intacto
para recuperação de eventual trabalho de Davi. Nenhuma resposta humana ou
`localStorage` do usuário foi inspecionado, preenchido ou exportado nesta
preparação. O estado científico continua o de [READINESS](../../READINESS.md).

## Material e vínculos

Os arquivos privados ficam sob
`~/.local/state/research-workbench/broad-research-20260911/`:

| Diretório | Conteúdo e situação |
| --- | --- |
| `owner-material/` | Legado v2: 50 trabalhos; não é suíte formal |
| `calibration-preparation-v3-20260913/` | Primeiro scaffold v3: 50 trabalhos, 100 tarefas de triagem |
| `calibration-preparation-v3-extraction-20260913/` | Sucessor: mesmas 100 tarefas e uma extração, fontes reproduzidas, referências e histórico pendentes |
| `owner-form-20260913/` | Somente uma cópia idêntica do HTML legado; servido em 8767 |
| `owner-form-v3-20260913/` | HTML v3 e PDF autorizado; servido em 8768 |

O sucessor foi produzido com `CalibrationCorpusSelectionV2` e
`build_calibration_scaffold_v2`, mantendo os manifests `screener_a_v2`,
`screener_b_v2` e `extractor_v3` existentes. O protocolo é v3, SHA-256
`fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f`.
As referências permanecem `OWNER_TODO_SENTINEL`; o mesmo marcador substitui
no rascunho o padrão `no_prior_tuning`, pois o histórico real ainda não foi
informado. Isso mantém o material inválido para execução até autoria e
validação, sem inventar ausência de ajuste anterior.

A auditoria `calibration-rebinding-audit-20260913.json` recupera os 50 casos
legados por ID exato do provedor: todos têm os mesmos campos exibidos em v3,
todos convergem para uma única proposta v3 por trabalho e nenhum representante
está na fila de identidade. As páginas brutas v2 e v3 têm hashes diferentes.
Assim, decisões antigas eventualmente existentes podem ter sua ligação
verificada depois; elas não foram copiadas nem tratadas como referências v3.

O HTML legado mantém SHA-256
`aba608e72251c0e0f7dffe58cce21bcc687afbb64efe89bd649f16359b841068` e o pacote,
`8b6004bdde869957b38d825c7c5674de98c5886b8dc85877fe2b2542e67756ce`.
O HTML novo tem SHA-256
`3861d7e5d7698e394583f3b5454ac974eb39ac9cc91705a1431657faec849a2f`, com pacote
`9a698c9f7422ea95f7aa39e01ec15965f340f1df8fc8b1399f072bd83e74ae8e`.

## Amostra e separação

A nova seleção é reprodutível com semente 20260913: três trabalhos distintos
por família temática Q01–Q16, preferindo OpenAlex, arXiv e DBLP, com ordenação
SHA-256 e substituição de fonte quando aquele estrato não tem candidatos;
acrescenta os dois trabalhos mais antigos disponíveis antes de 1995. São dois
registros de 1965, anteriores ao recorte de aquisição. A seleção não lhes
atribui elegibilidade. Ela é diagnóstica, não uma estimativa da prevalência do
corpus nem uma classificação científica pelas famílias de consulta.

Os 50 trabalhos retêm todas as 78 manifestações, apoiadas em 71 páginas.
Os representantes somam 13 OpenAlex, 14 arXiv e 23 DBLP; 26 representantes
não têm resumo. O formulário exibe todas as manifestações fornecidas aos
agentes, inclusive suas diferenças e ausências. Os anos vão de 1965 a 2026.
Foram excluídas todas as 50 obras legadas, as 75 páginas v3 que as sustentam e
todos os candidatos de identidade pendentes. A interseção com essa reserva é
zero tanto por obra quanto por página. As propostas não se tornam corpus aceito.

A comparação com os [64 challenge DOIs](../../search-design/2026-09-11-coverage/baseline-challenge-64.json)
e as [16 sementes](../../search-design/2026-09-07/seeds.json) encontrou zero
coincidências de obra, identificador ou título normalizado na nova seleção.
Entretanto, 25 casos compartilham páginas bibliográficas com propostas ligadas
a esses leads de desenvolvimento. O recibo privado
`development-overlap-audit.json` distingue as duas medidas. Não se alega
ineditismo histórico dessas páginas, recall independente ou sigilo de toda a
pesquisa. A regra de páginas disjuntas é aplicada às partições de calibração;
se Davi informar que usou essas mesmas páginas para ajustar a triagem, será
necessário registrar um sucessor da partição antes da verificação.

## Extração e uso humano

O caso V3-29 recebeu o PDF fixo arXiv:2508.17711v3, com CC BY 4.0 verificada e
atribuição no formulário. O `FullTextRecord` disponível tem SHA-256
`ac9adff69ca7c58bee0882a38b2b9df1aa54a014ca707dc9baac2e57e4c07396`;
os recibos originais ficam em
`~/.local/state/research-workbench/corpus-preparation-20260913/fulltext-v3/`.
A projeção nativa tem 26 páginas e não atesta validade científica ou fidelidade
da ordem visual de tabelas e colunas.

O pool do extractor contém 28 blocos contíguos, limitados a 5.000 caracteres,
cobrindo todas as linhas de todas as páginas. Cada bloco foi reproduzido pelo
resolver nativo a partir do PDF. A tarefa ocupa 111.704 caracteres, abaixo do
limite de um milhão. Nenhum bloco foi escolhido como referência humana:
Davi escolhe os valores, o estado observado/derivado, os campos não resolvidos,
os locators e o motivo. Ainda não se declara um caso positivo de extração.

Na triagem, Davi escolhe o campo de uma manifestação e seleciona o trecho
exato; a interface calcula o locator com offsets Unicode. Seleções maiores que
5.000 caracteres ou com espaços nas extremidades são recusadas, sem alterar
o texto humano. A exportação `minhas-decisoes-calibracao-v3.json` preserva os
vínculos do pacote, protocolo e scaffold; respostas parciais continuam parciais.

Há 50 trabalhos de título/resumo, uma extração e **zero tarefas de triagem de
texto completo**. Pelo [processo de calibração](../../../../../../docs/process/systematic-review-calibration.md),
50 trabalhos são exigidos por etapa de triagem avaliada, com os três julgamentos,
recall mínimo de 0,95 e zero falsas exclusões. Depois da medição, a auditoria
humana abrange 20% dos trabalhos de triagem e todos os casos de extração.
A preparação atual não satisfaz esses resultados nem habilita os papéis.

## Verificação operacional

Em navegador headless isolado: HTTP 200, 50 formulários de triagem, 120 campos
de fonte selecionáveis, seis campos de extração, respostas vazias, zero erros
JavaScript e zero gravações de armazenamento. Nenhum perfil do usuário foi
aberto. O browser solicitou somente o HTML; o PDF é aberto sob ação do leitor.
O servidor usa loopback e os diretórios públicos não contêm CAS, suítes ou
referências. Os JSON privados e caminhos para diretórios irmãos retornam 404.

```bash
python3 -m http.server 8768 --bind 127.0.0.1 \
  --directory "$HOME/.local/state/research-workbench/broad-research-20260911/owner-form-v3-20260913"
```

A verificação também identificou um limite concreto da CLI anterior: 10 MB
por entrada, frente a 12.416.114 bytes da seleção e 14.256.404 bytes do scaffold
(10.229.478 e 11.702.387 bytes compactos). A rejeição inicial por tamanho teve
código 2. Após a correção específica feita na integração, a validação nativa
alcançou os sentinelas e recusou corretamente o material ainda não escrito por
Davi, novamente com código 2. A ampliação do limite não remove o gate humano.

Os recibos `browser-readiness.json`, `form-binding.json` e `preparation.json`
registram esta preparação privada. Não houve inferência de modelo, decisão
científica atribuída a Davi, calibração executada ou alteração do legado.
