import os.path
import sys

from setuptools import find_packages, setup

def recursive_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

if sys.version_info < (3, 5):
    raise RuntimeError("Thonny requires Python 3.5 or later")

setupdir = os.path.dirname(__file__)

with open(os.path.join(setupdir, "thonny", "VERSION"), encoding="ASCII") as f:
    version = f.read().strip()

requirements = []
for line in open(os.path.join(setupdir, "requirements.txt"), encoding="ASCII"):
    if line.strip() and not line.startswith("#"):
        requirements.append(line)

setup(
    name="thonny",
    version=version,
    description="Python IDE for beginners",
    long_description="Thonny is a simple Python IDE with features useful for learning programming. See https://thonny.org for more info.",
    url="https://thonny.org",
    author="Aivar Annamaa and others",
    author_email="thonny@googlegroups.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Education",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Text Editors",
    ],
    keywords="IDE education debugger",
    project_urls={
        "Source code": "https://github.com/thonny/thonny",
        "Bug tracker": "https://github.com/thonny/thonny/issues",
    },
    platforms=["Windows", "macOS", "Linux"],
    install_requires=requirements,
    python_requires=">=3.5",
    packages=find_packages(),
    package_data={
        "": ["VERSION", "defaults.ini", "res/*"] + recursive_files("thonny/locale"),
        "thonny.plugins.help": ["*.rst"],
        "thonny.plugins.pi": ["res/*.*"],
        "thonny.plugins.printing": ["*.html"],
        "thonny.plugins.micropython": ["api_stubs/*.*"],
        "thonny.plugins.circuitpython": ["api_stubs/*.*"],
        "thonny.plugins.microbit": ["api_stubs/*.*"],
        "thonny.plugins.esp": ["esp32_api_stubs/*.*", "esp_8266_api_stubs/*.*"],
        "thonny.plugins.mypy": ["typeshed_extras/*.pyi"],
    },
    entry_points={"gui_scripts": ["thonny = thonny:launch"]},
)
