from fastapi import FastAPI

api = FastAPI()

@api.post("/openenv/reset")
def reset():
    return {"status": "ok"}

@api.get("/")
def root():
    return {"message": "OpenEnv API running"}