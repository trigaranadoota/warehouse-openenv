import asyncio
from env.tasks import get_task_env
from env.models import Action
from env.graders import get_grader


async def run_task(task_name):
    env = get_task_env(task_name)
    grader = get_grader(task_name)

    res = await env.reset()
    rewards = []

    for _ in range(10):
        res = await env.step(Action(action_type="MOVE", direction="RIGHT"))
        rewards.append(res.reward)
        if res.done:
            break

    score = grader(rewards)

    print(f"TASK: {task_name}")
    print("Rewards:", rewards)
    print("Score:", score)
    print("-" * 30)


async def main():
    for task in ["easy", "medium", "hard"]:
        await run_task(task)


asyncio.run(main())