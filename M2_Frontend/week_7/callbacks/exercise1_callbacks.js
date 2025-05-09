// Function to evaluate if a number is even or odd and call the appropriate callback
const evaluateNumber = (number, function1, function2) => {
	// If the number is even, call function1
	if (number % 2 === 0) {
		function1();
	} else {
		// If the number is odd, call function2
		function2();
	}
};

// Callback function to handle even numbers
const functionEven = (number) => {
	console.log(`The number ${number} is even!`);
};

// Callback function to handle odd numbers
const functionOdd = (number) => {
	console.log(`The number ${number} is odd!`);
};

// Test the evaluateNumber function with a sample input
let number = 23;
evaluateNumber(
	number,
	() => functionEven(number),
	() => functionOdd(number)
);
