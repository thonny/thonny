//-----------------------------------------------------------------------------
// Common.c
//   Routines which are common to running frozen executables.
//-----------------------------------------------------------------------------

#include <compile.h>
#include <eval.h>
#include <osdefs.h>

// define macro for converting a C string to a Python string (Unicode for 3.x)
#if PY_MAJOR_VERSION >= 3
    #define cxString_FromStringAndSize(str, size)  \
            PyUnicode_Decode(str, size, Py_FileSystemDefaultEncoding, NULL)
    #define cxString_FromString(str) \
            PyUnicode_Decode(str, strlen(str), Py_FileSystemDefaultEncoding, \
            NULL)
#else
    #define cxString_FromStringAndSize(str, size)  \
            PyString_FromStringAndSize(str, size);
    #define cxString_FromString(str) \
            PyString_FromString(str)
#endif

// PyEval_EvalCode() takes different parameter types on Python 2 & 3.
typedef
#if PY_MAJOR_VERSION >= 3
    PyObject
#else
    PyCodeObject
#endif
    EvalCodeType;


// global variables (used for simplicity)
static PyObject *g_FileName = NULL;
static PyObject *g_DirName = NULL;
static PyObject *g_ExclusiveZipFileName = NULL;
static PyObject *g_SharedZipFileName = NULL;
static PyObject *g_InitScriptZipFileName = NULL;

//-----------------------------------------------------------------------------
// cxString_ToString()
//   Convert an object to a C string.
//-----------------------------------------------------------------------------
static int cxString_ToString(
    PyObject *obj,                      // object to convert to C string
    PyObject **encodedObj,              // encoded object
    const char **str)                   // C string
{
#if PY_MAJOR_VERSION >= 3
    *encodedObj = PyUnicode_AsEncodedString(obj, Py_FileSystemDefaultEncoding,
            NULL);
    if (!*encodedObj)
        return FatalError("unable to encode string");
    *str = PyBytes_AS_STRING(*encodedObj);
#else
    Py_INCREF(obj);
    *encodedObj = obj;
    *str = PyString_AS_STRING(obj);
#endif
    return 0;
}


//-----------------------------------------------------------------------------
// GetDirName()
//   Return the directory name of the given path.
//-----------------------------------------------------------------------------
static int GetDirName(
    const char *path,                   // path to calculate dir name for
    PyObject **dirName)                 // directory name (OUT)
{
    size_t i;

    for (i = strlen(path); i > 0 && path[i] != SEP; --i);
    *dirName = cxString_FromStringAndSize(path, i);
    if (!*dirName)
        return FatalError("cannot create string for directory name");
    return 0;
}


//-----------------------------------------------------------------------------
// SetExecutableName()
//   Set the script to execute and calculate the directory in which the
// executable is found as well as the exclusive (only for this executable) and
// shared zip file names.
//-----------------------------------------------------------------------------
static int SetExecutableName(
    const char *fileName)               // script to execute
{
    char temp[MAXPATHLEN + 12], *ptr;
    const char *tempStr = NULL;
    PyObject *encodedObj;
#ifndef MS_WINDOWS
    char linkData[MAXPATHLEN + 1];
    struct stat statData;
    size_t linkSize, i;
    PyObject *dirName;
#endif

    // store file name
    g_FileName = cxString_FromString(fileName);
    if (!g_FileName)
        return FatalError("cannot create string for file name");

#ifndef MS_WINDOWS
    for (i = 0; i < 25; i++) {
        if (cxString_ToString(g_FileName, &encodedObj, &fileName) < 0)
            return -1;
        if (lstat(fileName, &statData) < 0) {
            PyErr_SetFromErrnoWithFilename(PyExc_OSError, (char*) fileName);
            return FatalError("unable to stat file");
        }
        if (!S_ISLNK(statData.st_mode))
            break;
        linkSize = readlink(fileName, linkData, sizeof(linkData));
        if (linkSize < 0) {
            PyErr_SetFromErrnoWithFilename(PyExc_OSError, (char*) fileName);
            return FatalError("unable to stat file");
        }
        Py_DECREF(encodedObj);
        if (linkData[0] == '/') {
            Py_DECREF(g_FileName);
            g_FileName = cxString_FromStringAndSize(linkData, linkSize);
        } else {
            if (cxString_ToString(g_FileName, &encodedObj, &fileName) < 0)
                return -1;
            if (GetDirName(fileName, &dirName) < 0) {
                Py_DECREF(encodedObj);
                return -1;
            }
            Py_DECREF(encodedObj);
            if (cxString_ToString(dirName, &encodedObj, &tempStr) < 0)
                return -1;
            if (strlen(tempStr) + linkSize + 1 > MAXPATHLEN) {
                Py_DECREF(dirName);
                Py_DECREF(encodedObj);
                return FatalError("cannot dereference link, path too large");
            }
            strcpy(temp, tempStr);
            Py_DECREF(encodedObj);
            strcat(temp, "/");
            strncat(temp, linkData, linkSize);
            Py_DECREF(g_FileName);
            g_FileName = cxString_FromString(temp);
        }
        if (!g_FileName)
            return FatalError("cannot create string for linked file name");
    }
#endif

    // calculate and store directory name
    if (GetDirName(fileName, &g_DirName) < 0)
        return -1;

    // calculate and store exclusive zip file name
    strcpy(temp, fileName);
    ptr = temp + strlen(temp) - 1;
    while (ptr > temp && *ptr != SEP && *ptr != '.')
        ptr--;
    if (*ptr == '.')
        *ptr = '\0';
    strcat(temp, ".zip");
    g_ExclusiveZipFileName = cxString_FromString(temp);
    if (!g_ExclusiveZipFileName)
        return FatalError("cannot create string for exclusive zip file name");

    // calculate and store shared zip file name
    if (cxString_ToString(g_DirName, &encodedObj, &tempStr) < 0)
        return -1;
    strcpy(temp, tempStr);
    Py_DECREF(encodedObj);
    ptr = temp + strlen(temp);
    *ptr++ = SEP;
    strcpy(ptr, "library.zip");
    g_SharedZipFileName = cxString_FromString(temp);
    if (!g_SharedZipFileName)
        return FatalError("cannot create string for shared zip file name");

    return 0;
}


