import os, sys
import asyncio, time, random
from typing import Any, cast
from pydantic import BaseModel
from collections.abc import Awaitable, Callable
from agent_framework import Agent, ContextProvider, AgentSession,  SessionContext, AgentResponse, AgentMiddleware, AgentContext
from agent_framework.orchestrations import MagenticBuilder
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

load_dotenv()
    
# Create class to add some context that you want to pass to system instructions for agent
class UserPreference(ContextProvider):
    """ Inject context that you want to inject into agent"""

    def __init__(self, context_text : str):
        super().__init__("context-provider")
        self._text = context_text

    async def before_run(
            self,
            *,
            agent : Any,
            session : AgentSession,
            context : SessionContext,
            state   : dict[str, Any]
                        ) :
        context.extend_instructions(self.source_id, self._text)

# this can be done through file read also by adding context to a file and reading that file
business_context_provider = UserPreference(
                                            """
                                            Customer 1 :
                                            TPID : 12345
                                            Account Name : Contoso
                                            Estimated Revenue : $1,000
                                            Recommended Product : ME3 to ME5 Upsell
                                            Existing Product : ME3


                                            Customer 2 :
                                            TPID : 54321
                                            Account Name : FOURTH COFFEE
                                            Estimated Revenue : $500
                                            Recommended Product : OE3 to ME3 Upsell
                                            Existing Product : ME3


                                            """
                                            )


class RetryMiddleware(AgentMiddleware):
    # Constructor defines wait time of 1 sec and max 3 retries
    def __init__(self, max_retries : int = 3, wait_time : float = 1.0):
        self.max_retries = max_retries
        self.wait_time   = wait_time

    async def process(
                self,
                context : AgentContext,
                call_next = Callable[ [], Awaitable[None]]
                        ) :
        for attempt in range(1,self.max_retries):
            try:
                await call_next()
                return 
            except Exception as e:
                if attempt == self.max_retries:
                    print("Max retires reached")
                    raise 
                print(f"Attempt failed. Retry in {self.wait_time}")


# Recommendation Agent to create reason to believe text based on customer data
def revenue_tool():
   chance = random.random()
   if chance <0.3:
       print(f"Chance : {chance}")
       raise RuntimeError("service not available")
   return "Recommended Generated"
       


final_agent = Agent(
                            client       = OpenAIChatClient(),
                            name         = "FinalAgent",
                            instructions = """ You are helpful assistant who can generate recommendations. 
                                                If asked for revenue, fetch tool for it.
                                               If tool fails, explain nwhat happened and retry.
                                            """ ,
                            tools = [revenue_tool],
                            middleware = [RetryMiddleware(max_retries=3, wait_time=1.0)]
                            )


async def main():
     
     query = "Give me revenue details"
               
     response = await final_agent.run(query)
     print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
