// Returns a promise that resolves with 'word' after 'time' milliseconds
function getWordByTime(word, time) {
	return new Promise((resolve) => {
		setTimeout(() => resolve(word), time);
	});
}

// Arrays of words and corresponding times (as numbers)
const words = ["very", "Dogs", "cute", "are"];
const delays = [300, 100, 400, 200];
const resolvedInOrder = [];

// Run all promises in parallel, pushing results in order of array
Promise.all(
	words.map(async (word, i) => {
		const result = await getWordByTime(word, delays[i]);
		resolvedInOrder.push(result);
	})
).then(() => {
	// Log the results after all promises have resolved
	console.log(resolvedInOrder);
});
