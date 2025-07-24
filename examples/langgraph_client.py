import asyncio

from dotenv import load_dotenv
from langgraph_sdk import get_client

load_dotenv(override=True)

# Assistant ID we want to use
ASSISTANT_ID = "simple_text2sql"

# Create client with auth header and assistant ID
client = get_client(url="http://127.0.0.1:2024")


async def main():
    message = {"role": "user", "content": "What can you do?"}

    print(f"\nTesting with assistant {ASSISTANT_ID}")
    async for chunk in client.runs.stream(
        None,  # Threadless run
        ASSISTANT_ID,  # This will go in the body automatically
        input={"messages": [message]},
        stream_mode="updates",
    ):
        print(f"Received event: {chunk.event}")
        print(f"Data: {chunk.data}\n")


if __name__ == "__main__":
    asyncio.run(main())
