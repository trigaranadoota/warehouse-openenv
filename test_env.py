import asyncio
from env.warehouse_env import WarehouseEnv
from env.models import Action

async def test():
    env = WarehouseEnv(task="easy")
    res = await env.reset()
    print("Reset:", res)

    res = await env.step(Action(action_type="MOVE", direction="RIGHT"))
    print("Step:", res)

asyncio.run(test())