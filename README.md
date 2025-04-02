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

![grade_full_scaled](https://github.com/user-attachments/assets/47a9fb19-981a-4a34-8c3f-bd8db2a5a717)

The selection can be lengthy, so you can choose to provide the arguments yourself:
```
[π] > grade math 101 assignment 1 100%
Updated Math 101 Assignment 1 to 100%.
```
Not all arguments (or even full course names) have to be provided.
For example, you can enter `[π] > grade math` or `[π] > grade 101`
and PyGrades will guide you through the rest of the process.

**Note**: If you need to remove a grade, type `none` in place of the grade
and accept the confirmation. For example:
```
[π] > grade math 101 assignment 1 none
Assignment 1 already has the grade 100.0%. Overwrite it with None? (y/n) y
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
╭────────────┬────────────────────────┬─────────────┬────────────┬──────────╮
│   Math 101 │ Grades                 │     Average │   Achieved │   Weight │
├────────────┼────────────────────────┼─────────────┼────────────┼──────────┤
│ Assignment │ 100, 85                │     92.50 % │     9.25 % │     20 % │
│            │ (3 pending, 1 to drop) │             │            │          │
├────────────┼────────────────────────┼─────────────┼────────────┼──────────┤
│    Midterm │ 82.5                   │     82.50 % │    16.50 % │     40 % │
│            │ (1 pending)            │             │            │          │
├────────────┼────────────────────────┼─────────────┼────────────┼──────────┤
│      Final │ (1 pending)            │         n/a │        n/a │     40 % │
├────────────┼────────────────────────┼─────────────┼────────────┼──────────┤
│          • │ Weighted Totals:       │ (A) 85.83 % │    25.75 % │    100 % │
╰────────────┴────────────────────────┴─────────────┴────────────┴──────────╯
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
│  Math 101 │    (A) 85.83 % │    25.75 % │
├───────────┼────────────────┼────────────┤
│  Chem 200 │  (2.3) 78.20 % │    14.08 % │
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
| A     80% <- Current (85.83%)
| B+    75%
| B     70%
| C+    65%
| C     60%
| D     50%
```
