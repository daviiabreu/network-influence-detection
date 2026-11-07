# Textos para disponibilidade de dados e código

Modelos de redação em inglês para adaptar **somente depois** de fixar a pergunta,
concluir as execuções e confirmar os depósitos. Substituir todos os campos entre
colchetes, conferir os direitos de redistribuição e testar cada link antes da
submissão. Não afirmar que existe DOI ou aprovação científica neste estágio.
O desenho v4 usa somente painéis sintéticos. Nenhum microdado do Swiss Household
Panel (SHP) foi usado: a geometria de N, ondas, entrada e atrito
vem de fontes publicadas, citadas no protocolo v1 congelado e na emenda v4.
Essas aproximações não reconstroem respondentes nem a máscara real do SHP.
Os registros privados de gate G2/G2c não fazem parte do depósito público;
saídas confirmatórias só entram após o fechamento e a liberação prevista.
Zenodo e, se aplicável, CoMSES dependem de conta e aprovação do Research Owner.

## JCSS — Data Availability Statement

> The synthetic input data, analysis-ready outputs, experiment specifications,
> run manifests, validation receipts, and code supporting the findings of this
> article are archived at Zenodo [version DOI and link]. No SHP microdata were
> used; synthetic panel geometry was informed by published sources cited in
> the protocol. The archived release
> identifies the exact code revision, Python environment, parameters, and random
> seeds and includes instructions for regenerating the reported results. [If
> applicable: Third-party data from SOURCE are subject to RESTRICTION; access is
> governed by CONDITIONS at ACCESS URL. Only the permitted metadata and hashes
> are included in the public archive.]

A [política oficial da JCSS](https://link.springer.com/journal/42001/submission-guidelines)
exige uma declaração de disponibilidade para pesquisa original: indicar onde
estão os dados que sustentam análise e resultados, com identificadores e links;
se houver restrição legítima, explicar acesso e condições de reutilização.
O depósito público é recomendado, sem licença específica imposta pela revista.

## JASSS — Code and data availability

> The model code and documentation are available as a versioned CoMSES Net
> Computational Model Library release [model URL/handle]. The code, synthetic
> inputs, analysis-ready outputs, specifications, run manifests, and validation
> receipts are archived together at Zenodo [version DOI and link]. No SHP
> microdata were used; panel geometry draws on the published sources cited in
> the protocol. The two
> records identify the same code revision [commit] and provide commands for
> reproducing the reported simulations. [If applicable: SOURCE data cannot be
> redistributed under LICENCE/CONDITION; permitted metadata and hashes are
> archived, and access conditions are described at ACCESS URL.]

O [guia oficial da JASSS](https://www.jasss.org/v02/page_content_includes/_include_submit.html)
recomenda informação suficiente para replicar simulações e depósito de código
e documentação no CoMSES/OpenABM. O registro pode ficar acessível apenas a
pareceristas antes da publicação, com link no manuscrito; a liberação pública
ocorre se o artigo for aprovado. O guia recomenda ODD para documentar modelos,
mas não o exige universalmente. O link CoMSES no texto do artigo é importante
porque os pareceristas recebem apenas o PDF.
