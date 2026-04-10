import sys
import os

# Fix import path for Docker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from env.tasks import get_task_env
import gradio as gr

app = FastAPI()

# Initialize environment
env = get_task_env("easy")


# ---------------- API ----------------
@app.get("/")
def root():
    return {
        "message": "Warehouse Robot OpenEnv API is running 🚀",
        "docs": "/docs",
        "endpoints": ["POST /reset", "POST /step", "GET /state"]
    }


@app.post("/reset")
async def reset():
    return await env.reset()


@app.post("/step")
async def step(action: str):
    return await env.step(type("Action", (), {"action": action}))


@app.get("/state")
async def state():
    return await env.state()


# ---------------- GRID RENDER ----------------
def render_grid(state):
    size = state["grid_size"]
    grid = [["⬜" for _ in range(size)] for _ in range(size)]

    ax, ay = state["agent_position"]
    gx, gy = state["goal_position"]

    grid[gx][gy] = "🎯"

    for ox, oy in state["obstacles"]:
        grid[ox][oy] = "⬛"

    grid[ax][ay] = "🤖"

    return "\n".join([" ".join(row) for row in grid])


# ---------------- UI FUNCTIONS ----------------
async def reset_ui():
    state = await env.reset()
    return render_grid(state)


async def move(action):
    result = await env.step(type("Action", (), {"action": action}))
    return render_grid(result["state"])


# ---------------- UI ----------------
def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# 🤖 Warehouse Robot Simulator")
        gr.Markdown("Move the robot to the goal while avoiding obstacles")

        output = gr.Textbox(label="Grid", lines=10)

        btn_reset = gr.Button("🔄 Reset")

        with gr.Row():
            btn_up = gr.Button("⬆️")

        with gr.Row():
            btn_left = gr.Button("⬅️")
            btn_down = gr.Button("⬇️")
            btn_right = gr.Button("➡️")

        btn_reset.click(reset_ui, outputs=output)
        btn_up.click(lambda: move("up"), outputs=output)
        btn_down.click(lambda: move("down"), outputs=output)
        btn_left.click(lambda: move("left"), outputs=output)
        btn_right.click(lambda: move("right"), outputs=output)

    return demo


# ---------------- RUN ----------------
def main():
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()