const listOfCelsiusTemperatures = [38, 44, 30, 22, 77]; // Initialize an array of Celsius temperatures.

console.log("List of Celsius Temperatures:\n", listOfCelsiusTemperatures); // Log the list of Celsius temperatures.

// Convert the Celsius temperatures to Fahrenheit using the map function.
const listOfFahrenheitTemperatures = listOfCelsiusTemperatures.map(
	(temp) => (temp * 9) / 5 + 32 // Formula to convert Celsius to Fahrenheit.
);

console.log("List of Fahrenheit Temperatures:\n", listOfFahrenheitTemperatures); // Log the list of Fahrenheit temperatures.
