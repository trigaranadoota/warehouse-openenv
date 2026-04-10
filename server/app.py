import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

# ---------------- PATHFINDING (BFS) ----------------
def find_path(grid_size, start, goal, obstacles):
    directions = [(0,1),(1,0),(0,-1),(-1,0)]
    queue = deque([(start, [start])])
    visited = set()
    visited.add(start)

    obstacles = set(tuple(o) for o in obstacles)

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

# ---------------- GRID DRAW ----------------
def draw_grid(grid_size, robot, goal, obstacles, path):
    grid = np.zeros((grid_size, grid_size))

    fig, ax = plt.subplots(figsize=(5,5))
    ax.set_xlim(0, grid_size)
    ax.set_ylim(0, grid_size)

    # Background
    ax.set_facecolor("white")

    # Draw grid lines
    for x in range(grid_size+1):
        ax.axhline(x, color='gray', linewidth=0.5)
        ax.axvline(x, color='gray', linewidth=0.5)

    # Obstacles
    for ox, oy in obstacles:
        ax.add_patch(plt.Rectangle((oy, grid_size-ox-1), 1, 1, color='black'))

    # Goal
    gx, gy = goal
    ax.add_patch(plt.Rectangle((gy, grid_size-gx-1), 1, 1, color='green'))

    # Path
    for px, py in path:
        ax.add_patch(plt.Rectangle((py, grid_size-px-1), 1, 1, color='lightblue', alpha=0.3))

    # Robot
    rx, ry = robot
    ax.add_patch(plt.Rectangle((ry, grid_size-rx-1), 1, 1, color='red'))
    ax.text(ry+0.5, grid_size-rx-0.5, "R", ha='center', va='center', color='white')

    # Axis
    ax.set_xticks(range(grid_size))
    ax.set_yticks(range(grid_size))
    ax.set_xticklabels(range(grid_size))
    ax.set_yticklabels(reversed(range(grid_size)))

    return fig


# ---------------- MAIN LOGIC ----------------
def run_simulation(grid_size, goal_x, goal_y, obstacles_text):
    grid_size = int(grid_size)
    goal = (int(goal_x), int(goal_y))
    robot = (0, 0)

    # Parse obstacles
    obstacles = []
    if obstacles_text.strip():
        for line in obstacles_text.split("\n"):
            x, y = map(int, line.split(","))
            obstacles.append((x, y))

    path = find_path(grid_size, robot, goal, obstacles)

    fig = draw_grid(grid_size, robot, goal, obstacles, path)

    return fig, str(path), str(obstacles), str(goal), grid_size


# ---------------- UI ----------------
with gr.Blocks() as demo:

    gr.Markdown("# 🤖 Warehouse Robot Simulator")
    gr.Markdown("AI finds optimal path automatically")

    with gr.Row():

        # LEFT: GRID
        grid_output = gr.Plot()

        # RIGHT: CONTROLS
        with gr.Column():

            start_btn = gr.Button("▶ Start / Recompute")

            grid_size = gr.Number(value=10, label="Grid Size")

            goal_x = gr.Number(value=5, label="Goal X")
            goal_y = gr.Number(value=5, label="Goal Y")

            obstacles = gr.Textbox(
                label="Obstacles (x,y per line)",
                value="1,1\n1,2\n2,2"
            )

            path_box = gr.Textbox(label="Path")
            obs_box = gr.Textbox(label="Obstacle Coordinates")
            goal_box = gr.Textbox(label="Goal Coordinates")
            grid_box = gr.Textbox(label="Grid Size Output")

    # Button trigger
    start_btn.click(
        run_simulation,
        inputs=[grid_size, goal_x, goal_y, obstacles],
        outputs=[grid_output, path_box, obs_box, goal_box, grid_box]
    )

    # Auto update when values change
    for inp in [grid_size, goal_x, goal_y, obstacles]:
        inp.change(
            run_simulation,
            inputs=[grid_size, goal_x, goal_y, obstacles],
            outputs=[grid_output, path_box, obs_box, goal_box, grid_box]
        )


# ---------------- RUN ----------------
def main():
    demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()