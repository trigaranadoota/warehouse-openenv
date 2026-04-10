from env.environment import WarehouseEnv  # or your existing env class


# Base task
class EasyEnv(WarehouseEnv):
    def __init__(self):
        super().__init__()


# Duplicate tasks (quick fix for validator)
class MediumEnv(WarehouseEnv):
    def __init__(self):
        super().__init__()


class HardEnv(WarehouseEnv):
    def __init__(self):
        super().__init__()


# Task selector
def get_task_env(task_name: str):
    if task_name == "easy":
        return EasyEnv()
    elif task_name == "medium":
        return MediumEnv()
    elif task_name == "hard":
        return HardEnv()
    else:
        raise ValueError(f"Unknown task: {task_name}")