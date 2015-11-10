"""
Base class for freezing scripts into executables.
"""

import datetime
import distutils.sysconfig
import imp
import marshal
import os
import shutil
import socket
import stat
import struct
import sys
import time
import zipfile

import cx_Freeze

__all__ = [ "ConfigError", "ConstantsModule", "Executable", "Freezer" ]

EXTENSION_LOADER_SOURCE = \
"""
def __bootstrap__():
    import imp, os, sys
    global __bootstrap__, __loader__
    __loader__ = None; del __bootstrap__, __loader__

    found = False
    for p in sys.path:
        if not os.path.isdir(p):
            continue
        f = os.path.join(p, "%s")
        if not os.path.exists(f):
            continue
        m = imp.load_dynamic(__name__, f)
        import sys
        sys.modules[__name__] = m
        found = True
        break
    if not found:
        del sys.modules[__name__]
        raise ImportError("No module named %%s" %% __name__)
__bootstrap__()
"""


MSVCR_MANIFEST_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<noInheritable/>
<assemblyIdentity
    type="win32"
    name="Microsoft.VC90.CRT"
    version="9.0.21022.8"
    processorArchitecture="{PROC_ARCH}"
    publicKeyToken="1fc8b3b9a1e18e3b"/>
<file name="MSVCR90.DLL"/>
<file name="MSVCM90.DLL"/>
<file name="MSVCP90.DLL"/>
</assembly>
"""

def process_path_specs(specs):
    """Prepare paths specified as config.
    
    The input is a list of either strings, or 2-tuples (source, target).
    Where single strings are supplied, the basenames are used as targets.
    Where targets are given explicitly, they must not be absolute paths.
    
    Returns a list of 2-tuples, or throws ConfigError if something is wrong
    in the input.
    """
    processedSpecs = []
    for spec in specs:
        if not isinstance(spec, (list, tuple)):
            source = spec
            target = None
        elif len(spec) != 2:
            raise ConfigError("path spec must be a list or tuple of "
                    "length two")
        else:
            source, target = spec
        source = os.path.normpath(source)
        if not target:
            target = os.path.basename(source)
        elif os.path.isabs(target):
            raise ConfigError("target path for include file may not be "
                    "an absolute path")
        processedSpecs.append((source, target))
    return processedSpecs


class Freezer(object):

    def __init__(self, executables, constantsModules = [], includes = [],
            excludes = [], packages = [], replacePaths = [], compress = None,
            optimizeFlag = 0, copyDependentFiles = None, initScript = None,
            base = None, path = None, createLibraryZip = None,
            appendScriptToExe = None, appendScriptToLibrary = None,
            targetDir = None, binIncludes = [], binExcludes = [],
            binPathIncludes = [], binPathExcludes = [], icon = None,
            includeFiles = [], zipIncludes = [], silent = False,
            namespacePackages = [], metadata = None,
            includeMSVCR = False):
        self.executables = list(executables)
        self.constantsModules = list(constantsModules)
        self.includes = list(includes)
        self.excludes = list(excludes)
        self.packages = list(packages)
        self.namespacePackages = list(namespacePackages)
        self.replacePaths = list(replacePaths)
        self.compress = compress
        self.optimizeFlag = optimizeFlag
        self.copyDependentFiles = copyDependentFiles
        self.initScript = initScript
        self.base = base
        self.path = path
        self.createLibraryZip = createLibraryZip
        self.includeMSVCR = includeMSVCR
        self.appendScriptToExe = appendScriptToExe
        self.appendScriptToLibrary = appendScriptToLibrary
        self.targetDir = targetDir
        self.binIncludes = [os.path.normcase(n) \
                for n in self._GetDefaultBinIncludes() + binIncludes]
        self.binExcludes = [os.path.normcase(n) \
                for n in self._GetDefaultBinExcludes() + binExcludes]
        self.binPathIncludes = [os.path.normcase(n) for n in binPathIncludes]
        self.binPathExcludes = [os.path.normcase(n) \
                for n in self._GetDefaultBinPathExcludes() + binPathExcludes]
        self.icon = icon
        self.includeFiles = process_path_specs(includeFiles)
        self.zipIncludes = process_path_specs(zipIncludes)
        self.silent = silent
        self.metadata = metadata
        self._VerifyConfiguration()

    def _AddVersionResource(self, fileName):
        try:
            from win32verstamp import stamp
        except:
            print("*** WARNING *** unable to create version resource")
            print("install pywin32 extensions first")
            return
        versionInfo = VersionInfo(self.metadata.version,
                comments = self.metadata.long_description,
                description = self.metadata.description,
                company = self.metadata.author,
                product = self.metadata.name)
        stamp(fileName, versionInfo)

    def _CopyFile(self, source, target, copyDependentFiles = False,
            includeMode = False):
        normalizedSource = os.path.normcase(os.path.normpath(source))
        normalizedTarget = os.path.normcase(os.path.normpath(target))
        if normalizedTarget in self.filesCopied:
            return
        if normalizedSource == normalizedTarget:
            return
        self._RemoveFile(target)
        targetDir = os.path.dirname(target)
        self._CreateDirectory(targetDir)
        if not self.silent:
            sys.stdout.write("copying %s -> %s\n" % (source, target))
        shutil.copyfile(source, target)
        shutil.copystat(source, target)
        if includeMode:
            shutil.copymode(source, target)
        self.filesCopied[normalizedTarget] = None
        if copyDependentFiles:
            for source in self._GetDependentFiles(source):
                target = os.path.join(targetDir, os.path.basename(source))
                self._CopyFile(source, target, copyDependentFiles)

    def _CreateDirectory(self, path):
        if not os.path.isdir(path):
            if not self.silent:
                sys.stdout.write("creating directory %s\n" % path)
            os.makedirs(path)

    def _FreezeExecutable(self, exe):
        if self.createLibraryZip:
            finder = self.finder
        else:
            finder = self._GetModuleFinder(exe)
        if exe.script is None:
            scriptModule = None
        else:
            scriptModule = finder.IncludeFile(exe.script, exe.moduleName)

        self._CopyFile(exe.base, exe.targetName, exe.copyDependentFiles,
                includeMode = True)
        if self.includeMSVCR:
            self._IncludeMSVCR(exe)

        # Copy icon
        if exe.icon is not None:
            if sys.platform == "win32":
                import cx_Freeze.util
                cx_Freeze.util.AddIcon(exe.targetName, exe.icon)
            else:
                targetName = os.path.join(os.path.dirname(exe.targetName),
                        os.path.basename(exe.icon))
                self._CopyFile(exe.icon, targetName,
                        copyDependentFiles = False)

        if not os.access(exe.targetName, os.W_OK):
            mode = os.stat(exe.targetName).st_mode
            os.chmod(exe.targetName, mode | stat.S_IWUSR)
        if self.metadata is not None and sys.platform == "win32":
            self._AddVersionResource(exe.targetName)

        # Write the zip file of Python modules. If we're using a shared
        # library.zip this is done by the Freeze method instead.
        if not exe.appendScriptToLibrary:
            if exe.appendScriptToExe:
                fileName = exe.targetName
            else:
                baseFileName, ext = os.path.splitext(exe.targetName)
                fileName = baseFileName + ".zip"
                self._RemoveFile(fileName)
            if not self.createLibraryZip and exe.copyDependentFiles:
                scriptModule = None
            self._WriteModules(fileName, exe.initScript, finder, exe.compress,
                    exe.copyDependentFiles, scriptModule)

    def _GetBaseFileName(self, argsSource = None):
        if argsSource is None:
            argsSource = self
        name = argsSource.base
        if name is None:
            if argsSource.copyDependentFiles:
                name = "Console"
            else:
                name = "ConsoleKeepPath"
        ext = ".exe" if sys.platform == "win32" else ""
        argsSource.base = self._GetFileName("bases", name, ext)
        if argsSource.base is None:
            raise ConfigError("no base named %s", name)

    def _GetDefaultBinExcludes(self):
        """Return the file names of libraries that need not be included because
           they would normally be expected to be found on the target system or
           because they are part of a package which requires independent
           installation anyway."""
        if sys.platform == "win32":
            return ["comctl32.dll", "oci.dll", "cx_Logging.pyd"]
        else:
            return ["libclntsh.so", "libwtc9.so"]

    def _GetDefaultBinIncludes(self):
        """Return the file names of libraries which must be included for the
           frozen executable to work."""
        if sys.platform == "win32":
            pythonDll = "python%s%s.dll" % sys.version_info[:2]
            return [pythonDll, "gdiplus.dll", "mfc71.dll", "msvcp71.dll",
                    "msvcr71.dll"]
        else:
            soName = distutils.sysconfig.get_config_var("INSTSONAME")
            if soName is None:
                return []
            pythonSharedLib = self._RemoveVersionNumbers(soName)
            return [pythonSharedLib]

    def _GetDefaultBinPathExcludes(self):
        """Return the paths of directories which contain files that should not
           be included, generally because they contain standard system
           libraries."""
        if sys.platform == "win32":
            import cx_Freeze.util
            systemDir = cx_Freeze.util.GetSystemDir()
            windowsDir = cx_Freeze.util.GetWindowsDir()
            return [windowsDir, systemDir, os.path.join(windowsDir, "WinSxS")]
        elif sys.platform == "darwin":
            return ["/lib", "/usr/lib", "/System/Library/Frameworks"]
        else:
            return ["/lib", "/lib32", "/lib64", "/usr/lib", "/usr/lib32",
                    "/usr/lib64"]

    def _GetDependentFiles(self, path):
        """Return the file's dependencies using platform-specific tools (the
           imagehlp library on Windows, otool on Mac OS X and ldd on Linux);
           limit this list by the exclusion lists as needed"""
        dependentFiles = self.dependentFiles.get(path)
        if dependentFiles is None:
            if sys.platform == "win32":
                origPath = os.environ["PATH"]
                os.environ["PATH"] = origPath + os.pathsep + \
                        os.pathsep.join(sys.path)
                import cx_Freeze.util
                try:
                    dependentFiles = cx_Freeze.util.GetDependentFiles(path)
                except cx_Freeze.util.BindError:
                    # Sometimes this gets called when path is not actually a library
                    # See issue 88
                    dependentFiles = []
                os.environ["PATH"] = origPath
            else:
                dependentFiles = []
                if sys.platform == "darwin":
                    command = 'otool -L "%s"' % path
                    splitString = " (compatibility"
                    dependentFileIndex = 0
                else:
                    command = 'ldd "%s"' % path
                    splitString = " => "
                    dependentFileIndex = 1
                for line in os.popen(command):
                    parts = line.expandtabs().strip().split(splitString)
                    if len(parts) != 2:
                        continue
                    dependentFile = parts[dependentFileIndex].strip()
                    if dependentFile in ("not found", "(file not found)"):
                        fileName = parts[0]
                        if fileName not in self.linkerWarnings:
                            self.linkerWarnings[fileName] = None
                            message = "WARNING: cannot find %s\n" % fileName
                            sys.stdout.write(message)
                        continue
                    if dependentFile.startswith("("):
                        continue
                    pos = dependentFile.find(" (")
                    if pos >= 0:
                        dependentFile = dependentFile[:pos].strip()
                    if dependentFile:
                        dependentFiles.append(dependentFile)
                if sys.platform == "darwin":
                    # Make library paths absolute. This is needed to use
                    # cx_Freeze on OSX in e.g. a conda-based distribution.
                    # Note that with @rpath we just assume Python's lib dir,
                    # which should work in most cases.
                    dirname = os.path.dirname(path)
                    dependentFiles = [p.replace('@loader_path', dirname)
                                      for p in dependentFiles]
                    dependentFiles = [p.replace('@rpath', sys.prefix + '/lib')
                                      for p in dependentFiles]
            dependentFiles = self.dependentFiles[path] = \
                    [f for f in dependentFiles if self._ShouldCopyFile(f)]
        return dependentFiles

    def _GetFileName(self, dirName, name, ext):
        if os.path.isabs(name):
            return name
        name = os.path.normcase(name)
        fullDir = os.path.join(os.path.dirname(cx_Freeze.__file__), dirName)
        if os.path.isdir(fullDir):
            for fileName in os.listdir(fullDir):
                checkName, checkExt = \
                        os.path.splitext(os.path.normcase(fileName))
                if name == checkName and ext == checkExt:
                    return os.path.join(fullDir, fileName)

    def _GetInitScriptFileName(self, argsSource = None):
        if argsSource is None:
            argsSource = self
        name = argsSource.initScript
        if name is None:
            if argsSource.copyDependentFiles:
                name = "Console"
            else:
                name = "ConsoleKeepPath"
        argsSource.initScript = self._GetFileName("initscripts", name, ".py")
        if argsSource.initScript is None:
            raise ConfigError("no initscript named %s", name)

    def _GetModuleFinder(self, argsSource = None):
        if argsSource is None:
            argsSource = self
        finder = cx_Freeze.ModuleFinder(self.includeFiles, argsSource.excludes,
                argsSource.path, argsSource.replacePaths,
                argsSource.copyDependentFiles, compress = argsSource.compress)
        for name in argsSource.namespacePackages:
            package = finder.IncludeModule(name, namespace = True)
            package.ExtendPath()
        for name in argsSource.includes:
            finder.IncludeModule(name)
        for name in argsSource.packages:
            finder.IncludePackage(name)
        return finder

    def _IncludeMSVCR(self, exe):
        msvcRuntimeDll = None
        targetDir = os.path.dirname(exe.targetName)
        for fullName in self.filesCopied:
            path, name = os.path.split(os.path.normcase(fullName))
            if name.startswith("msvcr") and name.endswith(".dll"):
                msvcRuntimeDll = name
                for otherName in [name.replace("r", c) for c in "mp"]:
                    sourceName = os.path.join(self.msvcRuntimeDir, otherName)
                    if not os.path.exists(sourceName):
                        continue
                    targetName = os.path.join(targetDir, otherName)
                    self._CopyFile(sourceName, targetName)
                break

        if msvcRuntimeDll is not None and msvcRuntimeDll == "msvcr90.dll":
            if struct.calcsize("P") == 4:
                arch = "x86"
            else:
                arch = "amd64"
            manifest = MSVCR_MANIFEST_TEMPLATE.strip().replace("{PROC_ARCH}",
                    arch)
            fileName = os.path.join(targetDir, "Microsoft.VC90.CRT.manifest")
            sys.stdout.write("creating %s\n" % fileName)
            open(fileName, "w").write(manifest)

    def _PrintReport(self, fileName, modules):
        sys.stdout.write("writing zip file %s\n\n" % fileName)
        sys.stdout.write("  %-25s %s\n" % ("Name", "File"))
        sys.stdout.write("  %-25s %s\n" % ("----", "----"))
        for module in modules:
            if module.path:
                sys.stdout.write("P")
            else:
                sys.stdout.write("m")
            sys.stdout.write(" %-25s %s\n" % (module.name, module.file or ""))
        sys.stdout.write("\n")

    

    def _RemoveFile(self, path):
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)

    def _RemoveVersionNumbers(self, libName):
        tweaked = False
        parts = libName.split(".")
        while parts:
            if not parts[-1].isdigit():
                break
            parts.pop(-1)
            tweaked = True
        if tweaked:
            libName = ".".join(parts)
        return libName

    def _ShouldCopyFile(self, path):
        """Return true if the file should be copied to the target machine. This
           is done by checking the binPathIncludes, binPathExcludes,
           binIncludes and binExcludes configuration variables using first the
           full file name, then just the base file name, then the file name
           without any version numbers.
           
           Files are included unless specifically excluded but inclusions take
           precedence over exclusions."""

        # check for C runtime, if desired
        path = os.path.normcase(path)
        dirName, fileName = os.path.split(path)
        if fileName.startswith("msvcr") and fileName.endswith(".dll"):
            self.msvcRuntimeDir = dirName
            return self.includeMSVCR

        # check the full path
        if path in self.binIncludes:
            return True
        if path in self.binExcludes:
            return False

        # check the file name by itself (with any included version numbers)
        if fileName in self.binIncludes:
            return True
        if fileName in self.binExcludes:
            return False

        # check the file name by itself (version numbers removed)
        name = self._RemoveVersionNumbers(fileName)
        if name in self.binIncludes:
            return True
        if name in self.binExcludes:
            return False

        # check the path for inclusion/exclusion
        for path in self.binPathIncludes:
            if dirName.startswith(path):
                return True
        for path in self.binPathExcludes:
            if dirName.startswith(path):
                return False

        return True

    def _VerifyCanAppendToLibrary(self):
        if not self.createLibraryZip:
            raise ConfigError("script cannot be appended to library zip if "
                    "one is not being created")

    def _VerifyConfiguration(self):
        if self.compress is None:
            self.compress = True
        if self.copyDependentFiles is None:
            self.copyDependentFiles = True
        if self.createLibraryZip is None:
            self.createLibraryZip = True
        if self.appendScriptToExe is None:
            self.appendScriptToExe = False
        if self.appendScriptToLibrary is None:
            self.appendScriptToLibrary = \
                    self.createLibraryZip and not self.appendScriptToExe
        if self.targetDir is None:
            self.targetDir = os.path.abspath("dist")
        self._GetInitScriptFileName()
        self._GetBaseFileName()
        if self.path is None:
            self.path = sys.path
        if self.appendScriptToLibrary:
            self._VerifyCanAppendToLibrary()

        for sourceFileName, targetFileName in \
                self.includeFiles + self.zipIncludes:
            if not os.path.exists(sourceFileName):
                raise ConfigError("cannot find file/directory named %s",
                        sourceFileName)
            if os.path.isabs(targetFileName):
                raise ConfigError("target file/directory cannot be absolute")

        for executable in self.executables:
            executable._VerifyConfiguration(self)

    def _WriteModules(self, fileName, initScript, finder, compress,
            copyDependentFiles, scriptModule = None):
        initModule = finder.IncludeFile(initScript, "cx_Freeze__init__")
        if scriptModule is None:
            for module in self.constantsModules:
                module.Create(finder)
            modules = [m for m in finder.modules \
                    if m.name not in self.excludeModules]
        else:
            modules = [initModule, scriptModule]
            self.excludeModules[initModule.name] = None
            self.excludeModules[scriptModule.name] = None
        modules.sort(key = lambda m: m.name)
        if not self.silent:
            self._PrintReport(fileName, modules)
        if scriptModule is None:
            finder.ReportMissingModules()

        targetDir = os.path.dirname(fileName)
        self._CreateDirectory(targetDir)

        # Prepare zip file. This can be library.zip, or named after the
        # executable, or even appended to the executable.
        if os.path.exists(fileName):
            mode = "a"
        else:
            mode = "w"
        outFile = zipfile.PyZipFile(fileName, mode, zipfile.ZIP_DEFLATED)

        filesToCopy = []
        for module in modules:
            if module.code is None and module.file is not None:
                # Extension module: save a Python loader in the zip file, and
                # copy the actual file to the build directory, because pyd/so
                # libraries can't be loaded from a zip file.
                fileName = os.path.basename(module.file)
                baseFileName, ext = os.path.splitext(fileName)
                if baseFileName != module.name and module.name != "zlib":
                    if "." in module.name:
                        fileName = module.name + ext
                    generatedFileName = "ExtensionLoader_%s.py" % \
                            module.name.replace(".", "_")
                    module.code = compile(EXTENSION_LOADER_SOURCE % fileName,
                            generatedFileName, "exec")
                target = os.path.join(targetDir, fileName)
                filesToCopy.append((module, target))

            if module.code is None:
                continue

            fileName = "/".join(module.name.split("."))
            if module.path:
                fileName += "/__init__"
            if module.file is not None and os.path.exists(module.file):
                mtime = os.stat(module.file).st_mtime
            else:
                mtime = time.time()
            zipTime = time.localtime(mtime)[:6]
            # starting with Python 3.3 the pyc file format contains the source
            # size; it is not actually used for anything except determining if
            # the file is up to date so we can safely set this value to zero
            if sys.version_info[:2] < (3, 3):
                header = imp.get_magic() + struct.pack("<i", int(mtime))
            else:
                header = imp.get_magic() + struct.pack("<ii", int(mtime), 0)
            data = header + marshal.dumps(module.code)
            zinfo = zipfile.ZipInfo(fileName + ".pyc", zipTime)
            if compress:
                zinfo.compress_type = zipfile.ZIP_DEFLATED
            outFile.writestr(zinfo, data)

        for sourceFileName, targetFileName in self.zipIncludes:
            outFile.write(sourceFileName, targetFileName)

        outFile.close()

        # Copy Python extension modules from the list built above.
        origPath = os.environ["PATH"]
        for module, target in filesToCopy:
            try:
                if module.parent is not None:
                    path = os.pathsep.join([origPath] + module.parent.path)
                    os.environ["PATH"] = path
                self._CopyFile(module.file, target, copyDependentFiles)
            finally:
                os.environ["PATH"] = origPath

    def Freeze(self):
        self.finder = None
        self.excludeModules = {}
        self.dependentFiles = {}
        self.filesCopied = {}
        self.linkerWarnings = {}
        self.msvcRuntimeDir = None
        import cx_Freeze.util
        cx_Freeze.util.SetOptimizeFlag(self.optimizeFlag)

        if self.createLibraryZip:
            self.finder = self._GetModuleFinder()
        for executable in self.executables:
            self._FreezeExecutable(executable)
        if self.createLibraryZip:
            fileName = os.path.join(self.targetDir, "library.zip")
            self._RemoveFile(fileName)
            self._WriteModules(fileName, self.initScript, self.finder,
                    self.compress, self.copyDependentFiles)

        for sourceFileName, targetFileName in self.includeFiles:
            if os.path.isdir(sourceFileName):
                # Copy directories by recursing into them.
                # TODO: Can we use shutil.copytree here?
                for path, dirNames, fileNames in os.walk(sourceFileName):
                    shortPath = path[len(sourceFileName) + 1:]
                    if ".svn" in dirNames:
                        dirNames.remove(".svn")
                    if "CVS" in dirNames:
                        dirNames.remove("CVS")
                    fullTargetDir = os.path.join(self.targetDir,
                            targetFileName, shortPath)
                    self._CreateDirectory(fullTargetDir)
                    for fileName in fileNames:
                        fullSourceName = os.path.join(path, fileName)
                        fullTargetName = os.path.join(fullTargetDir, fileName)
                        self._CopyFile(fullSourceName, fullTargetName,
                                copyDependentFiles = False)
            else:
                # Copy regular files.
                fullName = os.path.join(self.targetDir, targetFileName)
                self._CopyFile(sourceFileName, fullName,
                        copyDependentFiles = False)


class ConfigError(Exception):

    def __init__(self, format, *args):
        self.what = format % args

    def __str__(self):
        return self.what


class Executable(object):

    def __init__(self, script, initScript = None, base = None, path = None,
            targetDir = None, targetName = None, includes = None,
            excludes = None, packages = None, replacePaths = None,
            compress = None, copyDependentFiles = None,
            appendScriptToExe = None, appendScriptToLibrary = None,
            icon = None, namespacePackages = None, shortcutName = None,
            shortcutDir = None):
        self.script = script
        self.initScript = initScript
        self.base = base
        self.path = path
        self.targetDir = targetDir
        self.targetName = targetName
        self.includes = includes
        self.excludes = excludes
        self.packages = packages
        self.namespacePackages = namespacePackages
        self.replacePaths = replacePaths
        self.compress = compress
        self.copyDependentFiles = copyDependentFiles
        self.appendScriptToExe = appendScriptToExe
        self.appendScriptToLibrary = appendScriptToLibrary
        self.icon = icon
        self.shortcutName = shortcutName
        self.shortcutDir = shortcutDir

    def __repr__(self):
        return "<Executable script=%s>" % self.script

    def _VerifyConfiguration(self, freezer):
        if self.path is None:
            self.path = freezer.path
        if self.targetDir is None:
            self.targetDir = freezer.targetDir
        if self.includes is None:
            self.includes = freezer.includes
        if self.excludes is None:
            self.excludes = freezer.excludes
        if self.packages is None:
            self.packages = freezer.packages
        if self.namespacePackages is None:
            self.namespacePackages = freezer.namespacePackages
        if self.replacePaths is None:
            self.replacePaths = freezer.replacePaths
        if self.compress is None:
            self.compress = freezer.compress
        if self.copyDependentFiles is None:
            self.copyDependentFiles = freezer.copyDependentFiles
        if self.appendScriptToExe is None:
            self.appendScriptToExe = freezer.appendScriptToExe
        if self.appendScriptToLibrary is None:
            self.appendScriptToLibrary = freezer.appendScriptToLibrary
        if self.initScript is None:
            self.initScript = freezer.initScript
        else:
            freezer._GetInitScriptFileName(self)
        if self.base is None:
            self.base = freezer.base
        else:
            freezer._GetBaseFileName(self)
        if self.appendScriptToLibrary:
            freezer._VerifyCanAppendToLibrary()
        if self.icon is None:
            self.icon = freezer.icon
        if self.targetName is None:
            name, ext = os.path.splitext(os.path.basename(self.script))
            baseName, ext = os.path.splitext(self.base)
            self.targetName = name + ext
        if self.appendScriptToLibrary:
            name, ext = os.path.splitext(self.targetName)
            self.moduleName = "%s__main__" % os.path.normcase(name)
        else:
            self.moduleName = "__main__"
        self.targetName = os.path.join(self.targetDir, self.targetName)


class ConstantsModule(object):

    def __init__(self, releaseString = None, copyright = None,
            moduleName = "BUILD_CONSTANTS", timeFormat = "%B %d, %Y %H:%M:%S"):
        self.moduleName = moduleName
        self.timeFormat = timeFormat
        self.values = {}
        self.values["BUILD_RELEASE_STRING"] = releaseString
        self.values["BUILD_COPYRIGHT"] = copyright

    def Create(self, finder):
        """Create the module which consists of declaration statements for each
           of the values."""
        today = datetime.datetime.today()
        sourceTimestamp = 0
        for module in finder.modules:
            if module.file is None:
                continue
            if module.inZipFile:
                continue
            if not os.path.exists(module.file):
                raise ConfigError("no file named %s (for module %s)",
                        module.file, module.name)
            timestamp = os.stat(module.file).st_mtime
            sourceTimestamp = max(sourceTimestamp, timestamp)
        sourceTimestamp = datetime.datetime.fromtimestamp(sourceTimestamp)
        self.values["BUILD_TIMESTAMP"] = today.strftime(self.timeFormat)
        self.values["BUILD_HOST"] = socket.gethostname().split(".")[0]
        self.values["SOURCE_TIMESTAMP"] = \
                sourceTimestamp.strftime(self.timeFormat)
        module = finder._AddModule(self.moduleName)
        sourceParts = []
        names = list(self.values.keys())
        names.sort()
        for name in names:
            value = self.values[name]
            sourceParts.append("%s = %r" % (name, value))
        source = "\n".join(sourceParts)
        module.code = compile(source, "%s.py" % self.moduleName, "exec")
        return module


class VersionInfo(object):

    def __init__(self, version, internalName = None, originalFileName = None,
            comments = None, company = None, description = None,
            copyright = None, trademarks = None, product = None, dll = False,
            debug = False, verbose = True):
        parts = version.split(".")
        while len(parts) < 4:
            parts.append("0")
        self.version = ".".join(parts)
        self.internal_name = internalName
        self.original_filename = originalFileName
        self.comments = comments
        self.company = company
        self.description = description
        self.copyright = copyright
        self.trademarks = trademarks
        self.product = product
        self.dll = dll
        self.debug = debug
        self.verbose = verbose
