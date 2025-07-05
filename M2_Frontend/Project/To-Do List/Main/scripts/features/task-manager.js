// --- Task Management Business Logic ---
// Handles task operations and business rules
console.log("task-manager.js loaded");

const TaskManager = {
    // Add a new task
    async addTask(taskData) {
        console.log("TaskManager.addTask: Adding task", taskData);
        
        const { name, date, category } = taskData;
        const section = AppUtils.getSectionForDate(date);
        
        if (!section) {
            console.warn("TaskManager.addTask: Date is not in a valid section");
            return false;
        }

        const newTask = {
            text: name,
            date: date,
            category: category,
            completed: false,
            createdAt: AppUtils.getCurrentTimestamp()
        };

        const allTasks = await getAllTasks();
        allTasks[section].push(newTask);
        saveAllTasks(allTasks);
        
        console.log(`TaskManager.addTask: Successfully added task to ${section}`);
        return true;
    },

    // Edit an existing task
    async editTask(section, index, taskData) {
        console.log(`TaskManager.editTask: Editing task ${index} in ${section}`, taskData);
        
        const allTasks = await getAllTasks();
        if (!allTasks[section] || !allTasks[section][index]) {
            console.warn("TaskManager.editTask: Invalid task reference");
            return false;
        }

        const { name, date, category } = taskData;
        const newSection = AppUtils.getSectionForDate(date);
        
        if (!newSection) {
            console.warn("TaskManager.editTask: Date is not in a valid section");
            return false;
        }

        const task = allTasks[section][index];
        task.text = name;
        task.date = date;
        task.category = category;
        task.updatedAt = AppUtils.getCurrentTimestamp();

        // If section changed, move the task
        if (newSection !== section) {
            allTasks[section].splice(index, 1);
            allTasks[newSection].push(task);
            console.log(`TaskManager.editTask: Moved task from ${section} to ${newSection}`);
        }

        saveAllTasks(allTasks);
        return true;
    },

    // Delete a task
    async deleteTask(section, index) {
        console.log(`TaskManager.deleteTask: Deleting task ${index} from ${section}`);
        
        const allTasks = await getAllTasks();
        if (!allTasks[section] || !allTasks[section][index]) {
            console.warn("TaskManager.deleteTask: Invalid task reference");
            return false;
        }

        const taskName = allTasks[section][index].text;
        allTasks[section].splice(index, 1);
        saveAllTasks(allTasks);
        
        console.log(`TaskManager.deleteTask: Successfully deleted "${taskName}"`);
        return true;
    },

    // Toggle task completion
    async toggleTaskCompletion(section, index) {
        console.log(`TaskManager.toggleTaskCompletion: Toggling task ${index} in ${section}`);
        
        const allTasks = await getAllTasks();
        if (!allTasks[section] || !allTasks[section][index]) {
            console.warn("TaskManager.toggleTaskCompletion: Invalid task reference");
            return false;
        }

        const task = allTasks[section][index];
        task.completed = !task.completed;
        task.updatedAt = AppUtils.getCurrentTimestamp();
        
        saveAllTasks(allTasks);
        console.log(`TaskManager.toggleTaskCompletion: Task "${task.text}" marked as ${task.completed ? 'completed' : 'incomplete'}`);
        return true;
    },

    // Get tasks for a specific section
    async getTasksForSection(section) {
        console.log(`TaskManager.getTasksForSection: Getting tasks for ${section}`);
        const allTasks = await getAllTasks();
        return allTasks[section] || [];
    },

    // Get task statistics
    async getTaskStats() {
        console.log("TaskManager.getTaskStats: Calculating task statistics");
        const allTasks = await getAllTasks();
        
        const stats = {
            today: {
                total: allTasks.today?.length || 0,
                completed: allTasks.today?.filter(t => t.completed).length || 0
            },
            tomorrow: {
                total: allTasks.tomorrow?.length || 0,
                completed: allTasks.tomorrow?.filter(t => t.completed).length || 0
            },
            thisweek: {
                total: allTasks.thisweek?.length || 0,
                completed: allTasks.thisweek?.filter(t => t.completed).length || 0
            }
        };

        const totalTasks = stats.today.total + stats.tomorrow.total + stats.thisweek.total;
        const totalCompleted = stats.today.completed + stats.tomorrow.completed + stats.thisweek.completed;
        
        stats.overall = {
            total: totalTasks,
            completed: totalCompleted,
            percentage: totalTasks > 0 ? Math.round((totalCompleted / totalTasks) * 100) : 0
        };

        console.log("TaskManager.getTaskStats: Stats calculated", stats);
        return stats;
    }
};

// Expose globally
window.TaskManager = TaskManager;

console.log("task-manager.js: Task management module loaded");
