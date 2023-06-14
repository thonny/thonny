Entendendo os erros
===================

Se o seu programa apresentar erros ou resultados incorretos, não tente consertar nada antes de entender o problema. Você pode ler uma história mais longa em `outra página <debugging.rst>`_, mas aqui está uma lista de verificação rápida para colocar suas ideias em prática.

Você está assustado?
--------------------

Não fique! As mensagens de erro destinam-se a ajudar. Se você receber um erro, isso não significa que você é uma pessoa má. E não, você não quebrou o computador. Embora as mensagens de erro possam parecer um bloco de jargão a princípio, com a prática é possível extrair delas informações úteis.

Onde no código aconteceu o erro?
--------------------------------

As mensagens de erro no Thonny têm links que o levam ao local no código que causou o erro. No caso de vários links, o último é geralmente o mais relevante.

Se o erro aconteceu dentro de uma função, a mensagem possui vários links. Tente clicar um a um, de cima para baixo, e você verá como o Python chegou ao local do erro. Esse conjunto de links é chamado de *rastreamento da pilha*.

O que significa o erro?
-----------------------

A última linha do bloco de erro diz qual foi o problema do Python. Ao tentar compreender a mensagem, não se esqueça do contexto e tente combinar algumas partes da mensagem com o local vinculado ao código. Às vezes o Assistente do Thonny pode explicar o erro em termos mais simples, às vezes você precisa fazer uma busca na Internet pela mensagem (não se esqueça de adicionar "Python" à busca).

O que havia dentro das variáveis no momento do erro?
----------------------------------------------------

Abra a visualização de variáveis e veja você mesmo! Se o erro ocorreu dentro de uma função, você pode ver suas variáveis locais clicando nos
links do rastreamento da pilha.

Como o programa chegou a esse estado?
--------------------------------------

Veja `a página sobre depuração <debugging.rst>`_ ou `a página sobre como usar os depuradores do Thonny <debuggers.rst>`_.

