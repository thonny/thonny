from setuptools import setup, find_packages
import os.path
import sys

if sys.version_info < (3,4):
    raise RuntimeError("Thonny requires Python 3.4 or later")

setupdir = os.path.dirname(__file__)

with open(os.path.join(setupdir, 'thonny', 'VERSION'), encoding="ASCII") as f:
    version = f.read().strip()

requirements = []
for line in open(os.path.join(setupdir, 'requirements.txt'), encoding="ASCII"):
    if line.strip() and not line.startswith('#'):
        requirements.append(line)

setup(
      name="thonny",
      version=version,
      description="Python IDE for beginners",
      long_description="Thonny is a simple Python IDE with features useful for learning programming. See http://thonny.org for more info.",
      url="http://thonny.org",
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
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Education",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Text Editors",
      ],
      keywords="IDE education debugger",
      platforms=["Windows", "macOS", "Linux"],
      install_requires=requirements,
      python_requires=">=3.4",
      packages=find_packages(),
      package_data={'': ['VERSION',  'res/*'],
                    'thonny.plugins.help' : ['*.rst']},
      entry_points={
        'gui_scripts': [
            'thonny = thonny:launch',
        ]
      },      
)