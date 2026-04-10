from fastapi import FastAPI

api = FastAPI()

# Required OpenEnv endpoint
@api.post("/openenv/reset")
def reset():
    return {"status": "ok"}

# Optional root check
@api.get("/")
def root():
    return {"message": "OpenEnv API running"}