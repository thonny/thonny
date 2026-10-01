# Thonny repository map

## What this repository is

This is the source tree for **Thonny**, a cross-platform Python IDE designed for learning.  Its core is a Tkinter desktop application, but it is deliberately extensible: the frontend is a workbench which discovers plug-ins, and program execution/debugging happens in a separately managed backend process.  The tree also includes device-specific MicroPython support, translations, bundled type stubs, and release packaging for Linux, macOS, and Windows.

The project metadata in `pyproject.toml` identifies the in-development release as `6.0.0.dev1`, uses `uv_build`, requires Python 3.11+, and exposes the `thonny` GUI command.

## Top-level layout

| Path | Role |
| --- | --- |
| `thonny/` | The application package and the primary source directory. See the detailed map below. |
| `data/` | Versioned device/firmware catalogues and scripts which refresh them. Includes MicroPython/CircuitPython board variants, firmware mappings, and PyPI package summaries. |
| `docs/` | Contributor-facing documentation such as translation guidance. |
| `packaging/` | OS-specific build and installer assets: desktop integration for Linux, app/DMG scripts for macOS, and installer/launcher material for Windows. |
| `licenses/` | Third-party license notices. |
| `misc/` | Development experiments and maintenance helpers, including MicroPython and pylint utilities. |
| `codeium_proto/` | Protocol Buffer sources plus generation configuration for the Codeium-related `exa` package. |
| `exa/` | Generated protobuf and gRPC Python modules. Treat as generated integration code, not normal IDE core code. |
| `pyproject.toml`, `uv.lock`, `requirements.txt` | Build, dependency, developer-tool, and lockfile configuration. |
| `build.*`, `check.sh`, `format-and-check.sh` | Convenience scripts for building and quality checks. |
| `README.rst`, `CONTRIBUTING.rst`, `CHANGELOG.rst`, `CREDITS.rst` | Project orientation, contribution rules, release history, and acknowledgements. |

## Startup and high-level runtime

```text
python -m thonny / installed `thonny` command
    -> thonny/__main__.py
    -> thonny.main.run()
       -> command-line/profile validation, welcome flow, logging, DPI setup
       -> optional single-instance IPC delegation
       -> thonny.workbench.Workbench (Tk application)
          -> configuration, language/theme/window/layout setup
          -> built-in + third-party plugin discovery and registration
          -> editor, shell, menus, views, and event hub
          -> thonny.running.Runner
             -> BackendProxy launches/communicates with selected backend
                -> local CPython, SSH CPython, MicroPython, etc.
```

`thonny/__init__.py` supplies process-wide services used on both sides of this boundary: versioning, profile/user-directory resolution, IPC location, logging/debug configuration, the vendored-library path, and accessors for the active `Workbench` and `Runner`.

`main.py` is intentionally thin. It parses `--profile`, positional files, and `--replayer`; prepares the per-user directory and logging; shows the first-run experience when needed; delegates to an already-running instance when configured; then enters the workbench Tk main loop. On exit it asks the runner to tear down its backend.

## `thonny/`: core package

### Application shell and UI composition

| Module | Primary responsibility |
| --- | --- |
| `workbench.py` | The central `tk.Tk` subclass and application service hub. Owns configuration defaults, menus, commands, views, layout notebooks, themes/fonts, virtual-event dispatch, plugin discovery, secrets, IPC server behavior, and language-server lifecycle. Start here when changing application-wide behavior. |
| `editors.py` | Editor tabs and `EditorNotebook`; file opening/saving, document state, breakpoints, recent/previous file restoration, and editor-oriented actions. |
| `codeview.py` | Syntax-aware editable code view, encoding/newline handling, and Python-aware Return behavior. |
| `shell.py` | Interactive Shell view and its text widgets; presents output/input received through the runner and includes plotter support. |
| `ui_utils.py` | Shared Tk widgets, dialogs, style/theme helpers, key-sequence handling, platform UI behavior, and layout utilities. Large, widely reused UI utility module. |
| `custom_notebook.py` | Reusable tabbed-notebook implementation used to build the editor/view layout. |
| `tktextext.py` | Enhanced Tk text widgets, including editing, logging, selection, and text-frame behavior on which editor and shell views build. |
| `base_file_browser.py` | Reusable tree-based browser and filesystem operations, used by file-oriented views. |
| `config_ui.py`, `workdlg.py`, `gridtable.py`, `dnd.py` | Configuration-page controls, background work dialogs, table/grid UI, and drag-and-drop support. |
| `first_run.py` | First-launch configuration window. |
| `terminal.py` | Opens external system terminals/shells using platform-specific implementations. |

### Execution, debugging, and frontend/backend protocol

