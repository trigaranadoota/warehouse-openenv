import random
from typing import List, Tuple
from env.models import Observation, Action, StepResult


GRID_SIZE = 6


class WarehouseEnv:

    def __init__(self, task: str = "easy"):
        self.task = task

    async def reset(self):
        self.robot_pos = [0, 0]
        self.goal_pos = [5, 5]
        self.battery = 100.0
        self.carrying = False
        self.steps = 0

        if self.task == "easy":
            self.obstacles = []
        elif self.task == "medium":
            self.obstacles = [(2, 2), (3, 3)]
        else:
            self.obstacles = [(2, 2), (3, 3), (1, 4)]

        return StepResult(
            observation=self._get_obs(),
            reward=0.0,
            done=False
        )

    def _get_obs(self) -> Observation:
        return Observation(
            robot_pos=tuple(self.robot_pos),
            goal_pos=tuple(self.goal_pos),
            obstacles=self.obstacles,
            battery=self.battery,
            carrying=self.carrying
        )

    def _move(self, direction: str):
        x, y = self.robot_pos

        if direction == "UP":
            y -= 1
        elif direction == "DOWN":
            y += 1
        elif direction == "LEFT":
            x -= 1
        elif direction == "RIGHT":
            x += 1

        x = max(0, min(GRID_SIZE - 1, x))
        y = max(0, min(GRID_SIZE - 1, y))

        return [x, y]

    async def step(self, action: Action):
        self.steps += 1
        reward = -0.1

        new_pos = self.robot_pos

        if action.action_type == "MOVE" and action.direction:
            new_pos = self._move(action.direction)

            if tuple(new_pos) in self.obstacles:
                reward -= 5.0
            else:
                old_dist = self._distance(self.robot_pos, self.goal_pos)
                new_dist = self._distance(new_pos, self.goal_pos)

                if new_dist < old_dist:
                    reward += 1.0

                self.robot_pos = new_pos

        elif action.action_type == "PICK":
            if self.robot_pos == self.goal_pos and not self.carrying:
                self.carrying = True
                reward += 5.0
            else:
                reward -= 1.0

        elif action.action_type == "DROP":
            if self.robot_pos == [0, 0] and self.carrying:
                return StepResult(self._get_obs(), reward + 10.0, True)
            else:
                reward -= 1.0

        self.battery -= 1.0

        done = False

        if self.robot_pos == self.goal_pos and self.task != "hard":
            reward += 10.0
            done = True

        if self.battery <= 0 or self.steps > 50:
            done = True

        return StepResult(
            observation=self._get_obs(),
            reward=reward,
            done=done
        )

    async def state(self):
        return self._get_obs()

    async def close(self):
        pass

    def _distance(self, a: List[int], b: List[int]):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])