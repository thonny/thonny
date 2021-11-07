#include <Python.h>
#include <windows.h>
#pragma comment(linker,"\"/manifestdependency:type='win32' \
name='Microsoft.Windows.Common-Controls' version='6.0.0.0' \
processorArchitecture='*' publicKeyToken='6595b64144ccf1df' language='*'\"")

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

	Py_IsolatedFlag = 1;
	// Flag doesn't affect the back-end.
	// Clear misleading environment variables for good...
	_putenv("PYTHONHOME=");
	_putenv("PYTHONPATH=");
	_putenv("PYTHONSTARTUP=");
	_putenv("PYTHONINSPECT=");
	_putenv("TCL_LIBRARY=");
	_putenv("TK_LIBRARY=");

	Py_SetProgramName(argv[0]);
	Py_Initialize();
	PySys_SetArgvEx(argc, argv, 0);

	PyObject *py_main, *py_dict;
	py_main = PyImport_AddModule("__main__");
	py_dict = PyModule_GetDict(py_main);

	PyObject* result = PyRun_String(
		"try:\n"
		"    from runpy import run_module\n"
		"    run_module('thonny')\n"
		"except:\n"
		"    import traceback\n"
		"    raise RuntimeError(traceback.format_exc()[:1500])\n",
		Py_file_input,
		py_dict,
		py_dict
		);

	int code;
	if (!result) {
		PyObject *ptype, *pvalue, *ptraceback;
		PyErr_Fetch(&ptype, &pvalue, &ptraceback);

		PyObject* valueAsString = PyObject_Str(pvalue);

		wchar_t* error_msg = PyUnicode_AsWideCharString(valueAsString, NULL);
		MessageBox(0, error_msg, L"Thonny startup error", MB_OK | MB_ICONERROR);
		code = -1;
	}
	else {
		code = 1;
	}

	Py_Finalize();

	return code;
}