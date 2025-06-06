import cmd
import sys
import signal
from tabulate import tabulate

if sys.platform == "win32":
    import win32api
    import win32con

from utils import file_management as files
from utils import input_output as io
from utils import stats

class CmdParseException(Exception): pass 

SPLASH_MESSAGE = "Welcome to PyGrades! Ctrl + C at any time to cancel a command or exit."

SPLASH = tabulate([[SPLASH_MESSAGE]], tablefmt="rounded_grid")

HELP_ORDER = [
    "Evaluation:",
    "grade", "overview", "summary",
    "scale", "max", "needed",
    "adjust", "dropnum",
    "Program:",
    "switch", "save", "exit", "quit", "help"
]

class PyGrades(cmd.Cmd):
    intro = "Type help to list commands.\n"
    prompt = "[π] > "

    # ============= #
    # Cmd Overrides #
    # ============= #

    if sys.platform == "win32":
        def handle_close(self, event):
            if event in (
                win32con.CTRL_CLOSE_EVENT,
                win32con.CTRL_LOGOFF_EVENT,
                win32con.CTRL_SHUTDOWN_EVENT
            ):
                self.do_exit("")

    def customloop(self):
        '''cmdloop wrapper to gracefully exit on KeyboardInterrupt.'''
        self.exit = False
        while not self.exit:
            try:
                self.cmdloop()
            except KeyboardInterrupt:
                print()
                self.do_exit("")

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

    def do_help(self, arg):
        '''
        - List all commands, or get help for a specific one.

        Optional argument:
        [command] -> The command you want help with

        Syntax: help [command]
        '''
        if arg:
            super().do_help(arg)
        else:
            print("Enter 'help [command]' to get help for a specific command.")
            for name in HELP_ORDER:
                func = getattr(self, f"do_{name}", None)
                if func:
                    doc = func.__doc__
                    explanation = str(doc).split("\n")[1]
                    print(f"{name:<10}{explanation}")
                else:
                    print()
                    print(name)

    def do_grade(self, line):
        '''
        - Update a grade.

        Optional arguments:
        [course] \t -> Course identifier
        [assessment] \t -> Assessment name
        [number] \t -> Assessment number, if there are multiple
        [grade] \t -> Received grade (can be "none")

        Syntax: grade [course] [assessment] [number] [grade]
        '''
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
            message = assessment_str + f" already has the grade {current_grade}%."
            message += f" Overwrite it with {new_grade}{'%' if new_grade is not None else ''}? (y/n) "
            choice = io.input_until_valid(
                message = message,
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
        '''
        - Summarize grades for a course.

        Optional argument:
        [course] -> Course identifier

        Syntax: summary [course]
        '''
        show_all = line == "all"
        if show_all:
            for course in self.courses:
                self.do_summary(course)
                print()
            return

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
        '''
        - See an overview of all courses.

        Syntax: overview
        '''
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
        '''
        - View the grade scale for a course.

        Optional argument:
        [course] -> Course identifier

        Syntax: scale [course]
        '''
        course_name, _ = self.match_course(line)
        if not course_name:
            course_name = self.select_course()
        course = self.courses[course_name]

        scale = course["scale"]
        sorted_scale = sorted(
            scale.items(),
            reverse = True,
            key = lambda x: x[1]
        )

        # handle sentinel value representing no scale
        if "None" in scale.keys():
            print(f"{course_name} has no grade scale.")
            return

        weighted_avg = stats.total_weighted_average(course["assessments"])
        placement = stats.get_letter_grade(course, weighted_avg)

        rows = [f"- {course_name}"]
        for letter, minimum in sorted_scale:
            rows.append(f"| {letter}\t{minimum}%")
            if placement is not None and letter == placement:
                rows[-1] += f" <- Current ({weighted_avg:.2f}%)"

        for row in rows: print(row)

    def do_adjust(self, line):
        '''
        - Adjust the grading scale of a course.

        Optional arguments:
        [course] \t -> Course identifier
        [grade] \t -> Grade to adjust (ex. A+)
        [minimum] \t -> New minimum grade for the key (ex. 90%)

        Syntax: adjust [course] [key] [minimum]
        '''
        course_name, line = self.match_course(line)
        if not course_name:
            course_name = self.select_course()
        course = self.courses[course_name]
        
        # extract arguments for scale key and grade
        parts = line.split()
        if len(parts) == 0:
            scale_key = None
            new_grade = None
        elif len(parts) == 1:
            scale_key = parts[0]
            new_grade = None
        else:
            scale_key = parts[0]
            new_grade = parts[1]

        scale: dict = course["scale"]
        scale_keys = list(scale.keys())
        # create lowered key map to match input
        keys_lower_map = {key.lower(): key for key in scale_keys}

        # resolve scale key
        if scale_key in keys_lower_map:
            scale_key = keys_lower_map[scale_key]
        else:
            print(io.numbered_list(
                scale,
                suffix = lambda key: f"\t{scale[key]}%"
            ))
            choice = io.input_until_valid(
                "Enter the number of the grade to adjust: ",
                lambda c: io.in_range(c, 1, len(scale) + 1)
            )
            scale_key = scale_keys[int(choice) - 1]

        # resolve grade
        if new_grade is None or self.match_grade(new_grade) is None:
            new_grade = io.input_until_valid(
                f"Enter the new grade for {scale_key}: ",
                lambda c: c is not None and self.match_grade(c, course_name) is not None
            )
            new_grade = self.match_grade(new_grade, course_name)

        if type(new_grade) == str:
            new_grade = new_grade.replace("%", "")
            new_grade = float(new_grade)
        if new_grade == int(new_grade):
            new_grade = int(new_grade)

        # confirm adjustment
        old_grade = scale[scale_key]
        conf = io.input_until_valid(
            f"Move {scale_key} from {old_grade}% to {new_grade}%? (y/n) ",
            lambda c: io.yes_or_no(c)
        )
        if conf == 'y':
            scale[scale_key] = new_grade
            print(f"Updated {scale_key} for {course_name}.")
        else:
            print("Cancelled adjustment.")

    def do_dropnum(self, line):
        '''
        - Update the dropped amount for an assessment.

        Optional arguments:
        [course] \t -> Course identifier
        [assessment] \t -> Name of the assessment to update
        [number] \t -> New number of assessments to drop

        Syntax: dropnum [course] [assessment] [number]
        '''
        course_name, line = self.match_course(line)
        if not course_name:
            course_name = self.select_course()

        course = self.courses[course_name]
        assessments = course["assessments"]
        assessments_keys = list(assessments.keys())

        # create lowered key map to match input
        assessments_lower_map = {key.lower(): key for key in assessments_keys}

        # extract arguments for assessment and number
        parts = line.split()
        if len(parts) == 0:
            assessment_name = None
            new_number = None
        elif len(parts) == 1:
            assessment_name = parts[0]
            new_number = None
        else:
            assessment_name = parts[0]
            new_number = parts[1]

        # resolve assessment key
        if assessment_name in assessments_lower_map:
            assessment_name = assessments_lower_map[assessment_name]
        else:
            print(io.numbered_list(
                assessments,
                suffix = lambda key: f" ({assessments[key]["dropped"]} out of {assessments[key]["amount"]} dropped)"
            ))
            choice = io.input_until_valid(
                "Enter the assessment to update: ",
                lambda c: io.in_range(c, 1, len(assessments) + 1)
            )
            assessment_name = assessments_keys[int(choice) - 1]

        assessment = assessments[assessment_name]
        kept = assessment["amount"]
        
        if new_number is None or not new_number.isnumeric() or not (0 <= int(new_number) < kept):
            new_number = int(io.input_until_valid(
                "Enter the new dropped amount (must be less than the total amount): ",
                lambda c: io.in_range(c, 0, kept),
                repeat_message="Invalid number. Enter the new dropped amount: "
            ))
        else:
            new_number = int(new_number)

        current_number = assessment["dropped"]
        if current_number == new_number:
            print(f"{assessment_name} already drops {new_number}.")
        else:
            conf = io.input_until_valid(
                f"Drop {new_number} instead of {current_number} {assessment_name} in {course_name}? (y/n) ",
                lambda c: io.yes_or_no(c)
            )
            if conf == 'y':
                assessment["dropped"] = new_number
                print(f"Updated {assessment_name}.")
            else:
                print("Cancelled update.")
        
    def do_needed(self, line):
        '''
        - See how well you need to do to achieve a target grade.

        Optional arguments:
        [course] \t -> Course identifier
        [grade] \t -> Target grade (can be a percentage or scale key, ex. A+)

        Syntax: needed [course] [grade]
        '''
        course_name, target = self.parse_needed(line)
        if not course_name:
            course_name = self.select_course()

        if target is None or self.match_grade(target, course_name) is None:
            target = io.input_until_valid(
                "Enter a target grade: ",
                lambda c: c is not None and self.match_grade(c, course_name) is not None
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
            print(f"You have already achieved {target_str} in {course_name}.")
        else:
            print(f"{needed:.2f}% needed on remaining assessments to achieve {target_str}.")

    def do_max(self, line):
        '''
        - See what the maximum grade you can get in a course is.

        Optional argument:
        [course] -> Course identifier

        Syntax: max [course]
        '''
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
        '''
        - Save changes.
        '''
        success = files.write_data(self.courses, self.filename)
        if success:
            print("Saved changes.")
        else:
            raise SystemExit
        
    def do_switch(self, line):
        '''
        - Switch to another data file.
        '''
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

        data, filename = files.setup_cmd(startup=False)
        self.courses = data
        self.filename = filename
        print(f"\nLoaded data for {self.filename}.")
        print(self.intro, end="")

    def do_exit(self, line):
        '''
        - Save and exit the program.
        '''
        print("Saving and Exiting...")
        if hasattr(self, "courses") and hasattr(self, "filename"):
            files.write_data(self.courses, self.filename)
        self.exit = True
        return True
    
    def do_quit(self, line):
        '''
        - Quit without saving.
        '''
        conf = io.input_until_valid(
            "Are you sure you want to quit without saving? (y/n) ",
            lambda c: io.yes_or_no(c)
        )
        if conf != 'y':
            print("You can save and exit by typing 'exit'.")
        else:
            print("Quitting...")
            self.exit = True
            return True

    # ======= #
    # Parsers #
    # ======= #

    def match_course(self, line: str):
        '''
        Tries to match a course by any of its identifiers.

        Returns the course if found, and the line
        with the course identifier removed.
        '''
        if not line:
            return None, line
        
        line_ids = line.lower().split()

        matches = []
        for c in self.courses:
            course_ids = c.lower().split()
            # match the course if any ids intersect
            intersections = [id for id in line_ids if id in course_ids]
            if len(intersections) > 0:
                matches.append(c)
                
        if len(matches) == 1:
            course = matches[0]
            course_ids = course.lower().split()
            # remove identifiers from line
            line = list(filter(lambda id: id not in course_ids, line_ids))
            line = " ".join(line)

        else:
            course = None
        
        return course, line
    
    def match_grade(self, grade: str | float, course: str = "") -> float | None:
        '''
        Checks whether the grade is valid as a
        percentage or a scale key from the given course.

        Returns the grade as a percentage if valid.
        '''
        # try as scale key
        if course in self.courses.keys() and type(grade) == str:
            scale = self.courses[course]["scale"]
            scale_lower = {
                key.lower(): val for key, val in scale.items()
            }
            grade = grade.lower()
            if grade in scale_lower.keys():
                return scale_lower[grade]
            
        # try as percentage
        try:
            if type(grade) == str:
                grade = grade.replace("%", "")
            grade_f = float(grade)
            return grade_f if 0 <= grade_f <= 100 else None
        except ValueError:
            pass

        return None

    def parse_grade(self, line: str) -> tuple[str, str, int, int]:
        '''
        Parses all arguments for do_grade.
        If grade is -1, the user wishes to unset it.
        '''
        course, assessment, number, grade = None, None, None, None
        try:
            if not line:
                raise CmdParseException()
            
            course, line = self.match_course(line)
            if not course:
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
            
            if target is None and line:
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
    pg = PyGrades()

    # setup OS exit handlers
    if sys.platform == "win32":
        win32api.SetConsoleCtrlHandler(pg.handle_close, True)
    else:
        signal.signal(signal.SIGTERM, lambda signum, frame: pg.do_exit(""))

    pg.customloop()
