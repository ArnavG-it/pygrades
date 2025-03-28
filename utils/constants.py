LETTER_GRADES = ["A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"]

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