from pydantic import BaseModel
from typing import List, Tuple, Optional


class Observation(BaseModel):
    robot_pos: Tuple[int, int]
    goal_pos: Tuple[int, int]
    obstacles: List[Tuple[int, int]]
    battery: float
    carrying: bool


class Action(BaseModel):
    action_type: str  # MOVE / PICK / DROP / WAIT
    direction: Optional[str] = None  # UP/DOWN/LEFT/RIGHT


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict = {}