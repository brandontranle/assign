#!/usr/bin/env python3
'''
Change in this one is a best effort to auto-assign, once it is performed,
you have the ability to manually assign.

There are defaults to make it easy to test, hitting return on a query
gets the default.
Students n= 10 (A - J).
Projects n=10 (a - j)
Team projects default to 0, which means the Simple Ring Assignment algorithm,
which is the one I sent in powerpoint.
# of assessments per student is 3

Students are capital letters and projects are lowercase.
The same letter corresponds Student <==> Project as in A <==> a, B <==> b etc.

If teams are entered, enter each group of projects separated by a space,
then a comma to indicate a new team. For example, 3 teams, a b c, f g, h j

I calculate the number of assessments per project and display
so one can see where projects are over/under-subscribed. The default is 3,
which is where most of my testing has been, things will probably break where
we get near the boundary condition of Projects - # of team projects

Finally, I provide the ability to edit the assessments until there is a
reasonable distribution of assessments.

Take a look when you get the chance. I still need to do some significant
refactoring or put into a Jupyter notebook…
'''

from collections import defaultdict, Counter
import testdata


# get input for students, projects, teams and  maximum assessments/student
s_prompt = 'Enter Students, (defaults from testdata.py):\n'
students = input(s_prompt).split()
p_prompt = 'Enter Projects in Student order, (defaults from testdata.py):\n'
projects = input(p_prompt).split()
t_prompt = 'Enter Team Projects by pairs, (default, none): format 0 1,3 4\n'
teams = input(t_prompt).split(",")
AsmtsPerStudent = input("Enter assessments per student (default = 3):")
possible_projects = defaultdict(list)
asmtbyStudent = defaultdict(list)
projsByStudent = defaultdict(list)

distribution = Counter()
assessments = Counter()

partners = []
team_students = []
too_few = []
too_many = []


# DEFAULT DATA
# Provide default data if no data is entered
# print all values to be used
print(f"\nValues to be used for Assessment Assignments")
if not students:
    students = testdata.students
print(f"{students=}")
if not projects:
    projects = testdata.projects
print(f"{projects=}")
total_projects = len(projects)
print(f"Total Projects: {total_projects}")
if teams == ['']:
    print(f"No teams were identified. Use a simple ring assignment algorithm.")
    Teams = False
else:
    Teams = True
    team_projects = len(teams)
if not AsmtsPerStudent:
    AsmtsPerStudent = 3
else:
    AsmtsPerStudent = int(AsmtsPerStudent)
print(f"Assessements per student: {AsmtsPerStudent}")


