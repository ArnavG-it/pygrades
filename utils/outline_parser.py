import os

class OutlineParseError(Exception): pass

class OutlineParser:
    # Uses state pattern
    def parse(self, filename) -> dict | None:
        self.state = None
        self.line = None
        self.line_num = 1
        self.courses = {}
        self.current_course = None
        error = False

        try:
            with open(os.path.join("outlines", filename), "r") as f:
                for line in f:
                    if line:
                        self.line = line.strip()
                        transitioned = self._state_transition()
                        if self.line and not transitioned:
                            self._state_process()
                        self.line_num += 1

        except OutlineParseError as e:
            print(f"\nERROR at line {self.line_num}:")
            print(e)
            print()
            error = True

        return self.courses if not error else None

    def _state_transition(self):
        transitioned = True
        if self.line.lower().startswith("course"):
            self.state = "COURSE"
        elif self.line.lower().startswith("assessments"):
            self.state = "ASSESSMENTS"
        elif self.line.lower().startswith("scale"):
            self.state = "SCALE"
        else:
            transitioned = False
        return transitioned

    def _state_process(self):
        match self.state:  
            case "COURSE":
                self._parse_course()
            case "ASSESSMENTS":
                self._parse_assessments()
            case "SCALE":
                self._parse_scale()

    def _parse_course(self):
        if self.line == "all":
            raise OutlineParseError(f"Course cannot be named 'all'.")
        self.courses[self.line] = {
            "assessments": {},
            "scale": {}
        }
        self.current_course = self.line
        self.state = None

    def _parse_assessments(self):
        if not self.line[0].isdigit():
            raise OutlineParseError(f"Invalid assessment syntax: {self.line}")
        
        parts = self.line.split()  

        if len(parts) == 3:
            amount, name, weight = parts[0], parts[1], parts[2]
            drop, dropped = "", 0
        elif len(parts) == 5:
            amount, drop, dropped, name, weight = (
                parts[0], parts[1], parts[2], parts[3], parts[4]
            )
        else:
            raise OutlineParseError(f"Invalid assessment syntax: '{self.line}'")

        try:
            amount = int(amount)
            dropped = int(dropped)
            if len(parts) == 5 and drop != "drop":
                raise OutlineParseError(f"Invalid assessment syntax: '{self.line}'")
        except ValueError:
            raise OutlineParseError(f"Non-numeric values: '{self.line}'")

        if weight[-1] == '%' and weight[:-1].isnumeric():
            weight = int(weight[:-1])
        else:
            raise OutlineParseError(f"Invalid weight: '{self.line}'")

        self.courses[self.current_course]["assessments"][name] = {
            "weight": weight,
            "amount": amount,
            "dropped": dropped,
            "grades": [None] * amount
        }

    def _parse_scale(self):
        parts = self.line.split()
        if len(parts) != 2:
            raise OutlineParseError(f"Invalid grade: '{self.line}'")
        
        grade, minimum = parts[0], parts[1]

        minimum = minimum.replace("%", "")
        minimum = int(minimum)

        self.courses[self.current_course]["scale"][grade] = minimum
