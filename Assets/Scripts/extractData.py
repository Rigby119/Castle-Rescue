from flask import Flask, jsonify
import numpy as np
from testSystem import CastleRescueModel

app = Flask(__name__)

# Initial Parameters
WIDTH = 10
HEIGHT = 8
AGENTS = 6
MAX_ITERATIONS = 48
# Initialize model
model = CastleRescueModel(WIDTH, HEIGHT, AGENTS)

# Agents Grid
def get_agents_grid(model):
    grid = np.zeros((model.grid.height, model.grid.width), dtype=np.int8)
    for agent in model.schedule.agents:
        x, y = agent.pos
        grid[y, x] = agent.agent_id
    return grid

# POIs Grid
def get_pois_grid(model):
    grid = np.zeros((model.grid.height, model.grid.width), dtype=np.int8)
    grid[model.pois > 0] = 1
    return grid

# Fire/Smoke Grid
def get_fire_grid(model):
    return model.fire.astype(np.int8)

def get_walls_list(model):
    walls_list = []
    for y in range(model.grid.height):
        for x in range(model.grid.width):
            cell_walls = model.walls[y, x]
            for dir, state in cell_walls.items():
                if state == 0:
                    state = 1
                if state > 0:
                    walls_list.append({
                        "x": x,
                        "y": y,
                        "direction": dir,
                        "state": state
                    })
    return walls_list

def get_doors_list(model):
    doors_list = []
    for y in range(model.grid.height):
        for x in range(model.grid.width):
            cell_doors = model.doors[y, x]
            for dir, state in cell_doors.items():
                if state > 0:
                    doors_list.append({
                        "x": x,
                        "y": y,
                        "direction": dir,
                        "state": state
                    })
    return doors_list

'''
#List of Grids by step
fire_grids = []
agents_grids = []
pois_grids = []
'''

@app.route("/step", methods = ["GET"])
def step():
    if not model.finish_game():
        model.step() # Keep iterating
    fire = get_fire_grid(model).flatten().tolist()
    agents = get_agents_grid(model).flatten().tolist()
    pois = get_pois_grid(model).flatten().tolist()
    walls = get_walls_list(model)
    doors = get_doors_list(model)
    gameStatus = model.finish_game()
    print(walls)
    return jsonify({
        "width": WIDTH,
        "height": HEIGHT,
        "fire": fire,
        "agents": agents,
        "pois": pois,
        "walls": walls,
        "doors": doors,
        "gameStatus": gameStatus
    })

@app.route("/reset", methods = ["POST"])
def reset():
    global model
    model = CastleRescueModel(WIDTH, HEIGHT, AGENTS)
    return jsonify({"gameStatus": "reset"})

'''
# Test grids
print("Last Fire/Smoke Grid\nLen:", len(fire_grids), "\n\nGrid:", fire_grids[len(fire_grids)-1])
print("Last Agent Grid\nLen:", len(agents_grids), "\n\nGrid:", agents_grids[len(agents_grids)-1])
print("Last POIs Grid\nLen:", len(pois_grids), "\n\nGrid:", pois_grids[len(pois_grids)-1])
'''

if __name__ == "__main__":
    app.run(debug=True)