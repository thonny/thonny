Desenvolvimento Web com Flask
=============================

`Flask <https://palletsprojects.com/p/flask/>`_ é uma framework popular para criar aplicativos da Web em Python.

Os tutoriais de Flask geralmente solicitam a execução de programas Flask escrevendo alguns comandos no Terminal, mas isso pode intimidar alguns iniciantes. O Thonny tenta tornar as coisas mais fáceis e permite executar programas Flask como qualquer outro programa (teclando apenas F5). Se ele detectar que você está executando um programa Flask, ele o executa com algumas linhas de código anexadas, que iniciam o servidor de desenvolvimento com as configurações adequadas.

Depurando
---------

Se você quiser percorrer seu programa Flask, defina um ponto de interrupção dentro de alguma função e invoque o depurador (funciona nos modos "melhor" e "mais rápido", porém o mais rápido é... mais rápido). Recarregue sua página e comece entrando em uma função. Você pode querer desativar "Mostrar chamadas de função (quadros) em janelas separadas" em *Ferramentas → Opções → Executar e depurar* para uma operação mais confortável.

Detalhes
-------

O Thonny iniciará o servidor de desenvolvimento aproximadamente assim:

.. code::

	os.environ["FLASK_ENV"] = "development"
	app.run(threaded=False, use_reloader=False, debug=False)

``threaded=False`` é usado porque o depurador do Thonny suporta apenas programas de thread única, ``use_reloader=False`` é usado porque o `recarregamento automático não é confiável quando o Flask é iniciado assim <https://flask.palletsprojects. com/en/1.0.x/api/#flask.Flask.run>`_ e ``debug=False`` é usado porque parece causar menos erros de "Endereço já em uso".

Se você quiser mais controle sobre as configurações, você mesmo deve chamar o método ``run``, por exemplo:

.. code::

	...
	if __name__ == "__main__":
		app.run(port=5005, threaded=False, use_reloader=True, debug=True)

Neste caso, o Thonny não adicionará nada ao seu código.

