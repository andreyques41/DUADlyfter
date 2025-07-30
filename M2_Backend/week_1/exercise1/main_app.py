from flask import Flask, request, jsonify
import logging
from json_handler import read_json, write_json
from task_manager import tasks_to_json, save_tasks, load_tasks, validate_task_data
from models import Task, State

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './tasks.json'

@app.route("/gettasks", methods=["GET"])
def get_tasklist():
    try:
        tasks = load_tasks(DB_PATH, Task)

        state_filter = request.args.get("state")
        if state_filter:
            # Validate state filter against enum values
            valid_states = [state.value for state in State]
            if state_filter not in valid_states:
                return jsonify({"error": f"Invalid state. Valid options: {valid_states}"}), 400

            filtered_tasks = [task for task in tasks if task.state.value == state_filter]
            return tasks_to_json(filtered_tasks)
        else:
            return tasks_to_json(tasks)
    except Exception as e:
        logger.error(f"Error retrieving tasks: {e}")
        return jsonify({"error": "Failed to retrieve tasks"}), 500

@app.route("/addtask", methods=["POST"])
def add_new_task():
    request_body = request.json
    
    # Validate request body
    is_valid, error_message = validate_task_data(request_body)
    if not is_valid:
        logger.error(f"Validation failed: {error_message}")
        return jsonify({"error": error_message}), 400
    
    try:
        # Load existing tasks
        existing_tasks = load_tasks(DB_PATH, Task)
        
        # Create new task
        new_task = Task.from_dict(request_body)
        
        # Check if task ID already exists
        for task in existing_tasks:
            if task.id == new_task.id:
                logger.error(f"Task with ID {new_task.id} already exists")
                return jsonify({"error": f"Task with ID {new_task.id} already exists"}), 409
        
        # Add new task and save
        existing_tasks.append(new_task)
        save_tasks(existing_tasks, DB_PATH)
        
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid task data format: {e}")
        return jsonify({"error": "Invalid task data format"}), 400
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return jsonify({"error": "Failed to add task"}), 500

    return tasks_to_json(existing_tasks)

@app.route("/updatetask", methods=["PUT"])
def update_task():
    request_body = request.json
    
    # Validate request body
    is_valid, error_message = validate_task_data(request_body)
    if not is_valid:
        logger.error(f"Validation failed: {error_message}")
        return jsonify({"error": error_message}), 400
    
    try:
        # Load existing tasks
        existing_tasks = load_tasks(DB_PATH, Task)
        
        # Create updated task
        updated_task = Task.from_dict(request_body)
        
        # Find and update the task by ID
        task_found = False
        for i, task in enumerate(existing_tasks):
            if task.id == updated_task.id:
                existing_tasks[i] = updated_task
                task_found = True
                break
        
        if not task_found:
            return jsonify({"error": "Task not found"}), 404

        # Save updated tasks
        save_tasks(existing_tasks, DB_PATH)
        
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid task data format: {e}")
        return jsonify({"error": "Invalid task data format"}), 400
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({"error": "Failed to update task"}), 500

    return tasks_to_json(existing_tasks)

@app.route("/deletetask", methods=["DELETE"])
def delete_task():
    request_body = request.json
    
    # Validate request body (only need ID for delete)
    is_valid, error_message = validate_task_data(request_body, required_fields=["id"])
    if not is_valid:
        logger.error(f"Validation failed: {error_message}")
        return jsonify({"error": error_message}), 400
    
    try:
        # Load existing tasks
        existing_tasks = load_tasks(DB_PATH, Task)
        
        # Get ID to delete
        id_to_delete = request_body["id"]
        
        # Find and remove the task by ID
        task_found = False
        for i, task in enumerate(existing_tasks):
            if task.id == id_to_delete:
                del existing_tasks[i]
                task_found = True
                break
        
        if not task_found:
            return jsonify({"error": "Task not found"}), 404

        # Save updated tasks
        save_tasks(existing_tasks, DB_PATH)
        
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid task data format: {e}")
        return jsonify({"error": "Invalid task data format"}), 400
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return jsonify({"error": "Failed to delete task"}), 500

    return tasks_to_json(existing_tasks)

if __name__ == "__main__":
    try:
        # Initialize empty JSON file if it doesn't exist
        if read_json(DB_PATH) == []:
            write_json([], DB_PATH)
        app.run(host="localhost", debug=True, port=8000)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")