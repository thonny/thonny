Birdseye
========

O Birdseye é um depurador de Python feito por Alex Hall, que registra os valores de expressões quando o programa é executado e permite que você os explore após a conclusão do programa. Veja `https://birdseye.readthedocs.io <https://birdseye.readthedocs.io>`_ para mais informações.

O Birdseye não é instalado por padrão, mas é fácil de instalar por meio de *Ferramentas → Gerenciar plugins*. Você precisa instalar o pacote chamado ``birdseye``.

O Birdseye funciona de maneira diferente dos `depuradores integrados ao Thonny <debuggers.rst>`_. Quando você executa seu programa com *Executar → Depurar programa atual (Birdseye)* a execução deve demorar um pouco mais do que o normal, mas funciona tal como você tivesse usado *Executar programa atual*. Isso significa que os pontos de interrupção são ignorados e você não pode percorrer o programa. Mas quando o programa é concluído, o Thonny abre uma página web (servida por um servidor local, parte do Birdseye), que permite que você se aprofunde no processo de execução e aprenda como os resultados finais foram compostos de valores intermediários.

NB! Ao usar o Birdseye no Thonny você não precisa importar ``birdseye.eye`` ou usá-lo para decorar suas funções. O Thonny executa o Birdseye de forma que ele registre informações sobre todas as funções.

O servidor local usa a porta 7777 por padrão. Se esta porta for usada por outro aplicativo, configure outra porta em *Ferramentas → Opções → Executar e depurar* e reinicie o Thonny.

