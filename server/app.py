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
    for line in text.split("\n"):
        pt = parse_point(line)
        if pt:
            obs.append(pt)
    return obs

# ---------- PATHFINDING ----------
def bfs(grid, start, goal, obstacles):
    q = deque([(start, [start])])
    visited = set([start])
    obstacles = set(obstacles)

    while q:
        (x,y), path = q.popleft()
        if (x,y) == goal:
            return path

        for dx,dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < grid and 0 <= ny < grid:
                if (nx,ny) not in obstacles and (nx,ny) not in visited:
                    visited.add((nx,ny))
                    q.append(((nx,ny), path+[(nx,ny)]))
    return []

# ---------- DRAW ----------
def draw(grid, robot, goal, obstacles, path):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.set_xlim(0, grid)
    ax.set_ylim(0, grid)
    ax.set_facecolor("white")

    # grid lines
    for i in range(grid+1):
        ax.axhline(i, linewidth=0.5)
        ax.axvline(i, linewidth=0.5)

    # obstacles
    for x,y in obstacles:
        ax.add_patch(plt.Rectangle((y, grid-x-1),1,1,color='black'))

    # goal
    if goal:
        gx,gy = goal
        ax.add_patch(plt.Rectangle((gy, grid-gx-1),1,1,color='green'))

    # path
    for x,y in path:
        ax.add_patch(plt.Rectangle((y, grid-x-1),1,1,color='lightblue',alpha=0.3))

    # robot
    rx,ry = robot
    ax.add_patch(plt.Rectangle((ry, grid-rx-1),1,1,color='red'))
    ax.text(ry+0.5, grid-rx-0.5, "R", ha='center', va='center', color='white')

    return fig

# ---------- MAIN ----------
def run(grid_size, goal_text, obstacles_text):
    try:
        grid = int(grid_size)
        start = (0,0)

        goal = parse_point(goal_text)
        if not goal:
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
    gr.Markdown("# 🤖 Warehouse Robot")

    with gr.Row():
        output = gr.Plot()

        with gr.Column():
            btn = gr.Button("Start")

            grid = gr.Number(value=10, label="Grid Size")

            goal = gr.Textbox(value="(5,5)", label="Destination (x,y)")

            obstacles = gr.Textbox(
                label="Obstacles (one per line)",
                placeholder="(1,1)\n(2,2)"
            )

    btn.click(run, inputs=[grid, goal, obstacles], outputs=output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)