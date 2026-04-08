from typing import List


def grade_easy(rewards: List[float]) -> float:
    # Simple: total reward normalized
    max_reward = 50.0
    score = sum(rewards) / max_reward
    return max(0.0, min(score, 1.0))


def grade_medium(rewards: List[float]) -> float:
    max_reward = 70.0
    score = sum(rewards) / max_reward
    return max(0.0, min(score, 1.0))


def grade_hard(rewards: List[float]) -> float:
    max_reward = 100.0
    score = sum(rewards) / max_reward
    return max(0.0, min(score, 1.0))


def get_grader(task_name: str):
    if task_name == "easy":
        return grade_easy
    elif task_name == "medium":
        return grade_medium
    elif task_name == "hard":
        return grade_hard
    else:
        raise ValueError(f"Unknown task: {task_name}")