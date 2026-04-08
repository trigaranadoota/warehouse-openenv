import asyncio
import os
from typing import List, Optional

from openai import OpenAI

from env.models import Action
from env.tasks import get_task_env
from env.graders import get_grader

# Environment variables
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"

TASK_NAME = os.getenv("TASK", "easy")
MAX_STEPS = 20


# ✅ Initialize OpenAI client safely
client = None
if API_KEY:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


# ✅ Logging functions (MANDATORY FORMAT)
def log_start(task: str, model: str):
    print(f"[START] task={task} env=warehouse-openenv model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ✅ Smart action function (OpenAI + fallback)
def get_action(step: int) -> Action:
    # 🔹 If NO API key → fallback logic
    if client is None:
        if step % 2 == 0:
            return Action(action_type="MOVE", direction="RIGHT")
        else:
            return Action(action_type="MOVE", direction="DOWN")

    # 🔹 If API key exists → try LLM
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a warehouse robot. Choose one direction: UP, DOWN, LEFT, RIGHT."
                },
                {
                    "role": "user",
                    "content": f"Step {step}: What is the best next move?"
                }
            ],
            max_tokens=10,
            temperature=0.2,
        )

        text = (response.choices[0].message.content or "").strip().upper()

        if text in ["UP", "DOWN", "LEFT", "RIGHT"]:
            return Action(action_type="MOVE", direction=text)

    except Exception as e:
        print(f"[DEBUG] OpenAI error: {e}", flush=True)

    # 🔹 Safe fallback
    return Action(action_type="MOVE", direction="RIGHT")


# ✅ Main execution
async def main():
    env = get_task_env(TASK_NAME)
    grader = get_grader(TASK_NAME)

    rewards = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(TASK_NAME, MODEL_NAME)

    try:
        result = await env.reset()

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            action = get_action(step)

            result = await env.step(action)

            reward = result.reward
            done = result.done

            rewards.append(reward)
            steps_taken = step

            log_step(step, str(action), reward, done, None)

            if done:
                break

        score = grader(rewards)
        success = score > 0.3

    finally:
        await env.close()
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())