플라스크를 이용한 웹개발에 대해
==========================

`Flask <https://palletsprojects.com/p/flask/>`__ 는 웹 앱을 빌드하는데 널리 사용되는 프레임워크 입니다.

Flask 튜토리얼은 일반적으로 터미널에 몇 가지 명령을 입력하여 Flask 프로그램을 실행하도록 지시하지만
일부 초심자는 이를 두려워 할 수 있습니다. Thonny는 이를 쉽게 만들고 다른 프로그램과 마찬가지로 Flask 프로그램을
실행할 수 있도록 합니다 (간단한 F5 사용함으로). Flask 프로그램을 실행하고 있음을 감지하면
몇 줄의 코드를 추가 및 실행하여 적절한 설정으로 개발 서버를 시작합니다.

디버깅
---------
Flask 프로그램을 단계별로 진행하려면 일부 함수 내부에 브레이크 포인트를 설정하고 디버거를
호출합니다 (멋지고 빠른 작업이지만, 빠른건.. 빠른겁니다). 페이지를 새로 고침하고 함수 내부로
진입하세요. 보다 편안한 작업을 위해 "분리된 창에 있는 프레임" (도구 => 옵션
=> 실행 & 디버그)을 끌 수 있습니다.

세부사항들
-------
Thonny는 대략 다음과 같이 개발 서버를 시작합니다:

.. code::

	os.environ["FLASK_ENV"] = "development"
	app.run(threaded=False, use_reloader=False, debug=False)

``threaded=False`` Thonny의 디버거는 싱글-쓰레드 프로그램만 지원하기 때문에 이 옵션을 사용합니다,
``use_reloader=False`` 는 아래의 이유로 사용됩니다
`자동 재로딩은 안정적이지 않습니다. 링크 확인 <https://flask.palletsprojects.com/en/1.0.x/api/#flask.Flask.run>`_
그리고 ``debug=False`` "이미 사용 중인 주소" 에러를 더 적게 발생시키기 위해 사용됩니다.

만약 설정을 더 많이 제어하고 싶으면 ``run``-함수를 아래와 같이 직접 호출해야 합니다.
예:

.. code::

	...
	if __name__ == "__main__":
		app.run(port=5005, threaded=False, use_reloader=True, debug=True)

이 경우 Thonny는 코드에 아무것도 추가하지 않습니다.
