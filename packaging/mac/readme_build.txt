Thonny+Python bundle on Mac is based on official Python installer for Mac.
Steps for creating the bundle:

1. Install clean Python 3.7 into default Framework folder.
2. (If you want to bundle some 3rd party libraries, then pip-install these here)
3. Run create_base_bundle.sh. This will copy Python into ~/thonny_template_build_37
	and prepare most of the application bundle. It also relinks the binaries to make them relocatable.

Steps 1...3 need to be done once per new Python version.

4. Run create_release.sh. This will pip-install newest Thonny into the Python 
	copied into ~/thonny_template_build_37 and create distribution packages under dist. 
	This step needs to be done once after uploading new version of Thonny into PyPI.
  
