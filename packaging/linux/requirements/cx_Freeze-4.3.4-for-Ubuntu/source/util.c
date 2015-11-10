//-----------------------------------------------------------------------------
// util.c
//   Shared library for use by cx_Freeze.
//-----------------------------------------------------------------------------

#include <Python.h>

#ifdef MS_WINDOWS
#include <windows.h>
#include <imagehlp.h>
#include <Shlwapi.h>

#pragma pack(2)

typedef struct {
    BYTE bWidth;                        // Width, in pixels, of the image
    BYTE bHeight;                       // Height, in pixels, of the image
    BYTE bColorCount;                   // Number of colors in image
    BYTE bReserved;                     // Reserved ( must be 0)
    WORD wPlanes;                       // Color Planes
    WORD wBitCount;                     // Bits per pixel
    DWORD dwBytesInRes;                 // How many bytes in this resource?
    DWORD dwImageOffset;                // Where in the file is this image?
} ICONDIRENTRY;

typedef struct {
    WORD idReserved;                    // Reserved (must be 0)
    WORD idType;                        // Resource Type (1 for icons)
    WORD idCount;                       // How many images?
    ICONDIRENTRY idEntries[0];          // An entry for each image
} ICONDIR;

typedef struct {
    BYTE bWidth;                        // Width, in pixels, of the image
    BYTE bHeight;                       // Height, in pixels, of the image
    BYTE bColorCount;                   // Number of colors in image
    BYTE bReserved;                     // Reserved ( must be 0)
    WORD wPlanes;                       // Color Planes
    WORD wBitCount;                     // Bits per pixel
    DWORD dwBytesInRes;                 // How many bytes in this resource?
    WORD nID;                           // resource ID
} GRPICONDIRENTRY;

typedef struct {
    WORD idReserved;                    // Reserved (must be 0)
    WORD idType;                        // Resource Type (1 for icons)
    WORD idCount;                       // How many images?
    GRPICONDIRENTRY idEntries[0];       // An entry for each image
} GRPICONDIR;
#endif

//-----------------------------------------------------------------------------
// Globals
//-----------------------------------------------------------------------------
#ifdef MS_WINDOWS
static PyObject *g_BindErrorException = NULL;
static PyObject *g_ImageNames = NULL;
#endif

// define PyInt_* macros for Python 3.x
#ifndef PyInt_Check
#define PyInt_Check             PyLong_Check
#define PyInt_FromLong          PyLong_FromLong
#endif


#ifdef MS_WINDOWS
//-----------------------------------------------------------------------------
// BindStatusRoutine()
//   Called by BindImageEx() at various points. This is used to determine the
// dependency tree which is later examined by cx_Freeze.
//-----------------------------------------------------------------------------
static BOOL __stdcall BindStatusRoutine(
    IMAGEHLP_STATUS_REASON reason,      // reason called
    PCSTR imageName,                    // name of image being examined
    PCSTR dllName,                      // name of DLL
    ULONG_PTR virtualAddress,           // computed virtual address
    ULONG_PTR parameter)                // parameter (value depends on reason)
{
    char imagePath[MAX_PATH + 1];
    char fileName[MAX_PATH + 1];

    switch (reason) {
        case BindImportModule:
            strcpy(imagePath, imageName);
            PathRemoveFileSpec(imagePath);
            if (!SearchPath(imagePath, dllName, NULL, sizeof(fileName),
                    fileName, NULL)) {
                if (!SearchPath(NULL, dllName, NULL, sizeof(fileName),
                        fileName, NULL))
                    return FALSE;
            }
            Py_INCREF(Py_None);
            if (PyDict_SetItemString(g_ImageNames, fileName, Py_None) < 0)
                return FALSE;
            break;
        default:
            break;
    }

    return TRUE;
}


