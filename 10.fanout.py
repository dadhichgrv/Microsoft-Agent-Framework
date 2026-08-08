import os, sys
import asyncio, time
from typing import Any, cast
from agent_framework import Agent, AgentResponse, ContextProvider, AgentSession,  SessionContext
from agent_framework.orchestrations import SequentialBuilder, ConcurrentBuilder
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
                                            Product : ME3 to ME5 Upsell

                                            Customer 2 :
                                            TPID : 54321
                                            Account Name : FOURTH COFFEE
                                            Estimated Revenue : $500
                                            Product : OE3 to ME3 Upsell


                                            """
                                            )

# Create AGent that takes product, revennnue and priority name and generate recommendations

product_agent = Agent(
                        client = OpenAIChatClient(),
                        name   = "product_agent",
                        instructions = """
                                          Provide product of the account provided in the data payload.  """,
                        context_providers = [business_context_provider]
                        )


revenue_agent = Agent(
                client = OpenAIChatClient(),
                name = "revenue_agent",
                instructions = """ Provide estimated revenue of the account provided in the data payload. """  ,
                context_providers = [business_context_provider]
                      ) 

account_agent = Agent(
                client = OpenAIChatClient(),
                name = "account_agent",
                instructions = " Provide count of accounts in data payload. Also provide sum of estimated revenue of all accounts. Do not provide anything else",
                context_providers = [business_context_provider]
                      ) 
    
workflow = ConcurrentBuilder(
                            participants = [product_agent, revenue_agent, account_agent] 
                            ).build()

async def main():
     
     query = " Fourth Coffee Account"
     events = await workflow.run(query)
     outputs = events.get_outputs()

     if outputs:
         final : AgentResponse = outputs[0]

         for msg in final.messages:
             name = msg.author_name or "assistant"
             print(f"[{name}]")
             print(msg.text)
  

if __name__ == "__main__":
    asyncio.run(main())
