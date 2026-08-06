import os
import asyncio
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Create Agent
technical_agent = Agent (
                        client       = OpenAIChatClient(),
                        instructions = "You are an experienced technical assistant that explains complex query clearly in one line",
                        name         = "TechnicalBot"
                     )

poet_agent = Agent (
                        client       = OpenAIChatClient(),
                        instructions = "You are a poet assistant that writes poem in 2 lines on givenn topic",
                        name         = "PoetBot"
                     )

code_review_agent = Agent (
                        client       = OpenAIChatClient(),
                        instructions = "You are a code review assistant that checks for code and replies issues in 1 line",
                        name         = "CodeReviewBot"
                     )


TOPIC = "WHat is MCP Server"
CODE  = """ a = 3 
            b = 5
            def sum(a,b):
                show a+b
        """

# Call Agent 
async def main(): 
    #result = await agent.run("Explain briefly about Microsoft Agent Framework", stream = True)
    print("TECHINAL ASSISTANT \n")
    async for chunk in technical_agent.run(TOPIC, stream = True):
        if chunk.text:
            print(chunk.text, end = "", flush = True)

    print("\n POET ASSISTANT \n")
    async for chunk in poet_agent.run(TOPIC, stream = True):
        if chunk.text:
            print(chunk.text, end = "", flush = True)

    print("\n CODE ASSISTANT \n")
    async for chunk in code_review_agent .run(CODE, stream = True):
        if chunk.text:
            print(chunk.text, end = "", flush = True)

 
    
if __name__ == "__main__":
    asyncio.run(main())