//-----------------------------------------------------------------------------
// SetPathToSearch()
//   Set the path to search. This includes the file (for those situations where
// a zip file is attached to the executable itself), the directory where the
// executable is found (to search for extensions), the exclusive zip file
// name and the shared zip file name.
//-----------------------------------------------------------------------------
static int SetPathToSearch(void)
{
    PyObject *pathList;

    pathList = PySys_GetObject("path");
    if (!pathList)
        return FatalError("cannot acquire sys.path");
    if (PyList_Insert(pathList, 0, g_FileName) < 0)
        return FatalError("cannot insert file name into sys.path");
    if (PyList_Insert(pathList, 1, g_DirName) < 0)
        return FatalError("cannot insert directory name into sys.path");
    if (PyList_Insert(pathList, 2, g_ExclusiveZipFileName) < 0)
        return FatalError("cannot insert exclusive zip name into sys.path");
    if (PyList_Insert(pathList, 3, g_SharedZipFileName) < 0)
        return FatalError("cannot insert shared zip name into sys.path");
    return 0;
}


//-----------------------------------------------------------------------------
// GetImporterHelper()
//   Helper which is used to locate the importer for the initscript.
//-----------------------------------------------------------------------------
static PyObject *GetImporterHelper(
    PyObject *module,                   // zipimport module
    PyObject *fileName)                 // name of file to search
{
    PyObject *importer;

    importer = PyObject_CallMethod(module, "zipimporter", "O", fileName);
    if (importer)
        g_InitScriptZipFileName = fileName;
    else
        PyErr_Clear();
    return importer;
}


//-----------------------------------------------------------------------------
// GetImporter()
//   Return the importer which will be used for importing the initialization
// script. The executable itself is searched first, followed by the exclusive
// zip file and finally by the shared zip file.
//-----------------------------------------------------------------------------
static int GetImporter(
    PyObject **importer)                // importer (OUT)
{
    PyObject *module;

    module = PyImport_ImportModule("zipimport");
    if (!module)
        return FatalError("cannot import zipimport module");
    *importer = GetImporterHelper(module, g_FileName);
    if (!*importer) {
        *importer = GetImporterHelper(module, g_ExclusiveZipFileName);
        if (!*importer)
            *importer = GetImporterHelper(module, g_SharedZipFileName);
    }
    Py_DECREF(module);
    if (!*importer)
        return FatalError("cannot get zipimporter instance");
    return 0;
}


//-----------------------------------------------------------------------------
// PopulateInitScriptDict()
//   Return the dictionary used by the initialization script.
//-----------------------------------------------------------------------------
static int PopulateInitScriptDict(
    PyObject *dict)                     // dictionary to populate
{
    if (!dict)
        return FatalError("unable to create temporary dictionary");
    if (PyDict_SetItemString(dict, "__builtins__", PyEval_GetBuiltins()) < 0)
        return FatalError("unable to set __builtins__");
    if (PyDict_SetItemString(dict, "FILE_NAME", g_FileName) < 0)
        return FatalError("unable to set FILE_NAME");
    if (PyDict_SetItemString(dict, "DIR_NAME", g_DirName) < 0)
        return FatalError("unable to set DIR_NAME");
    if (PyDict_SetItemString(dict, "EXCLUSIVE_ZIP_FILE_NAME",
            g_ExclusiveZipFileName) < 0)
        return FatalError("unable to set EXCLUSIVE_ZIP_FILE_NAME");
    if (PyDict_SetItemString(dict, "SHARED_ZIP_FILE_NAME",
            g_SharedZipFileName) < 0)
        return FatalError("unable to set SHARED_ZIP_FILE_NAME");
    if (PyDict_SetItemString(dict, "INITSCRIPT_ZIP_FILE_NAME",
            g_InitScriptZipFileName) < 0)
        return FatalError("unable to set INITSCRIPT_ZIP_FILE_NAME");
    return 0;
}




//-----------------------------------------------------------------------------
// ExecuteScript()
//   Execute the script found within the file.
//-----------------------------------------------------------------------------
static int ExecuteScript(
    const char *fileName)               // name of file containing Python code
{
    PyObject *importer, *dict, *code, *temp;

    if (SetExecutableName(fileName) < 0)
        return -1;
    if (SetPathToSearch() < 0)
        return -1;
    importer = NULL;
    if (GetImporter(&importer) < 0)
        return -1;

    // create and populate dictionary for initscript module
    dict = PyDict_New();
    if (PopulateInitScriptDict(dict) < 0) {
        Py_XDECREF(dict);
        Py_DECREF(importer);
        return -1;
    }

    // locate and execute script
    code = PyObject_CallMethod(importer, "get_code", "s", "cx_Freeze__init__");
    Py_DECREF(importer);
    if (!code)
        return FatalError("unable to locate initialization module");
    temp = PyEval_EvalCode( (EvalCodeType*) code, dict, dict);
    Py_DECREF(code);
    Py_DECREF(dict);
    if (!temp)
        return FatalScriptError();
    Py_DECREF(temp);

    return 0;
}

