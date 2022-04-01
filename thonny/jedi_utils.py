"""
Utils to handle different jedi versions
"""
from logging import getLogger
from typing import Dict, List, Optional

import jedi.api.classes

try:
    # Since 0.17
    from jedi.api.classes import ParamName
except ImportError:
    try:
        # Since 0.15
        from jedi.api.classes import ParamDefinition as ParamName
    except ImportError:
        from jedi.api.classes import Definition as ParamName

try:
    # Since 0.16
    from jedi.api.classes import BaseSignature
except ImportError:
    try:
        # Since 0.15
        from jedi.api.classes import Signature as BaseSignature
    except ImportError:
        from jedi.api.classes import Definition as BaseSignature

from thonny.common import CompletionInfo, NameReference, SignatureInfo, SignatureParameter

logger = getLogger(__name__)

_last_jedi_completions: Optional[List[jedi.api.classes.Completion]] = None


def get_script_completions(
    source: str, row: int, column: int, filename: str, sys_path=None
) -> List[CompletionInfo]:
    _check_patch_jedi_typesheds(sys_path)
    global _last_jedi_completions
    try:
        script = _create_script(source, row, column, filename, sys_path)

        if _using_older_api():
            completions = script.completions()
        else:
            completions = script.complete(line=row, column=column, fuzzy=False)
    except Exception:
        logger.exception("Jedi error")
        completions = []

    completions = _filter_completions(completions, sys_path)
    _last_jedi_completions = completions
    return _export_completions(completions)


def get_interpreter_completions(
    source: str, namespaces: List[Dict], sys_path=None
) -> List[CompletionInfo]:
    _check_patch_jedi_typesheds(sys_path)
    global _last_jedi_completions
    try:
        interpreter = _create_interpreter(source, namespaces, sys_path)
        # assuming cursor is at the end of the source
        if hasattr(interpreter, "completions"):
            # up to jedi 0.17
            completions = interpreter.completions()
        else:
            completions = interpreter.complete()
    except Exception:
        logger.exception("Jedi error")
        completions = []

    completions = _filter_completions(completions, sys_path)
    _last_jedi_completions = completions
    return _export_completions(completions)


def get_completion_details(full_name: str) -> Optional[CompletionInfo]:
    if not _last_jedi_completions:
        return None

    # assuming this name can be found in the list of last completions
    try:
        for completion in _last_jedi_completions:
            if completion.type in {"function", "class"} and _jedi_verion_is_at_least("0.15"):
                signatures = [_export_signature(s) for s in completion.get_signatures()]
                raw_docstring = True
            else:
                signatures = None
                raw_docstring = False

            if completion.full_name == full_name:
                return CompletionInfo(
                    name=completion.name,
                    name_with_symbols=_get_completion_name_with_symbols(completion, signatures),
                    full_name=completion.full_name,
                    type=completion.type,
                    prefix_length=_get_completion_prefix_length(completion),
                    signatures=signatures,
                    docstring=completion.docstring(raw=raw_docstring),
                )
    except Exception:
        logger.exception("Jedi error")

    return None


def get_script_signatures(
    source: str, row: int, column: int, filename: str, sys_path=None
) -> List[SignatureInfo]:
    _check_patch_jedi_typesheds(sys_path)

    if not _jedi_verion_is_at_least("0.15"):
        # Too much hassle
        return []

    try:
        script = _create_script(source, row, column, filename, sys_path)
        if _using_older_api():
            sigs = script.call_signatures()
        else:
            sigs = script.get_signatures(line=row, column=column)
    except Exception:
        sigs = []

    return [_export_signature(sig) for sig in sigs]


def get_interpreter_signatures(
    source: str, namespaces: List[Dict], sys_path=None
) -> List[SignatureInfo]:
    _check_patch_jedi_typesheds(sys_path)

    if not _jedi_verion_is_at_least("0.15"):
        # Too much hassle
        return []

    try:
        # assuming cursor is at the end of the source
        interpreter = _create_interpreter(source, namespaces, sys_path)

        if _using_older_api():
            sigs = interpreter.call_signatures()
        else:
            sigs = interpreter.get_signatures()
    except Exception:
        logger.exception("Jedi error")
        sigs = []

    return [_export_signature(sig) for sig in sigs]


