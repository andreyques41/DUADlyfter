const axios = require("axios");

// Create an axios instance for API requests
const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 1000,
});

// Fetch data from the API endpoint and return elements array
async function fetchElements(apiInstance) {
	try {
		const response = await apiInstance.get();
		if (response.status < 200 || response.status >= 300) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const elements = response.data;
		if (!Array.isArray(elements)) {
			throw new Error("API did not return an array");
		}
		return elements;
	} catch (error) {
		throw new Error(`Network or Axios error: ${error.message}`);
	}
}

// Filter elements that have a valid 'data' object property
function filterElementsWithData(elements) {
	return elements.filter(
		(element) =>
			element.data &&
			typeof element.data === "object" &&
			!Array.isArray(element.data) &&
			element.data !== null
	);
}

// Log each element's name and its data key-value pairs
function logElements(elements) {
	elements.forEach((element) => {
		const name = element.name || "Unnamed";
		const dataEntries = Object.entries(element.data)
			.map(([key, value]) => `${key}: ${value}`)
			.join(", ");
		console.log(`${name} (${dataEntries})`);
	});
}

// Main function to orchestrate fetching, filtering, and logging
async function getElementsWithData(apiInstance) {
	try {
		const elements = await fetchElements(apiInstance);
		const filteredElements = filterElementsWithData(elements);
		logElements(filteredElements);
	} catch (error) {
		console.log(`There was a problem: ${error.message}`);
	}
}

// Execute the main function
getElementsWithData(apiInstance);
