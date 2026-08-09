import os, sys
import asyncio, time
from typing import Any, cast
from pydantic import BaseModel
from collections.abc import Awaitable, Callable
from agent_framework import Agent, ContextProvider, AgentSession, AgentResponse, SessionContext, FileCheckpointStorage
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
CHECKPOINT_PATH = ".checkpoint_history"


research_agent = Agent(
                        client = OpenAIChatClient(),
                        name   = "reserach_agent",
                        instructions = """
                                          You are a research analyst. Research topics and provide 5 short bullet points. """
                    
                        )


writer_agent = Agent(
                client = OpenAIChatClient(),
                instructions = """ You are blog writer agent. Write short blog in 100 words using research bullet points. """,  
                name = "writer_agent"
     
                      ) 
checkpoint_storage = FileCheckpointStorage(CHECKPOINT_PATH)
    
workflow = SequentialBuilder(
                            participants = [research_agent, writer_agent] ,
                            chain_only_agent_responses=True ,
                            intermediate_output_from = [research_agent],
                            checkpoint_storage = checkpoint_storage
                            ).build()

async def main():
     
     query = " AI in Interior Design"
     events = await workflow.run(query)
     outputs = events.get_outputs()

     for agent_response in outputs:
         agent_response : AgentResponse = agent_response


         for msg in agent_response.messages:
             name = msg.author_name or "assistant"
             print(f"[{name}]")
             print(msg.text)

# See savved checkpoints
     print("Workflow Name : ", workflow.name)
     saved = await checkpoint_storage.list_checkpoints(workflow_name = workflow.name)
     if saved:
         latest = saved[-1]
         print(f" Latest ID : {latest.checkpoint_id}")
         print(f" Timestamp : {latest.timestamp}")
         print(" To resume this workflow pass ")
         print(f" workflow.run(checkpoint_id = '{latest.checkpoint_id}') ")





if __name__ == "__main__":
    asyncio.run(main())
