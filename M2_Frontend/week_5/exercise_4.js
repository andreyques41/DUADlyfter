function splitString(inputString, splitBy) {
	let newString = "";
	let listOfWords = [];

	// Iterate through each character in the string and split it using 'splitBy' as a separator
	for (let char of inputString) {
		if (char !== splitBy)
			newString += char; // Append character to the current word
		else {
			listOfWords.push(newString); // Add the current word to the list
			newString = ""; // Reset for the next word
		}
	}

	// Add the last word to the list (if any)
	if (newString) listOfWords.push(newString);

	return listOfWords;
}

// Main function to execute the logic
function main() {
	const inputString = "This is a string!"; // Example input string
	console.log("Example string:\n", inputString); // Log the input string

	const listOfWords = splitString(inputString, " "); // Split the string into words by spaces
	console.log("List of words from string:\n", listOfWords); // Log the list of words
}

// Execute the main function
main();
