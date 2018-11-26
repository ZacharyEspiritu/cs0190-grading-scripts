import sys
import os
import csv

def confirm_file_exists(filename):
	if (not(os.path.isfile(filename))):
		print(filename + " is missing")
		sys.exit(1)

def main(argv):
	if not(len(argv) == 2):
		print("Improper argument. Proper usage: python3 lab_compilation.py <highest_lab_number>")
		sys.exit(1)

	final_lab = -1
	try:
		final_lab = int(argv[1])
	except:
		print("Argument must be an integer")
		sys.exit(1)
	
	grade_table = {}
	labs_range = list(range(1, final_lab+1))
	for i in labs_range:
		attendance_filename = "csvs/lab%s-attendance.csv" % i
		checkoff_filename = "csvs/lab%s-checkoff.csv" % i
		confirm_file_exists(attendance_filename)
		confirm_file_exists(checkoff_filename)
		with open(attendance_filename) as csvfile:
			reader = csv.reader(csvfile)
			next(reader, None) # skip the header
			for row in reader:
				login = row[1]
				if login not in grade_table:
					grade_table[login] = {}
				grade_table[login][i] = 1
		
		with open(checkoff_filename) as csvfile:
			reader = csv.reader(csvfile)
			next(reader, None) # skip the header
			for row in reader:
				logins = []
				if i <= 2: # not a partner lab
					logins.append(row[2])
				else: # a partner lab
					logins.append(row[2])
					if not(row[3] == ""):
						logins.append(row[3])
					if not(row[4] == ""):
						logins.append(row[4])
				
				for login in logins:
					if login not in grade_table:
						grade_table[login] = {}
						grade_table[login][i] = "Student was checked off but did not sign in"
					elif i not in grade_table[login]:
						grade_table[login][i] = "Student was checked off but did not sign in"
					else:
						grade_table[login][i] = 2


	with open("csvs/results.csv", 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(["login"] + labs_range)
		for key in sorted(grade_table.keys()):
			writer.writerow([key] + 
				[grade_table[key][i] if i in grade_table[key] else 0 for i in labs_range])
		print("Successfully wrote report to csvs/results.csv")
	


if __name__ == "__main__":
	main(sys.argv)