# Thonny Codebase Map


This is a navigation guide for the repository. The project has two important layers:

- The repository root contains documentation, build/release tooling, packaging assets, data files, and the Python application package.
- `thonny/` is the importable application package. Its `plugins/` directory supplies most optional UI, language-server, debugger, backend, and hardware support.

## Start Here

- Launch path: [`thonny/__main__.py`](thonny/__main__.py) -> [`thonny/main.py`](thonny/main.py) -> `Workbench` in [`thonny/workbench.py`](thonny/workbench.py).
- UI composition: `Workbench` creates the shell, editor notebook, menus, configuration, themes, and plugins.
- Execution path: `Runner` and proxy classes in [`thonny/running.py`](thonny/running.py) start or connect to a backend; [`thonny/backend.py`](thonny/backend.py) implements the backend command loop.
- Shared protocol: [`thonny/common.py`](thonny/common.py) defines command, response, event, debugging, path, and serialization structures used on both sides of the frontend/backend boundary.
- Main user surfaces: [`thonny/editors.py`](thonny/editors.py), [`thonny/shell.py`](thonny/shell.py), [`thonny/codeview.py`](thonny/codeview.py), and [`thonny/base_file_browser.py`](thonny/base_file_browser.py).
- Extension point: plugins are discovered and loaded by `Workbench._load_plugins`; a plugin normally exposes `load_plugin()` and registers commands, views, hooks, analyzers, themes, or backends.

## Repository Root

| Subsection | Contents and purpose |
| --- | --- |
| [`README.rst`](README.rst), [`CHANGELOG.rst`](CHANGELOG.rst), [`CONTRIBUTING.rst`](CONTRIBUTING.rst), [`CREDITS.rst`](CREDITS.rst), [`LICENSE.txt`](LICENSE.txt) | User/project documentation, release history, contributor guidance, credits, and licensing. |
| [`pyproject.toml`](pyproject.toml), [`requirements.txt`](requirements.txt), [`uv.lock`](uv.lock), [`mypy.ini`](mypy.ini), [`.pylintrc`](.pylintrc) | Python project metadata, dependencies, locked development environment, type-checking configuration, and lint configuration. |
| [`build.sh`](build.sh), [`build.bat`](build.bat), [`check.sh`](check.sh), [`format-and-check.sh`](format-and-check.sh), [`copy_libs.sh`](copy_libs.sh) | Cross-platform build, validation, formatting, and dependency-copying scripts. |
| [`packaging/`](packaging/) | Platform-specific installers, bundle metadata, portable/shared installation assets, icons, and package requirements for Linux, macOS, and Windows. |
| [`docs/`](docs/) | Small documentation and translation-support assets; currently includes `translate.md`. |
| [`data/`](data/) | Firmware/device variant mappings, MicroPython/CircuitPython metadata, PyPI summaries, and scripts for updating those generated or semi-generated data files. |
| [`misc/`](misc/) | Developer experiments, UI probes, debugging utilities, protocol experiments, and one-off investigation scripts. It is useful for historical context but is not the normal runtime path. |
| [`exa/`](exa/) | Auxiliary or experimental project material. Inspect locally before treating it as production code. |
| [`codeium_proto/`](codeium_proto/) | Protocol/support material for Codeium integration. |
| [`licenses/`](licenses/) | Third-party license notices and bundled dependency licensing information. |
| [`thonny/`](thonny/) | The application package described below. |

## Application Package: `thonny/`

### Bootstrap and global services

| File | Attributes and functionality |
| --- | --- |
| [`thonny/__init__.py`](thonny/__init__.py) | Global application state and lazy caches: version, user/configuration directories, IPC path, debug mode, workbench, and runner. Also adds `vendored_libs` to `sys.path` and exposes shared accessors. |
| [`thonny/__main__.py`](thonny/__main__.py) | Module entry point; delegates execution to `main.run()`. |
| [`thonny/main.py`](thonny/main.py) | Parses command-line options, prepares user data/logging, handles first-run and single-instance delegation, creates `Workbench`, and shuts down the runner. |
| [`thonny/defaults.ini`](thonny/defaults.ini) | Default configuration overrides read by `ConfigurationManager`; settings are grouped by configuration section. |
| [`thonny/VERSION`](thonny/VERSION) | Installed/application version string. |
| [`thonny/languages.py`](thonny/languages.py) | Supported language metadata, gettext translation selection, translation lookup (`tr`), and locale-specific button padding. |
| [`thonny/config.py`](thonny/config.py) | `ConfigurationManager`: INI persistence, typed defaults, Tk variable binding, snapshots, corruption recovery, and atomic saves. |
| [`thonny/first_run.py`](thonny/first_run.py) | First-launch configuration window and initial setup flow. |
| [`thonny/misc_utils.py`](thonny/misc_utils.py) | Cross-platform paths, URIs, environment/platform checks, subprocess helpers, clipboard and filesystem utilities. |