//-----------------------------------------------------------------------------
// GetFileData()
//   Return the data for the given file.
//-----------------------------------------------------------------------------
static int GetFileData(
    const char *fileName,               // name of file to read
    char **data)                        // pointer to data (OUT)
{
    DWORD numberOfBytesRead, dataSize;
    HANDLE file;

    file = CreateFile(fileName, GENERIC_READ, FILE_SHARE_READ, NULL,
            OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE)
        return -1;
    dataSize = GetFileSize(file, NULL);
    if (dataSize == INVALID_FILE_SIZE) {
        CloseHandle(file);
        return -1;
    }
    *data = PyMem_Malloc(dataSize);
    if (!*data) {
        CloseHandle(file);
        return -1;
    }
    if (!ReadFile(file, *data, dataSize, &numberOfBytesRead, NULL)) {
        CloseHandle(file);
        return -1;
    }
    CloseHandle(file);
    return 0;
}


//-----------------------------------------------------------------------------
// CreateGroupIconResource()
//   Return the group icon resource given the icon file data.
//-----------------------------------------------------------------------------
static GRPICONDIR *CreateGroupIconResource(
    ICONDIR *iconDir,                   // icon information
    DWORD *resourceSize)                // size of resource (OUT)
{
    GRPICONDIR *groupIconDir;
    int i;

    *resourceSize = sizeof(GRPICONDIR) +
            sizeof(GRPICONDIRENTRY) * iconDir->idCount;
    groupIconDir = PyMem_Malloc(*resourceSize);
    if (!groupIconDir)
        return NULL;
    groupIconDir->idReserved = iconDir->idReserved;
    groupIconDir->idType = iconDir->idType;
    groupIconDir->idCount = iconDir->idCount;
    for (i = 0; i < iconDir->idCount; i++) {
        groupIconDir->idEntries[i].bWidth = iconDir->idEntries[i].bWidth;
        groupIconDir->idEntries[i].bHeight = iconDir->idEntries[i].bHeight;
        groupIconDir->idEntries[i].bColorCount =
                iconDir->idEntries[i].bColorCount;
        groupIconDir->idEntries[i].bReserved = iconDir->idEntries[i].bReserved;
        groupIconDir->idEntries[i].wPlanes = iconDir->idEntries[i].wPlanes;
        groupIconDir->idEntries[i].wBitCount = iconDir->idEntries[i].wBitCount;
        groupIconDir->idEntries[i].dwBytesInRes =
                iconDir->idEntries[i].dwBytesInRes;
        groupIconDir->idEntries[i].nID = i + 1;
    }

    return groupIconDir;
}


//-----------------------------------------------------------------------------
// ExtAddIcon()
//   Add the icon as a resource to the specified file.
//-----------------------------------------------------------------------------
static PyObject *ExtAddIcon(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments
{
    char *executableName, *iconName, *data, *iconData;
    GRPICONDIR *groupIconDir;
    DWORD resourceSize;
    ICONDIR *iconDir;
    BOOL succeeded;
    HANDLE handle;
    int i;

    if (!PyArg_ParseTuple(args, "ss", &executableName, &iconName))
        return NULL;

    // begin updating the executable
    handle = BeginUpdateResource(executableName, FALSE);
    if (!handle) {
        PyErr_SetExcFromWindowsErrWithFilename(PyExc_WindowsError,
                GetLastError(), executableName);
        return NULL;
    }

    // first attempt to get the data from the icon file
    data = NULL;
    succeeded = TRUE;
    groupIconDir = NULL;
    if (GetFileData(iconName, &data) < 0)
        succeeded = FALSE;
    iconDir = (ICONDIR*) data;

    // next, attempt to add a group icon resource
    if (succeeded) {
        groupIconDir = CreateGroupIconResource(iconDir, &resourceSize);
        if (groupIconDir)
            succeeded = UpdateResource(handle, RT_GROUP_ICON,
                    MAKEINTRESOURCE(1),
                    MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL),
                    groupIconDir, resourceSize);
        else succeeded = FALSE;
    }

    // next, add each icon as a resource
    if (succeeded) {
        for (i = 0; i < iconDir->idCount; i++) {
            iconData = &data[iconDir->idEntries[i].dwImageOffset];
            resourceSize = iconDir->idEntries[i].dwBytesInRes;
            succeeded = UpdateResource(handle, RT_ICON, MAKEINTRESOURCE(i + 1),
                    MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), iconData,
                    resourceSize);
            if (!succeeded)
                break;
        }
    }

    // finish writing the resource (or discarding the changes upon an error)
    if (!EndUpdateResource(handle, !succeeded)) {
        if (succeeded) {
            succeeded = FALSE;
            PyErr_SetExcFromWindowsErrWithFilename(PyExc_WindowsError,
                    GetLastError(), executableName);
        }
    }

    // clean up
    if (groupIconDir)
        PyMem_Free(groupIconDir);
    if (data)
        PyMem_Free(data);
    if (!succeeded)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// ExtBeginUpdateResource()
