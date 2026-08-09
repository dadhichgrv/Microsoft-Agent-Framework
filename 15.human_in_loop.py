import os, sys
import asyncio, time
from typing import Any, cast
from pydantic import BaseModel
from collections.abc import Awaitable, Callable
from agent_framework import Agent, ContextProvider, AgentSession,  SessionContext, FunctionInvocationContext, FunctionMiddleware, MiddlewareTermination
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

# Human in the loop (Human APproval Middleware)
class HumanApprovalMiddleware(FunctionMiddleware):
    def __init__(self, tools_requiring_approval : set[str] | None = None):
        self.tools_requiring_approval = tools_requiring_approval

    async def process(
            self,
            # This context will have all funnction details
            context   : FunctionInvocationContext,
            call_next : Callable[[], Awaitable[None]]
                    ):
        
        print ("Inside Middleware")
        tool_name      = context.function.name
        print(f"Tool Name : {tool_name}")
        needs_approval = tool_name in self.tools_requiring_approval

        # If no approval needed , then call tool and move forward
        if not needs_approval:
            await call_next()
            return 
        
        decision = input("Allow ? (y/n)").strip().lower()

        # If declined then do not retry and terminate else call tool
        if decision !='y':
            context.result = f"[{tool_name} was denied by user. Do not retry"
            raise MiddlewareTermination()
        
        await call_next()


# Create tools to take some actions
def opportunity_creation():
    return "Opportunity Created"


def decline_lead():
    return "Lead Declined Successfuly"

def share_partner():
    return "Shared with partner"

# Final Agent to take decisions
orchestration_agent = Agent(
                            client       = OpenAIChatClient(),
                            name         = "Orchestrator",
                            instructions = """ You are orchestrator that can create opportunity, delete a lead or share lead with partner.
                                               You have three tools for these : 'opportunity_creation', 'decline_lead', ' share_partner'
                                            """ ,
                            context_providers = [business_context_provider],
                            tools = [opportunity_creation, decline_lead, share_partner],
                            middleware = [HumanApprovalMiddleware(tools_requiring_approval = {'decline_lead','share_partner'})]
                            )

async def main():
     
     query = " Share with partner for Fourth Coffee"
     response = await orchestration_agent.run(query)
     print(response.text)



if __name__ == "__main__":
    asyncio.run(main())
