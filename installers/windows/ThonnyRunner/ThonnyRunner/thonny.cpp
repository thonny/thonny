#include <Python.h>
#include <windows.h>

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE, PWSTR pCmdLine, int nCmdShow)
{
	LPWSTR *argv;
	int argc;

	argv = CommandLineToArgvW(GetCommandLine(), &argc);
	if (argv == NULL)
	{
		MessageBox(NULL, L"Unable to parse command line", L"Error", MB_OK);
		return 10;
	}

	Py_SetProgramName(argv[0]);
	Py_Initialize();
	PySys_SetArgvEx(argc, argv, 0);
	int code = PyRun_SimpleString(
		"from os.path import dirname, join\n"
		"from runpy import run_path\n"
		"import sys\n"
		"run_path(join(dirname(sys.executable), 'thonny_frontend.py'))\n"
		);
	Py_Finalize();

	return code;
}