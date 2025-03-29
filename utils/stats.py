def achieved_weight(assessment: dict):
    '''Returns the achieved weight of the assessment, in percent.'''
    weight = int(assessment["weight"])
    amount = assessment["amount"] - assessment["dropped"]

    kept, _ = filter_dropped(assessment)

    points = 0
    for grade in kept:
        if grade:
            points += grade

    achieved_weight = points / (amount * 100) * weight

    return achieved_weight

def interim_weight(grades: list):
    '''
    Returns the achieved weight of the assessment,
    ignoring ungraded assessments, in percent.
    '''
    grades = filter_ungraded(grades)
    return average(grades)

def average(l: list):
    if len(l) == 0:
        return 0
    sum = 0
    for n in l:
        sum += n
    return sum / len(l)

def total_graded_weight(assessments: dict):
    '''Calculates the weight of the course that has been graded.'''
    total = 0
    for name, data in assessments.items():
        grades = data["grades"]
        weight = data["weight"]
        _, dropped = filter_dropped(data)
        to_drop = data["dropped"] - len(dropped)
        graded = len(filter_ungraded(grades))
        total += graded / ((len(grades) - to_drop)) * weight
    return total

def total_weighted_average(assessments: dict):
    '''Calculates the achieved weighted average of a course.'''
    completed_weight = 0
    total = 0
    for name, data in assessments.items():
        weight = data["weight"]
        kept, _ = filter_dropped(data)
        total += interim_weight(kept) * weight / 100
        if len(filter_ungraded(kept)) > 0:
            completed_weight += data["weight"]

    if completed_weight > 0:
        total /= completed_weight
    total *= 100

    return total

def total_achieved(assessments: dict):
    '''Calculates the achieved weight of a course.'''
    return (
        total_weighted_average(assessments)
        * total_graded_weight(assessments)
        / 100
    )

def needed_for_target(assessments: dict, target_grade) -> float | None:
    '''
    Returns the average needed on each remaining grade
    to achieve the target grade.
    Returns None if no ungraded assessments remain.
    '''
    achieved_weighted_sum = 0
    remaining_fraction_sum = 0

    for _name, a in assessments.items():
        # calculate number of ungraded assessments
        kept, dropped = filter_dropped(a)
        to_keep = a["amount"] - a["dropped"]
        completed_grades = filter_ungraded(kept)
        incomplete = to_keep - len(completed_grades)

        # handle potential grades that could be dropped
        to_drop = a["dropped"] - len(dropped)
        if incomplete == 0:
            incomplete += to_drop

        # accumulate sums
        weight = a["weight"]
        achieved_weighted_sum += achieved_weight(a) * 100
        remaining_fraction_sum += incomplete / to_keep * weight

    if remaining_fraction_sum == 0:
        return None
    
    x = (target_grade * 100 - achieved_weighted_sum) / remaining_fraction_sum

    return x

def filter_dropped(assessment: dict, maximize = True) -> tuple[list, list]:
    '''
    Returns two lists: grades after dropping, and the dropped grades.
    By default, keeps as many grades as possible.
    If maximize is false, drops as many as possible.
    '''
    grades: list = assessment["grades"][:]
    dropped = []

    filtered_grades = filter_ungraded(grades)

    num_graded = len(filtered_grades)
    num_total = len(grades)
    num_dropped = assessment["dropped"]
    if maximize:
        num_to_drop = max(0, num_graded - (num_total - num_dropped))
    else:
        num_to_drop = num_dropped

    if num_to_drop > 0:
        for grade in filtered_grades:
            if len(dropped) < num_to_drop:
                dropped.append(grade)
            elif grade < max(dropped):
                dropped[dropped.index(max(dropped))] = grade

        for grade in dropped:
            grades.remove(grade)

    return grades, dropped

def get_letter_grade(course: dict, grade: float):
    scale = course["scale"].items()
    letter_grade = None
    maximum = 0
    for letter, value in scale:
        if grade >= value and value > maximum:
            maximum = value
            letter_grade = letter
    return letter_grade

def filter_ungraded(grades: list):
    return list(filter(
        lambda grade: grade is not None,
        grades
    ))