def get_definitions(
    source: str, row: int, column: int, filename: str, sys_path: List[str] = None
) -> List[NameReference]:
    _check_patch_jedi_typesheds(sys_path)

    try:
        script = _create_script(source, row, column, filename, sys_path)
        if _using_older_api():
            defs = script.goto_assignments(follow_imports=True)
        else:
            defs = script.goto(line=row, column=column, follow_imports=True)
    except Exception:
        logger.exception("Jedi error")
        defs = []

    return [_export_reference(d) for d in defs]


def get_references(
    source: str,
    row: int,
    column: int,
    filename: str,
    scope: str,
    sys_path: Optional[List[str]] = None,
) -> List[NameReference]:
    _check_patch_jedi_typesheds(sys_path)

    if scope == "file" and (
        _jedi_verion_is_at_least("0.16") and not _jedi_verion_is_at_least("0.17.1")
    ):
        # no means for asking for file scope and can be too slow otherwise in 0.16.* and 0.17.0
        return []

    try:
        script = _create_script(source + ")", row, column, filename, sys_path)
        if _using_older_api():
            try:
                references = script.usages(include_builtins=False)
            except Exception as e:
                logger.exception("Could not compute usages")
                return []
        else:
            # scope parameter was introduced in 0.17.1
            if _jedi_verion_is_at_least("0.17.1"):
                references = script.get_references(row, column, include_builtins=False, scope=scope)
            else:
                references = script.get_references(row, column, include_builtins=False)
    except Exception:
        logger.exception("Jedi error")
        return []

    # post-processing
    if scope == "file" and not _jedi_verion_is_at_least("0.17.1"):
        references = [
            ref
            for ref in references
            if ref.module_path == filename or ref.module_name == "__main__"
        ]

    # some refs (eg. in Jedi 0.16) may lack line and column
    references = [ref for ref in references if ref.line is not None and ref.column is not None]

    return [_export_reference(ref) for ref in references]


def _create_script(
    source: str, row: int, column: int, filename: str, sys_path: List[str]
) -> jedi.api.Script:
    if _jedi_verion_is_at_least("0.17"):
        if sys_path:
            project = jedi.Project(path=sys_path[0], sys_path=sys_path, smart_sys_path=False)
        else:
            project = None

        return jedi.Script(
            code=source,
            path=filename,
            project=project,
        )
    else:
        try:
            return jedi.Script(source, row, column, filename, sys_path=sys_path)
        except Exception as e:
            logger.info("Could not create Script with given sys_path", exc_info=e)
            return jedi.Script(source, row, column, filename)


def _create_interpreter(
    source: str, namespaces: List[Dict], sys_path: Optional[List[str]]
) -> jedi.api.Interpreter:
    if _using_older_api():
        try:
            return jedi.Interpreter(source, namespaces, sys_path=sys_path)
        except Exception as e:
            logger.info("Could not get completions with given sys_path", exc_info=e)
            return jedi.Interpreter(source, namespaces)
    else:
        # NB! Can't set project for Interpreter in 0.18
        # https://github.com/davidhalter/jedi/pull/1734
        return jedi.Interpreter(source, namespaces)


def _export_completions(completions: List[jedi.api.classes.Completion]) -> List[CompletionInfo]:
    return [_export_completion(comp) for comp in completions]


def _filter_completions(
    completions: List[jedi.api.classes.Completion], sys_path: Optional[List[str]]
) -> List[jedi.api.classes.Completion]:

    if sys_path is None:
        return completions

    result = []
    for completion in completions:
        if completion.name.startswith("__"):
            continue

        # print(completion.name, completion.module_path)
        for path in sys_path:
            result.append(completion)
            break

    return result