| Module | Primary responsibility |
| --- | --- |
| `running.py` | Frontend execution coordinator. `Runner` starts/stops/restarts backend processes, queues commands, manages interruption and state, turns backend messages into workbench events, and defines backend proxy abstractions. |
| `backend.py` | Backend-side framework. `BaseBackend` reads serialized frontend commands, runs a main loop, dispatches handlers, reports output/progress, and sends responses/events. |
| `common.py` | Shared protocol and utility layer. Defines command/response/event record classes (`ToplevelCommand`, `DebuggerCommand`, `BackendEvent`, etc.), serialization/parsing, path functions, distribution inspection, and platform helpers. This is the most important frontend/backend contract. |
| `plugins/cpython_backend/` | Local CPython backend: `cp_launcher.py` starts it, `cp_back.py` implements evaluation/run/debugger commands, and `cp_tracers.py` implements execution tracers used for debugging. |
| `plugins/cpython_frontend/` | Registers and configures the local CPython `SubprocessProxy`. |
| `plugins/cpython_ssh/` | SSH-based CPython proxy, backend, transfer, and configuration support. Optional `paramiko` dependency. |

### Editing, analysis, and language services

| Module | Primary responsibility |
| --- | --- |
| `lsp_proxy.py` | Generic JSON-RPC/LSP process proxy, request/response conversion, and language-server lifecycle mechanics. |
| `lsp_types.py` | Generated/structured Python definitions for LSP messages and capabilities. Large type-model file; edit only when updating the protocol model. |
| `ast_utils.py`, `roughparse.py`, `token_utils.py` | Python AST/token/partial-parse helpers used for editor semantics and robust handling of incomplete source. |
| `editor_helpers.py` | Smaller editor operations shared by plugins and core UI. |
| `plugins/basedpyright.py`, `plugins/ruff.py` | LSP providers for diagnostics, definitions, completions, and/or checks. |
| `plugins/autocomplete.py`, `calltip.py`, `goto_definition.py`, `problems.py` | Completion UI, signature help, go-to-definition, and diagnostic presentation. |
| `plugins/coloring.py`, `paren_matcher.py`, `highlight_names.py`, `locals_marker.py`, `outline.py`, `ast_view.py` | Syntax/highlighting and structural code-navigation/inspection features. |

### User settings, localization, and shared support

| Module or directory | Primary responsibility |
| --- | --- |
| `config.py` | INI-backed `ConfigurationManager`, persistence, defaults, and safe loading. |
| `defaults.ini` | Shipped baseline configuration values. |
| `languages.py` | Translation lookup and active-language selection. |
| `locale/` | gettext translations (`.po` sources, compiled `.mo` files, and translator metadata) for roughly 45 locales; includes update scripts. |
| `misc_utils.py` | Cross-platform and filesystem helpers, URI handling, process command construction, platform detection, and general application utilities. |
| `assistance.py` | Assistant/chat abstractions, chat data objects, assistant registration, and source-file context collection. |
| `memory.py` | Variable/object memory frames used by inspection views. |
| `export.py`, `rst_utils.py` | Content export and reStructuredText rendering helpers. |
| `udisks.py`, `dbus/` | Linux removable-media/device discovery via UDisks/DBus interface definitions. |

### Resources, tests, and third-party source

| Directory | Contents |
| --- | --- |
| `res/` | Application icons and UI image assets, including state/theme variants. |
| `test/` | Unit/plugin tests and test inventory. The present suite is comparatively small; test additions commonly live beside the relevant plugin under `thonny/test/plugins/`. |
| `vendored_libs/` | Vendored dependencies and static typing assets, notably pyserial and MicroPython/CircuitPython typesheds. `thonny.__init__` places this directory early on `sys.path`; avoid treating it as ordinary first-party code. |

## Plugin model

At startup, `Workbench._load_plugins()` enumerates `thonny.plugins`, imports modules/packages that expose `load_plugin()`, sorts them by optional `load_order_key`, and calls that hook. It then performs the same discovery under the `thonnycontrib` namespace after adding the user plug-in path. A plugin generally contributes one or more of the following through workbench registration APIs:

- commands and menus (`add_command`)
- dockable views (`add_view`)
- configuration pages
- themes/syntax themes
- language-server proxies
- execution backend specifications/proxies
- handlers for workbench and backend events

This makes `load_plugin()` the usual first place to read for feature wiring, and the rest of the module/package the place to follow the feature implementation.

### Plugin families

| Family | Locations | What it adds |
| --- | --- | --- |
| Essential IDE workflows | `files.py`, `find_replace.py`, `common_editing_commands.py`, `commenting_indenting.py`, `printing/`, `thonny_folders.py`, `notes.py`, `todo_view.py` | Filesystem view, search/replace, editing commands, printing, folders, notes, and task display. |
| Run/debug/inspection | `debugger.py`, `replayer.py`, `variables.py`, `heap.py`, `object_inspector.py`, `event_view.py`, `event_logging.py` | Debug controls, recorded-session replay, variable/object/heap display, and event inspection/logging. |
| Editor intelligence | `autocomplete.py`, `calltip.py`, `goto_definition.py`, `basedpyright.py`, `ruff.py`, `mypy/`, `pylint/` | Completion, calls, navigation, LSP integration, and static analysis. |
| UI and preferences | `base_ui_themes.py`, `clean_ui_themes.py`, `tidy_ui_themes.py`, `base_syntax_themes.py`, `tomorrow_syntax_theme.py`, and `*_config_page.py` | Built-in look-and-feel options, syntax palettes, and preferences pages. |
| Help and learning | `help/`, `pythontutor.py`, `birdseye_frontend.py`, `pgzero_frontend.py`, `chat.py`, `openai.py`, `github_copilot.py`, `ollama.py` | Help, educational visualizers, game/tool integrations, and optional assistant providers. Some modules may be present without a `load_plugin()` hook and are used by other plugins or are experimental. |
| Backend augmentation | `plugins/backend/` | Backend-side hooks for Birdseye, matplotlib, Flask, pgzero, and docking user windows. Their frontend counterparts register the UI behavior. |
| Environment/package management | `pip_gui.py`, `uv/`, `system_shell/`, `terminal_config_page.py` | Package manager UI, uv-based CPython environment, and access to an external shell. |

