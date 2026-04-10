import matplotlib
matplotlib.use("Agg")

import gradio as gr
import matplotlib.pyplot as plt
from collections import deque
from fastapi import FastAPI

# ---------- GLOBAL STATE ----------
STATE = {
    "position": (0, 0),
    "goal": (5, 5),
    "grid": 10,
    "obstacles": []
}

# ---------- PARSING ----------
def parse_point(text):
    try:
        text = text.strip().replace("(", "").replace(")", "")
        x, y = text.split(",")
        return int(x), int(y)
    except:
        return None

def parse_obstacles(text):
    obs = []
    if not text.strip():
        return obs

    for line in text.strip().split("\n"):
        pt = parse_point(line.strip())
        if pt:
            obs.append(pt)

    return obs

# ---------- PATHFINDING ----------
def bfs(grid, start, goal, obstacles):
    directions = [(0,1),(1,0),(0,-1),(-1,0)]
    queue = deque([(start, [start])])
    visited = set([start])
    obstacles = set(obstacles)

    while queue:
        (x,y), path = queue.popleft()

        if (x,y) == goal:
            return path

        for dx,dy in directions:
            nx, ny = x+dx, y+dy

            if (0 <= nx < grid and 0 <= ny < grid and
                (nx,ny) not in obstacles and (nx,ny) not in visited):

                visited.add((nx,ny))
                queue.append(((nx,ny), path + [(nx,ny)]))

    return []

# ---------- DRAW ----------
def draw(grid, robot, goal, obstacles, path):
    fig, ax = plt.subplots(figsize=(5,5))

    ax.set_xlim(0, grid)
    ax.set_ylim(0, grid)
    ax.set_facecolor("white")

    for i in range(grid+1):
        ax.axhline(i, linewidth=0.5, color='gray')
        ax.axvline(i, linewidth=0.5, color='gray')

    for x,y in obstacles:
        ax.add_patch(plt.Rectangle((y, x), 1, 1, color='black'))

    if goal:
        gx, gy = goal
        ax.add_patch(plt.Rectangle((gy, gx), 1, 1, color='green'))

    for x,y in path:
        ax.add_patch(plt.Rectangle((y, x), 1, 1, color='lightblue', alpha=0.4))

    rx, ry = robot
    ax.add_patch(plt.Rectangle((ry, rx), 1, 1, color='red'))
    ax.text(ry+0.5, rx+0.5, "R", ha='center', va='center', color='white')

    return fig

# ---------- GRADIO ----------
def run(grid_size, goal_text, obstacles_text):
    grid = int(grid_size)
    start = (0, 0)

    goal = parse_point(goal_text)
    obstacles = parse_obstacles(obstacles_text)

    STATE["position"] = start
    STATE["goal"] = goal
    STATE["grid"] = grid
    STATE["obstacles"] = obstacles

    path = bfs(grid, start, goal, obstacles)

    if path:
        return draw(grid, path[-1], goal, obstacles, path)
    else:
        return draw(grid, start, goal, obstacles, [])

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Warehouse Robot Simulator")

    with gr.Row():
        output = gr.Plot()

        with gr.Column():
            btn = gr.Button("▶ Start")
            grid = gr.Number(value=10, label="Grid Size")
            goal = gr.Textbox(value="(5,5)", label="Destination (x,y)")
            obstacles = gr.Textbox(
                label="Obstacles (one per line)",
                placeholder="(1,1)\n(2,2)",
                lines=8
            )

    btn.click(run, inputs=[grid, goal, obstacles], outputs=output)

# ---------- FASTAPI ----------
app = FastAPI()

# UI stays at root ✅
app = gr.mount_gradio_app(app, demo, path="/")

# ---------- ✅ OPENENV REQUIRED (CORRECT PATHS) ----------

@app.post("/openenv/reset")
def openenv_reset():
    STATE["position"] = (0, 0)
    return {"position": STATE["position"]}

@app.post("/openenv/step")
def openenv_step(action: str):
    x, y = STATE["position"]

    moves = {
        "UP": (-1, 0),
        "DOWN": (1, 0),
        "LEFT": (0, -1),
        "RIGHT": (0, 1)
    }

    if action in moves:
        dx, dy = moves[action]
        nx, ny = x + dx, y + dy

        if (0 <= nx < STATE["grid"] and
            0 <= ny < STATE["grid"] and
            (nx, ny) not in STATE["obstacles"]):

            STATE["position"] = (nx, ny)

    done = STATE["position"] == STATE["goal"]

    return {
        "position": STATE["position"],
        "done": done
    }

@app.get("/openenv/state")
def openenv_state():
    return STATE

# ---------- OPTIONAL (for Swagger UI like your screenshot) ----------
@app.post("/reset")
def reset():
    return openenv_reset()

@app.post("/step")
def step(action: str):
    return openenv_step(action)

@app.get("/state")
def state():
    return openenv_state()