//-----------------------------------------------------------------------------
// Win32Service.c
//   Base executable for handling Windows services.
//-----------------------------------------------------------------------------

#include <Python.h>
#include <windows.h>
#include <Winsvc.h>
#include <cx_Logging.h>

// define constants
#define CX_LOGGING_SECTION_NAME         "Logging"
#define CX_LOGGING_FILE_NAME_KEY        "FileName"
#define CX_LOGGING_LEVEL_KEY            "Level"
#define CX_LOGGING_MAX_FILES_KEY        "MaxFiles"
#define CX_LOGGING_MAX_FILE_SIZE_KEY    "MaxFileSize"
#define CX_LOGGING_PREFIX_KEY           "Prefix"
#define CX_SERVICE_MODULE_NAME          "MODULE_NAME"
#define CX_SERVICE_CLASS_NAME           "CLASS_NAME"
#define CX_SERVICE_NAME                 "NAME"
#define CX_SERVICE_DISPLAY_NAME         "DISPLAY_NAME"
#define CX_SERVICE_DESCRIPTION          "DESCRIPTION"
#define CX_SERVICE_AUTO_START           "AUTO_START"
#define CX_SERVICE_SESSION_CHANGES      "SESSION_CHANGES"

// the following was copied from cx_Interface.c, which is where this
// declaration normally happens
#ifndef PATH_MAX
    #define PATH_MAX _MAX_PATH
#endif

//define structure for holding information about the service
typedef struct {
    PyObject *cls;
    PyObject *nameFormat;
    PyObject *displayNameFormat;
    PyObject *description;
    DWORD startType;
    int sessionChanges;
} udt_ServiceInfo;

// define globals
static HANDLE gControlEvent = NULL;
static SERVICE_STATUS_HANDLE gServiceHandle;
static PyInterpreterState *gInterpreterState = NULL;
static PyObject *gInstance = NULL;
static char gIniFileName[PATH_MAX + 1];

//-----------------------------------------------------------------------------
// FatalError()
//   Called when an attempt to initialize the module zip fails.
//-----------------------------------------------------------------------------
static int FatalError(
    const char *message)		        // message to print
{
    return LogPythonException(message);
}


//-----------------------------------------------------------------------------
// FatalScriptError()
//   Called when an attempt to import the initscript fails.
//-----------------------------------------------------------------------------
static int FatalScriptError(void)
{
    return LogPythonException("initialization script didn't execute properly");
}

#include "Common.c"
#include "BaseModules.c"

