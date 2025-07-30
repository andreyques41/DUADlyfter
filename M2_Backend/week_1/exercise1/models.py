from dataclasses import dataclass
from enum import Enum

@dataclass
class State(Enum):
    # Define valid task states
    TODO = "toDo"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"

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
    def from_dict(cls, data):
        # Create Task object from dictionary data
        return cls(
            id=data["id"] if isinstance(data["id"], int) else int(data["id"]),
            title=data["title"],
            description=data["description"],
            state=State(data["state"])
        )
