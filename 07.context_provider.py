import os, sys
import asyncio
from typing import Any
from agent_framework import Agent, ContextProvider, AgentSession, SessionContext
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
                                            Customer1 :
                                            TPID : 12345
                                            Account Name : Contoso
                                            Estimated Revenue : $1,000
                                            Product : ME3 to ME5 Upsell

                                            Customer2 :
                                            TPID : 54321
                                            Account Name : FOURTH COFFEE
                                            Estimated Revenue : $500
                                            Product : OE3 to ME3 Upsell


                                            """
                                            )
        

business_agent = Agent(
                client = OpenAIChatClient(),
                instructions = "You are a business assistant that answers the user query in professional way",
                name = "BusinessAgent",
                context_providers = [business_context_provider]
                      ) 
    
session = business_agent.create_session()

async def main():
    while True:
        query = input("\n Enter Text \n")

        if query in ('bye','exit','quit'):
            break

        async for chunk in business_agent.run(query, session = session, stream = True):
            if chunk.text:
                print(chunk.text, end = "", flush = True)

   

if __name__ == "__main__":
    asyncio.run(main())