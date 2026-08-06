import os
import asyncio
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    client = OpenAIChatClient(),
    instructions = "You are an assistant that explains query clearly",
    name = "MemoryAgent"
                    )

# Create session to store short term memory
session = agent.create_session()

async def main():

    while True:
        query = input("Enter Text : ")
        print("\n")

        if query in ('bye','exit','quit'):
            break

        async for chunk in agent.run(query, session = session, stream = True):
            if chunk.text:
                print(chunk.text, end = "", flush = True)

    
if __name__ == "__main__":
    asyncio.run(main())