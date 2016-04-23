import os.path
import platform
import subprocess
import sys

from setuptools import setup
from setuptools.command.bdist_egg import bdist_egg
from setuptools.command.install import install

if sys.version_info < (3,4):
    raise RuntimeError("Thonny requires Python 3.4 or later")

WIN_SHORTCUT_NAME="Thonny.lnk"

def get_thonny_resource(filename):
    import thonny
    res_dir = os.path.realpath(os.path.join(os.path.dirname(thonny.__file__), "res"))
    return os.path.join(res_dir, filename)

def get_windows_folder(folder_id): 
    # http://stackoverflow.com/a/2234729/261181
    import ctypes
    from ctypes import create_unicode_buffer
    from ctypes.wintypes import HWND, HANDLE, DWORD, LPCWSTR, MAX_PATH
    _SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathW
    _SHGetFolderPath.argtypes = [HWND, ctypes.c_int, HANDLE, DWORD, LPCWSTR]
    auPathBuffer = create_unicode_buffer(MAX_PATH)
    _SHGetFolderPath(0, folder_id, 0, 0, auPathBuffer)
    return auPathBuffer.value

def get_windows_desktop_folder():
    return get_windows_folder(0)

def get_windows_start_menu_programs_folder():
    return get_windows_folder(2)

def get_thonny_executable():
    # TODO: check for unix and for user install
    return os.path.join(sys.exec_prefix, "Scripts", "thonny.exe")

def post_install():
    if platform.system() == "Windows":
        windows_post_install()
    else:
        raise RuntimeError("Only Windows is supported at the moment")

def windows_post_install():
    
    import thonnyappinstaller
    setup_exe = os.path.join(os.path.dirname(thonnyappinstaller.__file__), "shortcut.exe")
    
    def create_windows_shortcut(path):
        args = [setup_exe,
                 '/F:"' + path + '"',
                 '/A:C',
                 '/T:"' + get_thonny_executable() + '"',
                 '/P:"-m thonny"',
                 '/I:"' + get_thonny_resource("thonny.ico") + '"']
        subprocess.call(" ".join(args), shell=True)
                                                
    create_windows_shortcut(os.path.join(get_windows_desktop_folder(), WIN_SHORTCUT_NAME))
    create_windows_shortcut(os.path.join(get_windows_start_menu_programs_folder(), WIN_SHORTCUT_NAME))


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        post_install()
        
class CustomEggCommand(bdist_egg):
    def run(self):
        bdist_egg.run(self)
        post_install()


setup(
      name="thonnyapp",
      version="0.9.2",
      description="Launcher for Thonny (see https://pypi.python.org/pypi/thonny)",
      url="http://thonny.cs.ut.ee",
      author="Aivar Annamaa",
      license="MIT",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: Freeware",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
      ],
      keywords="IDE education debugger",
      install_requires=["thonny"],
      packages=["thonnyappinstaller"], 
      package_data={'thonnyappinstaller': ['shortcut.exe']},
      cmdclass={'bdist_egg': CustomEggCommand,
                'install': CustomInstallCommand}
)
        

    