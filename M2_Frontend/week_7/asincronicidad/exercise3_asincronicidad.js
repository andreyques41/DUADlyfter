// Display user info in the HTML
const sendUserInfo = (userName, userEmail) => {
	const userNameElem = document.getElementById("user-name");
	userNameElem.textContent = "User: " + userName;
	const userEmailElem = document.getElementById("user-email");
	userEmailElem.textContent = "Email: " + userEmail;
};

// Fetch user data asynchronously from Reqres API
async function getUser(userId) {
	try {
		const response = await fetch(`https://reqres.in/api/users/${userId}`, {
			headers: {
				"x-api-key": "reqres-free-v1", // Required API key header
			},
		});
		const data = await response.json();
		if (response.ok && data.data) {
			const user = data.data;
			const userName = `${user.first_name} ${user.last_name}`;
			const userEmail = user.email;
			sendUserInfo(userName, userEmail);
		} else {
			alert(`Error: The user with id ${userId} does not exist`);
		}
	} catch (error) {
		console.log(`There was a problem: ${error}`);
	}
}

// Handle button click: get user ID and fetch user data
const loginUser = () => {
	const userId = document.getElementById("user-input").value;
	if (userId) {
		getUser(userId);
	} else {
		alert("Please enter a user ID");
	}
};

// Add event listener to the submit button
const button = document.getElementById("submit-button");
button.addEventListener("click", loginUser);
