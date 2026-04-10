import matplotlib
matplotlib.use("Agg")

import gradio as gr
import matplotlib.pyplot as plt
from collections import deque
import time

# ---------------- PATHFINDING ----------------
def find_path(grid_size, start, goal, obstacles):
    directions = [(0,1),(1,0),(0,-1),(-1,0)]
    queue = deque([(start, [start])])
    visited = set([start])
    obstacles = set(obstacles)

    while queue:
        (x,y), path = queue.popleft()

        if (x,y) == goal:
            return path

        for dx, dy in directions:
            nx, ny = x+dx, y+dy

            if (0 <= nx < grid_size and 0 <= ny < grid_size and
                (nx,ny) not in obstacles and (nx,ny) not in visited):

                visited.add((nx,ny))
                queue.append(((nx,ny), path + [(nx,ny)]))

    return []

# ---------------- PARSING ----------------
def parse_point(text):
    x, y = text.replace("(", "").replace(")", "").split(",")
    return int(x.strip()), int(y.strip())

def parse_obstacles(text):
    obstacles = []
    if text.strip() == "":
        return obstacles

    for line in text.split("\n"):
        x, y = parse_point(line)
        obstacles.append((x, y))
    return obstacles

# ---------------- DRAW ----------------
def draw_grid(grid_size, robot, goal, obstacles, path):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.set_xlim(0, grid_size)
    ax.set_ylim(0, grid_size)
    ax.set_facecolor("white")

    # grid lines
    for i in range(grid_size+1):
        ax.axhline(i, color='gray', linewidth=0.5)
        ax.axvline(i, color='gray', linewidth=0.5)

    # obstacles (black)
    for ox, oy in obstacles:
        ax.add_patch(plt.Rectangle((oy, grid_size-ox-1), 1, 1, color='black'))

    # goal (green)
    gx, gy = goal
    ax.add_patch(plt.Rectangle((gy, grid_size-gx-1), 1, 1, color='green'))

    # path (light blue)
    for px, py in path:
        ax.add_patch(plt.Rectangle((py, grid_size-px-1), 1, 1, color='lightblue', alpha=0.3))

    # robot (red with R)
    rx, ry = robot
    ax.add_patch(plt.Rectangle((ry, grid_size-rx-1), 1, 1, color='red'))
    ax.text(ry+0.5, grid_size-rx-0.5, "R", ha='center', va='center', color='white')

    ax.set_xticks(range(grid_size))
    ax.set_yticks(range(grid_size))
    ax.set_xticklabels(range(grid_size))
    ax.set_yticklabels(reversed(range(grid_size)))

    return fig

# ---------------- SIMULATION ----------------
def run_simulation(grid_size, goal_text, obstacles_text):

    grid_size = int(grid_size)
    robot = (0, 0)

    goal = parse_point(goal_text)
    obstacles = parse_obstacles(obstacles_text)

    path = find_path(grid_size, robot, goal, obstacles)

    frames = []

    if not path:
        return [draw_grid(grid_size, robot, goal, obstacles, [])]

    for step in path:
        fig = draw_grid(grid_size, step, goal, obstacles, path)
        frames.append(fig)
        time.sleep(0.1)

    return frames

# ---------------- UI ----------------
with gr.Blocks() as demo:

    gr.Markdown("# 🤖 Warehouse Robot Simulator")

    with gr.Row():

        # LEFT → GRID
        output = gr.Gallery(label="Simulation")

        # RIGHT → CLEAN INPUTS ONLY
        with gr.Column():

            start_btn = gr.Button("▶ Start")

            grid_size = gr.Number(value=10, label="Grid Size")

            goal = gr.Textbox(
                value="(5,5)",
                label="Destination (x,y)"
            )

            obstacles = gr.Textbox(
                label="Obstacles (one per line)",
                placeholder="(1,1)\n(2,2)\n(3,3)"
            )

    start_btn.click(
        run_simulation,
        inputs=[grid_size, goal, obstacles],
        outputs=output
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)