import matplotlib
matplotlib.use("Agg")

import gradio as gr
import matplotlib.pyplot as plt
from collections import deque

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

# ---------- PATHFINDING (START ALWAYS (0,0)) ----------
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

# ---------- DRAW GRID (0,0 at BOTTOM-LEFT) ----------
def draw(grid, robot, goal, obstacles, path):
    fig, ax = plt.subplots(figsize=(5,5))

    ax.set_xlim(0, grid)
    ax.set_ylim(0, grid)
    ax.set_facecolor("white")

    # grid lines
    for i in range(grid+1):
        ax.axhline(i, linewidth=0.5, color='gray')
        ax.axvline(i, linewidth=0.5, color='gray')

    # obstacles (BLACK)
    for x,y in obstacles:
        ax.add_patch(plt.Rectangle((y, x), 1, 1, color='black'))

    # goal (GREEN)
    if goal:
        gx, gy = goal
        ax.add_patch(plt.Rectangle((gy, gx), 1, 1, color='green'))

    # path (LIGHT BLUE)
    for x,y in path:
        ax.add_patch(plt.Rectangle((y, x), 1, 1, color='lightblue', alpha=0.4))

    # robot (RED with "R")
    rx, ry = robot
    ax.add_patch(plt.Rectangle((ry, rx), 1, 1, color='red'))
    ax.text(ry+0.5, rx+0.5, "R", ha='center', va='center', color='white')

    # axes labels (IMPORTANT FIX)
    ax.set_xticks(range(grid))
    ax.set_yticks(range(grid))
    ax.set_xlabel("Y →")
    ax.set_ylabel("X ↑")

    return fig

# ---------- MAIN ----------
def run(grid_size, goal_text, obstacles_text):
    try:
        grid = int(grid_size)

        # ✅ FIXED: START ALWAYS (0,0)
        start = (0, 0)

        goal = parse_point(goal_text)
        if goal is None:
            return draw(grid, start, None, [], [])

        obstacles = parse_obstacles(obstacles_text)

        path = bfs(grid, start, goal, obstacles)

        if path:
            return draw(grid, path[-1], goal, obstacles, path)
        else:
            return draw(grid, start, goal, obstacles, [])

    except Exception as e:
        print("ERROR:", e)
        return None

# ---------- UI ----------
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Warehouse Robot Simulator")

    with gr.Row():
        output = gr.Plot()

        with gr.Column():
            btn = gr.Button("▶ Start / Recompute")

            grid = gr.Number(value=10, label="Grid Size")

            goal = gr.Textbox(
                value="(5,5)",
                label="Destination (x,y)"
            )

            obstacles = gr.Textbox(
                label="Obstacles (one per line)",
                placeholder="(1,1)\n(2,2)\n(3,4)",
                lines=8  # ✅ MULTI INPUT FIX
            )

    btn.click(run, inputs=[grid, goal, obstacles], outputs=output)

# ---------- RUN ----------
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)