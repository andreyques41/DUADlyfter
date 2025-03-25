HEADERS = ['Name', 'Section', 'Spanish score', 'English score', 'Socials score', 'Science score', 'Average score']
SUBJECTS = ['Spanish', 'English', 'Socials', 'Science']

class Student():
    name: str
    section: str
    scores: dict
    average_score: float
    def __init__(self, name: str = 'None', section: str = 'None', **scores: float):
        self.name = name
        self.section = section
        self.scores = scores
        self.average_score = sum(scores.values()) / len(scores) if scores else None

    def to_dict(self) -> dict:
        data = {
            'Name': self.name,
            'Section': self.section,
            'Average score': self.average_score
        }
        data.update({f"{subject.capitalize()} score": score for subject, score in self.scores.items()})
        return data

    def from_dict(self, dictionary: dict):
        try:
            self.name = dictionary['Name']
            self.section = dictionary['Section']
            self.average_score = dictionary['Average score']
            self.scores = {key.replace(' score', ''): float(value) for key, value in dictionary.items() if 'score' in key}
            return self
        except KeyError as ex:
            print(f'---Error: Missing key in data: {ex}. Required format: {HEADERS}')
            return None

def input_new_student() -> Student:
    name = get_non_empty_input('Name of student? \n')
    section = get_non_empty_input('Section of the student? \n')
    scores = {subject: get_valid_score(f"Score for {subject}? \n") for subject in SUBJECTS}
    
    return Student(name, section, **scores)

# Input information for multiple students until the user decides to stop
def input_students() -> list[Student]:
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
def get_valid_score(prompt: str, min_value: int = 0, max_value: int = 100) -> float:
    while True:
        try:
            value = float(input(prompt))
            if min_value <= value <= max_value:
                return value
            print(f'-----Error: Only values from {min_value} to {max_value} are allowed-----')
        except ValueError:
            print(f'-----Error: Input must be a number between {min_value} and {max_value}-----')

def get_non_empty_input(prompt: str) -> str:
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        print('-----Error: Input cannot be blank-----')

# Display all information for each student in the list
def show_all_info(students):
    for student in students:
        for attr, value in student.to_dict().items():
            print(f'{attr}: {value}')
        print('-' * 40)  # Add a separator for better readability

# Display the top 3 students based on their average scores
def show_top_students(students):
    try:
        top_students = sorted(students, key=lambda student: float(student.average_score), reverse=True)[:3]
        show_all_info(top_students)
    except Exception:
        print('-----Error: Average score must be a valid number-----')

# Calculate and display the average score of all students
def show_average_all_students(students):
    if students:
        average_score = sum(float(student.average_score) for student in students) / len(students)
        print(f'The average score of all students is: {average_score:.2f}')
    else:
        print('-----No students available to calculate the average score-----')