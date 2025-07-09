// --- Category UI Components ---
// Handles category display, colors, and visual elements
console.log("category-ui.js loaded");

// Simple color list for categories
const COLORS = ["green", "red", "blue", "yellow", "purple"];

/**
 * Gets the color class for a category
 * @param {string} categoryName - Name of the category
 * @returns {string} CSS color class name
 */
function getCategoryColorClassName(categoryName) {
	if (!categoryName) return "blue";

	// Find the category in sidebar and get its color
	const categoryItems = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	for (const item of categoryItems) {
		const categoryText = item.querySelector(".cat-text");
		if (categoryText && categoryText.textContent.trim() === categoryName) {
			return item.getAttribute("data-category-color") || "blue";
		}
	}

	return "blue"; // Default if not found
}

/**
 * Gets the next available color for a new category
 * @returns {string} Available color class name
 */
function getNextAvailableColor() {
	const usedColors = new Set();

	// Get all colors currently used
	const categoryItems = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	categoryItems.forEach((item) => {
		const color = item.getAttribute("data-category-color");
		if (color) usedColors.add(color);
	});

	// Return first unused color, or cycle through if all used
	for (const color of COLORS) {
		if (!usedColors.has(color)) return color;
	}

	return COLORS[categoryItems.length % COLORS.length];
}

/**
 * Creates a visual display element for a category
 * @param {string} categoryName - Name of the category
 * @returns {HTMLElement} Category display element
 */
function createCategoryDisplay(categoryName) {
	console.log(
		`createCategoryDisplay: Creating display for category '${categoryName}'`
	);

	const categoryItem = document.createElement("li");
	categoryItem.className = "cat-item";

	// Get the next available color for this new category
	const colorName = getNextAvailableColor();
	categoryItem.setAttribute("data-category-color", colorName);

	categoryItem.innerHTML = `
		<span class="category-color-box category-color-${colorName}"></span>
		<span class="cat-text">${categoryName}</span>
		<button class="delete-icon" aria-label="Delete category">
			&times;
		</button>
	`;

	console.log(
		`createCategoryDisplay: Created display for category '${categoryName}' with color ${colorName}`
	);
	return categoryItem;
}

/**
 * Updates the state of the add category item based on current category count
 */
function updateAddCategoryButtonState() {
	console.log("updateAddCategoryButtonState: Updating add category item state");

	const addCategoryItem = document.querySelector(".add-list");

	if (!addCategoryItem) {
		console.warn(
			"updateAddCategoryButtonState: Add category element not found"
		);
		return;
	}

	const canAddMore = canAddMoreCategories();

	// Update item state and appearance
	if (canAddMore) {
		addCategoryItem.style.pointerEvents = "auto";
		addCategoryItem.style.opacity = "1";
		addCategoryItem.title = "Click to add new category";
		addCategoryItem.classList.remove("disabled");
	} else {
		addCategoryItem.style.pointerEvents = "none";
		addCategoryItem.style.opacity = "0.5";
		addCategoryItem.title = "Maximum 10 categories allowed";
		addCategoryItem.classList.add("disabled");
	}

	console.log(`updateAddCategoryButtonState: Item enabled: ${canAddMore}`);
}

// Expose functions globally
window.getCategoryColorClassName = getCategoryColorClassName;
window.createCategoryDisplay = createCategoryDisplay;
window.updateAddCategoryButtonState = updateAddCategoryButtonState;
