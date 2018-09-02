from re import compile
from os.path import basename, dirname

course_assignments_dir = "/course/cs0190/assignments/"

config_impl = "impl_name"
config_test = "test_name"
config_imports = "import_replacements"
flag_regex = compile("^-([ait]|(ai|at))$")
wheat_dir = "/wheats"
chaff_dir = "/chaffs"
test_dir = "/tests"
handin_dir = "/handins"
impl_result_file = "/result/impls.csv"
test_result_file = "/result/tests.csv"
result_regex = "result/*_%s/results.json"
all_impl_keys = ["id", "passed", "total"]
arr_extension = "*.arr"
