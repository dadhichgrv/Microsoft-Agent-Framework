import os, sys
import asyncio

from collections.abc import Awaitable, Callable
from agent_framework import Agent, AgentContext, AgentResponse, Message
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

load_dotenv()

# Run middleware
# Case A : Before Agent Run
# Case B : After Agent Run
# Case C : Before and After Agent Run

async def content_safety_middleware(
        context : AgentContext,
        call_next : Callable[[], Awaitable[None]]
                                    ) :
    
    # Define banned phrases
    BANNED_PHRASES = ["jailbreak", "bypass any rule"]

    # context.message has messages before passed to agent and take last message
    last_msg = (context.messages[-1].text if context.messages else "").lower()

    # Check if phrase present in last message then print it is blocked and add it to after agent response 
    # here context.result stores after agent run
    for phrase in BANNED_PHRASES:
        if phrase in last_msg:
            print(f"Blocked - matched : '{phrase}' ")
            context.result = AgentResponse(
                messages = [Message("assistant",[f"Blocked : input contains contennt not allowed : '{phrase}' "])]
            )
            return 
        # Return Nothing ,  just pass it to context.result
        
    # Else move forward    
    await call_next()
    


middleware_agent = Agent(
                client = OpenAIChatClient(),
                instructions = "You are a business assistant that answers the user query in professional way",
                name = "MiddlewareAgent",
                middleware = [content_safety_middleware]
                      ) 
    
session = middleware_agent.create_session()

async def main():
    while True:
        query = input("\n Enter Text \n")

        if query in ('bye','exit','quit'):
            break

        async for chunk in middleware_agent.run(query, session = session, stream = True):
            if chunk.text:
                print(chunk.text, end = "", flush = True)

   

if __name__ == "__main__":
    asyncio.run(main())