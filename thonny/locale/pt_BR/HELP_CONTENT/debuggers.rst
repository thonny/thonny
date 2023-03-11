Usando depuradores
==================

Se você quiser ver como o Python executa seu programa passo a passo, execute-o no *modo de depuração* "melhor" ou "mais rápido". Você também pode executá-lo com `Birdseye <birdseye.rst>`_ e explorar as etapas de execução posteriormente.

Modo "melhor"
-------------

Este modo é recomendado para iniciantes.

Comece selecionando *Depurar programa atual (melhor)* no menu *Executar* ou pressione Ctrl+F5 (`no XFCE você precisa usar Shift+Ctrl+F5 <https://askubuntu.com/questions/92759/ctrlf5-in-google-chrome-in-xfce>`__). Você verá que a primeira instrução do programa é destacada e nada mais acontece. Nesse modo, você precisa notificar o Thonny de que está pronto para deixar o Python dar o próximo passo. Para isso, você tem duas opções principais:

* *Executar → Pular* (ou F6) faz grandes passos, ou seja, executa o código realçado e destaca a próxima parte do código.

* *Executar → Entrar* (ou F7) tenta fazer passos menores. Se o código destacado for feito de partes menores (comandos ou expressões), então a primeira delas será destacada e o Thonny aguardará o próximo comando. Se você chegou a um componente do programa que não possui subpartes (por exemplo, um nome de variável), então *Entrar* funciona como *Pular*, ou seja, executa (ou avalia) o código.

Se você se aprofundou em um comando ou expressão e deseja avançar mais rápido, pode usar *Executar → Sair*, que executa o código atualmente destacado e todas as partes do programa a seguir no mesmo nível. Existe um comando um pouco semelhante chamado *Continuar*, que executará o comando sem paradas até que seja concluído (ou até o próximo ponto de interrupção, veja abaixo).

Se você acidentalmente deu um grande passo e passou por cima de um trecho de código interessante, você pode **voltar o passo** selecionando *Executar → Voltar*. O Thonny mostrará o estado do programa como estava antes da última etapa. Agora você pode continuar com pequenos passos e ampliar este pedaço de código. (Como funciona? Mesmo quando você dá um grande passo, o Thonny salva todos os estados intermediários do programa, que podem ser refeitos depois que você dá o passo para trás.)

Se você deseja acessar uma parte específica do código, pode acelerar o processo colocando o cursor nessa linha e selecionando *Executar → Executar até o cursor*. Isso faz o Thonny dar passos automaticamente até esta linha. Você pode assumir o comando de lá.

Se você tiver os números de linha do editor ativados em *Ferramentas → Opções → Editor*, também poderá usar **pontos de interrupção**. Quando você clica ao lado de um comando na margem esquerda do editor, um ponto aparece. Quando você inicia o depurador, ele não para antes da primeira instrução, mas corre para a instrução marcada com o ponto, também conhecido como ponto de interrupção. Você pode colocar tantos pontos de interrupção em seus programas quantos forem necessários. Os pontos de interrupção podem ser removidos clicando na margem novamente.

Modo "mais rápido"
------------------

Quando seus programas crescem, você pode perceber que dar grandes passos com o depurador melhor às vezes leva muito tempo. É porque as sutilezas (por exemplo, possibilidade de passar pela avaliação da expressão e retroceder) exigem maquinário pesado e lento.

Com *Depurar programa atual (mais rápido)* você perde as sutilezas, mas pode percorrer seu programa muito mais rapidamente. Você pode usar os mesmos comandos (exceto "Voltar") como no depurador melhor. Este é o estilo de depuração mais profissional com que os programadores estão acostumados.

Estilos diferentes para mostrar a pilha de chamadas
---------------------------------------------------

Por padrão, o Thonny usa janelas empilhadas para apresentar a pilha de chamadas. Isso dá uma boa intuição sobre o conceito, mas pode se tornar complicado de usar. Portanto, desde a versão 3.0 pode-se escolher entre dois estilos diferentes para apresentar a pilha de chamadas. Em *Ferramentas → Opções → Executar e depurar* você pode alternar para um estilo mais tradicional, com uma visualização separada para apresentar e alternar quadros de chamada. Observe que ambos os estilos podem ser usados com ambos os modos de depuração.

Birdseye
--------

O comando *Depurar programa atual (Birdseye)* é explicado em uma `página separada <birdseye.rst>`_.

