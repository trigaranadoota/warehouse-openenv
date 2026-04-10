import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

# ---------------- DRAW GRID ----------------
def draw_grid(grid_size, robot, goal, obstacles, path):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.set_xlim(0, grid_size)
    ax.set_ylim(0, grid_size)
    ax.set_facecolor("white")

    for x in range(grid_size+1):
        ax.axhline(x, color='gray', linewidth=0.5)
        ax.axvline(x, color='gray', linewidth=0.5)

    for ox, oy in obstacles:
        ax.add_patch(plt.Rectangle((oy, grid_size-ox-1), 1, 1, color='black'))

    gx, gy = goal
    ax.add_patch(plt.Rectangle((gy, grid_size-gx-1), 1, 1, color='green'))

    for px, py in path:
        ax.add_patch(plt.Rectangle((py, grid_size-px-1), 1, 1, color='lightblue', alpha=0.3))

    rx, ry = robot
    ax.add_patch(plt.Rectangle((ry, grid_size-rx-1), 1, 1, color='red'))
    ax.text(ry+0.5, grid_size-rx-0.5, "R", ha='center', va='center', color='white')

    ax.set_xticks(range(grid_size))
    ax.set_yticks(range(grid_size))
    ax.set_xticklabels(range(grid_size))
    ax.set_yticklabels(reversed(range(grid_size)))

    return fig

# ---------------- MAIN LOGIC ----------------
def run_simulation(grid_size, goal_x, goal_y, obstacles_text, episodes):
    grid_size = int(grid_size)
    goal = (int(goal_x), int(goal_y))
    robot = (0, 0)

    obstacles = []
    if obstacles_text.strip():
        for line in obstacles_text.split("\n"):
            x, y = map(int, line.split(","))
            obstacles.append((x, y))

    path = find_path(grid_size, robot, goal, obstacles)

    frames = []

    if not path:
        fig = draw_grid(grid_size, robot, goal, obstacles, [])
        return [fig], "No path found", str(obstacles), str(goal), str(grid_size)

    delay = max(0.01, 0.2 - episodes * 0.003)

    for step in path:
        fig = draw_grid(grid_size, step, goal, obstacles, path)
        frames.append(fig)
        time.sleep(delay)

    return frames, str(path), str(obstacles), str(goal), str(grid_size)

# ---------------- UI ----------------
with gr.Blocks() as demo:

    gr.Markdown("# 🤖 Warehouse Robot Simulator")

    with gr.Row():

        # LEFT
        grid_output = gr.Gallery(label="Simulation")

        # RIGHT
        with gr.Column():

            start_btn = gr.Button("▶ Start / Recompute")

            grid_size = gr.Number(value=10, label="Grid Size")
            goal_x = gr.Number(value=5, label="Goal X")
            goal_y = gr.Number(value=5, label="Goal Y")

            obstacles = gr.Textbox(
                label="Obstacles (x,y per line)",
                placeholder="e.g.\n1,1\n2,2"
            )

            episodes = gr.Slider(1, 50, value=10, label="Episodes (Speed)")

            # OUTPUTS (READ ONLY)
            path_box = gr.Textbox(label="Optimal Path", interactive=False)
            obs_box = gr.Textbox(label="Obstacle Coordinates", interactive=False)
            goal_box = gr.Textbox(label="Goal Coordinates", interactive=False)
            grid_box = gr.Textbox(label="Grid Size Output", interactive=False)

    start_btn.click(
        run_simulation,
        inputs=[grid_size, goal_x, goal_y, obstacles, episodes],
        outputs=[grid_output, path_box, obs_box, goal_box, grid_box]
    )

# ---------------- RUN ----------------
def main():
    demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()