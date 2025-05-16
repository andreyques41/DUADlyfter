// Asynchronous function to fetch user data by ID
async function getUser(userId) {
	// 1. Log that the request is being sent
	console.log("1. Sending request");
	try {
		// 2. Await the server response
		const response = await fetch(`https://reqres.in/api/users/${userId}`);
		console.log("2. Response received");
		// 3. Parse the response as JSON
		const data = await response.json();
		console.log("3. Data received");
		if (response.ok) {
			// 4. Log user name and email if successful
			console.log(`Name: ${data.data.first_name} ${data.data.last_name}`);
			console.log(`Email: ${data.data.email}`);
		} else {
			// 5. Log error if response is not ok
			console.log(`Error: The user with id ${userId} does not exist`);
		}
	} catch (error) {
		// 6. Log any network or unexpected errors
		console.log(`3. There was a problem: ${error}`);
	}
	// 7. Log that the await is finished
	console.log("4. Await finished");
}

// Set user ID to fetch
const id = 23;
// Call the function to get user data
getUser(id);

// Log that the code reached the end
console.log("5. Code reached the end");
