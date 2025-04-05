# PyGrades
A command-line tool for students to track and assess their grades.

- Saves data between sessions.
- Tracks grades across multiple semesters.
- Supports custom grade scales and drop policies.
- Calculates important stats and projections.

Made by a student who hates spreadsheets.

<details open>
<summary>
<h2>Screenshots</h2>
</summary>
<p align="left">
  <!-- 541px width, 204px height -->
  <img 
    src="https://github.com/user-attachments/assets/293cbd77-de58-41f7-93c2-8a0999f5e92f"
    hspace="1"
  />
  <!-- 250px width, 204px height -->
  <img
    src="https://github.com/user-attachments/assets/cd31a129-2062-4fe7-9a2b-445392df9d11"
    hspace="3"
  />
  <!-- 800px width -->
  <img
    src="https://github.com/user-attachments/assets/9bbd73fd-69da-4bdb-8575-25897664e521"
    hspace="1"
  />
</p>
</details>

## Getting Started

The following guide provides plenty of tips on setting up and using PyGrades.
To get up and running, you only need to follow the steps up to (and including) **The Help Command**,
but reading the rest of the sections will let you get the most out of PyGrades.

**Make sure to also see [Creating an Outline](#creating-an-outline) to start tracking your grades.**

<details>
<summary>
<h3>Installation</h3><br>
PyGrades takes just a few steps to install.
</summary>
<br>

If you're on Windows, the simplest way to install and start using PyGrades
is by downloading `pygrades.Script.zip` from the
[latest release](https://github.com/ArnavG-it/pygrades/releases/latest).
Extract it anywhere on your computer and double-click the
`pygrades` application to launch it.

If you're on Mac or Linux, or just prefer running the script directly,
follow these steps:
1. Install a recent version of [Python 3](https://www.python.org/downloads/),
   if you don't have it already.
2. Download `pygrades.Script.zip` from the latest release and
   extract it anywhere on your computer.
3. Navigate to the extracted `pygrades` folder in your terminal.
4. Install the required packages using:
```
pip install -r requirements.txt
```
5. Start the program using:
```
python pygrades.py
```

(or the equivalent command for your Python version, such as `python3`)
</details>

<details>
<summary>
<h3>Loading Data</h3><br>
PyGrades can store and load from multiple data files.
</summary>
<br>

If PyGrades doesn't find any existing data, you will be asked to load the example outline.\
You can either:
- Type `y` and press Enter to proceed with the example (recommended for new users).
- See [Creating an Outline](#creating-an-outline) and create your own outline.
  You will need to restart the program to see the new outline.

If you do have existing data, you will be prompted to choose
which file to load (or to load a new outline if you wish).\
If you only have data from the example,
you can enter `y` to load the example data or `n` to create
new data from an outline:
```
Load data from Example? (Y/N)
```

If you see the following, the data was successfully loaded:
```
Loaded data for [filename].
Type help to list commands.
```

**Note**: Changes made to an outline after it has been loaded will not affect 
existing data. See [Updating a Loaded Outline](#updating-a-loaded-outline).
</details>

<details>
<summary>
<h3>The Help Command</h3><br>
The most important command.
</summary>

To see the list of commands that are available,
including some not discussed in this README
(such as `switch` and `quit`), type:
```
[π] > help
```
You can also quickly see the syntax of a specific command:
```
[π] > help grade
- Update a grade.

Optional arguments:
[course]         -> Course identifier
[assessment]     -> Assessment name
[number]         -> Assessment number, if there are multiple
[grade]          -> Received grade (can be "none")

Syntax: grade [course] [assessment] [number] [grade]
```

</details>

<details>
<summary>
<h3>Entering Grades</h3><br>
The most common action in a grade tracker.<br>
</summary>

To enter a grade, type the command:
```
[π] > grade
```

You will then be guided through the process of selecting a grade to enter, like so:

```
[π] > grade
1. Math 101
2. Chem 200
Please select a course: 1
Assessments for Math 101:
1. Assignment (0/5 graded)
2. Midterm (0/2 graded)
3. Final (pending)
Please select an assessment: 1
Grades for Assignment:
1. None
2. None
3. None
4. None
5. None
Please select which grade to update: 1
Enter the grade for Assignment 1: 85%
Updated Math 101 Assignment 1 to 85%.
```

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
</details>

<details>
<summary>
<h3>Viewing Stats</h3><br>
PyGrades provides multiple statistics and tables based on your grades.
</summary>

See [Interpreting Stats](#interpreting-stats) if you're unsure what any statistics mean.

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

You can use `[π] > summary all` to quickly see
the summaries of all your courses.

The `overview` command will provide a simpler glance at your semester:
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
</details>

<details>
<summary>
<h3>Calculating Projections</h3><br>
Beyond just seeing your current progress,
PyGrades can help you plan for the future.
</summary>
<br>
  
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
</details>

<details>
<summary>
<h3>Interpreting Stats</h3><br>
Understanding the stats is key to taking advantage of them.
</summary>

#### The Summary Table
The `summary` command calculates lots of numbers based on your grades.
The following example will be used for demonstration:
```
╭────────────┬─────────────────────────────┬───────────────┬────────────┬──────────╮
│   Chem 200 │ Grades                      │       Average │   Achieved │   Weight │
├────────────┼─────────────────────────────┼───────────────┼────────────┼──────────┤
│        Lab │ 80, 70, 90                  │       80.00 % │    12.00 % │     30 % │
│            │ (3 pending)                 │               │            │          │
├────────────┼─────────────────────────────┼───────────────┼────────────┼──────────┤
│       Quiz │ 90, 65, 80, 80, ~60~, 70    │       77.00 % │    15.40 % │     20 % │
│            │ (2 pending, 2 more to drop) │               │            │          │
├────────────┼─────────────────────────────┼───────────────┼────────────┼──────────┤
│      Final │ (1 pending)                 │           n/a │        n/a │     50 % │
├────────────┼─────────────────────────────┼───────────────┼────────────┼──────────┤
│          • │ Weighted Totals:            │ (2.3) 78.80 % │    27.40 % │    100 % │
╰────────────┴─────────────────────────────┴───────────────┴────────────┴──────────╯
```

In the **Grades** column, your grades for each assessment are listed in order.\
**Notes**:

- The number of pending grades and grades to be dropped are listed in brackets
for each assignment.
- If a grade is in tildes (such as `~60~`), it is one of your dropped grades
and doesn't count towards any calculations.
- Only the lowest excess grades are dropped. In the example above,
  5 quizzes are to be kept, but 6 have been graded, so one grade
  (`60%`) is dropped.

There are three stat columns: **Average**, **Achieved**, and **Weight**.\
These represent your progress in the course so far, your final grade
for the course, and the weight of each assessment, respectively.

- The **Average** column simply shows the average of your grades
  for an assessment, not counting assessments that haven't been graded yet.
  <details>
    <summary>Calculation</summary>

    - For the Lab assessment, of the three graded assessments, the average is `80%`.
    - For the Quiz assessment, since six quizzes are graded and only five are to
      be counted, the lowest grade of `60%` is dropped automatically.\
      The average of the remaining five is then `77%`.
    - The Final assessment hasn't been graded yet, so it has no average.
  </details>

- The **Weighted Total Average** in the last row shows how
  well you're doing in the course currently. It accounts for
  the weights of each assessment, and ignores ungraded assessments.
  <details>
    <summary>Calculation</summary>
  
    - For the Lab assessment, the weighted average is `80% x 30% = 24%`
    - For the Quiz assessment, the weighted average is `77% x 20% = 15.4%`
    - The total weight of the assessments (not counting the ungraded final)
      is `30% + 20% = 50%`.
    - Therefore, the weighted total average is `(24% + 15.4%) / 50% = 78.8%`.
  </details>

- The **Achieved** column shows how much your grades in each assessment
  contribute to the final grade. Dropped grades don't count towards this.
  <details>
    <summary>Calculation</summary>
  
    - For each assessment, the weighted average is multiplied by the number
      of graded assessments over the number of assessments that count towards the weight.
    - For the Lab assessment, the achieved weight is `80% x 30% x (3/6) = 24%`
    - For the Quiz assessment, the achieved weight is `77% x 20% x (5/5)= 15.4%`
    - The Final assessment has no grade, so it has no achieved weight.
  </details>

- The **Weighted Total Achieved** in the last row is the sum
  of the **Achieved** column. This is the total weight of the course you've secured,
  and it will likely be low until big assessments (like a final exam) have been graded.

- If your course has a grading scale,
  you will see the **corresponding grade** next to each weighted total
  (e.g., a `2.3` GPA corresponds to the weighted average of `78.80%`,
  and no grade corresponds to the achieved `27.40%`).
</details>

<details>
<summary>
<h3>Updating a Loaded Outline</h3><br>
PyGrades provides some commands for updating course outlines on the fly.
</summary>
<br>

**Note**: If you need to update the outline in a way
that isn't mentioned in this section, your options are
to:
- Modify the outline file and reload it. You will have
  to overwrite your save data corresponding to that outline
  (or change the name of the outline file to avoid this)
  and re-enter your grades.
- Modify the `data/[filename].json` file corresponding to your outline.
  This may corrupt your data, so **only do it if you are comfortable with JSON**
  (a backup is available in `data/backup/`).

<br>

For courses that have a grading scale,
you can change the minimum percentage of a grade:
```
[π] > adjust
```
For example:
```
[π] > adjust math A+ 87%
Move A+ from 90% to 87%? (y/n) y
Updated A+ for Math 101.
```

<br>

You can update the number of dropped grades
for an assessment using `dropnum`:
```
[π] > dropnum
```
For example:
```
[π] > dropnum math assignment 2
Drop 2 instead of 1 Assignment in Math 101? (y/n) y
Updated Assignment.
```
**Note**: PyGrades does not support dropping all grades of an assessment.
For example, you cannot drop all 5 out of 5 assignments.

</details>

<br>

## Creating an Outline

Before being able to track your own grades,
you need to provide a simple
outline file that describes your courses.

Create a text file in `outlines/` and give it a name.
This name could represent a specific semester, such as `Fall2025.txt`.

You can then just copy and paste the text
from `Example.txt` and replace the data with your own courses
(adding more courses as needed), or refer to the following
walkthrough for more detailed help.

**Note**: Your outline **must follow the correct formatting** in order to be read by the program.

<details>
<summary>
<h3>Outline Walkthrough</h3>
</summary>
  
Each course needs a name, assessments, and optionally a grading scale.
These categories have to be specified in that order.

#### Course Names

First, specify that you are providing a course name
by typing `Course:`, then provide the name on the next line.
For example:
```
Course:
Math 101
```

**Notes**: 
- The colon after `Course` is not required, but it helps with readability.
- Your courses can be named anything (except `all`, as that
is a keyword used in the command `[π] > summary all`).
- In the program, you can refer to courses by any
of their identifiers (either `math` or `101` in the above example),
so don't worry about making the names short.

#### Assessments

After your course name, add the line `Assessments:`, followed by
the assessments themselves.

First, specify the number of the particular assessment,
then its name, then its weight followed by a percent sign.
For example:
```
Assessments:
2 Midterm 40%
```
This line says that there are two midterms in the course,
with a weight of 40% (each midterm is worth 20% of the course grade.)

If the lowest grades of an assessment are to be dropped, specify
the number of dropped grades after the number of assessments, like so:
```
5 drop 1 Assignment 20%
```
This line says that there are five assignments, and one grade
will be dropped. The total weight is then distributed across the
remaining four assignments.

If your course has varying weights for the same assessment,
such as 25% for the better of two midterms and 15% for the worse,
make sure to list these with different names. For example:
```
1 Midterm-Better 25%
1 Midterm-Worse 15%
```

**Notes**:
- The total weight of the assessments for a course
  should add up to 100%.
- Each assessment should be on its own line.
- Assessments should not have spaces in their name.
  You can use dashes to combine words, like in the example above.

#### Grade Scales

If your course has one, you can provide a grade scale
(such as letter grades or GPAs).

First, specify the category with `Scale:`, and start your
scale on the next line.

For each grade, provide a name, then the **minimum percentage**
needed to achieve that grade, followed by a percent sign. For example:
```
Scale:
A+ 90%
A 80%
B+ 75%
B 70%
C+ 65%
C 60%
D 50%
```
The grade names can be anything, including decimal GPAs:
```
Scale:
4.0 94%
3.7 90%
... and so on
```

**Notes:**
- Each grade should be on its own line.
- Grades should not have spaces in their name. Consider
  using a colon or other characters if you wish to represent
  grade ranges (e.g., `A-:A+ 80%`).
- You might encounter inconsistent formatting
  when using the `[π] > scale` command if your grade names
  vary in length.
- Grades will be sorted in descending order by their percentage automatically.

#### Full Outline

After providing the assessments and optional grade scale
for a course, start the next course on the next line,
following the same steps.

Here is a full example of a valid outline (`outlines/Example.txt`):
```
Course:
Math 101

Assessments:
5 drop 1 Assignment 20%
2 Midterm 40%
1 Final 40%

Scale:
A+ 90%
A 80%
B+ 75%
B 70%
C+ 65%
C 60%
D 50%

Course:
Chem 200

Assessments:
6 Lab 30%
8 drop 3 Quiz 20%
1 Final 50%

Scale:
4.0 94%
3.7 90%
3.3 87%
3.0 83%
2.7 80%
2.3 77%
2.0 73%
1.7 70%
1.3 67%
1.0 60%
```
</details>

## Contributing
Feel free to open an issue if you encounter a bug
or want to see a new feature, or submit a pull request
if you have the solution!

[Back to Top](#pygrades)
