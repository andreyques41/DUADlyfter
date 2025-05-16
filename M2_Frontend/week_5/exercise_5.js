class Student {
	constructor(name, grades) {
		try {
			// Validate input: name must be a string, and grades must be an array
			if (!name || !grades || !Array.isArray(grades)) {
				throw new Error(
					"Invalid input: name must be a string and grades must be an array."
				);
			}
			this.name = name;

			// Calculate average, highest, and lowest grades
			const { avgGrade, highestGradeName, lowestGradeName } =
				this.calculateGrades(grades);
			this.avgGrade = avgGrade;
			this.highestGrade = highestGradeName;
			this.lowestGrade = lowestGradeName;
		} catch (error) {
			// Log any errors in the constructor
			console.error(`Error in constructor: ${error.message}`);
		}
	}

	calculateGrades(grades) {
		try {
			// Validate grades array
			if (!grades || !Array.isArray(grades) || grades.length === 0) {
				throw new Error("Grades must be a non-empty array.");
			}

			let total = 0;
			let highestGrade = 0;
			let highestGradeName = null;
			let lowestGrade = 100;
			let lowestGradeName = null;

			// Iterate through grades to calculate total, highest, and lowest grades
			for (let grade of grades) {
				// Validate each grade object
				if (
					!grade.hasOwnProperty("name") ||
					!grade.hasOwnProperty("grade") ||
					typeof grade.name !== "string" ||
					typeof grade.grade !== "number"
				) {
					throw new Error(
						`Invalid grade object: Each grade must have a 'name' (string) and 'grade' (number).`
					);
				}

				// Add grade to total
				total += grade.grade;

				// Update highest grade if current grade is higher
				if (grade.grade > highestGrade) {
					highestGrade = grade.grade;
					highestGradeName = grade.name;
				}

				// Update lowest grade if current grade is lower
				if (grade.grade < lowestGrade) {
					lowestGrade = grade.grade;
					lowestGradeName = grade.name;
				}
			}

			// Calculate average grade
			const avgGrade = total / grades.length;
			return { avgGrade, highestGradeName, lowestGradeName };
		} catch (error) {
			// Log any errors in grade calculation
			console.error(`Error in calculateGrades: ${error.message}`);
			return { avgGrade: 0, highestGradeName: null, lowestGradeName: null }; // Default values in case of error
		}
	}

	printStudentInfo() {
		try {
			// Print student information
			console.log(`Name: ${this.name}`);
			console.log(`Average Grade: ${this.avgGrade}`);
			console.log(`Highest Grade: ${this.highestGrade}`);
			console.log(`Lowest Grade: ${this.lowestGrade}`);
		} catch (error) {
			// Log any errors in printing student info
			console.error(`Error in printStudentInfo: ${error.message}`);
		}
	}
}

// Input
const inputStudent = {
	// Example student data
	name: "John Doe",
	grades: [
		{ name: "math", grade: 80 },
		{ name: "science", grade: 100 },
		{ name: "history", grade: 60 },
		{ name: "PE", grade: 90 },
		{ name: "music", grade: 98 },
	],
};

// Main function to execute the logic
function main() {
	try {
		// Create a new student and print their information
		const newStudent = new Student(inputStudent.name, inputStudent.grades);
		newStudent.printStudentInfo();
	} catch (error) {
		// Log any errors in the main function
		console.error(`Error in main: ${error.message}`);
	}
}

// Execute the main function
main();
