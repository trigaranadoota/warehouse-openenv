from fastapi import FastAPI
from env.tasks import get_task_env
from env.models import Action

app = FastAPI()

# Create environment (default task)
env = get_task_env("easy")


# ✅ Root route (VERY IMPORTANT for Hugging Face UI)
@app.get("/")
def home():
    return {
        "message": "Warehouse Robot OpenEnv API is running 🚀",
        "docs": "/docs",
        "endpoints": [
            "POST /reset",
            "POST /step",
            "GET /state"
        ]
    }


# ✅ Reset environment
@app.post("/reset")
async def reset():
    result = await env.reset()
    return result


# ✅ Take a step
@app.post("/step")
async def step(action: Action):
    result = await env.step(action)
    return result


# ✅ Get current state
@app.get("/state")
async def state():
    result = await env.state()
    return result


# ✅ Close environment (optional cleanup)
@app.on_event("shutdown")
async def shutdown():
    await env.close()
    # rebuild trigger