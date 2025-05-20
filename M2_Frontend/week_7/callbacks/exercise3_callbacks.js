// List of available light colors
const colors = [
	"red-light",
	"green-light",
	"blue-light",
	"yellow-light",
	"cyan-light",
	"pink-light",
];

// Get the button element
const button = document.getElementById("color-button");

// Function to get a random item from a list
const getRandomItem = (list) => {
	return list[Math.floor(Math.random() * list.length)];
};

// Variable to store the last color used
let lastColor = null;

// Function to change the light's color
const changeColor = () => {
	const light = document.getElementById("light");

	// Ensure the new color is different from the last color
	let color;
	do {
		color = getRandomItem(colors);
	} while (color === lastColor);

	// Update the last color
	lastColor = color;

	// Remove existing light-related classes and add the new color class
	light.className = light.className
		.split(" ")
		.filter((cls) => !cls.includes("light"))
		.join(" ");
	light.classList.add(color);
};

// Add a click event listener to the button
button.addEventListener("click", changeColor);
