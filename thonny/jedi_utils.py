"""
Utils to handle different jedi versions
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def get_statement_of_position(node, pos):
    import jedi.parser_utils

    func = getattr(
        jedi.parser_utils, "get_statement_of_position", _copy_of_get_statement_of_position
    )
    return func(node, pos)


# TODO: try to get rid of this
def _copy_of_get_statement_of_position(node, pos):
    # https://github.com/davidhalter/jedi/commit/9f3a2f93c48eda24e2dcc25e54eb7cc10aa73848
    from parso.python import tree

    for c in node.children:
        if c.start_pos <= pos <= c.end_pos:
            if (
                c.type
                not in (
                    "decorated",
                    "simple_stmt",
                    "suite",
                    "async_stmt",
                    "async_funcdef",
                )
                and not isinstance(c, (tree.Flow, tree.ClassOrFunc))
            ):
                return c
            else:
                try:
                    return _copy_of_get_statement_of_position(c, pos)
                except AttributeError:
                    pass  # Must be a non-scope
    return None


def parse_source(source):
    import parso

    return parso.parse(source)


def get_script_completions(source: str, row: int, column: int, filename: str, sys_path=None):
    import jedi

    if _using_older_jedi(jedi):
        try:
            script = jedi.Script(source, row, column, filename, sys_path=sys_path)
        except Exception as e:
            logger.info("Could not get completions with given sys_path", exc_info=e)
            script = jedi.Script(source, row, column, filename)

        completions = script.completions()
    else:
        script = jedi.Script(code=source, path=filename, project=_get_new_jedi_project(sys_path))
        completions = script.complete(line=row, column=column)

    return _tweak_completions(completions)


def get_interpreter_completions(source: str, namespaces: List[Dict], sys_path=None):
    import jedi

    if _using_older_jedi(jedi):
        try:
            interpreter = jedi.Interpreter(source, namespaces, sys_path=sys_path)
        except Exception as e:
            logger.info("Could not get completions with given sys_path", exc_info=e)
            interpreter = jedi.Interpreter(source, namespaces)
    else:
        # NB! Can't send project for Interpreter in 0.18
        # https://github.com/davidhalter/jedi/pull/1734
        interpreter = jedi.Interpreter(source, namespaces)
    if hasattr(interpreter, "completions"):
        # up to jedi 0.17
        return _tweak_completions(interpreter.completions())
    else:
        return _tweak_completions(interpreter.complete())


def _get_new_jedi_project(sys_path):
    if not sys_path:
        return None
    else:
        import jedi

        return jedi.Project(path=sys_path[0], added_sys_path=sys_path)


def _tweak_completions(completions):
    # In jedi before 0.16, the name attribute did not contain trailing '=' for argument completions,
    # since 0.16 it does. Need to ensure similar result for all supported versions.
    result = []
    for completion in completions:
        name = completion.name
        complete = completion.complete
        if complete.endswith("=") and not name.endswith("="):
            name += "="

        result.append(
            ThonnyCompletion(
                name=name,
                complete=complete,
                type=completion.type,
                description=completion.description,
                parent=completion.parent,
                full_name=completion.full_name,
            )
        )

    return result


def get_definitions(source: str, row: int, column: int, filename: str):
    import jedi

    if _using_older_jedi(jedi):
        script = jedi.Script(source, row, column, filename)
        return script.goto_definitions()
    else:
        script = jedi.Script(code=source, path=filename)
        return script.infer(line=row, column=column)


def _using_older_jedi(jedi):
    return jedi.__version__[:4] in ["0.13", "0.14", "0.15", "0.16", "0.17"]


class ThonnyCompletion:
    def __init__(self, name: str, complete: str, type, description, parent, full_name):
        self.name = name
        self.complete = complete
        self.type = type
        self.description = description
        self.parent = parent
        self.full_name = full_name

    def __getitem__(self, key):
        return self.__dict__[key]
