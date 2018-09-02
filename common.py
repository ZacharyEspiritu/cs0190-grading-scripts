import constants
import json
import sys
import os

def verify_config(config_path):
	# Open and store the config file
	with open(config_path) as config_file:
		config = json.load(config_file)

	if constants.config_impl not in config.keys() and constants.config_test in config.keys():
		print("config.json must contain an impl_name and test_name")
		sys.exit(1)
	elif constants.config_imports in config:
		import_replacements = config[constants.config_imports]
		for key in import_replacements:
			if not(os.path.isfile(import_replacements[key])):
				print("Could not find import replacement file: %s" % import_replacements[key])
				sys.exit(1)
			# TODO: actually replace stuff

	return (config[constants.config_impl], config[constants.config_test])

def concat_inputs(impl_file, test_file, assignment_dir, student_impl):
	# Concatenates the given inputs into a line that the autograder will run
	# Format is implementation file, test file, output directory
	return "%s %s %s/result/%s_%s_%s" % (impl_file, test_file, assignment_dir, \
		os.path.basename(impl_file), os.path.basename(test_file), \
		id_from_handin(impl_file if student_impl else test_file))

def id_from_handin(filepath):
	return os.path.basename(os.path.dirname(filepath))

def print_run_error(impl_file, test_file, message):
	print("WARNING: Run on impl: %s  and test: %s %s" % (impl_file, test_file, message))