//-----------------------------------------------------------------------------
// Service_SetStatus()
//   Set the status for the service.
//-----------------------------------------------------------------------------
static int Service_SetStatus(
    udt_ServiceInfo* info,              // service information
    DWORD status)			            // status to set
{
    SERVICE_STATUS serviceStatus;

    serviceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    serviceStatus.dwCurrentState = status;
    serviceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP;
    if (info->sessionChanges)
        serviceStatus.dwControlsAccepted |= SERVICE_ACCEPT_SESSIONCHANGE;
    serviceStatus.dwWin32ExitCode = 0;
    serviceStatus.dwServiceSpecificExitCode = 0;
    serviceStatus.dwCheckPoint = 0;
    serviceStatus.dwWaitHint = 0;
    if (!SetServiceStatus(gServiceHandle, &serviceStatus))
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// Service_Stop()
//   Stop the service. Note that the controlling thread must be ended before
// the main thread is ended or the control GUI does not understand that the
// service has ended.
//-----------------------------------------------------------------------------
static int Service_Stop(
    udt_ServiceInfo* info)              // service information
{
    PyThreadState *threadState;
    PyObject *result;

    // indicate that the service is being stopped
    if (Service_SetStatus(info, SERVICE_STOP_PENDING) < 0)
        return LogWin32Error(GetLastError(), "cannot set service as stopping");

    // create event for the main thread to wait on for the control thread
    gControlEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    if (!gControlEvent)
        return LogWin32Error(GetLastError(), "cannot create control event");

    // create a new Python thread and acquire the global interpreter lock
    threadState = PyThreadState_New(gInterpreterState);
    if (!threadState)
        return LogPythonException("unable to create new thread state");
    PyEval_AcquireThread(threadState);

    // call the "Stop" method
    result = PyObject_CallMethod(gInstance, "Stop", NULL);
    if (!result)
        return LogPythonException("exception calling Stop method");
    Py_DECREF(result);

    // destroy the Python thread and release the global interpreter lock
    PyThreadState_Clear(threadState);
    PyEval_ReleaseThread(threadState);
    PyThreadState_Delete(threadState);

    // indicate that the service has stopped
    if (Service_SetStatus(info, SERVICE_STOPPED) < 0)
        return LogWin32Error(GetLastError(), "cannot set service as stopped");

    // now set the control event
    if (!SetEvent(gControlEvent))
        return LogWin32Error(GetLastError(), "cannot set control event");

    return 0;
}


//-----------------------------------------------------------------------------
// Service_SessionChange()
//   Called when a session has changed.
//-----------------------------------------------------------------------------
static int Service_SessionChange(
    DWORD sessionId,                    // session that has changed
    DWORD eventType)                    // event type
{
    PyThreadState *threadState;
    PyObject *result;

    // create a new Python thread and acquire the global interpreter lock
    threadState = PyThreadState_New(gInterpreterState);
    if (!threadState)
        return LogPythonException("unable to create new thread state");
    PyEval_AcquireThread(threadState);

    // call Python method
    result = PyObject_CallMethod(gInstance, "SessionChanged", "ii",
            sessionId, eventType);
    if (!result)
        return LogPythonException("exception calling SessionChanged method");
    Py_DECREF(result);

    // destroy the Python thread and release the global interpreter lock
    PyThreadState_Clear(threadState);
    PyEval_ReleaseThread(threadState);
    PyThreadState_Delete(threadState);

    return 0;
}


//-----------------------------------------------------------------------------
// Service_Control()
//   Function for controlling a service. Note that the controlling thread
// must be ended before the main thread is ended or the control GUI does not
// understand that the service has ended.
//-----------------------------------------------------------------------------
static DWORD WINAPI Service_Control(
    DWORD controlCode,			        // control code
    DWORD eventType,                    // event type
    LPVOID eventData,                   // event data
    LPVOID context)                     // context
{
    udt_ServiceInfo *serviceInfo = (udt_ServiceInfo*) context;
    WTSSESSION_NOTIFICATION *sessionInfo;

    switch (controlCode) {
        case SERVICE_CONTROL_STOP:
            Service_Stop(serviceInfo);
            break;
        case SERVICE_CONTROL_SESSIONCHANGE:
            sessionInfo = (WTSSESSION_NOTIFICATION*) eventData;
            Service_SessionChange(sessionInfo->dwSessionId, eventType);
            break;
    }

    return NO_ERROR;
}


//-----------------------------------------------------------------------------
// Service_StartLogging()
//   Initialize logging for the service.
//-----------------------------------------------------------------------------
static int Service_StartLogging(
    const char *fileName)		        // name of file for defaults
{
    char defaultLogFileName[PATH_MAX + 1], logFileName[PATH_MAX + 1];
    unsigned logLevel, maxFiles, maxFileSize;
    char *ptr, prefix[100];
    size_t size;

    // determine the default log file name and ini file name
    ptr = strrchr(fileName, '.');
    if (ptr)
       size = ptr - fileName;
    else size = strlen(fileName);
    strcpy(defaultLogFileName, fileName);
    strcpy(&defaultLogFileName[size], ".log");
    if (strlen(gIniFileName) == 0) {
        strcpy(gIniFileName, fileName);
        strcpy(&gIniFileName[size], ".ini");
    }

    // read the entries from the ini file
    logLevel = GetPrivateProfileInt(CX_LOGGING_SECTION_NAME,
            CX_LOGGING_LEVEL_KEY, LOG_LEVEL_ERROR, gIniFileName);
    GetPrivateProfileString(CX_LOGGING_SECTION_NAME, CX_LOGGING_FILE_NAME_KEY,
            defaultLogFileName, logFileName, sizeof(logFileName),
            gIniFileName);
    maxFiles = GetPrivateProfileInt(CX_LOGGING_SECTION_NAME,
            CX_LOGGING_MAX_FILES_KEY, 1, gIniFileName);
    maxFileSize = GetPrivateProfileInt(CX_LOGGING_SECTION_NAME,
            CX_LOGGING_MAX_FILE_SIZE_KEY, DEFAULT_MAX_FILE_SIZE, gIniFileName);
    GetPrivateProfileString(CX_LOGGING_SECTION_NAME, CX_LOGGING_PREFIX_KEY,
            "[%i] %d %t", prefix, sizeof(prefix), gIniFileName);

    // start the logging process
    return StartLogging(logFileName, logLevel, maxFiles, maxFileSize, prefix);
}


//-----------------------------------------------------------------------------
// Service_SetupPython()
//   Setup Python usage for the service.
//-----------------------------------------------------------------------------
static int Service_SetupPython(
    char *programName,                  // name of the program (argv[0])
    udt_ServiceInfo *info)              // info about service (OUT)
{
    PyObject *module, *serviceModule, *temp;
    PyThreadState *threadState;
    char *fileName;

    // initialize Python
    Py_NoSiteFlag = 1;
    Py_FrozenFlag = 1;
    Py_IgnoreEnvironmentFlag = 1;
    PyImport_FrozenModules = gFrozenModules;
    Py_SetPythonHome("");
    Py_SetProgramName(programName);
    fileName = Py_GetProgramFullPath();
    Py_Initialize();

    // initialize logging
    if (Service_StartLogging(fileName) < 0)
        return -1;

    // ensure threading is initialized and interpreter state saved
    PyEval_InitThreads();
    threadState = PyThreadState_Swap(NULL);
    if (!threadState) {
        LogMessage(LOG_LEVEL_ERROR, "cannot set up interpreter state");
        Service_SetStatus(info, SERVICE_STOPPED);
        return -1;
    }
    gInterpreterState = threadState->interp;
    PyThreadState_Swap(threadState);

    // running base script
    LogMessage(LOG_LEVEL_DEBUG, "running base Python script");
    if (ExecuteScript(fileName) < 0)
        return -1;

    // acquire the __main__ module
    module = PyImport_ImportModule("__main__");
    if (!module)
        return LogPythonException("unable to import __main__");

    // determine name to use for the service
    info->nameFormat = PyObject_GetAttrString(module, CX_SERVICE_NAME);
    if (!info->nameFormat)
        return LogPythonException("cannot locate service name");

    // determine display name to use for the service
    info->displayNameFormat = PyObject_GetAttrString(module,
            CX_SERVICE_DISPLAY_NAME);
    if (!info->displayNameFormat)
        return LogPythonException("cannot locate service display name");

    // determine description to use for the service (optional)
    info->description = PyObject_GetAttrString(module,
            CX_SERVICE_DESCRIPTION);
    if (!info->description)
        PyErr_Clear();

    // determine if service should be automatically started (optional)
    info->startType = SERVICE_DEMAND_START;
    temp = PyObject_GetAttrString(module, CX_SERVICE_AUTO_START);
    if (!temp)
        PyErr_Clear();
    else if (temp == Py_True)
        info->startType = SERVICE_AUTO_START;

    // determine if service should monitor session changes (optional)
    info->sessionChanges = 0;
    temp = PyObject_GetAttrString(module, CX_SERVICE_SESSION_CHANGES);
    if (!temp)
        PyErr_Clear();
    else if (temp == Py_True)
        info->sessionChanges = 1;

    // import the module which implements the service
    temp = PyObject_GetAttrString(module, CX_SERVICE_MODULE_NAME);
    if (!temp)
        return LogPythonException("cannot locate service module name");
    serviceModule = PyImport_Import(temp);
    Py_DECREF(temp);
    if (!serviceModule)
        return LogPythonException("cannot import service module");

    // create an instance of the class which implements the service
    temp = PyObject_GetAttrString(module, CX_SERVICE_CLASS_NAME);
    if (!temp)
        return LogPythonException("cannot locate service class name");
    info->cls = PyObject_GetAttr(serviceModule, temp);
    Py_DECREF(temp);
    if (!info->cls)
        return LogPythonException("cannot get class from service module");

    return 0;
}


//-----------------------------------------------------------------------------
// Service_Install()
//   Install the service with the given name.
//-----------------------------------------------------------------------------
static int Service_Install(
    char *programName,                  // name of program being run
    char *name,                         // name of service
    char *configFileName)               // name of configuration file or NULL
{
    PyObject *fullName, *displayName, *formatArgs, *command, *commandArgs;
    char fullPathConfigFileName[PATH_MAX + 1];
    SC_HANDLE managerHandle, serviceHandle;
    SERVICE_DESCRIPTIONA sd;
    udt_ServiceInfo info;

    // set up Python
    if (Service_SetupPython(programName, &info) < 0)
        return -1;

    // determine name and display name to use for the service
    formatArgs = Py_BuildValue("(s)", name);
    if (!formatArgs)
        return LogPythonException("cannot create service name tuple");
    fullName = PyString_Format(info.nameFormat, formatArgs);
    if (!fullName)
        return LogPythonException("cannot create service name");
    displayName = PyString_Format(info.displayNameFormat, formatArgs);
    if (!displayName)
        return LogPythonException("cannot create display name");

    // determine command to use for the service
    command = PyString_FromFormat("\"%s\"", Py_GetProgramFullPath());
    if (!command)
        return LogPythonException("cannot create command");
    if (configFileName) {
        if (!_fullpath(fullPathConfigFileName, configFileName,
                sizeof(fullPathConfigFileName)))
            return LogWin32Error(GetLastError(),
                    "cannot calculate absolute path of config file name");
        commandArgs = PyString_FromFormat(" \"%s\"", fullPathConfigFileName);
        if (!commandArgs)
            return LogPythonException("cannot create command args");
        PyString_Concat(&command, commandArgs);
        if (!command)
            return LogPythonException("cannot append args to command");
    }

    // open up service control manager
    managerHandle = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    if (!managerHandle)
        return LogWin32Error(GetLastError(), "cannot open service manager");

    // create service
    serviceHandle = CreateService(managerHandle, PyString_AS_STRING(fullName),
            PyString_AS_STRING(displayName), SERVICE_ALL_ACCESS,
            SERVICE_WIN32_OWN_PROCESS, info.startType, SERVICE_ERROR_NORMAL,
            PyString_AS_STRING(command), NULL, NULL, NULL, NULL, NULL);
    if (!serviceHandle)
        return LogWin32Error(GetLastError(), "cannot create service");

    // set the description of the service, if one was specified
    if (info.description) {
        sd.lpDescription = PyString_AS_STRING(info.description);
        if (!ChangeServiceConfig2(serviceHandle, SERVICE_CONFIG_DESCRIPTION,
                    &sd))
            return LogWin32Error(GetLastError(),
                    "cannot set service description");
    }

    // if the service is one that should be automatically started, start it
    if (info.startType == SERVICE_AUTO_START) {
        if (!StartService(serviceHandle, 0, NULL))
            return LogWin32Error(GetLastError(), "cannot start service");
    }

    // close the service handles
    CloseServiceHandle(serviceHandle);
    CloseServiceHandle(managerHandle);

    return 0;
}


//-----------------------------------------------------------------------------
// Service_Uninstall()
//   Uninstall the service with the given name.
//-----------------------------------------------------------------------------
static int Service_Uninstall(
    char *programName,                  // name of program being run
    char *name)                         // name of service
{
    SC_HANDLE managerHandle, serviceHandle;
    PyObject *fullName, *formatArgs;
    SERVICE_STATUS statusInfo;
    udt_ServiceInfo info;

    // set up Python
    if (Service_SetupPython(programName, &info) < 0)
        return -1;

    // determine name of the service
    formatArgs = Py_BuildValue("(s)", name);
    if (!formatArgs)
        return LogPythonException("cannot create service name tuple");
    fullName = PyString_Format(info.nameFormat, formatArgs);
    if (!fullName)
        return LogPythonException("cannot create service name");

    // open up service control manager
    managerHandle = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    if (!managerHandle)
        return LogWin32Error(GetLastError(), "cannot open service manager");

    // create service
    serviceHandle = OpenService(managerHandle, PyString_AS_STRING(fullName),
            SERVICE_ALL_ACCESS);
    if (!serviceHandle)
        return LogWin32Error(GetLastError(), "cannot open service");
    ControlService(serviceHandle, SERVICE_CONTROL_STOP, &statusInfo);
    if (!DeleteService(serviceHandle))
        return LogWin32Error(GetLastError(), "cannot delete service");
    CloseServiceHandle(serviceHandle);
    CloseServiceHandle(managerHandle);

    return 0;
}


//-----------------------------------------------------------------------------
// Service_Run()
//   Initialize the service.
//-----------------------------------------------------------------------------
static int Service_Run(
    udt_ServiceInfo *info)              // information about the service
{
    PyObject *temp;

    // create an instance of the class which implements the service
    gInstance = PyObject_CallFunctionObjArgs(info->cls, NULL);
    if (!gInstance)
        return LogPythonException("cannot create instance of service class");

    // initialize the instance implementing the service
    LogMessageV(LOG_LEVEL_DEBUG, "initializing with config file %s",
            gIniFileName);
    temp = PyObject_CallMethod(gInstance, "Initialize", "s", gIniFileName);
    if (!temp)
        return LogPythonException("failed to initialize instance properly");
    Py_DECREF(temp);

    // run the service
    LogMessage(LOG_LEVEL_INFO, "starting up service");
    if (Service_SetStatus(info, SERVICE_RUNNING) < 0)
        return LogWin32Error(GetLastError(), "cannot set service as started");
    temp = PyObject_CallMethod(gInstance, "Run", NULL);
    if (!temp)
        return LogPythonException("exception running service");
    Py_DECREF(temp);
    Py_DECREF(gInstance);
    gInstance = NULL;

    // ensure that the Python interpreter lock is NOT held as otherwise
    // waiting for events will take a considerable period of time!
    PyEval_SaveThread();

    return 0;
}


//-----------------------------------------------------------------------------
// Service_Main()
//   Main routine for the service.
//-----------------------------------------------------------------------------
static void WINAPI Service_Main(
    int argc,				            // number of arguments
    char **argv)			            // argument values
{
    udt_ServiceInfo info;

    if (Service_SetupPython(argv[0], &info) < 0)
        return;

    // register the control function
    LogMessage(LOG_LEVEL_DEBUG, "registering control function");
    gServiceHandle = RegisterServiceCtrlHandlerEx("", Service_Control, &info);
    if (!gServiceHandle) {
        LogWin32Error(GetLastError(),
                "cannot register service control handler");
        return;
    }

    // run the service
    if (Service_Run(&info) < 0) {
        Service_SetStatus(&info, SERVICE_STOPPED);
        return;
    }

    // ensure that the main thread does not terminate before the control
    // thread does, as otherwise the service control mechanism does not
    // understand that the service has already ended
    if (gControlEvent) {
        if (WaitForSingleObject(gControlEvent, INFINITE) != WAIT_OBJECT_0)
            LogWin32Error(GetLastError(),
                    "cannot wait for control thread to terminate");

    // otherwise, the service terminated normally by some other means
    } else {
        LogMessage(LOG_LEVEL_INFO, "stopping service (internally)");
        Service_SetStatus(&info, SERVICE_STOPPED);
    }
}


//-----------------------------------------------------------------------------
// main()
//   Main routine for the service.
//-----------------------------------------------------------------------------
int main(int argc, char **argv)
{
    char *configFileName = NULL;

    SERVICE_TABLE_ENTRY table[] = {
        { "", (LPSERVICE_MAIN_FUNCTION) Service_Main },
        { NULL, NULL }
    };

    gIniFileName[0] = '\0';
    if (argc > 1) {
        if (stricmp(argv[1], "--install") == 0) {
            if (argc == 2) {
                fprintf(stderr, "Incorrect number of parameters.\n");
                fprintf(stderr, "%s --install <NAME> [<CONFIGFILE>]", argv[0]);
                return 1;
            }
            if (argc > 3)
                configFileName = argv[3];
            if (Service_Install(argv[0], argv[2], configFileName) < 0) {
                fprintf(stderr, "Service not installed. ");
                fprintf(stderr, "See log file for details.");
                return 1;
            }
            fprintf(stderr, "Service installed.");
            return 0;
        } else if (stricmp(argv[1], "--uninstall") == 0) {
            if (argc == 2) {
                fprintf(stderr, "Incorrect number of parameters.\n");
                fprintf(stderr, "%s --uninstall <NAME>", argv[0]);
                return 1;
            }
            if (Service_Uninstall(argv[0], argv[2]) < 0) {
                fprintf(stderr, "Service not installed. ");
                fprintf(stderr, "See log file for details.");
                return 1;
            }
            fprintf(stderr, "Service uninstalled.");
            return 0;
        }
        strcpy(gIniFileName, argv[1]);
    }


    return StartServiceCtrlDispatcher(table);
}

