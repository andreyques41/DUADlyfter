// --- Task Management Business Logic ---
// Handles task operations and business rules using class-based approach
console.log("task-manager.js loaded");

// Task Class - Represents individual tasks with methods and properties
class Task {
	constructor(name, date, category, options = {}) {
		this.text = name;
		this.date = date;
		this.category = category || ""; // Default to empty string if no category
		this.completed = options.completed || false;
		this.createdAt = options.createdAt || AppUtils.getCurrentTimestamp();
		this.updatedAt = options.updatedAt || AppUtils.getCurrentTimestamp();

		console.log(
			`Task.constructor: Created task "${name}" for ${date} in category "${this.category}" (empty if no category)`
		);
	}

	// Mark task as complete
	complete() {
		if (!this.completed) {
			this.completed = true;
			this.updatedAt = AppUtils.getCurrentTimestamp();
			console.log(`Task.complete: Task "${this.text}" marked as completed`);
		}
		return this;
	}

	// Mark task as incomplete
	incomplete() {
		if (this.completed) {
			this.completed = false;
			this.updatedAt = AppUtils.getCurrentTimestamp();
			console.log(`Task.incomplete: Task "${this.text}" marked as incomplete`);
		}
		return this;
	}

	// Toggle completion status
	toggleCompletion() {
		this.completed = !this.completed;
		this.updatedAt = AppUtils.getCurrentTimestamp();
		console.log(
			`Task.toggleCompletion: Task "${this.text}" toggled to ${
				this.completed ? "completed" : "incomplete"
			}`
		);
		return this;
	}

	// Update task properties
	update(newData) {
		const oldData = {
			text: this.text,
			date: this.date,
			category: this.category,
		};

		if (newData.name) this.text = newData.name;
		if (newData.date) this.date = newData.date;
		// Handle category update - allow empty string
		if (newData.hasOwnProperty('category')) this.category = newData.category || "";

		this.updatedAt = AppUtils.getCurrentTimestamp();
		console.log(`Task.update: Updated task from`, oldData, `to`, {
			text: this.text,
			date: this.date,
			category: this.category,
		});
		return this;
	}

	// Get the section this task belongs to based on its date
	getSection() {
		const section = AppUtils.getSectionForDate(this.date);
		console.log(
			`Task.getSection: Task "${this.text}" belongs to section "${section}"`
		);
		return section;
	}

	// Convert task to plain object for storage
	toJSON() {
		return {
			text: this.text,
			date: this.date,
			category: this.category,
			completed: this.completed,
			createdAt: this.createdAt,
			updatedAt: this.updatedAt,
		};
	}

	// Create Task instance from stored data
	static fromJSON(data) {
		const task = new Task(data.text, data.date, data.category, {
			completed: data.completed,
			createdAt: data.createdAt,
			updatedAt: data.updatedAt,
		});
		console.log(`Task.fromJSON: Restored task "${data.text}" from storage`);
		return task;
	}

	// Validate task data
	static isValid(data) {
		// Category is optional - only text and date are required
		const isValid = !!(data.text && data.date);
		if (!isValid) {
			console.warn("Task.isValid: Invalid task data", data);
		}
		return isValid;
	}
}

const TaskManager = {
	// Add a new task using Task class
	async addTask(taskData) {
		console.log("TaskManager.addTask: Adding task", taskData);

		const { name, date, category } = taskData;

		// Validate input
		if (!Task.isValid({ text: name, date, category })) {
			console.warn("TaskManager.addTask: Invalid task data");
			return false;
		}

		// Create new Task instance
		const newTask = new Task(name, date, category);
		const section = newTask.getSection();

		if (!section) {
			console.warn("TaskManager.addTask: Date is not in a valid section");
			return false;
		}

		const allTasks = await getAllTasks();

		// Convert to plain object for storage
		allTasks[section].push(newTask.toJSON());
		saveAllTasks(allTasks);

		console.log(`TaskManager.addTask: Successfully added task to ${section}`);
		return true;
	},

	// Edit an existing task using Task class
	async editTask(section, index, taskData) {
		console.log(
			`TaskManager.editTask: Editing task ${index} in ${section}`,
			taskData
		);

		const allTasks = await getAllTasks();
		if (!allTasks[section] || !allTasks[section][index]) {
			console.warn("TaskManager.editTask: Invalid task reference");
			return false;
		}

		const { name, date, category } = taskData;

		// Validate input
		if (!Task.isValid({ text: name, date, category })) {
			console.warn("TaskManager.editTask: Invalid task data");
			return false;
		}

		// Create Task instance from stored data
		const task = Task.fromJSON(allTasks[section][index]);

		// Update task properties
		task.update({ name, date, category });
		const newSection = task.getSection();

		if (!newSection) {
			console.warn("TaskManager.editTask: Date is not in a valid section");
			return false;
		}

		// If section changed, move the task
		if (newSection !== section) {
			allTasks[section].splice(index, 1);
			allTasks[newSection].push(task.toJSON());
			console.log(
				`TaskManager.editTask: Moved task from ${section} to ${newSection}`
			);
		} else {
			// Update in place
			allTasks[section][index] = task.toJSON();
		}

		saveAllTasks(allTasks);
		return true;
	},

	// Delete a task
	async deleteTask(section, index) {
		console.log(
			`TaskManager.deleteTask: Deleting task ${index} from ${section}`
		);

		const allTasks = await getAllTasks();
		if (!allTasks[section] || !allTasks[section][index]) {
			console.warn("TaskManager.deleteTask: Invalid task reference");
			return false;
		}

		const taskData = allTasks[section][index];
		const task = Task.fromJSON(taskData);
		const taskName = task.text;

		allTasks[section].splice(index, 1);
		saveAllTasks(allTasks);

		console.log(`TaskManager.deleteTask: Successfully deleted "${taskName}"`);
		return true;
	},

	// Toggle task completion using Task class
	async toggleTaskCompletion(section, index) {
		console.log(
			`TaskManager.toggleTaskCompletion: Toggling task ${index} in ${section}`
		);

		const allTasks = await getAllTasks();
		if (!allTasks[section] || !allTasks[section][index]) {
			console.warn("TaskManager.toggleTaskCompletion: Invalid task reference");
			return false;
		}

		// Create Task instance and toggle completion
		const task = Task.fromJSON(allTasks[section][index]);
		task.toggleCompletion();

		// Update stored data
		allTasks[section][index] = task.toJSON();
		saveAllTasks(allTasks);

		console.log(
			`TaskManager.toggleTaskCompletion: Task "${task.text}" marked as ${
				task.completed ? "completed" : "incomplete"
			}`
		);
		return true;
	},

	// Get tasks by category from desired section
	async getTasksByCategory(category, section) {
		console.log(
			`TaskManager.getTasksByCategory: Getting tasks for category "${category}"`
		);
		const allTasks = await getAllTasks();
		const categoryTasks = [];

		const sectionTasks = allTasks[section] || [];
		const categoryInSection = sectionTasks
			.filter((data) => data.category === category)
			.map((data) => Task.fromJSON(data));

		categoryTasks.push(...categoryInSection);

		console.log(
			`TaskManager.getTasksByCategory: Found ${categoryTasks.length} tasks in category "${category}" from section "${section}"`
		);
		return categoryTasks;
	},
};

// Expose globally
window.Task = Task;
window.TaskManager = TaskManager;

console.log("task-manager.js: Task class and TaskManager module loaded");
