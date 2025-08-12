from dataclasses import dataclass
from enum import Enum

class State(Enum):
    # Define valid task states
    TODO = "toDo"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    
    @classmethod
    def get_valid_values(cls):
        # Return list of valid state values for validation/error messages
        return [state.value for state in cls]

@dataclass
class Task:
    # Task data model with required fields
    id: int
    title: str
    description: str
    state: State

    def to_dict(self):
        # Convert Task object to dictionary for JSON serialization
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "state": self.state.value
        }

    @classmethod
    def from_dict(cls, data, id):
        # Create Task object from dictionary data with enhanced error handling
        try:
            return cls(
                id=id,
                title=data["title"],
                description=data["description"],
                state=State(data["state"])
            )
        except ValueError as e:
            # This catches invalid state values
            valid_states = State.get_valid_values()
            raise ValueError(f"Invalid state '{data.get('state')}'. Valid options: {valid_states}") from e
        except KeyError as e:
            # This catches missing required fields
            raise KeyError(f"Missing required field: {e}") from e
