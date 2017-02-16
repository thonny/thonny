Thonny+Python bundle on Mac is based on official Python installer for Mac.
Steps for creating the bundle:

1. Install clean Python 3.4 or later into default Framework folder.
2. (If you want to bundle some 3rd party libraries, then pip-install these here)
3. Run install_tcltk.sh. This will download, compile and install latest suitable Tcl/Tk framework.
	(Tcl/Tk coming with Mac is too old. NB! It needs to be official Tcl, 
	ActiveTcl doesn't have suitable license!)
3. Run create_base_bundle.sh. This will copy Python and Tcl/Tk into ~/thonny_template_build 
	and prepare most of the application bundle. It also relinks the binaries to make them relocatable.

Steps 1...4 need to be done once per new Python/Tk version.

4. Run create_dist_bundle.sh. This will pip-install newest Thonny into the Python 
	copied into ~/thonny_template_build and create a distribution bundle under dist. 
	This step needs to be done once after uploading new version of Thonny into PyPI.
  
