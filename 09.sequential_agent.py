import os, sys
import asyncio
from typing import Any, cast
from agent_framework import Agent, AgentResponse, AgentResponseUpdate, ContextProvider, AgentSession,  SessionContext
from agent_framework.orchestrations import SequentialBuilder
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

analyst_agent = Agent(
                        client = OpenAIChatClient(),
                        name   = "analyst_agent",
                        instructions = """
                                          You are a business data analyst. Provide short structural analysis of the account metrics provided in the data payload.  """,
                        context_providers = [business_context_provider]
                        )


summary_agent = Agent(
                client = OpenAIChatClient(),
                instructions = """
   ROLE: Executive Summarizer.
    TASK: Write a brief, direct business summary of the raw metrics provided in the input text.
    OUTPUT FORMAT: Start directly with the summary data. Write as a direct corporate statement for a client dashboard.
    """  
                ,
                name = "summary_agent"
     
                      ) 

email_agent = Agent(
                client = OpenAIChatClient(),
                instructions = " Draft a professional customer outreach email using only the provided summary."
                ,
                name = "email_agent"
     
                      ) 
    
workflow = SequentialBuilder(
                            participants = [analyst_agent, summary_agent, email_agent] ,
                            chain_only_agent_responses=True ,
                            intermediate_output_from = [analyst_agent, summary_agent]
                           
                            ).build()

async def main():
     
     query = " Fourth Coffee Account"
     events = await workflow.run(query)

     for agent_response in events.get_outputs():
         agent_response : AgentResponse = agent_response

         for msg in agent_response.messages:
             name = msg.author_name or "assistant"
             print(f"[{name}]")
             print(msg.text)
  

if __name__ == "__main__":
    asyncio.run(main())