//   Wrapper for BeginUpdateResource().
//-----------------------------------------------------------------------------
static PyObject *ExtBeginUpdateResource(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments
{
    BOOL deleteExistingResources;
    char *fileName;
    HANDLE handle;

    deleteExistingResources = TRUE;
    if (!PyArg_ParseTuple(args, "s|i", &fileName, &deleteExistingResources))
        return NULL;
    handle = BeginUpdateResource(fileName, deleteExistingResources);
    if (!handle) {
        PyErr_SetExcFromWindowsErrWithFilename(PyExc_WindowsError,
                GetLastError(), fileName);
        return NULL;
    }
    return PyInt_FromLong((long) handle);
}


//-----------------------------------------------------------------------------
// ExtUpdateResource()
//   Wrapper for UpdateResource().
//-----------------------------------------------------------------------------
static PyObject *ExtUpdateResource(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments
{
    int resourceType, resourceId, resourceDataSize;
    char *resourceData;
    HANDLE handle;

    if (!PyArg_ParseTuple(args, "iiis#", &handle, &resourceType, &resourceId,
            &resourceData, &resourceDataSize))
        return NULL;
    if (!UpdateResource(handle, MAKEINTRESOURCE(resourceType),
            MAKEINTRESOURCE(resourceId),
            MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), resourceData,
            resourceDataSize)) {
        PyErr_SetExcFromWindowsErr(PyExc_WindowsError, GetLastError());
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// ExtEndUpdateResource()
//   Wrapper for EndUpdateResource().
//-----------------------------------------------------------------------------
static PyObject *ExtEndUpdateResource(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments
{
    BOOL discardChanges;
    HANDLE handle;

    discardChanges = FALSE;
    if (!PyArg_ParseTuple(args, "i|i", &handle, &discardChanges))
        return NULL;
    if (!EndUpdateResource(handle, discardChanges)) {
        PyErr_SetExcFromWindowsErr(PyExc_WindowsError, GetLastError());
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// ExtGetDependentFiles()
//   Return a list of files that this file depends on.
//-----------------------------------------------------------------------------
static PyObject *ExtGetDependentFiles(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments
{
    PyObject *results;
    char *imageName;

    if (!PyArg_ParseTuple(args, "s", &imageName))
        return NULL;
    g_ImageNames = PyDict_New();
    if (!g_ImageNames)
        return NULL;
    if (!BindImageEx(BIND_NO_BOUND_IMPORTS | BIND_NO_UPDATE | BIND_ALL_IMAGES,
                imageName, NULL, NULL, BindStatusRoutine)) {
        Py_DECREF(g_ImageNames);
        PyErr_SetExcFromWindowsErrWithFilename(g_BindErrorException,
                GetLastError(), imageName);
        return NULL;
    }
    results = PyDict_Keys(g_ImageNames);
    Py_DECREF(g_ImageNames);
    return results;
}


//-----------------------------------------------------------------------------
// ExtGetSystemDir()
//   Return the Windows system directory (C:\Windows\system for example).
//-----------------------------------------------------------------------------
static PyObject *ExtGetSystemDir(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments (ignored)
{
#if PY_MAJOR_VERSION >= 3
    OLECHAR dir[MAX_PATH + 1];
    if (GetSystemDirectoryW(dir, sizeof(dir)))
        return PyUnicode_FromUnicode(dir, wcslen(dir));
#else
    char dir[MAX_PATH + 1];
    if (GetSystemDirectory(dir, sizeof(dir)))
        return PyString_FromString(dir);
#endif

    PyErr_SetExcFromWindowsErr(PyExc_RuntimeError, GetLastError());
    return NULL;
}


//-----------------------------------------------------------------------------
// ExtGetWindowsDir()
//   Return the Windows directory (C:\Windows for example).
//-----------------------------------------------------------------------------
static PyObject *ExtGetWindowsDir(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments (ignored)
{
#if PY_MAJOR_VERSION >= 3
    OLECHAR dir[MAX_PATH + 1];
    if (GetWindowsDirectoryW(dir, sizeof(dir)))
        return PyUnicode_FromUnicode(dir, wcslen(dir));
#else
    char dir[MAX_PATH + 1];
    if (GetWindowsDirectory(dir, sizeof(dir)))
        return PyString_FromString(dir);
#endif

    PyErr_SetExcFromWindowsErr(PyExc_RuntimeError, GetLastError());
    return NULL;
}
#endif


//-----------------------------------------------------------------------------
// ExtSetOptimizeFlag()
//   Set the optimize flag as needed.
//-----------------------------------------------------------------------------
static PyObject *ExtSetOptimizeFlag(
    PyObject *self,                     // passthrough argument
    PyObject *args)                     // arguments
{
    if (!PyArg_ParseTuple(args, "i", &Py_OptimizeFlag))
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Methods
//-----------------------------------------------------------------------------
static PyMethodDef g_ModuleMethods[] = {
    { "SetOptimizeFlag", ExtSetOptimizeFlag, METH_VARARGS },
#ifdef MS_WINDOWS
    { "BeginUpdateResource", ExtBeginUpdateResource, METH_VARARGS },
    { "UpdateResource", ExtUpdateResource, METH_VARARGS },
    { "EndUpdateResource", ExtEndUpdateResource, METH_VARARGS },
    { "AddIcon", ExtAddIcon, METH_VARARGS },
    { "GetDependentFiles", ExtGetDependentFiles, METH_VARARGS },
    { "GetSystemDir", ExtGetSystemDir, METH_NOARGS },
    { "GetWindowsDir", ExtGetWindowsDir, METH_NOARGS },
#endif
    { NULL }
};


#if PY_MAJOR_VERSION >= 3
//-----------------------------------------------------------------------------
//   Declaration of module definition for Python 3.x.
//-----------------------------------------------------------------------------
static struct PyModuleDef g_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    "cx_Freeze.util",
    NULL,
    -1,
    g_ModuleMethods,                       // methods
    NULL,                                  // m_reload
    NULL,                                  // traverse
    NULL,                                  // clear
    NULL                                   // free
};
#endif


//-----------------------------------------------------------------------------
// Module_Initialize()
//   Initialization routine for the module.
//-----------------------------------------------------------------------------
static PyObject *Module_Initialize(void)
{
    PyObject *module;

#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&g_ModuleDef);
#else
    module = Py_InitModule("cx_Freeze.util", g_ModuleMethods);
#endif
    if (!module)
        return NULL;
#ifdef MS_WINDOWS
    g_BindErrorException = PyErr_NewException("cx_Freeze.util.BindError",
            NULL, NULL);
    if (!g_BindErrorException)
        return NULL;
    if (PyModule_AddObject(module, "BindError", g_BindErrorException) < 0)
        return NULL;
#endif
    return module;
}


//-----------------------------------------------------------------------------
// Entry point for the module.
//-----------------------------------------------------------------------------
#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_util(void)
{
    return Module_Initialize();
}
#else
void initutil(void)
{
        Module_Initialize();
}
#endif

