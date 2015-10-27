import imp
import os
import shutil
import tempfile
import zipfile

test_dir = os.path.dirname(__file__)
samples_dir = os.path.join(test_dir, 'samples')

from cx_Freeze.finder import ZipModulesCache, ModuleFinder, Module

def clean_pyc_files():    
    for dirpath, dirnames, filenames in os.walk(samples_dir):
        for filename in filenames:
            if filename.endswith(('.pyc', '.pyo')):
                os.unlink(os.path.join(dirpath, filename))
        if '__pycache__' in dirnames:
            dirnames.remove('__pycache__')
            shutil.rmtree(os.path.join(dirpath, '__pycache__'))

def prepare_zip_file():
    clean_pyc_files()
    tmpd = tempfile.mkdtemp()
    egg = os.path.join(tmpd, 'testpkg1.egg')
    eggzip = zipfile.PyZipFile(egg, 'w', zipfile.ZIP_DEFLATED)
    eggzip.writepy(os.path.join(samples_dir, 'testmod1.py'))
    eggzip.writepy(os.path.join(samples_dir, 'testpkg1'))
    eggzip.close()
    return egg

def test_ZipModulesCache():
    egg = prepare_zip_file()
    try:
        zmc = ZipModulesCache()
        
        mod = zmc.find(egg, 'testmod1')
        assert mod is not None
        assert mod[2][2] == imp.PY_COMPILED
        
        pkg = zmc.find(egg, 'testpkg1')
        assert pkg is not None
        assert pkg[2][2] == imp.PKG_DIRECTORY
        
        # This needs to be called after zmc.find(egg, *)
        submod = zmc.find(os.path.join(egg, 'testpkg1'), 'submod')
        assert submod is not None
        assert submod[2][2] == imp.PY_COMPILED
    finally:
        os.unlink(egg)

def test_FindModule_from_zip():
    egg = prepare_zip_file()
    try:
        mf = ModuleFinder()
        mf.path = [egg]
        mod = mf._InternalImportModule('testpkg1.submod', deferredImports=[])
        assert isinstance(mod, Module)
    finally:
        os.unlink(egg)