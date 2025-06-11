// Asynchronous function to fetch and process elements with 'data' property

// Fetch data from the API endpoint
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

// Filter elements that have 'data' property, is an object, not array, and not null
function filterElementsWithData(elements) {
	return elements.filter(
		(element) =>
			element.data &&
			typeof element.data === "object" &&
			!Array.isArray(element.data) &&
			element.data !== null
	);
}

// Log the filtered elements with their data entries
function logElements(elements) {
	elements.forEach((element) => {
		const name = element.name || "Unnamed"; // Fallback if name is missing
		const dataEntries = Object.entries(element.data)
			.map(([key, value]) => `${key}: ${value}`)
			.join(", ");
		console.log(`${name} (${dataEntries})`);
	});
}

// Main function to orchestrate fetching, filtering, and logging
async function getElementsWithData() {
	try {
		const elements = await fetchElements(`https://api.restful-api.dev/objects`);
		const filteredElements = filterElementsWithData(elements);
		logElements(filteredElements);
	} catch (error) {
		console.log(`There was a problem: ${error.message}`);
	}
}

// Call the function to execute the fetch and log process
getElementsWithData();
