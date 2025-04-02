import os
import glob
import json

from utils import input_output as io
from utils.outline_parser import OutlineParser
from utils.validation import (
    validate_json, validate_outline, validate_schema,
    handle_creation_error, DATA_TEMPLATE
)

def setup_cmd(startup = True) -> tuple[dict, str]:
    '''
    Sets up the CLI with valid data.
    Can raise SystemExit.

    Returns the data and filename without extension.
    '''
    setup_dirs()

    chosen_data = None
    while chosen_data is None:
        chosen_data = select_data(startup)
        if not chosen_data:
            chosen_outline = select_outline()
            if chosen_outline and "Example" in chosen_outline:
                choice = io.input_until_valid(
                    "Load the example? (Y/N) ",
                    lambda c: io.yes_or_no(c),
                    repeat_message = "Invalid input. Load the example? (Y/N) "
                )
            else: choice = ''
            if not chosen_outline or choice == 'n':
                print("Please see the README for help with creating an outline.")
                io.notify_and_exit()
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

def select_data(startup = True) -> str | None:
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
        # avoid prompting for the file that was just switched from
        if not startup: return None

        message = f"Load data from {data_filenames[0][:-len(".json")]}? (Y/N) "
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

    parser = OutlineParser()
    course_data = parser.parse(outline_filename)
    error = validate_outline(course_data)

    if course_data is None:
        io.notify_and_exit()

    if error is not None:
        handle_creation_error(error, course_data)
    
    write_data(course_data, data_filename)

    return os.path.join("data", data_filename)
