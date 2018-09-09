import sys
import os
import json
import glob
import constants
import common
import subprocess
from run_analysis import get_failed_check_blocks
from tempfile import NamedTemporaryFile as tempfile

def main(argv):
	# Start by verifying command line arguments
	if not(len(argv) == 3):
		help("Improper number of arguments")

	# Store command line arguments in more helpful variables
	assignment_name = argv[1]
	student_id = argv[2]

	# Verify the assignment directory and configuration file exist
	assignment_dir = constants.course_assignments_dir + assignment_name
	config_path = assignment_dir + "/config.json"
	if not(os.path.isdir(assignment_dir)):
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
	handin_dir = os.path.join(assignment_dir + constants.handin_dir, student_id)
	if not(os.path.isdir(wheat_dir) and os.path.isdir(chaff_dir)
			and os.path.isdir(handin_dir) and os.path.isdir(test_dir)):
		print("One or more of the wheats, chaffs, handins, or test directories was not found")
		sys.exit(1)

	# Get lists of relevant assignment files
	wheats = glob.glob(os.path.join(wheat_dir, constants.arr_extension), recursive=False)
	chaffs = glob.glob(os.path.join(chaff_dir, constants.arr_extension), recursive=False)
	tests = glob.glob(os.path.join(test_dir, constants.arr_extension), recursive=False)

	common.replace_on_files(wheats + chaffs + tests, replacement_arr)

	# Get all student handin directories and create the list of file combinations to run
	runs = []
	files = glob.glob(os.path.join(handin_dir, constants.arr_extension))
	found_impl = os.path.join(handin_dir, impl_name) in files
	found_test = os.path.join(handin_dir, test_name) in files
	if not(found_impl) or not(found_test):
		print("ERROR: The student did not submit all of the required files")
		sys.exit(1)

	# For each .arr file the student handed in, see if it needs to be run
	# in some way with other files
	for f in files:
		if impl_name in f:
			runs.extend([common.concat_inputs(f, test, assignment_dir, True)
				for test in tests])
		elif test_name in f:
			runs.extend([common.concat_inputs(impl, f, assignment_dir, False)
				for impl in wheats + chaffs])

	runs_str = "\n".join(runs)
	#print(runs_str)

	# Pass these arguments into the actual script
	# (tempfile required for the stdin parameter) along with the prehook
	temp = tempfile(delete=True)
	temp.write(str.encode(runs_str))
	temp.seek(0)
	subprocess.run(["/home/jswrenn/projects/powder-monkey/evaluate/evaluate-many.sh", "/course/cs0190/tabin/cs0190-grading-scripts/prehook.sh"], stdin=temp)
	temp.close()

	# Once all the tests have been run, print the output
	all_json = json.loads(subprocess.run(["/course/cs0190/tabin/cs0190-grading-scripts/slurp_single.sh", \
		os.path.join(assignment_dir, constants.result_regex % student_id)], \
		stdout=subprocess.PIPE).stdout.decode())
	
	testing_results = {
		"passed": 0,
		"total": 0
	}
	for run in all_json:
		result_impl = run["impl"]
		result_test = run["tests"]
		run_result = run["result"]
		# If there's an issue, just skip it and it'll be manually resolved
		if "Err" in run_result:
			common.print_run_error(result_impl, result_test, \
				"produced a %s error." % (run_result["Err"]))
			continue
		check_blocks = run_result["Ok"]
		
		if constants.handin_dir in result_impl:
			for check_block in check_blocks:
				check_block_name = check_block["name"]
				if check_block["error"]:
					print("ERROR: There was an error in the check block: %s, " + \
						"so the final number of tests will be off from the official count." % \
						check_block_name)
				else:
					tests_in_check = 0
					tests_passed_in_check = 0
					for test in check_block["tests"]:
						tests_in_check += 1
						if test["passed"]: tests_passed_in_check += 1
					testing_results["passed"] += tests_passed_in_check
					testing_results["total"] += tests_in_check
					testing_results[check_block_name + " (%d)" % tests_in_check] = tests_passed_in_check
		elif constants.handin_dir in result_test:
			print("The student check blocks on the following line failed %s" % result_impl)
			print(";".join(get_failed_check_blocks(check_blocks)))
		else:
			common.print_run_error(result_impl, result_test, \
				"was not recognized as a student submission.")
	
	print("Final student implementation vs. instructor test results: ")
	print(json.dumps(testing_results, indent=4))




def help(first_error):
	print(first_error)
	print("Example usage: cs19_autograde <assignment_name> <student_id>")
	sys.exit(1)



if __name__ == "__main__":
	main(sys.argv)