### Frontend orchestration and communication

| File | Attributes and functionality |
| --- | --- |
| [`thonny/workbench.py`](thonny/workbench.py) | Central `tk.Tk` application object. Owns views, menus, commands, hooks, themes, configuration, language servers, backend registrations, plugin loading, event dispatch, fonts, and window lifecycle. |
| [`thonny/running.py`](thonny/running.py) | Frontend execution coordinator. `Runner` manages lifecycle/state, commands, interrupts, restart, output events, and debugger communication; `BackendProxy` subclasses represent subprocess, SSH, or other transports. |
| [`thonny/common.py`](thonny/common.py) | Frontend/backend shared contract: records and dataclasses, command/response/event classes, debugging metadata, path helpers, message serialization/parsing, constants, and protocol status values. |
| [`thonny/backend.py`](thonny/backend.py) | Backend-side command loop. `BaseBackend` reads serialized commands, handles input/EOF/interrupts, executes operations, sends output/events, and reports connection or internal errors. |
| [`thonny/lsp_proxy.py`](thonny/lsp_proxy.py) | Language Server Protocol process/connection proxy and request/notification transport used by editor intelligence features. |
| [`thonny/lsp_types.py`](thonny/lsp_types.py) | Typed LSP structures: initialization, capabilities, documents, positions/ranges, diagnostics, completion, signatures, symbols, and responses. |
| [`thonny/program_analysis.py`](thonny/program_analysis.py) | Program-analyzer abstraction and registration-facing functionality for diagnostics, analysis results, and editor tooling. |
| [`thonny/assistance.py`](thonny/assistance.py) | Assistant framework and assistant registration/dispatch used by help or guided tooling plugins. |

### Editor, shell, and document interaction

| File | Attributes and functionality |
| --- | --- |
| [`thonny/editors.py`](thonny/editors.py) | Editor document lifecycle: local/remote/untitled URIs, file loading/saving, modified state, language-server synchronization, breakpoints, notebook tabs, and editor commands. |
| [`thonny/codeview.py`](thonny/codeview.py) | Reusable syntax-aware text widget/frame, tags, cursor/selection behavior, line numbers, margins, file types, and editor presentation. |
| [`thonny/shell.py`](thonny/shell.py) | Interactive shell view and shell text widget. Handles prompt/input editing, program output, ANSI/control sequences, object links, command history, plotter visibility, and shell menus. |
| [`thonny/terminal.py`](thonny/terminal.py) | Terminal widget/process integration for running commands in an external or embedded terminal surface. |
| [`thonny/tktextext.py`](thonny/tktextext.py) | Tk text-widget extensions, index/line utilities, text frames, and configurable text behavior shared by code and shell views. |
| [`thonny/base_file_browser.py`](thonny/base_file_browser.py) | File browser model and dialogs, filesystem navigation, backend file operations, path selection, and file/project actions. |
| [`thonny/export.py`](thonny/export.py) | Exporting editor/project content and related file-selection workflow. |
| [`thonny/editor_helpers.py`](thonny/editor_helpers.py) | Small editor/document helpers used by editor features and plugins. |
| [`thonny/custom_notebook.py`](thonny/custom_notebook.py) | Notebook/tab container behavior, page records, tab movement/closing, and notebook events. |
| [`thonny/dnd.py`](thonny/dnd.py) | Drag-and-drop support for Tk widgets and file interactions. |

### UI framework and utility modules

