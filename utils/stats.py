def achieved_weight(assessment: dict):
    '''Returns the achieved weight of the assessment, in percent.'''
    weight = int(assessment["weight"])
    amount = int(assessment["amount"])
    grades = assessment["grades"]

    points = 0
    for grade in grades:
        if grade:
            points += grade

    achieved_weight = points / (amount * 100) * weight

    return achieved_weight

def interim_weight(assessment: dict):
    '''
    Returns the achieved weight of the assessment,
    ignoring ungraded assessments, in percent.
    '''
    grades = assessment["grades"]
    grades = list(filter(lambda g: g is not None, grades))
    return average(grades)

def average(l: list):
    if len(l) == 0:
        return 0
    sum = 0
    for n in l:
        sum += n
    return sum / len(l)

def filter_dropped(assessment: dict) -> tuple[list, list]:
    grades = assessment["grades"]
    num_to_drop = assessment["dropped"]
    dropped = []

    for grade in grades:
        if grade is not None:
            if len(dropped) < num_to_drop:
                dropped.append(grade)
            elif grade < max(dropped):
                dropped[dropped.index(max(dropped))] = grade

    for grade in dropped:
        grades.remove(grade)

    return grades, dropped

