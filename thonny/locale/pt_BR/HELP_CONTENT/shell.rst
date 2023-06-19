Shell
=====

A Shell é o principal meio de execução e comunicação com seu programa. Ela se parece principalmente com o REPL oficial do Python (o laço de leitura-avaliação-impressão), mas existem algumas diferenças e recursos extras.

Comandos Python
---------------

Assim como o REPL oficial do Python, o Shell do Thonny aceita expressões e instruções de Python, tanto de uma linha quanto com várias linhas. Se você pressionar o ENTER, Thonny usará algumas heurísticas para prever se você deseja enviar o comando ou continuar digitando o restante do comando na próxima linha. Se você deseja enviar o comando, mas Thonny oferece uma nova linha, verifique se você esqueceu de fechar alguns parênteses.

Comandos mágicos
----------------

Se você selecionar *Executar →  Executar programa atual* ou pressionar F5, verá como o Thonny insere um comando começando com ``%Run`` no Shell. Comandos começando com ``%`` são chamados de *comandos mágicos* (assim como em `IPython <https://ipython.org/>`_) e executam certas ações, que não podem ser (facilmente) expressas como comandos do Python. Os comandos mágicos do Thonny geralmente têm comandos de menu correspondentes, então você não precisa escrevê-los manualmente.

Comandos do sistema
-------------------

Se você precisar executar rapidamente um comando simples do sistema, não precisará iniciar um terminal. Basta prefixar o comando com ``!`` (por exemplo, ``!pytest meu-programa.py``) e inseri-lo no Shell do Thonny.

Histórico de comandos
---------------------

Se você deseja emitir o mesmo comando ou um comando semelhante várias vezes, não precisa digitá-lo todas as vezes -- use a tecla "seta para cima" para buscar o comando anterior no histórico de comandos. Pressionando novamente "seta para cima" traz para você o comando antes disso e assim por diante. Use a tecla "seta para baixo" para mover na direção oposta no histórico.

Saída colorida
--------------

Se você tiver seu Shell no modo de emulação de terminal (consulte *Ferramentas → Opções → Shell*), poderá usar `códigos ANSI <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ para produzir saída colorida.

Tente o seguinte exemplo:

.. code::

	print("\033[31m" + "Vermelho" + "\033[m")
	print("\033[1;3;33;46m" + "Texto amarelo em itálico e negrito sobre fundo ciano" + "\033[m")

Você pode querer usar um pacote como `colorama <https://pypi.org/project/colorama/>`_ para produzir os códigos de cores.

Sobrescrevendo as linhas de saída
---------------------------------

Emuladores de terminal apropriados suportam códigos ANSI que permitem escrever em posições arbitrárias na tela do terminal. O Shell do Thonny não é tão capaz, mas suporta alguns truques mais simples.

Tente o seguinte programa:

.. code::

	from time import sleep
	
	for i in range(100):
	    print(i, "%", end="")
	    sleep(0.05)
	    print("\r", end="")
	print("Concluído!")

O truque depende do caractere ``"\r"``, que faz com que o cursor de saída volte ao início da linha atual, para que a próxima impressão substitua o texto impresso anteriormente. Observe como usamos ``print(..., end="")`` para evitar a criação de uma nova linha.

O primo de ``"\r"`` é ``"\b"``, que move o cursor de saída para a esquerda em um caractere. Este não faz nada se já estiver na primeira posição de uma linha.

Fazendo som
-----------

Quando o Shell está no modo de emulação de terminal, você pode produzir um som de sino (ou "ding") exibindo o caractere ``"\a"``.

Exibindo imagens
----------------

Você pode exibir imagens no shell codificando seu arquivo GIF ou PNG com Base64 e imprimindo-o como URL de dados de linha única:

.. code::

	print("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")

Plotar séries de números
------------------------

Você pode visualizar séries de números impressos no Shell usando o `Plotador <plotter.rst>`_.

