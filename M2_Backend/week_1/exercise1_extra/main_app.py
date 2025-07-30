from flask import Flask, request, jsonify
import logging
import os
from json_handler import read_json, write_json
from task_manager import tasks_to_json, save_tasks, load_tasks, validate_task_data
from models import Task, State
from flask.views import MethodView

app = Flask(__name__)

# Configure logging at module level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './tasks.json'

class ModelAPI(MethodView):
    # MethodView for RESTful API operations
    init_every_request = False

    def __init__(self, model):
        # Initialize with model and configuration
        self.logger = logger
        self.db_path = DB_PATH
        self.model = model

    def get(self):
        # GET: Retrieve all tasks or filter by state
        try:
            tasks = load_tasks(self.db_path, self.model)

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
            self.logger.error(f"Error retrieving tasks: {e}")
            return jsonify({"error": "Failed to retrieve tasks"}), 500

    def post(self):
        # POST: Create a new task
        request_body = request.json
        
        # Validate request body
        is_valid, error_message = validate_task_data(request_body)
        if not is_valid:
            self.logger.error(f"Validation failed: {error_message}")
            return jsonify({"error": error_message}), 400
        
        try:
            # Load existing tasks
            existing_tasks = load_tasks(self.db_path, self.model)
            
            # Create new task
            new_task = self.model.from_dict(request_body)
            
            # Check if task ID already exists
            for task in existing_tasks:
                if task.id == new_task.id:
                    self.logger.error(f"Task with ID {new_task.id} already exists")
                    return jsonify({"error": f"Task with ID {new_task.id} already exists"}), 409
            
            # Add new task and save
            existing_tasks.append(new_task)
            save_tasks(existing_tasks, self.db_path)
            
        except (KeyError, ValueError) as e:
            self.logger.error(f"Invalid task data format: {e}")
            return jsonify({"error": "Invalid task data format"}), 400
        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            return jsonify({"error": "Failed to add task"}), 500

        return tasks_to_json(existing_tasks)

    def put(self):
        # PUT: Update an existing task
        request_body = request.json
        
        # Validate request body
        is_valid, error_message = validate_task_data(request_body)
        if not is_valid:
            self.logger.error(f"Validation failed: {error_message}")
            return jsonify({"error": error_message}), 400
        
        try:
            # Load existing tasks
            existing_tasks = load_tasks(self.db_path, self.model)
            
            # Create updated task
            updated_task = self.model.from_dict(request_body)
            
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
            save_tasks(existing_tasks, self.db_path)
            
        except (KeyError, ValueError) as e:
            self.logger.error(f"Invalid task data format: {e}")
            return jsonify({"error": "Invalid task data format"}), 400
        except Exception as e:
            self.logger.error(f"Error updating task: {e}")
            return jsonify({"error": "Failed to update task"}), 500

        return tasks_to_json(existing_tasks)

    def delete(self):
        # DELETE: Remove a task by ID
        request_body = request.json
        
        # Validate request body (only need ID for delete)
        is_valid, error_message = validate_task_data(request_body, required_fields=["id"])
        if not is_valid:
            self.logger.error(f"Validation failed: {error_message}")
            return jsonify({"error": error_message}), 400
        
        try:
            # Load existing tasks
            existing_tasks = load_tasks(self.db_path, self.model)
            
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
            save_tasks(existing_tasks, self.db_path)
            
        except (KeyError, ValueError) as e:
            self.logger.error(f"Invalid task data format: {e}")
            return jsonify({"error": "Invalid task data format"}), 400
        except Exception as e:
            self.logger.error(f"Error deleting task: {e}")
            return jsonify({"error": "Failed to delete task"}), 500

        return tasks_to_json(existing_tasks)

def register_api(app, model, name):
    # Register MethodView with Flask app
    app.add_url_rule(f'/{name}', view_func=ModelAPI.as_view(name, model=model))

if __name__ == "__main__":
    try:
        # Initialize empty JSON file if it doesn't exist
        if not os.path.exists(DB_PATH):
            write_json([], DB_PATH)
        
        # Register the API routes using MethodView
        register_api(app, Task, 'tasks')
        
        app.run(host="localhost", debug=True, port=8000)
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to start application: {e}")