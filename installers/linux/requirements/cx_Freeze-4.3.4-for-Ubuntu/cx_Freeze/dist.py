import distutils.command.bdist_rpm
import distutils.command.build
import distutils.command.install
import distutils.core
import distutils.dir_util
import distutils.dist
import distutils.errors
import distutils.log
import distutils.util
import distutils.version
import os
import sys

import cx_Freeze
from cx_Freeze.common import normalize_to_list

__all__ = [ "bdist_rpm", "build", "build_exe", "install", "install_exe",
            "setup" ]

class Distribution(distutils.dist.Distribution):

    def __init__(self, attrs):
        self.executables = []
        distutils.dist.Distribution.__init__(self, attrs)


class bdist_rpm(distutils.command.bdist_rpm.bdist_rpm):

    def finalize_options(self):
        distutils.command.bdist_rpm.bdist_rpm.finalize_options(self)
        self.use_rpm_opt_flags = 1

    def _make_spec_file(self):
        contents = distutils.command.bdist_rpm.bdist_rpm._make_spec_file(self)
        contents.append('%define __prelink_undo_cmd %{nil}')
        return [c for c in contents if c != 'BuildArch: noarch']


class build(distutils.command.build.build):
    user_options = distutils.command.build.build.user_options + [
        ('build-exe=', None, 'build directory for executables')
    ]

    def get_sub_commands(self):
        subCommands = distutils.command.build.build.get_sub_commands(self)
        if self.distribution.executables:
            subCommands.append("build_exe")
        return subCommands

    def initialize_options(self):
        distutils.command.build.build.initialize_options(self)
        self.build_exe = None

    def finalize_options(self):
        distutils.command.build.build.finalize_options(self)
        if self.build_exe is None:
            dirName = "exe.%s-%s" % \
                    (distutils.util.get_platform(), sys.version[0:3])
            self.build_exe = os.path.join(self.build_base, dirName)


