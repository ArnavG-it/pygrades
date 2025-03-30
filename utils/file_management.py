import os
import glob
import json
import jsonschema

from utils import input_output as io

class OutlineParseError(Exception): pass

class DataFileError(Exception): pass

DATA_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "properties": {
            "assessments": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "weight": {"type": "number"},
                        "amount": {"type": "number"},
                        "dropped": {"type": "number"},
                        "grades": {
                            "type": "array",
                            "items": {
                                "type": ["number", "null"]
                            }
                        }
                    },
                    "required": ["weight", "amount", "dropped", "grades"]
                }
            },
            "scale": {
                "type": "object",
                "additionalProperties": {
                    "type": "number"
                }
            }
        },
        "required": ["assessments", "scale"]
    }
}

def setup_cmd() -> tuple[dict, str]:
    '''
    Sets up the CLI with valid data.
    Can raise SystemExit.

    Returns the data and filename without extension.
    '''
    setup_dirs()

    chosen_data = None
    while chosen_data is None:
        chosen_data = select_data()
        if not chosen_data:
            chosen_outline = select_outline()
            if not chosen_outline:
                print("No grade outline files were found. Please create one.")
                io.notify_and_exit()
            else:
                chosen_data = create_data(chosen_outline)

    data = load_data(chosen_data)

    if data is None:
        io.notify_and_exit()

    filename, _ = filename_from_path(chosen_data)

    return data, filename

def setup_dirs():
    if not os.path.exists("outlines"):
        os.mkdir("outlines")

    if not os.path.exists("data"):
        os.mkdir("data")

    backup_path = os.path.join("data", "backup")
    if not os.path.exists(backup_path):
        os.mkdir(backup_path)
        
    corrupt_path = os.path.join("data", "corrupt")
    if not os.path.exists(corrupt_path):
        os.mkdir(corrupt_path)

def filename_from_path(path) -> tuple[str, str]:
    filename = os.path.basename(path)
    [name, ext] = os.path.splitext(filename)
    return name, ext

def get_unique_filepath(path, name, ext) -> str:
    count = 1
    filepath = os.path.join(path, f"{name}{ext}")
    while os.path.exists(filepath):
        filepath = os.path.join(path, f"{name}({count}){ext}")
        count += 1
    return filepath

def validate_schema(data: dict) -> DataFileError | None:
    try:
        jsonschema.validate(data, DATA_SCHEMA)
        return None
    except jsonschema.ValidationError as e:
        return DataFileError(e)
    
def validate_json(filepath) -> DataFileError | None:
    with open(filepath, 'r') as f:
        try:
            d = json.load(f)
            return None
        except json.decoder.JSONDecodeError as e:
            return DataFileError(e)

def write_data(data, filename) -> bool:
    '''
    Writes to data/ and backs up old data.
    If data is corrupted, writes to data/corrupt/.
    Returns true if successful.
    '''
    path = "data"

    # backup existing data
    existing_filepath = os.path.join(path, filename) + ".json"
    if os.path.exists(existing_filepath):
        with open(existing_filepath, 'r') as f:
            backup_data = json.load(f)
        backup_path = os.path.join(path, "backup")
        backup_filepath = os.path.join(backup_path, f"{filename}(backup).json")
        with open(backup_filepath, 'w') as f:
            json.dump(backup_data, f, indent=4)

    # check for corrupted data
    error = validate_schema(data)
    if error:
        print("\nERROR: Data is corrupted:\n")
        print(error)
        print()
        # prepare corrupted file to be written
        path = os.path.join(path, "corrupt")
        filename += "(corrupted)"

    if ".json" not in filename:
        filename += ".json"

    filepath = os.path.join(path, filename)

    if error:
        # further prepare corrupted file
        name, ext = filename_from_path(filepath)
        filepath = get_unique_filepath(path, name, ext)
        print(f"NOTICE: Corrupted data will be written to {filepath}")
        print(f"NOTICE: No changes to {existing_filepath} were saved.")

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

    return error is None

def load_data(filepath) -> dict | None:
    data = {}

    # check for invalid JSON
    json_error = validate_json(filepath)
    if json_error:
        print("\nERROR: Invalid JSON syntax in data file:\n")
        print(json_error)
        print()
        continue_with_backup = handle_corrupted_load(filepath)
        if not continue_with_backup:
            return None

    with open(filepath, 'r') as f:
        data = json.load(f)

    # check for invalid data
    schema_error = validate_schema(data)
    if schema_error:
        print("\nERROR: Invalid schema in data file:\n")
        print(schema_error)
        print()
        cont = handle_corrupted_load(filepath)
        if cont:
            # continue with backup data if requested
            data = load_data(filepath)
        else:
            return None
    
    return data

