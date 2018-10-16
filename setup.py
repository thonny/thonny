import os.path
import sys

from setuptools import find_packages, setup

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
        "Topic :: Education",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Text Editors",
    ],
    keywords="IDE education debugger",
    project_urls={
        "Source code": "https://bitbucket.org/plas/thonny",
        "Bug tracker": "https://bitbucket.org/plas/thonny/issues",
    },
    platforms=["Windows", "macOS", "Linux"],
    install_requires=requirements,
    python_requires=">=3.5",
    packages=find_packages(),
    package_data={
        "": ["VERSION", "res/*"],
        "thonny.plugins.help": ["*.rst"],
        "thonny.plugins.micropython": ["api_stubs/*.*"],
    },
    entry_points={"gui_scripts": ["thonny = thonny:launch"]},
)
