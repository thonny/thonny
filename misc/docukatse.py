import docutils.frontend
import docutils.parsers
import docutils.parsers.rst
import docutils.parsers.rst.roles as roles
import docutils.utils
from docutils import nodes

# ... here 'fileobj' is a file-like object holding the contents of the input
# reST file.

# Parse the file into a document with the rst parser.
default_settings = docutils.frontend.OptionParser(
    components=(docutils.parsers.rst.Parser,)
).get_default_values()
parser = docutils.parsers.rst.Parser()


def reet_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    """"""
    # Once nested inline markup is implemented, this and other methods should
    # recursively call inliner.nested_parse().
    options["classes"] = "reet"
    return [nodes.inline(rawtext, docutils.utils.unescape(text), **options)], []


# register_generic_role('reet', nodes.literal)
roles.register_local_role("reet", reet_role)

document = docutils.utils.new_document("katse", default_settings)

src = """
.. note:: This is a ``note`` admonition.
   This is the second line of the first paragraph.

   - The note contains all indented body elements
     following.
   - It includes this bullet list.
"""

parser.parse(src, document)
print(document)
