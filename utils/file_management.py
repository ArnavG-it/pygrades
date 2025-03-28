import os
import glob
import json
import jsonschema

from utils import io
from utils.constants import LETTER_GRADES, DATA_SCHEMA

class OutlineParseError(Exception): pass

def setup_dirs():
    if not os.path.exists("outlines"):
        os.mkdir("outlines")
    if not os.path.exists("data"):
        os.mkdir("data")

def filename_from_path(path) -> tuple[str, str]:
    filename = os.path.basename(path)
    [name, ext] = os.path.splitext(filename)
    return name, ext

def validate_schema(data: dict) -> bool:
    try:
        jsonschema.validate(data, DATA_SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        print(e.message)
        return False
    
def validate_json(filepath) -> bool:
    with open(filepath, 'r') as f:
        try:
            d = json.load(f)
            return True
        except json.decoder.JSONDecodeError as e:
            print(e)
            return False

def write_data(data, filename):
    if not validate_schema(data):
        print("\nERROR: Data is corrupted.")
        filename += "--corrupted"
        print(f"Corrupted data will be written to {filename}.json")

    if ".json" not in filename:
        filename += ".json"
    filepath = os.path.join("data", filename)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_data(filepath) -> dict | None:
    if not validate_json(filepath):
        print("ERROR: Invalid JSON syntax in data file.")
        return None
    with open(filepath, 'r') as f:
        data = json.load(f)
        if not validate_schema(data):
            print("ERROR: Invalid schema in data file.")
            return None
        return data

def select_outline() -> str | None:
    '''
    Finds an outline file (with help from the user, if needed).
    Returns the name of the file, if found.
    '''
    outline_files = glob.glob("outlines/*.txt")
    outline_files = [os.path.basename(path) for path in outline_files]

    chosen_outline = None

    if len(outline_files) == 1:
        chosen_outline = outline_files[0]

    elif len(outline_files) > 1:
        print("Found multiple grade outline files:")
        print(io.numbered_list(outline_files))

        choice = io.input_until_valid(
            "Please choose one to load: ",
            repeat_message = "Invalid input. Please choose one to load: ",
            func = lambda c:
                io.in_range(c, 1, len(outline_files) + 1)
        )

        io.clear_lines(len(outline_files) + 2)

        chosen_outline = outline_files[int(choice) - 1]
    
    return chosen_outline

def select_data() -> str | None:
    '''
    Finds a data file to load, or goes to creation if none exist.
    Returns the filepath, if found.
    '''
    data_filepaths = glob.glob("data/*.json")
    data_filepaths = list(filter(lambda f: "corrupted" not in f, data_filepaths))
    data_filenames = [os.path.basename(f) for f in data_filepaths]

    if len(data_filenames) == 0:
        return None
    
    elif len(data_filenames) == 1:
        message = f"Load {data_filenames[0][:-len(".json")]}? (Y/N) "
        choice = io.input_until_valid(
            message = message,
            repeat_message = "Invalid input. " + message,
            func = lambda c:
                io.yes_or_no(c)
        )

        io.clear_lines(1)

        if choice == 'y':
            return data_filepaths[0]
        else:
            return None

    else:
        print("Multiple data files found:")
        print(io.numbered_list(data_filenames))

        message = "Choose one to load (0 to load a new outline): "
        choice = io.input_until_valid(
            message = message,
            repeat_message = "Invalid input. " + message,
            func = lambda c:
                io.in_range(c, 0, len(data_filenames) + 1)
        )

        io.clear_lines(len(data_filenames) + 2)

        if int(choice) > 0:
            return data_filepaths[int(choice) - 1]
        else:
            return None

def create_data(outline_filename) -> str | None:
    '''
    Creates a data file based on an outline.
    Returns the filepath of the created file.
    '''
    filename_without_extension = os.path.splitext(outline_filename)[0]

    data_files = glob.glob("data/*.json")
    data_files = [os.path.basename(path) for path in data_files]

    data_filename = filename_without_extension + ".json"

    if data_filename in data_files:
        message = f"Data corresponding to {data_filename} already exists. Overwrite it? (Y/N) "
        choice = io.input_until_valid(
            message = message,
            repeat_message = "Invalid input. " + message,
            func = lambda c:
                io.yes_or_no(c)
        )

        io.clear_lines(1)

        if choice == 'n':
            return None

    course_data = parse_outline(outline_filename)

    write_data(course_data, data_filename)

    return os.path.join("data", data_filename)

def parse_outline(filename) -> dict:
    '''Parses an outline file into a dictionary of courses.'''
    courses = {}
    with open(os.path.join("outlines", filename), "r") as f:
        current_course = None
        line_num = 0
        for line in f:
            line_num += 1
            line = line.strip()
            if line:
                if line.startswith("Course "):
                    # Create a new course
                    current_course = line[len("Course "):]
                    courses[current_course] = {
                        "assessments": {},
                        "scale": {}
                    }

                elif line[0].isdigit() and current_course:
                    # Add a grade item
                    try:
                        parts = line.split()
                        if len(parts) != 3:
                            raise OutlineParseError()
                        
                        amount, name, weight = parts[0], parts[1], parts[2]

                        if amount.isnumeric():
                            amount = int(amount)
                            dropped = 0
                        elif 'd' in amount:
                            parts = amount.split('d')
                            total, dropped = parts[0], parts[1]
                            if not (
                                total.isnumeric() and dropped.isnumeric()
                                and int(dropped) < int(total)
                            ):
                                raise OutlineParseError()
                            amount = int(total)
                            dropped = int(dropped)

                        if weight[-1] == '%' and weight[:-1].isnumeric():
                            weight = int(weight[:-1])
                        else:
                            raise OutlineParseError()

                        courses[current_course]["assessments"][name] = {
                            "weight": weight,
                            "amount": amount,
                            "dropped": dropped,
                            "grades": [None] * amount
                        }
                    except OutlineParseError as e:
                        print(f"Error parsing line {line_num}, '{line}'")

                elif line[0] in "ABCDEF" and current_course:
                    # Add to the grade scale
                    try:
                        parts = line.split()
                        if len(parts) != 2:
                            raise OutlineParseError()
                        
                        letter, minimum = parts[0], int(parts[1])

                        if letter not in LETTER_GRADES or minimum > 100:
                            raise OutlineParseError()

                        courses[current_course]["scale"][letter] = minimum
                    except OutlineParseError as e:
                        print(f"Error parsing line {line_num}, '{line}'")

    return courses
