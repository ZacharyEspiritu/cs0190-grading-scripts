import constants
import csv
from sys import exit

def analyze(assignment_dir, result_json, analyze_impls, analyze_tests):
	# Iterate over each run in result_json and construct a dictionary
	# that will correspond with the CSV structure we want
	print("===== BEGINNING ANALYSIS =====")

	# Initialize data structures that will be used later. Impls are more complicated
	if analyze_impls:
		impl_fields = constants.all_impl_keys.copy()
		impl_test_counts = {}
		impl_dict = {}
	if analyze_tests:
		test_fields = ["id"]
		test_dict = {}

	# Iterate through each run of an impl + test combo
	for run in result_json:
		result_impl = run["impl"]
		result_test = run["tests"]
		run_result = run["result"]
		# If there's an issue, just skip it and it'll be manually resolved
		if "Err" in run_result:
			print_run_error(result_impl, result_test, \
				"produced a %s error." % (run_result["Err"]))
			continue
		check_blocks = run_result["Ok"]
		
		if constants.handin_dir in result_impl:
			# If the run tested a student implementation handin
			if not(analyze_impls):
				continue

			# Initialize this (eventually) row of the CSV
			student_id = constants.id_from_handin(result_impl)
			impl_dict[student_id] = {
				"id": student_id
			}
			tests_passed = 0
			tests_total = 0
			# Count the number of tests (passed and total) in each check block and store it
			for check_block in check_blocks:
				check_block_name = check_block["name"]
				tests_ran = False
				if check_block["error"] and check_block_name not in impl_test_counts:
					print("ERROR: The first user failed a check block, and I can't account " \
						"for that yet. Please put a user with all check blocks passing first, " \
						"then re-run the script with the -a flag.")
					exit(1)
				elif check_block["error"]:
					tests_total += impl_test_counts[check_block_name]["num"]
				else:
					tests_ran = True
					tests_in_check = 0
					tests_passed_in_check = 0
					for test in check_block["tests"]:
						tests_in_check += 1
						tests_total += 1
						if test["passed"]: 
							tests_passed += 1
							tests_passed_in_check += 1
				
				if tests_ran and check_block_name not in impl_fields:
					output_name = "%s (%d)" % (check_block_name, tests_in_check)
					impl_test_counts[check_block_name] = {
						"name": output_name,
						"num": tests_in_check
					}
					impl_fields.append(check_block_name)
				
				impl_dict[student_id][impl_test_counts[check_block_name]["name"]] = \
					tests_passed_in_check if tests_ran else 0
			
			# Write the number of tests total and the number the student passed
			impl_dict[student_id]["passed"] = tests_passed
			impl_dict[student_id]["total"] = tests_total
		elif constants.handin_dir in result_test:
			# If the run tested a student testing handin
			if not(analyze_tests):
				continue

			# Only initialize this row if another wheat/chaff hasn't been run
			# yet on this student
			student_id = constants.id_from_handin(result_test)
			if student_id not in test_dict:
				test_dict[student_id] = {
					"id": student_id
				}
			failed_check_blocks = []
			# Only look to see if the student's tests failed any tests in the check block,
			# we don't care how many
			for check_block in check_blocks:
				check_block_name = check_block["name"]
				if check_block["error"]:
					failed_check_blocks.append(check_block_name)
					continue
				else:
					for test in check_block["tests"]:
						if not(test["passed"]):
							failed_check_blocks.append(check_block_name)
							break

			if result_impl not in test_fields:
				test_fields.append(result_impl)
				
			# Put the names of all of the check blocks that failed the wheat/chaff in the cell
			test_dict[student_id][result_impl] = \
				"" if len(failed_check_blocks) == 0 else ";".join(failed_check_blocks)
		else:
			print_run_error(result_impl, result_test, \
				"was not recognized as a student submission.")

	# Now that we've stored student data in the proper dictionaries, write them to CSVs
	if analyze_impls:
		write_csv(assignment_dir + constants.impl_result_file, \
			constants.all_impl_keys + [entry["name"] for entry in impl_test_counts.values()], \
			impl_dict)

	if analyze_tests:
		write_csv(assignment_dir + constants.test_result_file, test_fields, test_dict)



def write_csv(filename, fields, dict):
	# Writes dict with columns fields to a CSV at filename
	with open(filename, 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=fields)
		writer.writeheader()
		for key in sorted(dict, key=int):
			# If the autograder missed some runs, flag it via the 
			# ERROR but don't cause the program to fail
			for field in fields:
				if field not in dict[key].keys():
					dict[key][field] = "ERROR: This run was not found"
			assert(set(dict[key].keys()) == set(fields))
			writer.writerow(dict[key])
		print("Successfully wrote report to %s" % filename)

def print_run_error(impl_file, test_file, message):
	print("WARNING: Run on impl: %s  and test: %s %s" % (impl_file, test_file, message))
