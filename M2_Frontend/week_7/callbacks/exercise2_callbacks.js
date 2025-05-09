const fs = require("fs");
const path = require("path");

// Define file paths for the two text files
const file1Path = path.join(__dirname, "text_file1.txt");
const file2Path = path.join(__dirname, "text_file2.txt");

// Function to compare data from two files and log common lines
const compareData = (err, data2, data1) => {
	if (err) {
		console.error("Error reading text_file2.txt:", err);
		return;
	}

	// Split file contents into lines
	let linesData1 = data1.split("\r\n");
	let linesData2 = data2.split("\r\n");

	// Find and log common lines between the two files
	const msg = linesData1
		.filter((value) => linesData2.includes(value))
		.join(" ");
	console.log(msg);
};

// Read the first file and then the second file, passing their data to compareData
fs.readFile(file1Path, "utf8", (err, data1) => {
	if (err) {
		console.error("Error reading text_file1.txt:", err);
		return;
	}
	fs.readFile(file2Path, "utf8", (err, data2) =>
		compareData(err, data2, data1)
	);
});
