import asyncio
import json
from droidrun import DroidAgent, DroidrunConfig

async def run_task(goal: str):
    config = DroidrunConfig()
    agent = DroidAgent(goal=goal, config=config)
    result = await agent.run()

    parsed = None
    if result.reason:
        try:
            parsed = json.loads(result.reason)
        except:
            parsed = None

    return {
        "success": result.success,
        "json": parsed,
        "raw_reason": result.reason
    }

def run_task_sync(goal: str):
    return asyncio.run(run_task(goal))
