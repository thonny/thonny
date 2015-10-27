import os
import sys
import subprocess

if sys.version_info[0] < 3:
    input = raw_input

class SetupWriter(object):
    bases = {
        "C" : "Console",
        "G" : "Win32GUI",
        "S" : "Win32Service"
    }

    @property
    def base(self):
        return self.bases[self.baseCode]

    @property
    def defaultExecutableName(self):
        name, ext = os.path.splitext(self.script)
        return name

    def __init__(self):
        self.name = self.description = self.script = ""
        self.executableName = self.defaultExecutableName
        self.setupFileName = "setup.py"
        self.version = "1.0"
        self.baseCode = "C"

    def GetBooleanValue(self, label, default = False):
        defaultResponse = default and "y" or "n"
        while True:
            response = self.GetValue(label, defaultResponse,
                    separator = "? ").lower()
            if response in ("y", "n", "yes", "no"):
                break
        return response in ("y", "yes")

    def GetValue(self, label, default = "", separator = ": "):
        if default:
            label += " [%s]" % default
        return input(label + separator).strip() or default

    def PopulateFromCommandLine(self):
        self.name = self.GetValue("Project name", self.name)
        self.version = self.GetValue("Version", self.version)
        self.description = self.GetValue("Description", self.description)
        self.script = self.GetValue("Python file to make executable from",
                self.script)
        self.executableName = self.GetValue("Executable file name",
                self.defaultExecutableName)
        basesPrompt = "(C)onsole application, (G)UI application, or (S)ervice"
        while True:
            self.baseCode = self.GetValue(basesPrompt, "C")
            if self.baseCode in self.bases:
                break
        while True:
            self.setupFileName = self.GetValue("Save setup script to",
                    self.setupFileName)
            if not os.path.exists(self.setupFileName):
                break
            if self.GetBooleanValue("Overwrite %s" % self.setupFileName):
                break

    def Write(self):
        output = open(self.setupFileName, "w")
        w = lambda s: output.write(s + "\n")

        w("from cx_Freeze import setup, Executable")
        w("")
        
        w("# Dependencies are automatically detected, but it might need")
        w("# fine tuning.")
        w("buildOptions = dict(packages = [], excludes = [])")
        w("")
        
        if self.base.startswith('Win32'):
            w("import sys")
            w("base = %r if sys.platform=='win32' else None" % self.base)
        else:
            w("base = %r" % self.base)
        w("")

        w("executables = [")
        if self.executableName != self.defaultExecutableName:
            w("    Executable(%r, base=base, targetName = %r)" % \
                    (self.script, self.executableName))
        else:
            w("    Executable(%r, base=base)" % self.script)
        w("]")
        w("")
 
        w(("setup(name=%r,\n"
           "      version = %r,\n"
           "      description = %r,\n"
           "      options = dict(build_exe = buildOptions),\n"
           "      executables = executables)") % \
           (self.name, self.version, self.description))

def main():
    writer = SetupWriter()
    writer.PopulateFromCommandLine()
    writer.Write()
    print("")
    print("Setup script written to %s; run it as:" % writer.setupFileName)
    print("    python %s build" % writer.setupFileName)
    if writer.GetBooleanValue("Run this now"):
        subprocess.call(["python", writer.setupFileName, "build"])

