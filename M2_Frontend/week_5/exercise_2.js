const listOfNumbers = [2, 4, 5, 2, 6, 33, 75, 44]; // Initialize an array of numbers.

console.log("Original list:\n", listOfNumbers); // Log the original list of numbers.

let evenNumbers = []; // Initialize an empty array to store even numbers.

// Use a for loop to filter even numbers from the list.
for (let i = 0; i < listOfNumbers.length; i++) {
	if (listOfNumbers[i] % 2 === 0) evenNumbers.push(listOfNumbers[i]);
}

console.log("Only pair list with For method:\n", evenNumbers); // Log the filtered list using the for loop.

evenNumbers = []; // Reset the array for the next method.

// Use the filter function to filter even numbers from the list.
evenNumbers = listOfNumbers.filter((number) => number % 2 === 0);

console.log("Only pair list with Filter function:\n", evenNumbers); // Log the filtered list using the filter function.
