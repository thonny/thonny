Encaixando janelas do usuário
=============================

Ao desenvolver seus programas de Tartaruga (ou outros usando Tkinter), você pode querer olhar para a janela da última execução enquanto corrige algo no seu código. Se você tem uma tela grande ou várias telas, não é difícil encaixar sua janela ao lado da do Thonny, mas na próxima execução o gerenciador de janelas pode posicioná-la em outro lugar e você irá precisar arrumar as janelas novamente.
 
Use **Encaixar janelas do usuário** no menu **Executar** para ajudá-lo nessa situação. Se você marcar esta opção e executar um programa usando Tkinter, o Thonny vai executar os seguintes truques de mágica:

* Ele lembra onde você posiciona sua janela. Da próxima vez, ele coloca a janela na mesma posição.

* Ele faz com que sua janela fique no topo mesmo se você clicar na janela do Thonny para começar a modificar o código. Na verdade, depois que sua janela do Tkinter se torna visível, o Thonny foca automaticamente sua própria janela para que você possa continuar editando o programa sem capturar o mouse. Quando terminar, basta pressionar F5 novamente e a janela antiga será substituída pela nova.
 
Permanecer no topo atualmente não funciona com programas de Tartaruga no macOS (https://github.com/thonny/thonny/issues/798).

