# PyGrades
A command-line tool for students to track and assess their grades.
</p>

- Saves data between sessions.
- Tracks grades across multiple semesters.
- Supports custom grade scales and drop policies.
- Calculates important stats and projections.

<details open>
<summary>
<h2>Screenshots</h2>
</summary>
<p align="left">
  <!-- 570px width, 214px height -->
  <img 
    src="https://github.com/user-attachments/assets/5b3432ba-8bfe-4cfa-bfda-813fe1b862ac"
    hspace="2"
  />
  <!-- 261px width, 214px height -->
  <img
    src="https://github.com/user-attachments/assets/523e9d12-e833-4141-98f6-eeff27e909b3"
    hspace="2"
  />
  <!-- 840px width -->
  <img
    src="https://github.com/user-attachments/assets/9df471bd-446c-4b10-bb0b-17d428b34eed"
    hspace="2"
  />
</p>
</details>

## Getting Started

The following dropdowns provide plenty of tips on setting up and using PyGrades.

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
existing data. Reloading the outline will overwrite existing data for that semester,
and the program will ask for confirmation before doing so.
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
</details>

<details>
<summary>
<h3>Viewing Stats</h3><br>
PyGrades provides multiple statistics and tables based on your grades.
</summary>

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


## Creating an Outline

Before being able to track your own grades,
you will have to provide a simple
outline file that describes your courses.

Create a text file in `outlines/` and give it a name.
This name could represent a specific semester, such as `Winter2025.txt`.

Your outline **must have the correct formatting** in order to be
correctly read by the program. You can simply copy and paste the text
from `Example.txt` and replace the data with your own courses
(adding more courses as needed), and/or refer to the following guide.

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
- Your courses can be named anything (except for `all`, as that
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
Scale
4.0 94%
3.7 90%
... and so on
```

**Notes:**
- Each grade should be on its own line.
- Grades should not have spaces in their name. Consider
  using a colon or other characters if you wish to represent
  grade ranges \
  (ex. `A-:A+ 80%`).
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