class build_exe(distutils.core.Command):
    description = "build executables from Python scripts"
    user_options = [
        ('build-exe=', 'b',
         'directory for built executables'),
        ('optimize=', 'O',
         'optimization level: -O1 for "python -O", '
         '-O2 for "python -OO" and -O0 to disable [default: -O0]'),
        ('excludes=', 'e',
         'comma-separated list of modules to exclude'),
        ('includes=', 'i',
         'comma-separated list of modules to include'),
        ('packages=', 'p',
         'comma-separated list of packages to include'),
        ('namespace-packages=', None,
         'comma-separated list of namespace packages to include'),
        ('replace-paths=', None,
         'comma-separated list of paths to replace in included modules'),
        ('path=', None,
         'comma-separated list of paths to search'),
        ('init-script=', 'i',
         'name of script to use during initialization'),
        ('base=', None,
         'name of base executable to use'),
        ('compressed', 'c',
         'create a compressed zipfile'),
        ('copy-dependent-files', None,
         'copy all dependent files'),
        ('create-shared-zip', None,
         'create a shared zip file containing shared modules'),
        ('append-script-to-exe', None,
         'append the script module to the exe'),
        ('include-in-shared-zip', None,
         'include the script module in the shared zip file'),
        ('icon', None,
         'include the icon along with the frozen executable(s)'),
        ('constants=', None,
         'comma-separated list of constants to include'),
        ('include-files=', 'f',
         'list of tuples of additional files to include in distribution'),
        ('include-msvcr=', None,
         'include the Microsoft Visual C runtime files'),
        ('zip-includes=', None,
         'list of tuples of additional files to include in zip file'),
        ('bin-includes', None,
         'list of names of files to include when determining dependencies'),
        ('bin-excludes', None,
         'list of names of files to exclude when determining dependencies'),
        ('bin-path-includes', None,
         'list of paths from which to include files when determining '
         'dependencies'),
        ('bin-path-excludes', None,
         'list of paths from which to exclude files when determining '
         'dependencies'),
        ('silent', 's',
         'suppress all output except warnings')
    ]
    boolean_options = ["compressed", "copy_dependent_files",
            "create_shared_zip", "append_script_to_exe",
            "include_in_shared_zip", "include_msvcr", "silent"]

    def add_to_path(self, name):
        sourceDir = getattr(self, name.lower())
        if sourceDir is not None:
            sys.path.insert(0, sourceDir)

    def build_extension(self, name, moduleName = None):
        if moduleName is None:
            moduleName = name
        sourceDir = getattr(self, name.lower())
        if sourceDir is None:
            return
        origDir = os.getcwd()
        scriptArgs = ["build"]
        command = self.distribution.get_command_obj("build")
        if command.compiler is not None:
            scriptArgs.append("--compiler=%s" % command.compiler)
        os.chdir(sourceDir)
        distutils.log.info("building '%s' extension in '%s'", name, sourceDir)
        distribution = distutils.core.run_setup("setup.py", scriptArgs)
        modules = [m for m in distribution.ext_modules if m.name == moduleName]
        if not modules:
            messageFormat = "no module named '%s' in '%s'"
            raise distutils.errors.DistutilsSetupError(messageFormat %
                    (moduleName, sourceDir))
        command = distribution.get_command_obj("build_ext")
        command.ensure_finalized()
        if command.compiler is None:
            command.run()
        else:
            command.build_extensions()
        dirName = os.path.join(sourceDir, command.build_lib)
        os.chdir(origDir)
        if dirName not in sys.path:
            sys.path.insert(0, dirName)
        return os.path.join(sourceDir, command.build_lib,
                command.get_ext_filename(moduleName))

    def initialize_options(self):
        self.list_options = [
            'excludes',
            'includes',
            'packages',
            'namespace_packages',
            'replace_paths',
            'constants',
            'include_files',
            'zip_includes',
            'bin_excludes',
            'bin_includes',
            'bin_path_includes',
            'bin_path_excludes',
        ]

        for option in self.list_options:
            setattr(self, option, [])

        self.optimize = 0
        self.build_exe = None
        self.compressed = None
        self.copy_dependent_files = None
        self.init_script = None
        self.base = None
        self.path = None
        self.create_shared_zip = None
        self.append_script_to_exe = None
        self.include_in_shared_zip = None
        self.include_msvcr = None
        self.icon = None
        self.silent = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_exe', 'build_exe'))
        self.optimize = int(self.optimize)

        if self.silent is None:
            self.silent = False

        # Make sure all options of multiple values are lists
        for option in self.list_options:
            setattr(self, option, normalize_to_list(getattr(self, option)))

    def run(self):
        metadata = self.distribution.metadata
        constantsModule = cx_Freeze.ConstantsModule(metadata.version)
        for constant in self.constants:
            parts = constant.split("=")
            if len(parts) == 1:
                name = constant
                value = None
            else:
                name, stringValue = parts
                value = eval(stringValue)
            constantsModule.values[name] = value
        freezer = cx_Freeze.Freezer(self.distribution.executables,
                [constantsModule], self.includes, self.excludes, self.packages,
                self.replace_paths, self.compressed, self.optimize,
                self.copy_dependent_files, self.init_script, self.base,
                self.path, self.create_shared_zip, self.append_script_to_exe,
                self.include_in_shared_zip, self.build_exe, icon = self.icon,
                includeMSVCR = self.include_msvcr,
                includeFiles = self.include_files,
                binIncludes = self.bin_includes,
                binExcludes = self.bin_excludes,
                zipIncludes = self.zip_includes,
                silent = self.silent,
                namespacePackages = self.namespace_packages,
                binPathIncludes = self.bin_path_includes,
                binPathExcludes = self.bin_path_excludes,
                metadata = metadata)
        freezer.Freeze()

    def set_source_location(self, name, *pathParts):
        envName = "%s_BASE" % name.upper()
        attrName = name.lower()
        sourceDir = getattr(self, attrName)
        if sourceDir is None:
            baseDir = os.environ.get(envName)
            if baseDir is None:
                return
            sourceDir = os.path.join(baseDir, *pathParts)
            if os.path.isdir(sourceDir):
                setattr(self, attrName, sourceDir)


