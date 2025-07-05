// --- Category Dropdown Management ---
// Populates all category dropdowns in the UI
console.log("categories.js loaded");

function populateAllCategoryDropdowns() {
	console.log(
		"populateAllCategoryDropdowns: Starting category dropdown population"
	);

	// Get all category items except the add button
	const catList = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	const categories = Array.from(catList).map((c) => c.textContent.trim());
	console.log("populateAllCategoryDropdowns: Found categories:", categories);

	if (categories.length === 0) {
		console.warn(
			"populateAllCategoryDropdowns: No categories found in sidebar"
		);
	}

	// Get all category selects (add/edit)
	const selects = [
		document.getElementById("sidebar-add-task-category"),
		document.getElementById("sidebar-edit-task-category"),
	].filter(Boolean);

	console.log(
		"populateAllCategoryDropdowns: Found",
		selects.length,
		"dropdown selects"
	);

	if (selects.length === 0) {
		console.warn(
			"populateAllCategoryDropdowns: No category select elements found"
		);
		return;
	}

	selects.forEach((select) => {
		console.log(
			`populateAllCategoryDropdowns: Populating select '${select.id}'`
		);
		select.innerHTML = '<option value="">Select category</option>';

		catList.forEach((cat) => {
			const option = document.createElement("option");
			option.value = cat.textContent.trim();
			option.textContent = cat.textContent.trim();
			select.appendChild(option);
		});

		console.log(
			`populateAllCategoryDropdowns: Added ${catList.length} options to select '${select.id}'`
		);
	});

	console.log(
		"populateAllCategoryDropdowns: All category dropdowns populated successfully"
	);
}

// Expose globally
window.populateAllCategoryDropdowns = populateAllCategoryDropdowns;

// Check availability of exposed functions
if (window.populateAllCategoryDropdowns) {
	console.log(
		"categories.js: populateAllCategoryDropdowns function is available"
	);
} else {
	console.warn(
		"categories.js: populateAllCategoryDropdowns function not found"
	);
}
