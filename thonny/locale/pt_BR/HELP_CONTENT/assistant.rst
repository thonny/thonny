Assistente
==========

O painel Assistente ajuda você de duas maneiras.

Se o seu programa terminar com um erro, ele tenta explicá-lo em termos mais simples e oferece alguns conselhos para encontrar e corrigir o problema.

Às vezes seu programa pode não funcionar como você deseja, mesmo que você não receba nenhuma mensagem de erro. Nesse caso às vezes ajuda investigar o código cuidadosamente para detectar certos cheiros ruins ou peculiaridades, que podem levar à descoberta do problema. Existem duas ferramentas populares, que são usadas para tais investigações: `Pylint <pylint.pycqa.org>`_ e `Mypy <http://mypy-lang.org/>`_.

O Mypy tenta detectar certas contradições em seu código, por exemplo quando uma função parece esperar um argumento inteiro, mas seu código a chama com uma string. Pylint não é tão bom com esse tipo de verificação, mas pode fazer muitas outras análises. O número de checagens do Pylint é tão grande que a maioria dos usuários acaba pulando verificações que não consideram relevantes. O Thonny já escolheu muitas verificações do Pylint que provavelmente são relevantes para iniciantes. Se você quiser mais checagens, você pode executar o Pylint em seu código via linha de comando. Se você quiser omitir certas checagens escolhidas pelo Thonny, então vá para *Ferramentas → Opções → Assistente* e digite o nome da verificação. A lista de todas as checagens do Pylint pode ser vista em https://pylint.pycqa.org/en/latest/messages/messages_list.html

