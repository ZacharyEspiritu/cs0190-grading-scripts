# cs0190-grading-scripts
Grading scripts for CSCI0190 at Brown University.

## cs19\_bulk\_autograde
### Overview
This script runs an arbitrary number of student hand-ins against instructor tests and/or wheats and chaffs. The script simply takes an assignment name as a parameter, and does the rest, assuming the predefined directory hierarchy. For example the command:

`cs19_bulk_autograde docdiff`

will first look for a folder at `constants.course_assignments_dir`. For CS 19, it is set to `/course/cs0190/assignments/`. This directory should contain a folder for each assignment. The parameter `docdiff` tells the script to look for a folder with that name in `constants.course_assignments_dir`. Assignment folders require a specific structure to be read correctly. The following tree shows a simplified `docdiff` folder as an example:

```
/course/assignments/assignments/docdiff/
├── chaffs
│   ├── chaff-1.arr
│   ├── chaff-2.arr
│   └── chaff-3.arr
├── config.json
├── handins
│   ├── 1
│   │   ├── code.arr
│   │   └── tests.arr
│   ├── 2
│   │   ├── code.arr
│   │   └── tests.arr
│   ├── ...
│
├── tests
│   └── docdiff-test-suite.arr
└── wheats
    ├── docdiff-code-2017-sol.arr
    └── docdiff-code-2018-sol.arr
```

In particular, the features to note are:
 - chaffs folder, containing chaffs to be run against student tests
 - wheats folder, containing wheats to be run against student tests
 - handins folder, containing sub-folders that MUST BE NUMBERED FOR ANONYMITY, that themselves contain a testing file and/or a code file. The files in each student folder must have the same name, specified in [config.json](#configuration)
 - tests folder, containing instructor tests to run against student implementations
 - config.json, with settings the scripts needs to be run ([explained here](#configuration))

### Results
The raw results of the run will be placed at `constants.course_assignments_dir/result`. There will be a folder for each run - that is the cross product of implementation and testing files. Instructor implementations and tests will even be run against each other as a "sanity" check. The script will also create files at `constants.course_assignments_dir/result/impls.csv` and `constants.course_assignments_dir/result/tests.csv` that give concise detail about each student's performance. Each student's performance is represented as a row in the CSVs. 

`impls.csv` starts with the student's id, the number of instructor tests they passed, and the total number of instructor tests (should be the same for each student). The following columns indicate how many tests the student passed in each check block. The total number of tests in the check block is in parenthesis in the file header.

`tests.csv` starts with the student's id, and then names each check block that failed an instructor wheat or chaff. If the implementation passed the student's test suite, the cell will be blank. The name of the implementation is in the header.

### Configuration
This file specifies what names the script should look for for student hand-ins. `impl_name` sets the name of students' implementation files and `test_name` sets the name of students' testing files. 

In addition, the `import_replacements` dictionary lists files a student may be importing, and what to replace them with. In the following example of the CS 19 assignment Tour Guide, the support code file is called mapdata.arr. The value corresponding to that name indicates where an offline version of the file can be found. It is essential that any support code is listed here, as the offline Pyret interpreter cannot grab files from Google Drive.

```json
{
	"impl_name": "code.arr",
	"test_name": "tests.arr",
	"import_replacements": {
		"mapdata.arr": "/course/cs0190/assignments/tour-guide/mapdata.arr"
	}
}
```

### Other options
The script can optionally be run with parameters put in between the script name and the assignment name. There are 5 allowed parameters, detailed below.
 - `cs19_bulk_autograde -i docdiff` - Only runs student implementations against the instructor test suite. Student tests will not be run and only an `impls.csv` result file will be created.
 - `cs19_bulk_autograde -t docdiff` - Only runs instructor implementations (wheats and chaffs) against the student test suites. Student implementations will not be tested and only a `tests.csv` result file will be created.
 - `cs19_bulk_autograde -a docdiff` - Assumes that the actual grader has already been run and the `result` folder is populated with individual runs. Produces both output CSV files based on the existing results.
   - `cs19_bulk_autograde -ai docdiff` - Only runs analysis on student implementations. Combination of `-a` and `-i` behavior.
   - `cs19_bulk_autograde -at docdiff` - Only runs analysis on student tests. Combination of `-a` and `-t` behavior.

## cs19\_autograde
This script runs all the wheats and chaffs on a single student submission. There are no extra flags, and it assumes the same directory structure and prerequisites of the script above. Output is simply printed to stdout when the grading is complete, letting individual UTAs easily double check the bulk autograder, which was most likely run by the HTAs. The way to call the script is:

`cs19_autograde <assignment> <student_id>`

For example, if I wanted to get a printed report of student 1's performance on DocDiff, I would run:

`cs19_autograde docdiff 1`




