# Input a new student's information, including their name, section, scores, and average score
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

# Input information for multiple students until the user decides to stop
def input_students():
    students = []
    students.append(input_new_student())
    while True:
        extra_student_flag = get_non_empty_input('Do you want to add an extra student? (y/n) \n').lower()
        if extra_student_flag == 'y':
            students.append(input_new_student())
        elif extra_student_flag == 'n':
            break
        else:
            print('-----Error: Please enter "y" or "n"-----')
    return students

# Prompt the user to input a valid score within a specified range
def get_valid_score(prompt, min_value=0, max_value=100):
    while True:
        try:
            value = float(input(prompt))
            if min_value <= value <= max_value:
                return value
            print(f'-----Error: Only values from {min_value} to {max_value} are allowed-----')
        except ValueError:
            print(f'-----Error: Only values from {min_value} to {max_value} are allowed-----')

# Ensure the user provides a non-empty input
def get_non_empty_input(prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        print('-----Error: Input cannot be blank-----')

# Display all information for each student in the list
def show_all_info(students):
    for student in students:
        print("\n".join(f'{key}: {value}' for key, value in student.items()))
        print('-' * 40)  # Add a separator for better readability

# Display the top 3 students based on their average scores
def show_top_students(students):
    try:
        top_students = sorted(students, key=lambda student: float(student['Average score']), reverse=True)[:3]
        show_all_info(top_students)
    except Exception as ex:
        print('-----Error: Only integers are allowed in the Average score field from the CSV file-----')

# Calculate and display the average score of all students
def show_average_all_students(students):
    if students:
        average_score = sum(float(student['Average score']) for student in students) / len(students)
        print(f'The average score of all students is: {average_score:.2f}')
    else:
        print('-----No students available to calculate the average score-----')