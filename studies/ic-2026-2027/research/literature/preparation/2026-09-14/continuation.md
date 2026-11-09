# Conferência assistida e pendências de acesso

O [formulário de conferência](http://127.0.0.1:8771/) contém as 50 propostas de
título/resumo e os seis campos de extração já preenchidos. Permite corrigir,
confirmar cada item, exportar uma revisão parcial e retomá-la pelo arquivo.
Nenhum item começa confirmado. Editar uma resposta desfaz sua confirmação.
O histórico de ajuste começa desconhecido e depende de declaração real.

A [proposta de emenda](assisted-reference-amendment-proposal.md) permite
aproveitar a redação da IA com conferência e adoção explícita por Davi,
preservando a autoria assistida e o alcance limitado das métricas. Ela está
pronta para decisão e não foi aplicada. A calibração científica não executou.

## O que o formulário conserva

As fontes originais sustentam 16 propostas de inclusão, 21 de exclusão e
13 incertas. As 50 propostas e os seis campos são cópias exatas do primeiro
rascunho. Os 17 suplementos aparecem separadamente; o resultado editorial de
19 inclusões, 29 exclusões e dois incertos não substitui o gabarito das
tarefas originais. Falta de evidência suficiente pode continuar incerta.

A exportação usa `ai-assisted-owner-review-1` e referencia os hashes do pacote,
protocolo e dois rascunhos. Guarda correções, confirmações declaradas e
histórico; não declara referência independente, aprovação científica ou
entrada nativa de calibração. `title_abstract_reference_source_policy` descreve
a política de fontes, não testemunha quais páginas uma pessoa leu.

O servidor está restrito a `127.0.0.1:8771` e serve apenas HTML, JavaScript e
o pacote de propostas. As respostas editadas permanecem na página até a
exportação; não são enviadas ao servidor nem salvas automaticamente. Os
diretórios são 0700 e os arquivos privados 0600. O download do navegador usa
seu próprio diretório e suas permissões; o formulário não muda essa configuração.

## Busca adicional dos dois casos

V3-27 permanece incerto. A [página de projetos de Xiao Liu](https://sites.google.com/site/drxiaoliu/research/projects),
vinculada pelo [perfil institucional Deakin](https://experts.deakin.edu.au/36542-xiao-liu),
contextualiza a recomendação de aplicativos por informação social e cita o
capítulo. Ela não esclarece a regra do CD estendido nem substitui o capítulo.
V3-39 também permanece incerto: a [página institucional de Meiping Song](https://ist.dlmu.edu.cn/professor/songmeipin.html)
não forneceu o artigo ou seu método. Nenhum caso foi excluído pela falha de acesso.

Um subagente realizou a busca delimitada e o coordenador conferiu as novas
páginas primárias. Foram retidos dois corpos HTML, suas projeções, resultados
textuais da ferramenta e recibos de tentativas. A conferência reproduziu os
32 hashes e tamanhos do manifesto. Texto retornado por uma ferramenta não é
apresentado como corpo HTML original. Não houve obtenção dos dois textos completos.

## Auditoria paralela do corpus

Outro subagente conferiu novamente os nove candidatos sem título, os dez
conflitos de DOI e as projeções primárias de metadados. A próxima parcela
técnica é uma transição nativa de emendas bibliográficas, inicialmente para
os três títulos Springer já confirmados e a anotação do alias DOI, com uma
prévia do efeito na fila de identidades.

A auditoria encontrou dois títulos recuperados que também aparecem sob outros
DOIs na projeção existente: Policy Analysis encontra
`10.1080/13876980108412655`; Settlement encontra
`10.1111/j.1571-9979.1998.tb00171.x`. São encontros para revisão de identidade,
não fusões confirmadas. Aplicar os títulos pode gerar novos candidatos; a
fila sucessora não deve pressupor congelamento dos mesmos 20.964 pares.
Essa transição não foi implementada nesta parcela. O estado agregado continua
incompleto, com metadados e identidades pendentes.

## Verificação

O navegador exibiu 50 casos, seis campos e zero confirmações humanas, com
filtros de 13 incertos e 17 consultas posteriores. A expansão do suplemento
mostrou sua distinção da resposta original. Não foram observados erros de
console. Os três recursos HTTP corresponderam aos arquivos e quatro caminhos
privados testados retornaram 404.

Em uma cópia de teste separada, foram verificados edição, invalidação da
confirmação, estado completo, download efetivo e retomada de arquivo. O evento
de download da ferramenta expirou, mas o arquivo sintético foi localizado e
validado em Downloads. Nenhuma resposta humana real foi lida ou criada.

A revisão independente encontrou três problemas de retomada: o formulário
podia exportar mais bytes do que aceitava importar; a nota de histórico não
tinha o mesmo limite da importação; e uma nota isolada não acionava o aviso
de saída. As correções foram retestadas no sucessor, incluindo um arquivo
sintético de 14.288.265 bytes, adulterações de vínculos recusadas e seis
handlers que invalidam confirmação após edição. O candidato anterior está
preservado. Esses testes validam a ferramenta, não os julgamentos científicos.

O protocolo, scaffold, primeiro JSON e HTML da IA e formulário humano v3
mantiveram seus cinco hashes de referência. O armazenamento canônico não
recebeu novas observações, decisões ou alterações nesta preparação.
Os sete checks de estrutura e os nove testes do contrato documental de
revisão sistemática passaram; 35 links locais dos documentos afetados resolveram.

Os artefatos privados ficam sob
`~/.local/state/research-workbench/calibration-continuation-20260914/`.

| Artefato | SHA-256 |
| --- | --- |
| `review-form/public/review-data.json` | `b90d7945e7ed80967a9a10697bc364f54aa333c95c2668566791257e07bc19c8` |
| `review-form/public/index.html` | `5b746fe448106a5c7df7cbe2c4acf8547c421f90f4f239253e9a42ba9495ead6` |
| `review-form/public/review.js` | `6d5477c0db25748525032c7ff84c08787af7f53df672ed16430d08393bad0077` |
| `review-form/validation-v2.json` | `b13756fbb775d43ce2d5ad9ea5da3b1d0de4949cce67ffbb0e3beb00c1ca3846` |
| `review-form-audit.md` | `08d08b4decce998c35696097a22eaee554ebad9ec5ab8a937cd1f494332e8966` |
| `access-followup/findings.json` | `23c52955a6cf4856d2c53578bd03eee7d6a0846fa0beb402a99d0df52b74ea7c` |
| `method-audit.md` | `f027cb7e24bf6535b826b7eaf6a9adc3c09c09b873eda14f1704475f6dd45cd8` |
| `corpus-next-step.md` | `8444106597ba310f94405913a555f7e9ba20bb417cbca46ee7af57a8233f4bd2` |
