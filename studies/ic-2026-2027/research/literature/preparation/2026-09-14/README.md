# Rascunho assistido do formulário de calibração

Em 2026-09-14, Davi pediu que o assistente preenchesse o formulário e destacou
que a modelagem matemática já orienta muitas das decisões. Foi preparado um
rascunho de autoria da IA para os 50 casos de título e resumo e os seis campos
de extração do artigo selecionado. O recorte aplicado é o do
[protocolo v3](../../protocol/opinion-dynamics-systematic-map-v3.json): modelos
matemáticos ou computacionais de opiniões, crenças e influência social humana.
Não houve ampliação para toda aplicação de modelagem matemática.

O rascunho propõe 16 inclusões para avaliação posterior, 21 exclusões e mantém
13 casos incertos, com justificativas e trechos das fontes. O filtro
“Pontos a conferir” reúne 17 casos: os 13 incertos e quatro inclusões com
pendências destacadas. Isso organiza a leitura; não define quantos julgamentos
humanos bastariam para a calibração formal.

## Evidência e revisão

Os mesmos títulos, resumos e metadados do formulário v3 sustentam a triagem.
A extração usa o PDF fixo arXiv 2508.17711v3, com licença CC BY 4.0, já retido
no [pacote anterior](../2026-09-13/README.md). A execução dos validadores nativos
reproduziu 68 trechos bibliográficos e 21 trechos do texto completo. Essa
correspondência confirma a origem dos trechos, não a correção dos julgamentos.

Três subagentes dividiram a autoria da triagem; cada lote foi examinado por um
revisor diferente de seu autor, incluindo o coordenador. A extração escrita
pelo coordenador recebeu revisão de outro agente. A revisão apontou uma
precisão incorporada em um sucessor: o artigo usa escores de sentimento dos
posts como aproximação de opinião, sem medir diretamente crenças individuais.
Os arquivos anteriores permanecem preservados. A concordância entre agentes
não foi usada como medida independente de acurácia.

A conferência no navegador verificou a renderização, os filtros de 50, 13 e
17 casos, a abertura dos trechos e os seis campos de extração, sem erros de
console observados. As respostas HTTP do formulário e do download coincidiram
byte a byte com os arquivos publicados localmente. O servidor serve somente
esses dois arquivos, vinculado a `127.0.0.1:8769`.

## Autoria e estado científico

O [processo atual de calibração](../../../../../../docs/process/systematic-review-calibration.md)
exige referências de autoria humana. Este material é uma assistência explícita
da IA, com esquema próprio `ai-authored-calibration-assistance-1`; não foi
importado como resposta humana. Os 50 casos foram vistos pelo assistente e
pelos subagentes, e suas propostas foram disponibilizadas ao usuário. Qualquer
uso posterior como referência deverá declarar essa assistência e ser avaliado
conforme o desenho de calibração adotado. Não se declara independência humana
nem se inventa histórico de ajuste dos agentes.

O scaffold e os dois formulários humanos anteriores mantiveram seus hashes,
e os campos reservados à autoria humana continuam pendentes. O inventário de
tamanho, datas e inode dos 6.577 arquivos do armazenamento de conteúdo ficou
inalterado durante a validação. Não foi executada calibração científica, nem
aplicada qualquer exclusão definitiva ao corpus. Este rascunho também não
conclui a triagem, a extração ou a síntese da revisão ampla.

## Localização e integridade

Os arquivos locais estão em
`~/.local/state/research-workbench/calibration-assistance-20260914/`.
`public/index.html` apresenta o rascunho; `public/ai-draft.json` contém os mesmos
bytes de `validated-draft.json`. As propostas individuais, fontes e revisões
permanecem fora do Git. A versão do código usada na validação foi
`efcb958037bb85848a3054f77ab153f150c5800b`.

| Arquivo local | SHA-256 |
| --- | --- |
| `validated-draft.json` | `ed1a884f33ba2255508c4c03802a7de97490db2e5f8773621e3c5126159f04ff` |
| `public/index.html` | `72c309c90bf429b9ddb886c4b1f13c9be188e9a291482cbfb1ff8015d749bd53` |
| `validation.json` | `803911c408c344c8def57f3f29421f5f123f15ecc7c4f690743ef9584e482186` |
| `delivery-check.json` | `61e304fbdf344b1052e35bfa4b0caf57571c5868233790a9b1574b4c28d42138` |
| `authorship-and-scope.json` | `1e72cfea411d706ea86739379bc622a26ec77cfe08ad1060f1391fe1862d112c` |
| `extraction-revision.json` | `3dd41cba76b0bb91b19d3e94a632782ddbdc9c1ed24fc6a91164897e6f519775` |
