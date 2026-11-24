import platform

from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.micropython.mp_front import (
    GenericBareMetalMicroPythonConfigPage,
    GenericBareMetalMicroPythonProxy,
    LocalMicroPythonConfigPage,
    LocalMicroPythonProxy,
    SshMicroPythonConfigPage,
    SshMicroPythonProxy,
    add_micropython_backend,
)

_DEVICE_BACKEND = "GenericMicroPython"
_RETIRED_DEVICE_BACKENDS = ("ESP32", "ESP8266", "RP2040", "RPiPico")


def load_plugin():
    add_micropython_backend(
        _DEVICE_BACKEND,
        GenericBareMetalMicroPythonProxy,
        tr("Device MicroPython"),
        GenericBareMetalMicroPythonConfigPage,
        sort_key="31",
    )

    get_workbench().set_default("serial.last_backend_per_vid_pid", {})
    _migrate_device_backends(_DEVICE_BACKEND, _RETIRED_DEVICE_BACKENDS)

    if platform.system() in ("Linux", "Darwin"):
        add_micropython_backend(
            "LocalMicroPython",
            LocalMicroPythonProxy,
            tr("Local MicroPython"),
            LocalMicroPythonConfigPage,
            bare_metal=False,
            local_rtc=False,
            sort_key="21",
        )
        get_workbench().set_default("LocalMicroPython.executable", "micropython")

    add_micropython_backend(
        "SshMicroPython",
        SshMicroPythonProxy,
        tr("Remote MicroPython (SSH)"),
        SshMicroPythonConfigPage,
        bare_metal=False,
        local_rtc=False,
        sort_key="22",
    )
    get_workbench().set_default("SshMicroPython.executable", "micropython")
    get_workbench().set_default("SshMicroPython.cwd", None)
    get_workbench().set_default("SshMicroPython.host", "")
    get_workbench().set_default("SshMicroPython.port", "22")
    get_workbench().set_default("SshMicroPython.user", "")
    get_workbench().set_default("SshMicroPython.auth_method", "password")
    get_workbench().set_default("SshMicroPython.make_uploaded_shebang_scripts_executable", True)

    get_workbench().set_default("esptool.show_advanced_options", False)


def _migrate_device_backends(target_backend, retired_backends):
    workbench = get_workbench()
    selected = workbench.get_option("run.backend_name")
    if selected in retired_backends:
        for name in workbench.get_options_snapshot():
            if not name.startswith(target_backend + "."):
                continue
            option = name.split(".", 1)[1]
            if option == "last_configurations":
                continue
            old_name = f"{selected}.{option}"
            # The config parser needs a string default to read saved passwords verbatim.
            if option == "webrepl_password":
                workbench.set_default(old_name, "")
            if workbench.has_option(old_name):
                value = workbench.get_option(old_name)
                if (
                    option == "write_block_size"
                    and selected in ("RP2040", "RPiPico")
                    and value == 64
                ):
                    value = 256
                workbench.set_option(name, value)
        workbench.set_option("run.backend_name", target_backend)

    history_key = f"{target_backend}.last_configurations"
    history = list(workbench.get_option(history_key))
    for backend in retired_backends:
        legacy_key = f"{backend}.last_configurations"
        legacy_history = workbench.get_option(legacy_key, [])
        if not legacy_history:
            continue
        for previous in legacy_history:
            converted = {
                name.replace(backend + ".", target_backend + ".", 1): value
                for name, value in previous.items()
            }
            converted["run.backend_name"] = target_backend
            if converted not in history:
                history.append(converted)
        workbench.set_option(history_key, history)
        workbench.set_option(legacy_key, [])

    port_history_key = "serial.last_backend_per_vid_pid"
    port_history = workbench.get_option(port_history_key)
    if any(backend in retired_backends for backend in port_history.values()):
        workbench.set_option(
            port_history_key,
            {
                ids: target_backend if backend in retired_backends else backend
                for ids, backend in port_history.items()
            },
        )
