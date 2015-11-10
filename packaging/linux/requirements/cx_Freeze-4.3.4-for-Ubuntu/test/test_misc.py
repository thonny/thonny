from os.path import join as pjoin
import sys

from nose.tools import assert_raises

from cx_Freeze.freezer import process_path_specs, ConfigError

rootdir = "C:\\" if sys.platform=='win32' else '/'

def test_process_path_specs():
    inp = [pjoin(rootdir, 'foo', 'bar'),
           (pjoin(rootdir, 'foo', 'qux'), pjoin('baz', 'xyz'))]
    outp = process_path_specs(inp)
    assert outp == [(pjoin(rootdir, 'foo', 'bar'), 'bar'),
                    (pjoin(rootdir, 'foo', 'qux'), pjoin('baz', 'xyz'))]

def test_process_path_specs_bad():
    with assert_raises(ConfigError):
        process_path_specs([(pjoin(rootdir, 'foo'), pjoin(rootdir, 'bar'))])
    
    with assert_raises(ConfigError):
        process_path_specs([('a', 'b', 'c')])