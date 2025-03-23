import cmd
import json

import file_utils as files
import io_utils as io

SPLASH_MESSAGE = "Welcome to PyGradeTracker! Ctrl + C at any time to exit."

SPLASH = f"""
|{'=' * (len(SPLASH_MESSAGE) + 2)}|
| {SPLASH_MESSAGE} |
|{'=' * (len(SPLASH_MESSAGE) + 2)}|
"""

class GradeTracker(cmd.Cmd):
    intro = "Type help or ? to list commands."
    prompt = "> "

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
        '''Returns the chosen assessment name and number'''
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
        grades = assessments[assessment]["grades"]

        if len(grades) > 1:
            print(f"Grades for {assessment}: ")
            print(io.numbered_list(grades))
            message = "Please select which grade to update: "
            choice = io.input_until_valid(
                message = message,
                repeat_message = "Invalid choice. " + message,
                func = lambda c:
                    io.in_range(c, 1, len(grades) + 1)
            )
            choice = int(choice) - 1
        else:
            choice = 0

        io.clear_lines(len(grades) + 2)

        return (assessment, choice)

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
        pass

    def do_grade(self, line):
        '''Update a grade.'''
        course = self.select_course()
        print(f"Assessments for {course}:")
        (assessment, num) = self.select_assessment(course)

        grades = self.courses[course]["assessments"][assessment]["grades"]
        current_grade = grades[num]

        assessment_str = assessment + (f" {num + 1}" if len(grades) > 1 else "")

        new_grade = io.input_until_valid(
            f"Enter the grade for {assessment_str}: ",
            func = lambda c:
                io.in_range(c, 0, 101)
        )
        io.clear_lines(1)

        if current_grade > 0:
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
        print(f"Updated {course} {assessment_str} to {new_grade}.")
    
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