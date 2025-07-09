// --- Category Event Listeners ---
// Handles all category-related event listeners and interactions
console.log("category-events.js loaded");

/**
 * Sets up event listeners for a category item (delete and click functionality)
 * @param {HTMLElement} categoryItem - The category item element
 */
function setupCategoryEventListeners(categoryItem) {
	console.log(
		"setupCategoryEventListeners: Setting up event listeners for category item"
	);

	const deleteButton = categoryItem.querySelector(".delete-icon");
	const categoryTextElement = categoryItem.querySelector(".cat-text");

	if (!deleteButton || !categoryTextElement) {
		console.error(
			"setupCategoryEventListeners: Required elements not found in category item"
		);
		return;
	}

	const categoryName = categoryTextElement.textContent.trim();

	// Delete button click handler
	deleteButton.addEventListener("click", async (event) => {
		event.stopPropagation();
		console.log(
			`setupCategoryEventListeners: Delete button clicked for category '${categoryName}'`
		);

		try {
			const deleteSuccess = await deleteCategory(categoryName);
			if (deleteSuccess) {
				console.log(
					`setupCategoryEventListeners: Category '${categoryName}' deleted successfully`
				);
			}
		} catch (error) {
			console.error(
				`setupCategoryEventListeners: Error deleting category '${categoryName}':`,
				error
			);
		}
	});

	// Category item click handler for filtering
	categoryItem.addEventListener("click", (event) => {
		// Don't trigger if delete button was clicked
		if (event.target.classList.contains("delete-icon")) {
			return;
		}

		console.log(
			`setupCategoryEventListeners: Category '${categoryName}' clicked for filtering`
		);

		// Call the category filter toggle function
		if (typeof window.CategoryFilter?.toggle === "function") {
			window.CategoryFilter.toggle(categoryName);
		} else {
			console.error("CategoryFilter.toggle function not found");
		}
	});

	console.log(
		`setupCategoryEventListeners: Event listeners set up for category '${categoryName}'`
	);
}

/**
 * Sets up the add category event listeners (using the simple add-list item)
 */
function setupAddCategoryEventListener() {
	console.log(
		"setupAddCategoryEventListener: Setting up add category event listeners"
	);

	const addCategoryItem = document.querySelector(".add-list");

	if (!addCategoryItem) {
		console.error(
			"setupAddCategoryEventListener: Add category element not found"
		);
		return;
	}

	// Click handler for the add category item
	addCategoryItem.addEventListener("click", async () => {
		console.log("setupAddCategoryEventListener: Add category item clicked");

		const categoryName = prompt("Enter a new category name:");

		if (categoryName && categoryName.trim()) {
			const trimmedName = categoryName.trim();
			try {
				const addSuccess = await addNewCategory(trimmedName);
				if (addSuccess) {
					console.log(
						`setupAddCategoryEventListener: Category '${trimmedName}' added successfully`
					);
				}
			} catch (error) {
				console.error(
					`setupAddCategoryEventListener: Error adding category '${trimmedName}':`,
					error
				);
			}
		} else if (categoryName !== null) {
			// User clicked OK but entered empty string
			console.warn(
				"setupAddCategoryEventListener: Empty category name provided"
			);
			alert("Please enter a category name.");
		}
		// If categoryName is null, user clicked Cancel - do nothing
	});

	console.log(
		"setupAddCategoryEventListener: Add category event listeners set up successfully"
	);
}

/**
 * Initializes all category event listeners
 */
function initializeCategoryEventListeners() {
	console.log(
		"initializeCategoryEventListeners: Initializing all category event listeners"
	);

	// Set up event listeners for existing category items
	const existingCategoryItems = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);

	existingCategoryItems.forEach((categoryItem) => {
		setupCategoryEventListeners(categoryItem);
	});

	// Set up add category event listeners
	setupAddCategoryEventListener();

	// Update add button state
	updateAddCategoryButtonState();

	console.log(
		`initializeCategoryEventListeners: Event listeners initialized for ${existingCategoryItems.length} categories`
	);
}

// Expose functions globally
window.setupCategoryEventListeners = setupCategoryEventListeners;
window.setupAddCategoryEventListener = setupAddCategoryEventListener;
window.initializeCategoryEventListeners = initializeCategoryEventListeners;
