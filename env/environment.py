import random


class WarehouseEnv:
    def __init__(self, size=5):
        self.size = size
        self.reset()

    async def reset(self):
        # Agent starts at top-left
        self.agent_pos = [0, 0]

        # Goal at bottom-right
        self.goal_pos = [self.size - 1, self.size - 1]

        # Random obstacles
        self.obstacles = []
        for _ in range(3):
            obs = [random.randint(0, self.size - 1), random.randint(0, self.size - 1)]
            if obs != self.agent_pos and obs != self.goal_pos:
                self.obstacles.append(obs)

        return self._get_state()

    async def step(self, action):
        move = action.action.lower()

        x, y = self.agent_pos

        if move == "up":
            x -= 1
        elif move == "down":
            x += 1
        elif move == "left":
            y -= 1
        elif move == "right":
            y += 1

        # Stay within bounds
        x = max(0, min(self.size - 1, x))
        y = max(0, min(self.size - 1, y))

        new_pos = [x, y]

        # Check obstacle
        if new_pos in self.obstacles:
            reward = -1
            done = False
        elif new_pos == self.goal_pos:
            self.agent_pos = new_pos
            reward = 10
            done = True
        else:
            self.agent_pos = new_pos
            reward = -0.1
            done = False

        return {
            "state": self._get_state(),
            "reward": reward,
            "done": done
        }

    async def state(self):
        return self._get_state()

    async def close(self):
        pass

    # ✅ GRADER (IMPORTANT)
    def compute_reward(self, state=None):
        if self.agent_pos == self.goal_pos:
            return 10
        return -0.1

    def _get_state(self):
        return {
            "agent_position": self.agent_pos,
            "goal_position": self.goal_pos,
            "obstacles": self.obstacles,
            "grid_size": self.size
        }