Técnicas de depuração
=====================

Se o seu programa não estiver funcionando corretamente, não entre em pânico. Você tem várias possibilidades para consertar a situação. Por exemplo:

* Deixe alguém consertar.
* Altere *algo* no código e tente novamente.
* Aborde o problema em duas fases: 1) diagnosticando o problema e 2) corrigindo-o.

Pedir ajuda pode ser uma boa ideia, mas não lhe dará essa doce sensação de realização. De qualquer forma, é melhor não usar isso sem primeiro fazer algum esforço por conta própria.

Se seus programas forem pequenos, você pode ganhar a loteria alterando algo aleatoriamente e tentando novamente (repita várias vezes), mas perderá mesmo se ganhar, pois não aprenderá nada.

Se você deseja se tornar bom em programação, realmente precisa abordar o problema de forma mais sistemática. Entre outras coisas, isso significa que você precisa identificar o motivo pelo qual o seu programa se comporta mal antes de tentar corrigi-lo. O processo de encontrar a origem do problema é chamado de *depuração*.

Rastreando o fluxo/pensamento do programa junto com o Python
------------------------------------------------------------

Muito provavelmente seu programa não está totalmente errado. Pode haver um erro de digitação em algum lugar ou você esqueceu ou entendeu mal alguma coisa. *NB! Não adquira o hábito de pensar que o Python o entendeu mal -- é uma máquina que nem mesmo tenta entendê-lo.* A chave para a depuração é descobrir exatamente onde e quando suas suposições sobre o comportamento do programa divergem do real comportamento.

Se o seu programa imprimir uma resposta final errada, isso informa algo sobre o comportamento do programa, mas geralmente não é suficiente para localizar o problema com precisão. Você também precisa verificar quais das **etapas intermediárias** se alinham com suas suposições e quais não.

Uma técnica óbvia (e muito útil) é adicionar **declarações de impressão extras** no código, que informam onde o Python está e o que ele realizou até agora, por exemplo.

.. code::

	print("amigos antes do laço for", amigos)

NB! Às vezes, você precisa introduzir novas variáveis e quebrar expressões complexas em partes menores para imprimir informações mais detalhadas.

Embora a depuração de impressão seja usada até mesmo por profissionais (eles podem chamá-la de *logging*), existe uma alternativa, que é mais confortável na maioria dos casos. Chama-se **percorrer o código** e é a especialidade do Thonny. Vá para o capítulo `Usando depuradores <debuggers.rst>`_ para saber mais.

Revisão de código
-----------------

Outra técnica útil é a revisão de código. É um pouco semelhante a rastrear o fluxo do programa, mas você faz isso em sua cabeça, tentando ver o quadro geral em vez de seguir pequenos passos.

Observe cada uma das instruções em seu código e tente entender sua finalidade e como ela se relaciona com sua tarefa.

Para cada **variável** pergunte a si mesmo:

* O nome da variável revela seu propósito? É melhor nomeá-la no singular ou no plural?
* Que tipo de valores podem acabar nesta variável? Strings, inteiros, listas de strings, listas de floats, ...?
* Qual é o papel da variável? Ele deve ser atualizado repetidamente para que eventualmente contenha informações úteis? O objetivo é usar as mesmas informações em vários lugares e reduzir o copiar e colar? Algo mais?

Para cada **laço** pergunte a si mesmo:

* Como você sabe que o laço é necessário?
* Quantas vezes o corpo do laço deve ser executado? Do que isso depende?
* Qual código deve estar dentro do laço e qual deve estar fora?
* O que deve ser feito antes do laço e o que deve ser feito depois dele?

Para cada **expressão** complexa, pergunte-se:

* Em que ordem devem estar as etapas de avaliação dessa expressão? O Python concorda com isso? Em caso de dúvida, use o depurador ou introduza variáveis auxiliares e divida a expressão em partes menores.
* Que tipo de valor deve sair dessa expressão? String? Lista de strings?

Você também pode estar perdendo algumas partes importantes em seu programa:

* Sua tarefa exige tratar diferentes situações de maneira diferente? Se sim, então você provavelmente precisa de um comando `if`.
* A tarefa requer fazer algo várias vezes? Se sim, provavelmente você precisa de um laço.

Ainda perdido?
--------------

"Encontre o lugar onde suas suposições quebram" - isso é definitivamente mais fácil de dizer do que fazer. No caso de programas complexos, é fácil chegar à situação em que você não tem mais certeza do que supõe e por que começou com essa coisa de programação.

Nesse caso, é útil simplificar sua tarefa o máximo possível e tentar implementar primeiro o problema mais simples. Pegue um novo editor e comece do zero ou copie o código existente e jogue fora tudo o que não é essencial para o problema. Por exemplo, você pode assumir que o usuário é cooperativo e sempre insere dados "bons". Se a tarefa exigir fazer algo repetidamente, jogue fora a parte "repetidamente", se a tarefa envolver uma condição complexa para fazer algo, simplifique a condição, etc.