def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n:
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y:
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """

    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s %s|%s: ' % (prompt, 'Y', 'n')
    else:
        prompt = '%s %s|%s: ' % (prompt, 'N', 'y')

    while True:
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


# Simple assignment algorithm for initial assignments
# Use a ring counter "ring_n" to assign the next project then
# loop back to zero once end of projects has been reached.
# This will assign all possible projects to each student,
# excepting the student's project, starting with the next
# project in the list
def ring_assignments():
    for s_index, student in enumerate(students):
        ring_n = s_index + 1
        for p_index, project in enumerate(projects):
            if ring_n == total_projects:
                ring_n = 0
            if p_index != s_index:
                possible_projects[student].append(projects[ring_n])
                ring_n += 1


# asmtbyStudent: for each student, show the assessments assigned
# limited by AsmtsPerStudent
def get_asmts():
    [asmtbyStudent[student].append(values[i])
     for student, values in possible_projects.items()
     for i in range(AsmtsPerStudent)]


def print_asmts():
    print(f"\nStudent Assessments Assigned")
    for student, asmts in asmtbyStudent.items():
        print(f"{student}: ", end="")
        for asmt in asmts:
            print(f"{asmt} ", end="")
        print()
    [print(f"{i} {distribution[i]}") for i in sorted(distribution)]


# identify the students in each team
def get_teamStudents():
    [partners.append(team.split()) for team in teams]
    print(f"Number of teams: {len(partners)} ", end="")
    for index, partner in enumerate(partners):
        print(f" Team {index}: ", end="")
        for project in partner:
            print(f"{students[getStudent(project)[0]]} ", end="")
            team_students.append(students[getStudent(project)[0]])
    print()


# for each student, identify all projects they are associated with
def get_projsByStudent():
    global projsByStudent
    projsByStudent = {students[i]: list(project)
                      for i, project in enumerate(projects)}
    for team_projs in partners:
        for project in team_projs:
            student = students[getStudent(project)[0]]
            for conflict in team_projs:
                if conflict not in projsByStudent[student]:
                    projsByStudent[student].append(conflict)


# Given a project, returns the index of the student who worked on project
def getStudent(proj):
    return([i for i, project in enumerate(projects)
            if proj == projects[i]])


def print_conflicts():
    print(f"Student Assessment Conflicts")
    for student, projects in projsByStudent.items():
        print(f"{student}:", end="")
        [print(f"{project} ", end="") for project in projects]
        print()


def remove_conflicts():
    for student in team_students:
        for asmt in asmtbyStudent[student]:
            if asmt in projsByStudent[student]:
                asmtbyStudent[student].remove(asmt)


def man_reassign():
    print(f"")
    print(f"Manual assignment: (Add or Change) ")
    print(f"Add: Enter student and assessment to add, as in: A b<cr>, ")
    print(f"Change: Enter student, current assessment, ", end="")
    print(f" new assessment, as in : A b c < cr >")
    Change = True
    while(Change):
        change = input("Add: A b or Change: A b c or <enter> to quit:").split()
        if not change:
            Change = False
        if len(change) == 2:
            if change[1].startswith("-"):
                asmtbyStudent[change[0]].remove(change[1].strip("-"))
            else:
                asmtbyStudent[change[0]].append(change[1].strip("+"))
        if len(change) == 3:
            print(f"{asmtbyStudent[change[0]]}")
            asmtbyStudent[change[0]].remove(change[1])
            asmtbyStudent[change[0]].append(change[2])


# distribution: for each project, update then show the assessment count
def get_distribution():
    distribution.clear()
    for student, values in asmtbyStudent.items():
        distribution.update(values)


# create lists too_few/too_many to show how many projects are
# under/over assigned
def check_distribution():
    too_few.clear()
    too_many.clear()
    for project, count in distribution.items():
        if count < AsmtsPerStudent:
            for i in range(AsmtsPerStudent - count):
                too_few.append(project)
        if count > AsmtsPerStudent:
            for i in range(count - AsmtsPerStudent):
                too_many.append(project)


def auto_reassign():
    for student, asmts in asmtbyStudent.items():
        if len(asmts) < AsmtsPerStudent:
            for project in too_few:
                if project not in projsByStudent[student] and\
                        project not in asmts:
                    asmtbyStudent[student].append(project)
                    too_few.remove(project)


# begin assigning assessments,
# start with simple ring assignments
ring_assignments()

# if no teams exist, keep the ring assignments limited by asmts/student
# print the assessments by student then the count of each assessment
if not Teams:
    get_asmts()
    get_distribution()
    print_asmts()

# if teams have been identified for project:
else:
    # identify the students which are in a team
    get_teamStudents()

    # get the projects on which a student has worked, this creates conflicts
    # as a student can't assess their own work
    get_projsByStudent()

    # for each student in a team, limit the assignments by asmts/student
    # then remove the conflicting assessment(s) for a student in a team
    get_asmts()
    remove_conflicts()

    # assign asmts/student and count the number of asmts/project
    # print_asmts()

    # get the distribution and print it
    get_distribution()

    check_distribution()
    if (too_few or too_many):
        auto_reassign()
        get_distribution()
        print_asmts()

        REASSIGN = True
        while(REASSIGN):

            # Offer opportunity to re-assign projects to students
            # check_distribution()
            request = confirm(
                prompt="Manually assign assessments to students?")

            if request:
                man_reassign()
                get_distribution()
                print_asmts()

            else:
                REASSIGN = False
