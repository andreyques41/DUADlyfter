// Function to fetch and display names of three Pokémon by their IDs
async function getPokemons(id1, id2, id3) {
	try {
		// Start fetching data for each Pokémon
		const response1 = fetch(`https://pokeapi.co/api/v2/pokemon/${id1}`);
		const response2 = fetch(`https://pokeapi.co/api/v2/pokemon/${id2}`);
		const response3 = fetch(`https://pokeapi.co/api/v2/pokemon/${id3}`);

		// Wait for all fetches to complete
		const responses = await Promise.all([response1, response2, response3]);
		// Check if all responses are successful
		if (responses.every((response) => response.ok)) {
			// Parse JSON data for all responses
			const data = await Promise.all(
				responses.map((response) => response.json())
			);

			const names = data.map((pokemon) => pokemon.name);

			// Print the name of each Pokémon
			console.log(`Pokémon names: ${names.join(" ")}`);
		} else {
			// Handle case where one or more fetches failed
			console.log("Error: One or more Pokémon could not be fetched.");
		}
	} catch (error) {
		// Handle network or other errors
		console.log(`There was a problem: ${error}`);
	}
}

// Call the function with three Pokémon IDs
getPokemons(2, 5, 7);
