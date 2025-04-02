# PyGrades
A lightweight tool for tracking and assessing grades.

## Features

- View your performance and see what you need to do to reach your target grade.

- Save your data across sessions and track grades for multiple semesters.

- Specify course outlines, such as grading scales and drop policies.

## Usage

### Loading an Outline

The first time you install and run PyGrades, you will be prompted to load the example outline.

You can:
- Type `y` and press Enter to proceed with the example (recommended for new users).
- See [Creating an Outline]() and create your own outline.
  You will need to restart the program to see new files.

If you see the following, the outline was successfully loaded:
```
Loaded data for [filename].
Type help to list commands.
```

### Entering Grades

To enter a grade, type the command:
```
[π] > grade
```

You will then be guided through the process of selecting a grade to enter, like so:

![pygrades_grade](https://github.com/user-attachments/assets/6896f11a-d9dd-40bb-8b52-7cb19876db08)

The selection can be lengthy, so you can choose to provide the arguments yourself:
```
[π] > grade math 101 assignment 1 85%
Updated Math 101 Assignment 1 to 85.0%.
```
Not all arguments (or even full course names) have to be provided.
For example, you can enter `[π] > grade math` or `[π] > grade 101`
and PyGrades will guide you through the rest of the process.
This applies to **all commands** that require choosing a course.

**Note**: If you need to remove a grade, type `none` in place of the grade
and accept the confirmation. For example:
```
[π] > grade math 101 assignment 1 none
Assignment 1 already has the grade 85.0%. Overwrite it with None? (y/n) y
Updated Math 101 Assignment 1 to None.
```

### Viewing Stats

PyGrades provides multiple statistics and tables based on your grades.
See [Understanding Stats]() if you're unsure what any statistics mean.

The easiest way to see your progress in a specific course is with the `summary` command:
```
[π] > summary
1. Math 101
2. Chem 200
Please select a course: 1
╭────────────┬────────────────────────┬──────────────┬────────────┬──────────╮
│   Math 101 │ Grades                 │      Average │   Achieved │   Weight │
├────────────┼────────────────────────┼──────────────┼────────────┼──────────┤
│ Assignment │ 85, 90                 │      87.50 % │     8.75 % │     20 % │
│            │ (3 pending, 1 to drop) │              │            │          │
├────────────┼────────────────────────┼──────────────┼────────────┼──────────┤
│    Midterm │ 75                     │      75.00 % │    15.00 % │     40 % │
│            │ (1 pending)            │              │            │          │
├────────────┼────────────────────────┼──────────────┼────────────┼──────────┤
│      Final │ (1 pending)            │          n/a │        n/a │     40 % │
├────────────┼────────────────────────┼──────────────┼────────────┼──────────┤
│          • │ Weighted Totals:       │ (B+) 79.17 % │    23.75 % │    100 % │
╰────────────┴────────────────────────┴──────────────┴────────────┴──────────╯
```

Again, you can directly provide course names,
such as `[π] > summary math 101` or just `[π] > summary math`.

You can use `[π] > summary all` to quickly get
the summaries of all your courses.

The `overview` command will provide a simpler glance at your semeseter:
```
[π] > overview
╭───────────┬────────────────┬────────────╮
│   Example │   Wtd. Average │   Achieved │
├───────────┼────────────────┼────────────┤
│  Math 101 │   (B+) 79.17 % │    23.75 % │
├───────────┼────────────────┼────────────┤
│  Chem 200 │  (3.7) 93.10 % │    16.76 % │
╰───────────┴────────────────┴────────────╯
```

Lastly, if your courses have grading scales,
use `scale` to see exactly where you land:
```
[π] > scale
1. Math 101
2. Chem 200
Please select a course: 1
- Math 101
| A+    90%
| A     80%
| B+    75% <- Current (79.17%)
| B     70%
| C+    65%
| C     60%
| D     50%
```

### Calculating Projections

Beyond just seeing your current progress,
PyGrades can help you plan for the future.

The `needed` command will calculate the average grade you
need to get on your remaining assessments to achieve a certain grade.
You can enter this grade as either a percentage or scale item:
```
[π] > needed
1. Math 101
2. Chem 200
Please select a course: 1
Enter a target grade: A
80.67% needed on remaining assessments to achieve 80.0% (A).
```

In tandem, the `max` command will calculate the maximum
grade you can achieve, accounting for grades that could be dropped:
```
[π] > max
1. Math 101
2. Chem 200
Please select a course: 1
The maximum grade possible for Math 101 is 94.50% (A+)
```
