// --- Category Dropdown Management ---
// Populates all category dropdowns in the UI
console.log("categories.js loaded");
function populateAllCategoryDropdowns() {
	console.log("Populating all category dropdowns...");
	// Get all category items except the add button
	const catList = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	console.log(
		"Found categories:",
		Array.from(catList).map((c) => c.textContent.trim())
	);
	// Get all category selects (add/edit)
	const selects = [
		document.getElementById("sidebar-add-task-category"),
		document.getElementById("sidebar-edit-task-category"),
	].filter(Boolean);
	console.log(
		"Populating selects:",
		selects.map((s) => s.id)
	);
	selects.forEach((select) => {
		select.innerHTML = '<option value="">Select category</option>';
		catList.forEach((cat) => {
			const option = document.createElement("option");
			option.value = cat.textContent.trim();
			option.textContent = cat.textContent.trim();
			select.appendChild(option);
			console.log(
				`Added category option '${option.value}' to select '${select.id}'`
			);
		});
	});
	console.log("All category dropdowns populated.");
}

// Expose globally
window.populateAllCategoryDropdowns = populateAllCategoryDropdowns;
