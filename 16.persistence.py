import os, sys
import asyncio, time
from typing import Any, cast
from pydantic import BaseModel
from collections.abc import Awaitable, Callable
from agent_framework import Agent, ContextProvider, AgentSession,  SessionContext, FileHistoryProvider
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

# Path to store single agent history in your folder
HISTORY_PATH = ".single_agent_history"

# Agent to persist historical connversation
persistence_agent = Agent(
                            client       = OpenAIChatClient(),
                            name         = "persistent_agent",
                            instructions = """ You are a persistence agent. Remember everything that user tells you across multiple
                                                sessions. 
                                            """ ,
                        # Providing 2 contexts : one is business data and other is chat histroy
                            context_providers = [business_context_provider, FileHistoryProvider(HISTORY_PATH)]
                            )

async def main():
     
     session = persistence_agent.create_session(session_id = "persistence")
     while True:
         query = input("Enter user query : ")

         if query in ['bye','exit']:
             break
         response = await persistence_agent.run(query, session = session)
         print(f"Agent Response : {response.text}")



if __name__ == "__main__":
    asyncio.run(main())
