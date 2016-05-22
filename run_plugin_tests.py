from tests.plugin_tests import coloring_tests, global_local_marker_tests,\
paren_matcher_tests, name_highlighter_tests
import sys

print("Running coloring tests...")
coloring_tests.run_tests()
print("Running global/local marker tests...")
global_local_marker_tests.run_tests()
print("Running name highlighter tests...")
name_highlighter_tests.run_tests()
print("Running paren highlighter tests...")
paren_matcher_tests.run_tests()