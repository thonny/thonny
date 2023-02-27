Plotador
========

O Plotador é um complemento para o Shell, que extrai números da saída do programa e os exibe como um gráfico de linhas. Pode ser útil para observar dados de sensores ao vivo provenientes de dispositivos conectados ou até mesmo para analisar dados estáticos (se você não quiser usar ferramentas mais sérias). É inspirado no `Editor Mu Python <https://codewith.mu/>`__.

Você pode abri-lo no menu "Exibir" ou no menu de contexto do Shell.

Por exemplo, tente o seguinte programa (você pode pará-lo com Ctrl+C ou com o botão "Parar/reiniciar backend" na barra de ferramentas):

.. code::

	from time import sleep
	from random import randint
	
	p1 = 0
	while True:
	    p1 += randint(-1, 1)
	    p2 = randint(-10, 10)
	    print("caminhada aleatória:", p1, " apenas aleatório:", p2)
	    sleep(0.05)

Ao executá-lo com o Plotador aberto, você verá um gráfico de linhas com duas séries se formando. Cada coluna no gráfico corresponde a uma linha no Shell. A coluna mais à direita no gráfico sempre corresponde à linha visível mais abaixo no shell, mesmo se você parar o programa e rolar o texto no shell.

O Plotador começa a desenhar quando detecta pelo menos duas linhas consecutivas contendo o mesmo padrão de números e texto ao redor. Os números são plotados e o texto ao redor se torna a legenda no canto inferior direito do plotador.

Velocidade da animação
----------------------

A menos que você esteja plotando um número fixo de linhas, é uma boa ideia não inundar o Shell e o Plotador com dados. É por isso que o exemplo acima faz uma pequena pausa (``sleep(0.05)``) antes de enviar a próxima linha.

Faixa do eixo y
---------------

O Plotador tenta detectar um intervalo adequado para o seu gráfico sem precisar alterá-lo com muita frequência. Por esta razão ele aumenta o alcance sempre que necessário, mas somente reduz a faixa no início de uma nova série.

Se alguns outliers tornaram o intervalo muito grande, você pode reduzi-lo manualmente, esperando até que os outliers estejam fora da imagem e clicando no Plotador.

Se você quiser aumentar o intervalo (ou apenas comparar seus dados com certos valores), simplesmente inclua constantes adequadas em suas linhas de dados, por exemplo: ``print(0, medida1, medida2, 100)``.

