# Function to input a new student's information
def input_new_student():
    subjects = ['Spanish', 'English', 'Socials', 'Science']
    name = get_non_empty_input('Name of student? \n')
    section = get_non_empty_input('Section of the student? \n')
    scores = {f"{subject} score": get_valid_score(f"Score for {subject}? \n") for subject in subjects}
    average_score = sum(scores.values()) / len(subjects)

    return {
        "Name": name,
        "Section": section,
        **scores,
        "Average score": float(average_score)
    }

def input_students():
    students = []
    students.append(input_new_student())
    while True:
        extra_student_flag = get_non_empty_input('Do you want to add an extra student? (y/n) \n').lower()
        if extra_student_flag == 'y':
            students.append(input_new_student())
        elif extra_student_flag == 'n':
            return students
        else:
            print('-----Error: Please enter "y" or "n"-----')

# Prompt the user to input a positive integer.
def get_valid_score(prompt):
    while True:
        try:
            value = float(input(prompt))
            if 0 <= value <= 100:
                return value
            print('-----Error: Only values from 0 to 100 are allowed-----')
        except ValueError:
            print('-----Error: Only values from 0 to 100 are allowed-----')

# Helper function to ensure input is not blank
def get_non_empty_input(prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        print('-----Error: Input cannot be blank-----')

# Function to display all information about students
def show_all_info(students):
    for student in students:
        for key, value in student.items():
            print(f'{key}: {value}', end='\t')
        print()  # Add a newline after each student's info

# Function to display the top-performing students
def show_top_students(students):
    try:
        top_students = sorted(students, key=lambda student: float(student['Average score']), reverse=True)[:3]
        show_all_info(top_students)
    except Exception as ex:
        print('-----Error: Only integers are allowed in the Average score field from the CSV file-----')

# Function to calculate and display the average performance of all students
def show_average_all_students(students):
    if students:
        try:
            average_score = sum(float(student['Average score']) for student in students) / len(students)
            print(f'The average score of all students is: {average_score}')
        except Exception as ex:
            print('-----Error: Only integers are allowed in the Average score field from the CSV file-----')
    else:
        print('-----No students available to calculate the average score-----')
