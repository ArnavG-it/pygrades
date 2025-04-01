import json
import jsonschema

import utils.input_output as io

class DataError(Exception): pass

DATA_SCHEMA = {
    "type": "object",
    "minProperties": 1,
    "additionalProperties": {
        "type": "object",
        "minProperties": 1,
        "properties": {
            "assessments": {
                "type": "object",
                "minProperties": 1,
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
                "minProperties": 1,
                "additionalProperties": {
                    "type": "number"
                }
            }
        },
        "required": ["assessments", "scale"]
    }
}

DATA_TEMPLATE = {
    "Course Name": {
        "assessments": {
            "weight": "number",
            "amount": "number",
            "dropped": "number",
            "grades": ["null", "null", "..."]
        },
        "scale": {
            "grade": "minimum",
            "...": "..."
        }
    }
}

def validate_schema(data: dict) -> jsonschema.ValidationError | None:
    try:
        jsonschema.validate(data, DATA_SCHEMA)
        return None
    except jsonschema.ValidationError as e:
        return e
    
def validate_json(filepath) -> json.decoder.JSONDecodeError | None:
    with open(filepath, 'r') as f:
        try:
            d = json.load(f)
            return None
        except json.decoder.JSONDecodeError as e:
            return e
        
def validate_outline(courses: dict) -> (
    jsonschema.ValidationError | AssertionError | None
):
    '''Does checks on course data to ensure it's sensible.'''
    try:
        error = validate_schema(courses)
        if error:
            path = list(error.path)
            if len(path) == 2:
                course = path[0]
                field = path[1]

                if field == "assessments":
                    assert False, (
                        f"No assessments found for {course}."
                    )

                # try to fill empty scale
                if field == "scale":
                    courses[course]["scale"] = {"None": 0}
                    return validate_outline(courses)
        else:
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

        """ except jsonschema.ValidationError as e:
        path = list(error.path)
        if len(path) == 2:
            course = path[0]
            field = path[1]

            if field == "assessments":
                # this doesn't get caught, maybe move to try
                assert False, (
                    f"No assessments found for {course}."
                )

            # try to fill empty scale
            if field == "scale":
                courses[course]["scale"] = {"None": 0}
                validate_outline(courses)
                return
        error = e """
        
    except AssertionError as e:
        error = e
    
    return error

def handle_creation_error(error, data):
    '''Provide error messages and exit the program.'''
    print("\nERROR: Error while generating data.\n")

    if isinstance(error, jsonschema.ValidationError):
        print("This is the data generated from the outline:\n")
        print(json.dumps(data, indent=2))

        print("\nCorrect data should look like:")
        print(json.dumps(DATA_TEMPLATE, indent=2))
        print("\nThe first error found was:")
        field = " -> ".join(str(x) for x in error.path) if error.path else "Root"
        print(f"Invalid format in '{field}'.")
        print(f"Reason: {error.message}")

    elif isinstance(error, AssertionError):
        print("Error in provided course data:")
        print(error)
        print("\nNote that the error may be due to incorrect formatting in the outline.")

    else:
        print(error)

    print("\nPlease see the README for help with creating an outline.")
    io.notify_and_exit()