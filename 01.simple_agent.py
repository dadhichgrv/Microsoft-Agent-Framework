import os
import asyncio
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Client
client= OpenAIChatClient(
    model    = "gpt-5-mini",  
    api_key  = os.getenv("OPENAI_API_KEY"),
    base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Create Agent
agent = Agent (
client       = client,
instructions = "You are an assistant that explains query clearly in brief",
name         = "AssistantBot"
                )

# Call Agent 
async def main(): 
    #result = await agent.run("Explain briefly about Microsoft Agent Framework", stream = True)

    async for chunk in agent.run("Explain briefly about Microsoft Agent Framework for agent building", stream = True):
        if chunk.text:
            print(chunk.text, end = "", flush = True)

    print()
    
if __name__ == "__main__":
    asyncio.run(main())