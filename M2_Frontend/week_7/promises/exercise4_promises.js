// Asynchronous function to fetch user data by ID
function getUser(userId) {
	// 1. Log that the request is being sent
	console.log("1. Sending request");
	fetch(`https://reqres.in/api/users/${userId}`, {
		headers: {
			"x-api-key": "reqres-free-v1", // Required API key header
		},
	})
		.then((response) => {
			console.log("2. Response received");
			return response.json().then((data) => ({ response, data }));
		})
		.then(({ response, data }) => {
			console.log("3. Data received");
			if (response.ok) {
				// 4. Log user name and email if successful
				console.log(`Name: ${data.data.first_name} ${data.data.last_name}`);
				console.log(`Email: ${data.data.email}`);
			} else {
				// 5. Log error if response is not ok
				console.log(`Error: The user with id ${userId} does not exist`);
			}
		})
		.catch((error) => {
			// 6. Log any network or unexpected errors
			console.log(`3. There was a problem: ${error}`);
		})
		.finally(() => {
			// 7. Log that the await is finished
			console.log("4. Await finished");
		});
}

// Set user ID to fetch
const id = 5;
// Call the function to get user data
getUser(id);

// Log that the code reached the end
console.log("5. Code reached the end");
