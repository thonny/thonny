#include <Windows.h>

int __stdcall wWinMain(HINSTANCE hInstance,
            HINSTANCE hPrevInstance, 
            LPWSTR     lpCmdLine, 
            int       cmdShow)
{
	// get path of this exe
	HMODULE hModule = GetModuleHandleW(NULL);
	WCHAR lpFileName[1010];
	GetModuleFileNameW(hModule, lpFileName, 1000);

	// remove extension
	lpFileName[wcsnlen_s(lpFileName, 1000)-4] = NULL; // could use PathRemoveExtensionW(lpFileName), but don't want that dependency

	// construct shortcut path
	wcscat_s(lpFileName, TEXT("_shortcut.lnk"));

	// TODO: check that shortcut exists

	// open the shortcut with params given to this program
	ShellExecute(NULL, L"open", lpFileName, lpCmdLine, NULL, SW_SHOWDEFAULT);

    return 0;
}