| File | Attributes and functionality |
| --- | --- |
| [`thonny/ui_utils.py`](thonny/ui_utils.py) | Shared Tk widgets, dialogs, styling, themes, keyboard sequences, tooltips, platform UI behavior, and layout helpers. |
| [`thonny/config_ui.py`](thonny/config_ui.py) | Configuration dialog framework and reusable configuration page controls. |
| [`thonny/plugins/theme_and_font_config_page.py`](thonny/plugins/theme_and_font_config_page.py) | Theme/font configuration UI support. |
| [`thonny/gridtable.py`](thonny/gridtable.py) | Grid-based table widget and cell/row/column management. |
| [`thonny/workdlg.py`](thonny/workdlg.py) | Progress/work dialog UI and status reporting. |
| [`thonny/venv_dialog.py`](thonny/venv_dialog.py) | Virtual-environment selection/creation dialog support. |
| [`thonny/udisks.py`](thonny/udisks.py) | Linux UDisks/DBus removable-device integration. [`thonny/dbus/`](thonny/dbus/) contains the DBus XML interfaces used by it. |
| [`thonny/memory.py`](thonny/memory.py) | Memory/value inspection support and data structures used by object/heap inspection features. |

### Parsing, syntax, and source analysis

| File | Attributes and functionality |
| --- | --- |
| [`thonny/ast_utils.py`](thonny/ast_utils.py) | AST traversal and source-structure helpers. |
| [`thonny/roughparse.py`](thonny/roughparse.py) | Lightweight parsing of incomplete Python source for shell/editor indentation and command decisions. |
| [`thonny/token_utils.py`](thonny/token_utils.py) | Tokenization helpers and token-based source inspection. |
| [`thonny/rst_utils.py`](thonny/rst_utils.py) | reStructuredText parsing/rendering helpers for documentation/help content. |

## Plugins: `thonny/plugins/`

Plugins are loaded dynamically by [`thonny/workbench.py`](thonny/workbench.py). Most plugin modules register behavior in `load_plugin()` rather than being called directly. They may add commands, views, event handlers, configuration pages, syntax themes, analyzers, language servers, or backend implementations.

### Core editor and UI plugins

| Area | Modules | Functionality |
| --- | --- | --- |
| Editing commands | `common_editing_commands.py`, `commenting_indenting.py`, `find_replace.py`, `cells.py`, `shell_macro.py`, `paren_matcher.py` | Editing actions, comments/indentation, search/replace, cell execution, shell macros, and bracket matching. |
| Editor intelligence | `autocomplete.py`, `calltip.py`, `goto_definition.py`, `outline.py`, `highlight_names.py`, `coloring.py`, `problems.py`, `basedpyright.py`, `ruff.py`, `mypy/`, `pylint/` | Completion, signatures, navigation, symbols, highlighting, diagnostics, and static-analysis integrations. |
| Debugging and inspection | `debugger.py`, `statement_boxes.py`, `locals_marker.py`, `variables.py`, `heap.py`, `object_inspector.py`, `ast_view.py`, `event_view.py` | Debugger controls, execution markers, locals/variables, heap/object inspection, AST display, and event tracing. |
| Files and project workflow | `files.py`, `thonny_folders.py`, `pip_gui.py`, `uv/`, `venv_dialog` integration | File commands, project folders, package installation, UV/environment workflows, and package metadata views. |
| Help/content | `about.py`, `help/`, `notes.py`, `todo_view.py`, `pythontutor.py`, `birdseye_frontend.py` | About/help views, notes and TODOs, program visualizers, and external analysis integrations. |
| Themes and appearance | `base_ui_themes.py`, `clean_ui_themes.py`, `tidy_ui_themes.py`, `base_syntax_themes.py`, `tomorrow_syntax_theme.py` | Built-in UI and syntax theme definitions and theme registration. |
| AI/assistant integrations | `chat.py`, `github_copilot.py`, `openai.py`, `ollama.py`, `codeium.py.txt` | Optional assistant/chat integrations and related configuration or protocol material. |
| System surfaces | `system_shell/`, `terminal_config_page.py`, `dock_user_windows_frontend.py`, `event_logging.py`, `replayer.py`, `printing/` | System terminal, terminal settings, user-window docking, event logging/replay, and printing support. |

### Backend and execution plugins