def _export_completion(completion: jedi.api.classes.Completion) -> CompletionInfo:
    # In jedi before 0.16, the name attribute did not contain trailing '=' for argument completions,
    # since 0.16 it does. Need to ensure similar result for all supported versions.

    return CompletionInfo(
        name=completion.name and completion.name.strip("="),
        name_with_symbols=_get_completion_name_with_symbols(completion),
        full_name=completion.full_name and completion.full_name.strip("="),
        type=completion.type,
        prefix_length=_get_completion_prefix_length(completion),
        signatures=None,  # must be queried separately
        docstring=None,  # must be queried separately
    )


def _export_signature(sig: BaseSignature) -> SignatureInfo:
    as_string = sig.to_string()
    if "->" in as_string:
        # No documented API for getting the return type in 0.18
        return_type = as_string.split("->")[-1].strip()
    else:
        return_type = None

    current_param_index = None
    call_bracket_start = None
    if hasattr(sig, "index"):
        # only in subclass (Signature or CallSignature)
        current_param_index = sig.index
    if hasattr(sig, "bracket_start"):
        # only in subclass (Signature or CallSignature)
        call_bracket_start = sig.bracket_start

    return SignatureInfo(
        name=sig.name,
        params=[_export_param(p) for p in sig.params],
        return_type=return_type,
        current_param_index=current_param_index,
        call_bracket_start=call_bracket_start,
    )


def _export_param(param: ParamName) -> SignatureParameter:
    # No documented API for getting separate annotation and default, need to parse
    s = param.to_string()

    if s.count("=") == 1:
        without_default, default = s.split("=")
    else:
        without_default = (s,)
        default = None

    if without_default.count(":") == 1:
        annotation = without_default.split(":")[-1].strip()
    else:
        annotation = None

    if hasattr(param, "kind"):
        # Since 0.15
        kind = param.kind
    else:
        kind = "unknown"

    return SignatureParameter(
        kind=str(kind), name=param.name, annotation=annotation, default=default
    )


def _export_reference(ref) -> NameReference:
    return NameReference(
        module_name=ref.module_name,
        module_path=None if not ref.module_path else str(ref.module_path),
        row=ref.line,
        column=ref.column,
        length=len(ref.name),
    )


def _get_completion_name_with_symbols(
    completion: jedi.api.classes.Completion,
    signatures: Optional[List[BaseSignature]] = None,
) -> str:
    if completion.type == "param":
        # Older jedi versions may give trailing "=" also for actual arguments.
        # NB! Not all params are names of the params!
        return completion.name_with_symbols
    elif completion.type == "function":
        if not signatures:
            # signatures not found or haven't been computed yet
            return completion.name + "("
        else:
            # logger.info("name: %s, type: %s, sigs: %s", completion.name, completion.type, signatures)
            # assuming type=instance can also have signature
            # if it can only be called with 0 params, then add closing paren as well
            different_param_counts = {len(sig.params) for sig in signatures}
            if different_param_counts == {0}:
                return completion.name + "()"
            else:
                return completion.name + "("

    elif completion.type == "keyword" and completion.name != "pass":
        return completion.name + " "

    return completion.name_with_symbols


def _get_completion_prefix_length(completion: jedi.api.classes.Completion) -> int:
    if hasattr(completion, "get_completion_prefix_length"):
        # since 0.18.0
        return completion.get_completion_prefix_length()
    else:
        return completion._like_name_length


def _jedi_verion_is_at_least(ver: str) -> bool:
    return list(map(int, jedi.__version__.split(".")[:3])) >= list(map(int, ver.split(".")))


def _check_patch_jedi_typesheds(sys_path: Optional[List[str]]) -> None:
    if sys_path is None:
        return

    if not _jedi_verion_is_at_least("0.17"):
        return

    from jedi.inference.gradual import typeshed

    def _patched_get_typeshed_directories(version_info):
        for path in sys_path:
            if "api_stubs" in path:
                yield typeshed.PathInfo(path, False)

    typeshed._get_typeshed_directories = _patched_get_typeshed_directories


def _using_older_api():
    return jedi.__version__[:4] in ["0.13", "0.14", "0.15"]
