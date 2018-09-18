import sys
import os
import json
import glob
import run_analysis
import constants
import common
from re import match
from subprocess import run
from tempfile import NamedTemporaryFile as tempfile

def main(argv):
	# Start by verifying command line arguments
	if not(len(argv) == 2 or len(argv) == 3):
		help("Improper number of arguments")
	elif len(argv) == 3 and not(constants.flag_regex.match(argv[1])):
		help("Improper argument: %s" % argv[1])

	# Store command line arguments in more helpful variables
	run_impls = True
	run_tests = True
	run_analysis_only = False
	if len(argv) == 2:
		assignment_name = argv[1]
	else:
		assignment_name = argv[2]
		run_analysis_only = argv[1][1] == 'a'
		run_impls = should_run(argv[1], run_analysis_only, 'i')
		run_tests = should_run(argv[1], run_analysis_only, 't')

	# Verify the assignment directory and configuration file exist
	assignment_dir = constants.course_assignments_dir + assignment_name
	config_path = assignment_dir + "/config.json"
	if run_analysis_only:
		analyze(assignment_dir, run_impls, run_tests)
		sys.exit(1)
	elif not(os.path.isdir(assignment_dir)):
		print("Please provide a valid assignment name with a correpsonding directory")
		sys.exit(1)
	elif not(os.path.isfile(config_path)):
		print("Could not find config.json for the given assignment")
		sys.exit(1)

	# Verify the config file has the necessary variables and points to files that exist
	impl_name, test_name, replacement_arr = common.verify_config(config_path)

	# Verify that all components of an assignment are present
	wheat_dir = assignment_dir + constants.wheat_dir
	chaff_dir = assignment_dir + constants.chaff_dir
	test_dir = assignment_dir + constants.test_dir
	handin_dir = assignment_dir + constants.handin_dir
	if not(os.path.isdir(wheat_dir) and os.path.isdir(chaff_dir)
			and os.path.isdir(handin_dir) and os.path.isdir(test_dir)):
		print("One or more of the wheats, chaffs, handins, or test directories was not found")
		sys.exit(1)

	# Get lists of relevant assignment files
	wheats = glob.glob(os.path.join(wheat_dir, constants.arr_extension), recursive=False)
	chaffs = glob.glob(os.path.join(chaff_dir, constants.arr_extension), recursive=False)
	tests = glob.glob(os.path.join(test_dir, constants.arr_extension), recursive=False)

	common.replace_on_files(wheats + chaffs, replacement_arr)

	# Get all student handin directories and create the list of file combinations to run
	runs = []
	for d in os.listdir(handin_dir):
		de = os.path.join(handin_dir, d)
		# If the thing listed is a directory, look into it
		if os.path.isdir(de):
			files = glob.glob(os.path.join(de, constants.arr_extension))
			found_impl = os.path.join(de, impl_name) in files
			found_test = os.path.join(de, test_name) in files
			if (run_impls and not(found_impl)) or (run_tests and not(found_test)):
				print("WARNING: %s did not submit all of the required files" % d)
			# For each .arr file the student handed in, see if it needs to be run
			# in some way with other files
			common.replace_on_files(files, replacement_arr)
			for f in files:
				if run_impls and impl_name in f:
					runs.extend([common.concat_inputs(f, test, assignment_dir, True)
						for test in tests])
				elif run_tests and test_name in f:
					runs.extend([common.concat_inputs(impl, f, assignment_dir, False)
						for impl in wheats + chaffs])

	# Run all of the wheats and chaffs against instructor tests. They won't be added
	# to the nice output, but their result will be in the result folders if necessary
	for f in wheats + chaffs:
		runs.extend([common.concat_inputs(f, test, assignment_dir, False) for test in tests])

	runs_str = "\n".join(runs)
	#print(runs_str)
	#print(len(runs))

	# Pass these arguments into the actual script
	# (tempfile required for the stdin parameter) along with the prehook
	print()
	temp = tempfile(delete=True)
	temp.write(str.encode(runs_str))
	temp.seek(0)
	run(["/home/jswrenn/projects/powder-monkey/evaluate/evaluate-many.sh", "/course/cs0190/tabin/cs0190-grading-scripts/prehook.sh"], stdin=temp)
	temp.close()

	# Once all the tests have been run, run analysis
	analyze(assignment_dir, run_impls, run_tests)



def analyze(assignment_dir, run_impls, run_tests):
	# slurp compiles the result.json files from all of the assignments into one
	# file, which will make processing them in Python quicker
	slurp_result = run(["/course/cs0190/tabin/cs0190-grading-scripts/slurp.sh", assignment_dir]).returncode
	if slurp_result > 0:
		print("There was an issue with the JSON produced by the autograder. " \
			+ "Please run find_bad_json, fix the issues, and run this script again " \
			+ "with the --analysis flag.")
		sys.exit(1)

	# Now open the slurped file and pass it in to be analyzed
	with open(assignment_dir + "/result/results.json") as result:
		result_json = json.load(result)
		run_analysis.analyze(assignment_dir, result_json, run_impls, run_tests)

def should_run(arg, run_analysis_only, arg_char):
	# Returns true if arg indicates arg_char category ('t' for test or 'i' for impl) should be run
	if run_analysis_only:
		return (len(arg) == 2) or (arg[2] == arg_char)
	else:
		return arg[1] == arg_char

def help(first_error):
	print(first_error)
	print("Example usage: cs19_bulk_autograde [-i,-t,-a,-ai,-at] <assignment_name>")
	sys.exit(1)



if __name__ == "__main__":
	main(sys.argv)
