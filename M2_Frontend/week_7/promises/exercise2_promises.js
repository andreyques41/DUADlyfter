// Function to fetch and display the name of the first Pokémon whose fetch resolves
async function getPokemons(id1, id2, id3) {
	try {
		// Start fetching data for each Pokémon (returns promises)
		const response1 = fetch(`https://pokeapi.co/api/v2/pokemon/${id1}`);
		const response2 = fetch(`https://pokeapi.co/api/v2/pokemon/${id2}`);
		const response3 = fetch(`https://pokeapi.co/api/v2/pokemon/${id3}`);

		// Promise.any resolves as soon as the first promise fulfills (not rejects)
		const response = await Promise.any([response1, response2, response3]);
		// Check if the response is successful (status 200-299)
		if (response.ok) {
			// Parse JSON data from the first fulfilled response
			const data = await response.json();
			const name = data.name;

			// Print the name of the Pokémon from the first completed promise
			console.log(`Pokémon name of the first completed promise: ${name}`);
		} else {
			// If the first fulfilled response is not ok (rare), log error
			console.log("Error: Not a single Pokémon could be fetched.");
		}
	} catch (error) {
		// Handle network or other errors (e.g., all promises rejected)
		console.log(`There was a problem: ${error}`);
	}
}

// Call the function with three Pokémon IDs
getPokemons(2, 5, 7);
