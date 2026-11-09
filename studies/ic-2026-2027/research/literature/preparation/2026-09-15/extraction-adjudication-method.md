# Regra de avaliação da extração na calibração

Método `owner_field_adjudication`, versão 1, registrado em 15/09/2026 antes
de executar os revisores sobre as referências assistidas adotadas. A
[fundamentação](extraction-evaluation-evidence.md) distingue orientações das
fontes e escolhas locais. Esta regra integra uma sucessora explícita da suíte,
`calibration-4`; os protocolos de busca, critérios de elegibilidade, tarefas,
referências e limiares de triagem permanecem vinculados aos mesmos bytes.

O problema confirmado é que a referência de cada um dos seis campos usa um
subtrecho reproduzível do PDF, enquanto o extrator recebe um conjunto de
localizadores mais amplos e só pode citar seus membros exatos. Igualdade do
JSON inteiro rejeitaria todas essas saídas válidas. Texto livre acrescenta
outra fonte de divergência: uma paráfrase pode preservar ou alterar o sentido,
e igualdade textual não distingue essas situações.

O validador automático exige a saída tipada, vinculada ao protocolo, à tarefa
e à obra corretos, com cobertura dos campos solicitados, valores e estados
permitidos, e localizadores do conjunto autorizado. A reprodução das fontes
continua obrigatória na execução e no replay. O comparador conserva o
diagnóstico de igualdade exata com a referência. Esse diagnóstico não decide
sozinho a fidelidade científica no método novo. As suítes anteriores conservam
sua comparação e seus resultados originais.

O Research Owner avalia **todos** os campos de todos os casos de extração
executados, inclusive quando a saída coincide literalmente com a referência.
Para cada campo, lê a saída, a referência e o trecho citado, e registra uma
justificativa e uma das decisões: equivalente, divergência substantiva ou
pendente. Uma decisão equivalente exige confirmação separada de:

- suporte das afirmações na fonte, sem extrapolação ou contradição;
- completude das informações exigidas pelo campo e das ressalvas relevantes;
- preservação de números, sinais, unidades, população, período e negações;
- preservação dos limites de medidas indiretas e das interpretações dos autores.

Uma conversão numérica precisa estar documentada na justificativa; não haverá
tolerância numérica escolhida depois de observar a resposta. Uma medida de
sentimento usada como aproximação da opinião não pode virar medição direta
de crença. Conteúdo adicional sem suporte, perda de uma limitação, mudança
de população ou interpretação causal sem evidência é divergência substantiva.
Ausência de informação deve ser explicitada; ambiguidade que impeça decidir
permanece pendente. Um campo não resolvido não recebe equivalência por
aprovação genérica. A validade dos bytes de um trecho comprova sua origem;
a leitura do responsável é que avalia se ele sustenta o conteúdo.

Cada decisão referencia o localizador efetivamente usado na saída. Não se
reescrevem os localizadores nem os valores da referência para produzir
coincidência. Se a referência estiver incorreta, a correção exige sucessor
com motivo e evidência; esse evento não apaga a divergência original nem
transforma o lote exposto em uma verificação independente nova.

A suíte nova incorpora a política e os hashes desta regra e da fundamentação.
Seu predecessor é a projeção no formato `calibration-3`, preservando referências,
tarefas e proveniência. Essa projeção é uma identidade dos dados anteriores
à mudança de método; não afirma que uma suíte 3 foi validada ou executada.
Referências com subtrechos fora do conjunto da tarefa também são recusadas
pela validação legada. A suíte 4 mantém a reprodução desses subtrechos como
evidência do responsável, sem acrescentá-los ao conjunto fornecido ao agente.
O relatório automático registra o hash da política,
o hash de cada resposta e os vínculos dos campos e localizadores, sem expor
o texto dos artigos. A adjudicação vincula protocolo, suíte, relatório,
respostas, responsável, data e todos os campos. Sua identidade também entra
na evidência exigida pela decisão final do responsável, junto das execuções
que já compõem a auditoria.

Não há aprovação automática de paráfrases nem novo modelo avaliador. Enquanto
faltar adjudicação, o resultado não é `pass`. Divergências substantivas ou
pendências impedem aprovação, assim como falhas estruturais, fontes inválidas,
falsas exclusões e demais falhas da calibração. A auditoria de 20% das obras
de triagem continua obrigatória. A conferência prévia das referências não
substitui a leitura das respostas que ainda serão produzidas.

O resultado mede concordância, nos casos executados, com referências propostas
por IA e adotadas pelo responsável. Não mede acurácia contra referências
humanas independentes nem encerra a revisão sistemática. Esta especificação
não declara ausência de ajuste anterior, execução ou aceitação científica.
