Executando seus programas com argumentos de linha de comando
============================================================

Quando você está editando *me_programa.py* e pressiona F5, o Thonny constrói um comando mágico ``%Run meu_programa.py`` e o envia para o Shell, que pede ao backend do Thonny para executar esse programa.

Quando você vai para o Shell e pega o comando ``%Run`` de volta (com a seta para cima), você pode adicionar *argumentos de linha de comando* a ele. Por exemplo, altere o comando para ``%Run meu_programa.py primeiro segundo`` e pressione ENTER.

Ao executar seu programa desta forma, você pode acessar os argumentos através de ``sys.argv``:

.. code::

    import sys
    print(sys.argv)

Corrigindo os argumentos da linha de comando
--------------------------------------------

Se você precisar usar o mesmo conjunto de argumentos várias vezes, pode se tornar tedioso modificar ``%Run`` manualmente. Neste caso, verifique **Argumentos de programa** no menu **Visualizar**. Isso abre uma pequena caixa de entrada ao lado dos botões da barra de ferramentas. A partir de agora, tudo o que você digitar nesta caixa será anexado a ``%Run <nome do programa>`` toda vez que você pressionar F5.