| Subsection | Contents and functionality |
| --- | --- |
| [`thonny/plugins/backend/`](thonny/plugins/backend/) | Backend extensions for Birdseye, docked user windows, Flask, Matplotlib, and Pygame Zero. These are loaded into the execution process when applicable. |
| [`thonny/plugins/cpython_frontend/`](thonny/plugins/cpython_frontend/) | CPython frontend registration and the `cp_front.py` frontend integration. |
| [`thonny/plugins/cpython_backend/`](thonny/plugins/cpython_backend/) | CPython backend implementation, launcher, tracing/debugging support, and backend-side execution behavior. |
| `basedpyright.py`, `ruff.py`, `mypy/`, `pylint/` | Language tooling integrations. They configure subprocess/LSP clients or diagnostics and expose results to the editor/problems UI. |

### Hardware and remote-device plugins

| Subsection | Contents and functionality |
| --- | --- |
| `micropython/` | MicroPython frontend/backend, REPL communication, project managers, firmware flashing dialogs, serial/miniterm support, and device variants. |
| `circuitpython/` | CircuitPython frontend/backend, device definitions, and board communication. |
| `rpi_pico/`, `rp2040/` | Raspberry Pi Pico/RP2040 workflows, firmware/device support, and flashing or board-specific UI. |
| `microbit/`, `calliope/` | micro:bit and Calliope device workflows and firmware/programming support. |
| `esp/` | ESP-family device support and flashing integration. |
| `ev3/`, `pi/`, `prime_inventor/` | LEGO EV3, Raspberry Pi, and Prime Inventor device/backends or project workflows. |
| `simplified_micropython/` | Simplified MicroPython typeshed and associated editor/device support. |
| `cpython_ssh/` | Remote CPython over SSH backend/frontend integration. |

## Localization and Resources

| Subsection | Contents and purpose |
| --- | --- |
| [`thonny/locale/`](thonny/locale/) | Translation source/catalog files and per-language locale directories. `languages.py` selects a language and gettext loads `LC_MESSAGES/thonny.mo`. Update scripts maintain the catalogs. |
| [`thonny/res/`](thonny/res/) | Runtime icons, toolbar images, disabled image variants, application icons, and small platform helper assets such as `PrintLnkTarget.vbs`. |
| [`thonny/dbus/`](thonny/dbus/) | DBus XML interface descriptions for Linux removable-device integration. |
| [`thonny/vendored_libs/`](thonny/vendored_libs/) | Bundled third-party Python libraries and device/typeshed support that Thonny puts on its import path. |
| [`thonny/thonny/`](thonny/thonny/) | Additional bundled typeshed/vendor data: MicroPython, simplified MicroPython, MicroPython Unix, and CircuitPython type information plus serial support. |

## Tests

- [`thonny/test/`](thonny/test/) is the test package. It currently contains [`test_common.py`](thonny/test/test_common.py), plugin-focused tests under [`test/plugins/`](thonny/test/plugins/), and [`what_to_test.txt`](thonny/test/what_to_test.txt), which records testing scope/ideas.
- The tests are relatively small compared with the application. When changing protocol, configuration, editor, runner, or plugin behavior, also use the relevant narrow runtime or static-check command described by the repository scripts.

## Useful Navigation Recipes

- To understand startup: [`thonny/main.py`](thonny/main.py), then `Workbench.__init__` and `_load_plugins` in [`thonny/workbench.py`](thonny/workbench.py).
- To understand “Run”: [`thonny/running.py`](thonny/running.py) -> a `BackendProxy` -> [`thonny/backend.py`](thonny/backend.py) -> a backend plugin such as [`thonny/plugins/cpython_backend/`](thonny/plugins/cpython_backend/).
- To understand editor typing/diagnostics: [`thonny/editors.py`](thonny/editors.py) -> [`thonny/codeview.py`](thonny/codeview.py) -> [`thonny/lsp_proxy.py`](thonny/lsp_proxy.py) and editor-analysis plugins.
- To understand shell output and inspection: [`thonny/shell.py`](thonny/shell.py) -> [`thonny/common.py`](thonny/common.py) event types -> `Runner` event dispatch in [`thonny/running.py`](thonny/running.py).
- To add a feature: find a neighboring plugin with the same kind of command/view, implement registration in a plugin module, and let `Workbench` load it.
- To trace a configuration option: search for `set_default("section.option", ...)`, then follow `get_option`, `get_variable`, and `ConfigurationManager.save()` in [`thonny/config.py`](thonny/config.py).



