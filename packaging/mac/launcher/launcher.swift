import Foundation

// Get the main bundle path
let bundlePath = Bundle.main.bundlePath

// Path to the Python interpreter inside the bundle
let pythonPath = "\(bundlePath)/Contents/Frameworks/Python.framework/Versions/Current/Resources/Python.app/Contents/MacOS/Python"

// Path to the main Python script inside the bundle
let mainScriptPath = "\(bundlePath)/Contents/Resources/launch.py"

// Ensure Python interpreter and script exist
let fileManager = FileManager.default
if fileManager.fileExists(atPath: pythonPath) && fileManager.fileExists(atPath: mainScriptPath) {

    // Prepare arguments (execv expects C-style array of arguments)
    let arguments = [pythonPath, mainScriptPath]
    let args = arguments.map { $0.withCString(strdup) }

    // Append nil to the arguments array
    let argv = args + [nil]

    // Use execv to replace the current process with the Python interpreter
    execv(argv[0]!, argv)

    // If execv returns, it means there was an error
    perror("execv failed")

} else {
    print("Python interpreter or main script not found!")
}