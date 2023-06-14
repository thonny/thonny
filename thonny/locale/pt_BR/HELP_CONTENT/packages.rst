Instalando pacotes de terceiros
===============================

O Thonny tem duas opções para instalar bibliotecas de terceiros.

Com pip-GUI
-----------

No menu "Ferramentas", selecione "Gerenciar pacotes..." e siga as instruções.

Com pip na linha de comando
---------------------------

#. No menu "Ferramentas", selecione "Abrir shell do sistema...". Você deve obter uma nova janela de terminal informando o nome correto do comando *pip* (geralmente ``pip`` ou ``pip3``). A seguir, vamos supor que o nome do comando é ``pip``.

#. Digite ``pip install <nome do pacote>`` (ex. ``pip install pygame``) e pressione ENTER. Você deve ver *pip* baixando e instalando o pacote e imprimindo uma mensagem de sucesso.

#. Feche o terminal (opcional).

#. Volte para o Thonny.

#. Redefina o interpretador selecionando "Parar/reiniciar backend" no menu "Executar" (isso é necessário apenas na primeira vez que você instalar o pip).

#. Comece a usar o pacote.

.. NOTE::
    A opção "Abrir shell do sistema..." não está disponível ao executar a partir do Flatpak no Linux.
    Os aplicativos Flatpak são colocados em sandbox para proteger o sistema hospedeiro e os dados do usuário.
    Então permitir que o Thonny abra uma shell no sistema hospedeiro contornaria essas proteções.
    Para instalar pacotes de Python a partir da linha de comando, abra diretamente o aplicativo de terminal do seu sistema.

Usando pacotes científicos de Python 
====================================

A distribuição do Python que acompanha o Thonny não contém bibliotecas de programação científica (por exemplo, `NumPy <http://numpy.org/>`_ e `Matplotlib <http://matplotlib.org/>`_).

Versões recentes dos pacotes científicos de Python mais populares (por exemplo, numpy, pandas e matplotlib) têm pacotes disponíveis para plataformas populares, então você provavelmente pode instalá-los com pip. Caso tenha problemas, tente usar o Thonny junto com uma distribuição de Python separada e destinada a computação científica (por exemplo, `Anaconda <https://www.anaconda.com>`_ ou `Pyzo <http://www.pyzo.org/>`_).

Exemplo: Usando o Anaconda
--------------------------

Vá para https://www.anaconda.com/products/individual e baixe uma distribuição binária adequada para a sua plataforma. Provavelmente você vai querer um instalador gráfico e uma versão de 64 bits (você pode precisar da versão de 32 bits se tiver um sistema muito antigo).

Instale-o e descubra onde ele coloca o executável do Python (*pythonw.exe* no Windows e *python3* ou *python* no Linux e Mac).

No Thonny abra o menu "Ferramentas" e selecione "Opções...". Na caixa de diálogo de opções, abra a guia "Interpretador" e mostre a localização do executável do Python incluído no Anaconda.

Depois de ter feito isso, na próxima vez que você executar seu programa, ele será executado através do Python do Anaconda e todas as bibliotecas instaladas lá estarão disponíveis.

