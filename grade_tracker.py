import cmd

from tabulate import tabulate

from utils import file_management as files
from utils import io
from utils import stats

class CmdParseException(Exception): pass 

SPLASH_MESSAGE = "Welcome to PyGradeTracker! Ctrl + C at any time to exit."

SPLASH = f"""
|{'=' * (len(SPLASH_MESSAGE) + 2)}|
| {SPLASH_MESSAGE} |
|{'=' * (len(SPLASH_MESSAGE) + 2)}|
"""

class GradeTracker(cmd.Cmd):
    intro = "Type help or ? to list commands."
    prompt = "> "

    """Helper Functions"""

    def parse_grade(self, line: str) -> tuple[str, str, int, int]:
        course, assessment, number, grade = None, None, None, None
        try:
            if not line:
                raise CmdParseException()
            
            # match course by name or code
            matches = []
            for c in self.courses:
                name, code = c.lower().split()
                if name in line or code in line:
                    if name and code in line:
                        matches = [c]
                        break
                    else:
                        matches.append(c)
                    
            if len(matches) == 1:
                course = matches[0]
                name, code = course.lower().split()
                # remove identifiers from line
                line = line.replace(name, "").strip()
                line = line.replace(code, "").strip()

            else:
                raise CmdParseException("No valid course specified.")

            # match assessment
            assessment = None
            assessments = self.courses[course]["assessments"]
            for a in assessments:
                if a.lower() in line:
                    assessment = a
                    # remove identifier from line
                    line = line.replace(a.lower(), "").strip()
                    break
            
            if assessment is None:
                raise CmdParseException()
            
            grades = assessments[assessment]["grades"]

            line = line.split()

            # handle different cases for number and grade

            # no number or grade given
            if len(line) == 0:
                raise CmdParseException()
            
            # both number and grade given
            elif len(line) > 1:
                number = line[0]
                grade = line[1]

            # grade given for unique assessment
            elif len(grades) == 1:
                number = 1
                grade = line[0]
            
            # number given for non-unique assessment
            else:
                number = line[0]
                
            try:
                if number:
                    number = int(number)
                if grade:
                    grade = grade.replace('%', "")
                    grade = int(grade)
            except ValueError:
                number, grade = None, None
                raise CmdParseException(f"Unknown syntax: {" ".join(line)}")
                
            number -= 1 

            if number not in range(0, max(1, len(grades))):
                number, grade = None, None
                raise CmdParseException(f"Invalid assessment number: {number + 1}")
            
        except CmdParseException as e:
            if str(e):
                print(e)

        finally:
            return course, assessment, number, grade

    def select_course(self, allow_all = False) -> str | None:
        print(io.numbered_list(self.courses))
        message = "Please select a course" + (allow_all * " (0 for all)") + ": "
        choice = io.input_until_valid(
            message = message,
            repeat_message = "Invalid choice. " + message,
            func = lambda c:
                io.in_range(c, int(not allow_all), len(self.courses) + 1)
        )

        io.clear_lines(len(self.courses) + 2)

        if choice == 0:
            return None
        else:
            return list(self.courses.keys())[int(choice) - 1]
        
    def select_assessment(self, course) -> tuple[str, int] | None:
        '''Returns the chosen assessment name.'''
        assessments = self.courses[course]["assessments"]

        def suffix(assessment):
            s = ""
            grades = assessments[assessment]["grades"]
            if len(grades) > 1:
                s += f" ({len(grades)} total)"
            else:
                s += f" ({grades[0]}%)"
            return s
        
        print(io.numbered_list(
            data = assessments,
            suffix = suffix
        ))

        choice = io.input_until_valid(
            message = "Please select an assessment: ",
            repeat_message = "Invalid choice. Please select an assessment: ",
            func = lambda c:
                io.in_range(c, 1, len(assessments) + 1)
        )

        io.clear_lines(len(assessments) + 2)

        assessment = list(assessments.keys())[int(choice) - 1]

        return assessment
    
    def select_assessment_number(self, course, assessment):
        grades = self.courses[course]["assessments"][assessment]["grades"]

        if len(grades) > 1:
            print(f"Grades for {assessment}: ")
            print(io.numbered_list(grades))
            message = "Please select which grade to update: "
            number = io.input_until_valid(
                message = message,
                repeat_message = "Invalid choice. " + message,
                func = lambda c:
                    io.in_range(c, 1, len(grades) + 1)
            )
            number = int(number) - 1
        else:
            number = 0

        io.clear_lines(len(grades) + 2)

        return number

    """Cmd Functions"""

    def preloop(self):
        print(SPLASH)

        files.setup_dirs()

        chosen_data = None
        while chosen_data is None:
            chosen_data = files.select_data()
            if not chosen_data:
                chosen_outline = files.select_outline()
                if not chosen_outline:
                    print("No grade outline files were found. Please create one.")
                    raise SystemExit
                else:
                    chosen_data = files.create_data(chosen_outline)

        self.courses = files.load_data(chosen_data)

        filename, _ = files.filename_from_path(chosen_data)
        self.filename = filename

        print(f"Loaded grades for {self.filename}.")

    def precmd(self, line):
        return line.lower()
    
    def do_summary(self, line):
        '''Summarize grades for a course.'''
        course, _, _, _ = self.parse_grade(line)
        if not course:
            course = self.select_course()

        table = []
        assessments = self.courses[course]["assessments"].items()

        total_weight = 0
        total_achieved = 0
        weighted_average = 0

        for name, data in assessments:
            grades = data["grades"]
            grades_str = ", ".join([f"{grade}" for grade in grades if grade is not None])

            ungraded = grades.count(None)
            if ungraded > 0:
                if len(grades) > 1:
                    grades_str += "\n"
                else:
                    grades_str += " "
                grades_str += f"({ungraded} not done)"

            weight = data["weight"]

            achieved = stats.achieved_weight(data)
            total_achieved += achieved

            average = stats.interim_weight(data)
            if average != 0:
                total_weight += weight
                weighted_average += average * weight / 100

            achieved_str = f"{achieved:.2f} %"
            average_str = f"{average:.2f} %"

            weight_str = f"{weight} %"

            table.append([name, grades_str, average_str, achieved_str, weight_str])
        
        weighted_average /= total_weight / 100 if total_weight else 1

        total_achieved_str = f"{total_achieved:.2f} %"
        weighted_average_str = f"{weighted_average:.2f} %"
        
        table.append(["Total", "", weighted_average_str, total_achieved_str, "100 %"])

        print(f"-- {course} Grades --")
        print(tabulate(
            table,
            headers=["", "Grades", "Average", "Achieved", "Weight"],
            tablefmt="rounded_grid",
            stralign="right",
            colalign=("right", "left",)
        ))

    def do_grade(self, line):
        '''Update a grade.'''
        course, assessment, num, new_grade = self.parse_grade(line)
        
        if not course:
            course = self.select_course()

        if not assessment:
            print(f"Assessments for {course}:")
            assessment = self.select_assessment(course)

        grades = self.courses[course]["assessments"][assessment]["grades"]

        if num is None:
            num = self.select_assessment_number(course, assessment)

        assessment_str = assessment + (f" {num + 1}" if len(grades) > 1 else "")

        if new_grade is None:
            new_grade = io.input_until_valid(
                f"Enter the grade for {assessment_str}: ",
                func = lambda c:
                    # abitrary upper bound for bonus marks
                    io.in_range(c, 0, 1000)
            )
            io.clear_lines(1)
        
        current_grade = grades[num]

        if current_grade is not None:
            choice = io.input_until_valid(
                message = (
                    assessment_str +
                    f" already has the grade {current_grade}. Overwrite it with {new_grade}? (y/n) "
                ),
                func = lambda c:
                    io.yes_or_no(c)
            )
            io.clear_lines(1)
            if choice == 'n':
                print("Cancelled updating grade.")
                return
            
        grades[num] = int(new_grade)
        print(f"Updated {course} {assessment_str} to {new_grade}%.")
    
    def do_test(self, line):
        print(stats.achieved_weight(self.courses["COMP 2140"]["assessments"]["Assignment"], True))

    def do_exit(self, line):
        '''Exit the program.'''
        print("Exiting...")
        files.write_data(self.courses, self.filename)
        return True
    
    def customloop(self):
        '''cmdloop wrapper to gracefully exit on KeyboardInterrupt.'''
        doExit = False
        while not doExit:
            try:
                self.cmdloop()
            except KeyboardInterrupt:
                self.do_exit("")
            finally:
                doExit = True

if __name__ == '__main__':
    GradeTracker().customloop()