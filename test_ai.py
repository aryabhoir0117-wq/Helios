# test_ai.py
import asyncio
from explanation import explain_root_cause

async def main():
    result = await explain_root_cause(
        "High CPU usage detected: 0.85 cores",
        "Recent deployment 'v1.2.3' likely trigger."
    )
    print("RESULT:", result)

asyncio.run(main())