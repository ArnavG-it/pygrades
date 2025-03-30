import cmd
from tabulate import tabulate

from utils import file_management as files
from utils import io
from utils import stats

class CmdParseException(Exception): pass 

SPLASH_MESSAGE = (
    "Welcome to PyGrades! Ctrl + C at any time to cancel a command or exit."
)

SPLASH = f"""
|{'=' * (len(SPLASH_MESSAGE) + 2)}|
| {SPLASH_MESSAGE} |
|{'=' * (len(SPLASH_MESSAGE) + 2)}|
"""

class PyGrades(cmd.Cmd):
    intro = "Type help or ? to list commands.\n"
    prompt = "> "

    # ============= #
    # Cmd Overrides #
    # ============= #

    def customloop(self):
        '''cmdloop wrapper to gracefully exit on KeyboardInterrupt.'''
        doExit = False
        while not doExit:
            try:
                self.cmdloop()
            except KeyboardInterrupt:
                print()
                self.do_exit("")
            finally:
                doExit = True

    def preloop(self):
        print(SPLASH)
        data, filename = files.setup_cmd()
        self.courses = data
        self.filename = filename
        print(f"\nLoaded data for {self.filename}.")

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except KeyboardInterrupt:
            print(f"\nCancelled '{line}'")
            return

    def precmd(self, line):
        return line.lower()
    
    def postcmd(self, stop, line):
        print()
        if stop:
            return True
        
    # ======== #
    # Commands #
    # ======== #

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
                    c is not None and (
                        io.in_range(c.replace("%", ""), 0, 1000)
                        or c.lower() == "none"
                    )
            )
            if new_grade.lower() == "none":
                new_grade = -1
            else:
                new_grade = new_grade.replace("%", "")

        # resolve sentinel value grade to None
        if new_grade == -1:
            new_grade = None

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
            if choice == 'n':
                print("Cancelled updating grade.")
                return
        
        if new_grade is not None:
            grades[num] = float(new_grade)
        else:
            grades[num] = None
        print(f"Updated {course} {assessment_str} to {new_grade}{'%' * (new_grade is not None)}.")

    def do_summary(self, line):
        '''Summarize grades for a course.'''
        course, _ = self.match_course(line)
        if not course:
            course = self.select_course()

        table = []
        assessments = self.courses[course]["assessments"]

        for name, data in assessments.items():
            grades: list = data["grades"]
            kept, dropped = stats.filter_dropped(data)
            graded = len(stats.filter_ungraded(grades))

            # find the index of the last grade that is not None
            rev_grades = grades[::-1]
            last_grade = next((i for i, g in enumerate(rev_grades) if g is not None), len(grades))
            latest_grade = len(grades) - last_grade - 1

            # copies for iterative mutation
            kept_copy = kept[:]
            dropped_copy = dropped[:]

            # create formatted strings for grades column
            grades_str = ""
            i = 0
            for grade in grades:
                if grade is not None:
                    fraction = grade != int(grade)
                    grade_str = f"{grade:.1f}" if fraction else f"{grade:.0f}"

                    if grade in dropped_copy:
                        grades_str += f"~{grade_str}~"
                        dropped_copy.remove(grade)
                    else:
                        grades_str += f"{grade_str}"
                        kept_copy.remove(grade)

                    if i != latest_grade:
                        grades_str += ", "
                
                elif len(kept) > 0 <= i < latest_grade:
                    grades_str += "None, "

                i += 1

            ungraded = grades.count(None)
            to_drop = data["dropped"] - len(dropped)

            if ungraded > 0 or to_drop > 0:
                pending_str = " pending"
                dropped_str = (" more " if len(dropped) > 0 else " ") + "to drop"
                grades_str += "\n" if len(grades) > 1 else ""
                grades_str += "("
                if ungraded and not to_drop:
                    grades_str += f"{ungraded}{pending_str}"
                elif to_drop and not ungraded:
                    grades_str += to_drop + dropped_str
                else:
                    grades_str += f"{ungraded}{pending_str}, {to_drop}{dropped_str}"
                grades_str += ")"

            # calculate and format assessment stats
            weight = data["weight"]

            achieved = stats.achieved_weight(data)
            average = stats.interim_weight(kept)

            achieved_str = f"{achieved:.2f} %" if graded else "n/a"
            average_str = f"{average:.2f} %" if graded else "n/a"

            weight_str = f"{weight} %"

            # add row to table
            table.append([name, grades_str, average_str, achieved_str, weight_str])

        # add totals to table
        weighted_average_str, total_achieved_str = stats.course_totals(self.courses[course])
        table.append(["•", "Weighted Totals:", weighted_average_str, total_achieved_str, "100 %"])

        print(tabulate(
            table,
            headers=[f"{course}", "Grades", "Average", "Achieved", "Weight"],
            tablefmt="rounded_grid",
            stralign="right",
            colalign=("right", "left",)
        ))

    def do_overview(self, line):
        '''View the status of each course.'''
        table = []
        for name, data in self.courses.items():
            weighted_average_str, total_achieved_str = stats.course_totals(data)

            table.append([name, weighted_average_str, total_achieved_str])

        print(tabulate(
            table,
            headers=[self.filename, "Wtd. Average", "Achieved"],
            tablefmt = "rounded_grid",
            stralign="right"
        ))

    def do_scale(self, line):
        '''View the grade scale for a course.'''
        course_name, _ = self.match_course(line)
        if not course_name:
            course_name = self.select_course()
        course = self.courses[course_name]

        weighted_avg = stats.total_weighted_average(course["assessments"])
        placement = stats.get_letter_grade(course, weighted_avg)

        scale = course["scale"]
        rows = [f"- {course_name}"]
        for letter, minimum in scale.items():
            rows.append(f"| {letter}\t{minimum}%")
            if placement is not None and letter == placement:
                rows[-1] += f" <- Current ({weighted_avg:.2f}%)"

        for row in rows: print(row)

    def do_needed(self, line):
        course_name, target = self.parse_needed(line)
        if not course_name:
            course_name = self.select_course()

        if target is None or not self.match_grade(target, course_name):
            target = io.input_until_valid(
                "Enter a target grade: ",
                lambda c: c is not None and self.match_grade(c, course_name)
            )
            target = self.match_grade(target, course_name)

        course = self.courses[course_name]
        assessments = course["assessments"]
        scale = course["scale"]

        needed = stats.needed_for_target(assessments, target)
        
        target_str = f"{target:.1f}%"
        scale_key = stats.get_letter_grade(course, target)
        if scale_key is not None and scale[scale_key] == target:
            target_str += f" ({scale_key})"

        if needed is None:
            print(f"All assessments in {course_name} have already been graded.")
        elif needed > 100:
            print(f"Cannot achieve {target_str} in {course_name}.")
        elif needed <= 0:
            print(f"You have already achieved {target_str}% in {course_name}.")
        else:
            print(f"{needed:.2f}% needed on remaining assessments to achieve {target_str}.")

    def do_max(self, line):
        course, _ = self.match_course(line)
        if not course:
            course = self.select_course()
        
        max = stats.max_grade_possible(self.courses[course]["assessments"])
        scale_key = stats.get_letter_grade(self.courses[course], max)

        s = f"The maximum grade possible for {course} is {max:.2f}%"
        if scale_key:
            s += f" ({scale_key})"
        print(s)

    def do_save(self, line):
        success = files.write_data(self.courses, self.filename)
        if success:
            print("Saved changes.")
        else:
            raise SystemExit
        
    def do_switch(self, line):
        '''Switch to another data file.'''
        save = io.input_until_valid(
            f"Save changes to {self.filename}? (y/n)",
            lambda c: io.yes_or_no(c)
        )
        
        print()
        if save == 'y':
            files.write_data(self.courses, self.filename)
            print("Successfully saved data.")
        else:
            print("NOTICE: Continuing without saving.")
            print("(You can cancel this command with Ctrl + C)")
        print()

        data, filename = files.setup_cmd()
        self.courses = data
        self.filename = filename
        print(f"\nLoaded data for {self.filename}.")
        print(self.intro, end="")

    def do_exit(self, line):
        '''Save and exit the program.'''
        print("Saving and Exiting...")
        if hasattr(self, "courses") and hasattr(self, "filename"):
            files.write_data(self.courses, self.filename)
        return True
    
    def do_quit(self, line):
        '''Quit without saving.'''
        conf = io.input_until_valid(
            "Are you sure you want to quit without saving? (y/n) ",
            lambda c: io.yes_or_no(c)
        )
        if conf != 'y':
            print("You can save and exit by typing 'exit'.")
        else:
            print("Quitting...")
            return True

    # ======= #
    # Parsers #
    # ======= #

    def match_course(self, line: str):
        '''
        Tries to match a course by its name or code.

        Returns the course if found, and the line
        with the course identifier removed.
        '''
        if not line:
            return None, line
        
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
            course = None
        
        return course, line
    
    def match_grade(self, grade: str | float, course: str = "") -> float | None:
        '''
        Checks whether the grade is valid as a
        percentage or a scale key from the given course.

        Returns the grade as a percentage if valid.
        '''
        # try as percentage
        try:
            if type(grade) == str:
                grade = grade.replace("%", "")
            grade_f = float(grade)
            return grade_f if 0 < grade_f <= 100 else None
        except ValueError:
            pass

        # try as scale key
        if course in self.courses.keys():
            scale = self.courses[course]["scale"]
            scale_lower = {
                key.lower(): val for key, val in scale.items()
            }
            grade = grade.lower()
            if grade in scale_lower.keys():
                return scale_lower[grade]
        
        return None

    def parse_grade(self, line: str) -> tuple[str, str, int, int]:
        '''
        Parses all arguments for do_grade.
        If grade is -1, the user wishes to unset it.
        '''
        course, assessment, number, grade = None, None, None, None
        try:
            course, line = self.match_course(line)
            if not course and line != "":
                print(line)
                raise CmdParseException("No valid course provided.")
            
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
                    if grade.lower() == "none":
                        grade = -1
                    else:
                        grade = grade.replace('%', "")
                        grade = float(grade)
            except ValueError:
                number, grade = None, None
                raise CmdParseException(f"Unknown syntax: {" ".join(line)}")
                
            number -= 1 

            if number not in range(0, max(1, len(grades))):
                n = number
                number, grade = None, None
                raise CmdParseException(f"Invalid assessment number: {n + 1}")
            
        except CmdParseException as e:
            if str(e):
                print(e)

        return course, assessment, number, grade
        
    def parse_needed(self, line) -> tuple[str, float]:
        course, target = None, None
        try:
            if not line:
                raise CmdParseException()

            course, line = self.match_course(line)
            if not course:
                raise CmdParseException(f"No valid course provided.")

            target = self.match_grade(line, course)
            
            if not target:
                raise CmdParseException(f"No valid target grade provided.")

        except CmdParseException as e:
            if str(e):
                print(e)

        return course, target
    
    # ======================= #
    # Numbered List Selectors #
    # ======================= #

    def select_course(self) -> str | None:
        print(io.numbered_list(self.courses))
        message = "Please select a course: "
        choice = io.input_until_valid(
            message = message,
            repeat_message = "Invalid choice. " + message,
            func = lambda c:
                io.in_range(c, 1, len(self.courses) + 1)
        )
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
            filtered_grades = stats.filter_ungraded(grades)
            if len(grades) > 1:
                s += f" ({len(filtered_grades)}/{len(grades)} graded)"
            elif grades[0] is not None:
                s += f" ({grades[0]}%)"
            else:
                s += " (pending)"
            return s
        
        print(io.numbered_list(
            data = assessments,
            suffix = suffix
        ))

        choice = io.input_until_valid(
            message = "Please select an assessment: ",
            repeat_message = "Invalid choice. Please select an assessment: ",
            func = lambda c:
                c is not None and (
                    io.in_range(c, 1, len(assessments) + 1)
                    or c.lower().capitalize() in assessments.keys()
                )
        )

        if choice.isnumeric():
            assessment = list(assessments.keys())[int(choice) - 1]
        else: # key str
            assessment = choice.lower().capitalize()

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

        return number

# ===== #
# Entry #
# ===== #

if __name__ == '__main__':
    PyGrades().customloop()