## Runtime and device backends

The selected backend is a runtime-specific implementation behind the protocol in `common.py` and `backend.py`. The frontend `Runner` owns a `BackendProxy`; a proxy launches its backend and carries serialized commands/responses over standard streams or a remote transport.

| Runtime target | Frontend/proxy | Backend implementation |
| --- | --- | --- |
| Local CPython | `plugins/cpython_frontend/cp_front.py` | `plugins/cpython_backend/cp_back.py` plus `cp_tracers.py` |
| CPython over SSH | `plugins/cpython_ssh/cps_front.py` | `plugins/cpython_ssh/cps_back.py` |
| Generic/local/SSH MicroPython | `plugins/micropython/mp_front.py` | `mp_back.py`, `os_mp_backend.py`, `bare_metal_backend.py` |
| CircuitPython | `plugins/circuitpython/cirpy_front.py` | `cirpy_back.py` |
| ESP8266/ESP32 | `plugins/esp/` | `esp8266_back.py`, `esp32_back.py` |
| BBC micro:bit / Calliope mini | `plugins/microbit/`, `plugins/calliope/` | Their `*_back.py` subclasses of simplified MicroPython support |
| Raspberry Pi Pico / RP2040 / Prime Inventor | `plugins/rpi_pico/`, `plugins/rp2040/`, `plugins/prime_inventor/` | Their respective `*_back.py` subclasses |
| LEGO EV3 | `plugins/ev3/` | `ev3_back.py`, using SSH Unix MicroPython support |

The `micropython/` package is the shared foundation for most board packages. Its front end provides backend selection/configuration and serial/SSH proxies; its backend provides REPL interaction, file transfer, flashing workflows, and generic bare-metal/Unix variants. Firmware and board metadata is kept in the top-level `data/` directory, rather than hard-coded solely in these packages.

## Where to make common changes

| Change needed | Best starting point |
| --- | --- |
| Application startup, profiles, first-run, or single-instance behavior | `thonny/main.py`, then `thonny/__init__.py` |
| New global menu command, view, event, theme, or preference | `thonny/workbench.py` APIs; normally implement as a plugin with `load_plugin()` |
| Editor file/tab behavior | `thonny/editors.py` and `thonny/codeview.py` |
| Shell behavior or frontend execution state | `thonny/shell.py` and `thonny/running.py` |
| Backend command/event protocol | `thonny/common.py` and `thonny/backend.py`; update both sides together |
| Local CPython execution/debugging | `plugins/cpython_backend/cp_back.py` and `cp_tracers.py` |
| Language intelligence or diagnostics | `lsp_proxy.py`, relevant `lsp_types.py` models, then provider/UI plugins |
| A new board or MicroPython runtime | Start from `plugins/micropython/`, then add a small board package and metadata in `data/` |
| Translations | `thonny/languages.py`, `thonny/locale/`, and `docs/translate.md` |
| Packaging/release changes | Corresponding `packaging/linux`, `packaging/mac`, or `packaging/windows` tree |

## Practical reading order for a new contributor

1. Read `README.rst`, `CONTRIBUTING.rst`, and `pyproject.toml` for project intent, tooling, and dependencies.
2. Trace `thonny/__main__.py` -> `thonny/main.py` -> `thonny/workbench.py` to understand startup and the frontend composition root.
3. Read `thonny/common.py`, `thonny/running.py`, and `thonny/backend.py` together to understand the process boundary before modifying execution behavior.
4. Find the feature’s `load_plugin()` hook under `thonny/plugins/`, then follow its registered commands, views, and event bindings.
5. For hardware work, read `plugins/micropython/__init__.py`, `mp_front.py`, `mp_back.py`, and the closest board-specific package before introducing a new variant.

## Boundary notes

- `workbench.py`, `ui_utils.py`, `running.py`, and `shell.py` are high-centrality modules: a change there can affect many unrelated features.
- The frontend/backend records in `common.py` cross a serialized process boundary. Preserve backward-compatible fields and ensure a protocol change is understood by every relevant proxy/backend.
- `vendored_libs/`, generated files under `exa/`, and compiled translation `.mo` files should generally be updated through their source/update workflow rather than manually edited.
- Platform-specific details are intentionally localized in `terminal.py`, `misc_utils.py`, `udisks.py`, device plugins, and `packaging/`; avoid spreading platform conditionals into feature code when one of these layers is appropriate.
