from setuptools import setup
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
      url="http://thonny.org",
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
      install_requires=requirements,
      packages=["thonny",
                "thonny.shared",  
                "thonny.shared.thonny",  
                "thonny.plugins", 
                "thonny.plugins.system_shell"],
      package_data={'': ['VERSION',  'res/*']},
      entry_points={
        'gui_scripts': [
            'thonny = thonny:launch',
        ]
      },      
)