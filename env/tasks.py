from env.warehouse_env import WarehouseEnv


def get_task_env(task_name: str):
    if task_name == "easy":
        return WarehouseEnv(task="easy")

    elif task_name == "medium":
        return WarehouseEnv(task="medium")

    elif task_name == "hard":
        return WarehouseEnv(task="hard")

    else:
        raise ValueError(f"Unknown task: {task_name}")