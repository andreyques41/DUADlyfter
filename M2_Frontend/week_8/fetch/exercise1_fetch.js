// Fetch and process elements with a 'data' property

// Fetch data from API
async function fetchElements(url) {
	try {
		const response = await fetch(url);
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const elements = await response.json();
		if (!Array.isArray(elements)) {
			throw new Error("API did not return an array");
		}
		return elements;
	} catch (error) {
		throw new Error(`Network or fetch error: ${error.message}`);
	}
}

// Filter elements with valid 'data' object
function filterElementsWithData(elements) {
	return elements.filter(
		(element) =>
			element.data &&
			typeof element.data === "object" &&
			!Array.isArray(element.data) &&
			element.data !== null
	);
}

// Log filtered elements and their data
function logElements(elements) {
	elements.forEach((element) => {
		const name = element.name || "Unnamed"; // Fallback if name is missing
		const dataEntries = Object.entries(element.data)
			.map(([key, value]) => `${key}: ${value}`)
			.join(", ");
		console.log(`${name} (${dataEntries})`);
	});
}

// Main function to fetch, filter, and log
async function getElementsWithData() {
	try {
		const elements = await fetchElements(`https://api.restful-api.dev/objects`);
		const filteredElements = filterElementsWithData(elements);
		logElements(filteredElements);
	} catch (error) {
		console.log(`There was a problem: ${error.message}`);
	}
}

// Run main function
getElementsWithData();