def handle_corrupted_load(filepath) -> bool:
    '''
    Assumes the given filepath is corrupted.
    Creates a known corrupted version of the file,
    and tries to restore from backup.

    Returns whether there was a backup and the user
    wishes to continue with it.
    '''
    print()
    name, ext= filename_from_path(filepath)

    # write existing file to data/corrupt
    path = os.path.join("data", "corrupt")
    corrupt_filepath = get_unique_filepath(path, name + "(corrupt)", ext)
    os.rename(filepath, corrupt_filepath)

    print(f"NOTICE: Moved {filepath} to {corrupt_filepath}")

    # write backup to filepath
    backup_path = os.path.join("data", "backup")
    backup_filepath = os.path.join(backup_path, f"{name}(backup).json")
    if os.path.exists(backup_filepath):
        backup = {}
        with open(backup_filepath, 'r') as f:
            backup = json.load(f)
        write_data(backup, name)

        print(f"NOTICE: Restored data from backup.\n")

        cont = io.input_until_valid(
            "Continue with backup data? (y/n) ",
            lambda c: io.yes_or_no(c)
        )

        return cont == 'y'

    else:
        print("NOTICE: No backup data found. Quitting the program...")
        return False
    
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

        chosen_outline = outline_files[int(choice) - 1]
    
    return chosen_outline

def select_data() -> str | None:
    '''
    Finds a data file to load.
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

        if int(choice) > 0:
            return data_filepaths[int(choice) - 1]
        else:
            return None

def create_data(outline_filename) -> str | None:
    '''
    Creates a data file based on an outline.
    Will raise SystemExit if the outline is invalid.
    Returns the filepath of the created file.
    '''
    print(f"Creating data based on {outline_filename}...")
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

        if choice == 'n':
            return None

    course_data = parse_outline(outline_filename)
    
    if course_data is None:
        print("Please see the README for help creating an outline.")
        io.notify_and_exit()
    
    valid = validate_outline(course_data)

    if not valid:
        print("Please see the README for help creating an outline.")
        io.notify_and_exit()
    
    write_data(course_data, data_filename)

    return os.path.join("data", data_filename)

def parse_outline(filename) -> dict | None:
    '''
    Parses an outline file into a dictionary of courses.
    Returns None if the outline is invalid.
    '''
    courses = {}
    error = False
    with open(os.path.join("outlines", filename), "r") as f:
        current_course = None
        line_num = 0
        for line in f:
            line_num += 1
            line = line.strip()
            if line:
                try:
                    if line.startswith("Course "):
                        # Create a new course
                        current_course = line[len("Course "):]
                        if current_course == "all":
                            current_course = None
                            raise OutlineParseError(f"Course can not be named 'all'.")
                        courses[current_course] = {
                            "assessments": {},
                            "scale": {}
                        }

                    elif line[0].isdigit() and current_course:
                        # Add a grade item
                        parts = line.split()
                        
                        if len(parts) == 3:
                            amount, name, weight = parts[0], parts[1], parts[2]
                            drop, dropped = "", 0
                        elif len(parts) == 5:
                            amount, drop, dropped, name, weight = (
                                parts[0], parts[1], parts[2], parts[3], parts[4]
                            )
                        else:
                            raise OutlineParseError(f"Invalid assessment syntax: '{line}'")

                        try:
                            amount = int(amount)
                            dropped = int(dropped)
                            if len(parts) == 5 and drop != "drop":
                                raise OutlineParseError(f"Invalid assessment syntax: '{line}'")
                        except ValueError:
                            raise OutlineParseError(f"Non-numeric values: '{line}'")

                        if weight[-1] == '%' and weight[:-1].isnumeric():
                            weight = int(weight[:-1])
                        else:
                            raise OutlineParseError(f"Invalid weight: '{line}'")

                        courses[current_course]["assessments"][name] = {
                            "weight": weight,
                            "amount": amount,
                            "dropped": dropped,
                            "grades": [None] * amount
                        }

                    elif line[0] in "ABCDEF" and current_course:
                        # Add to the grade scale
                        parts = line.split()
                        if len(parts) != 2:
                            raise OutlineParseError(f"Invalid letter grade: '{line}'")
                        
                        letter, minimum = parts[0], int(parts[1])

                        courses[current_course]["scale"][letter] = minimum
                except OutlineParseError as e:
                    print(f"Error at line {line_num}:")
                    print(e)
                    error = True

    return courses if not error else None

def validate_outline(courses: dict) -> bool:
    '''Does numerical checks on course data to ensure it's sensible.'''
    schema_error = validate_schema(courses)
    if schema_error: return False

    error = False
    try:
        for c_name, course in courses.items():
            # sort the scale in descending order
            scale = course["scale"]
            course["scale"] = dict(sorted(
                scale.items(),
                key = lambda pair: pair[1],
                reverse = True
            ))

            total_weight = 0
            for a_name, a in course["assessments"].items():
                weight = a["weight"]
                assert weight > 0, (
                    f"Weight must be positive for {c_name} {a_name}."
                )

                total_weight += a["weight"]

                dropped = a["dropped"]
                assert dropped >= 0, (
                    f"Dropped amount is negative in {c_name} {a_name}."
                )

                assert a["amount"] > a["dropped"], (
                    f"Too many dropped assessments in {c_name} {a_name}."
                )
                
            assert total_weight == 100, (
                f"Total weight does not add up to 100% in {c_name}."
            )
    except AssertionError as e:
        print("\nERROR: Numerical inconsistency in outline:")
        print(e)
        print()
        error = True
    
    return not error