class install(distutils.command.install.install):
    user_options = distutils.command.install.install.user_options + [
            ('install-exe=', None,
             'installation directory for executables')
    ]

    def expand_dirs(self):
        distutils.command.install.install.expand_dirs(self)
        self._expand_attrs(['install_exe'])

    def get_sub_commands(self):
        subCommands = distutils.command.install.install.get_sub_commands(self)
        if self.distribution.executables:
            subCommands.append("install_exe")
        return [s for s in subCommands if s != "install_egg_info"]

    def initialize_options(self):
        distutils.command.install.install.initialize_options(self)
        self.install_exe = None

    def finalize_options(self):
        if self.prefix is None and sys.platform == "win32":
            try:
                import winreg
            except:
                import _winreg as winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion")
            prefix = str(winreg.QueryValueEx(key, "ProgramFilesDir")[0])
            metadata = self.distribution.metadata
            self.prefix = "%s/%s" % (prefix, metadata.name)
        distutils.command.install.install.finalize_options(self)
        self.convert_paths('exe')
        if self.root is not None:
            self.change_roots('exe')

    def select_scheme(self, name):
        distutils.command.install.install.select_scheme(self, name)
        if self.install_exe is None:
            if sys.platform == "win32":
                self.install_exe = '$base'
            else:
                metadata = self.distribution.metadata
                dirName = "%s-%s" % (metadata.name, metadata.version)
                self.install_exe = '$base/lib/%s' % dirName


class install_exe(distutils.core.Command):
    description = "install executables built from Python scripts"
    user_options = [
        ('install-dir=', 'd', 'directory to install executables to'),
        ('build-dir=', 'b', 'build directory (where to install from)'),
        ('force', 'f', 'force installation (overwrite existing files)'),
        ('skip-build', None, 'skip the build steps')
    ]

    def initialize_options(self):
        self.install_dir = None
        self.force = 0
        self.build_dir = None
        self.skip_build = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_exe', 'build_dir'))
        self.set_undefined_options('install',
                ('install_exe', 'install_dir'),
                ('force', 'force'),
                ('skip_build', 'skip_build'))

    def run(self):
        if not self.skip_build:
            self.run_command('build_exe')
        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)
        if sys.platform != "win32":
            baseDir = os.path.dirname(os.path.dirname(self.install_dir))
            binDir = os.path.join(baseDir, "bin")
            if not os.path.exists(binDir):
                os.makedirs(binDir)
            sourceDir = os.path.join("..", self.install_dir[len(baseDir) + 1:])
            for executable in self.distribution.executables:
                name = os.path.basename(executable.targetName)
                source = os.path.join(sourceDir, name)
                target = os.path.join(binDir, name)
                if os.path.exists(target):
                    os.unlink(target)
                os.symlink(source, target)
                self.outfiles.append(target)

    def get_inputs(self):
        return self.distribution.executables or []

    def get_outputs(self):
        return self.outfiles or []


def _AddCommandClass(commandClasses, name, cls):
    if name not in commandClasses:
        commandClasses[name] = cls


def setup(**attrs):
    attrs.setdefault("distclass", Distribution)
    commandClasses = attrs.setdefault("cmdclass", {})
    if sys.platform == "win32":
        if sys.version_info[:2] >= (2, 5):
            _AddCommandClass(commandClasses, "bdist_msi", cx_Freeze.bdist_msi)
    elif sys.platform == "darwin":
        _AddCommandClass(commandClasses, "bdist_dmg", cx_Freeze.bdist_dmg)
        _AddCommandClass(commandClasses, "bdist_mac", cx_Freeze.bdist_mac)
    else:
        _AddCommandClass(commandClasses, "bdist_rpm", cx_Freeze.bdist_rpm)
    _AddCommandClass(commandClasses, "build", build)
    _AddCommandClass(commandClasses, "build_exe", build_exe)
    _AddCommandClass(commandClasses, "install", install)
    _AddCommandClass(commandClasses, "install_exe", install_exe)
    distutils.core.setup(**attrs)

