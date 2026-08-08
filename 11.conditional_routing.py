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


opportunity_agent = Agent(
                        client = OpenAIChatClient(),
                        name   = "oppty_agent",
                        instructions = """ You are opportunity creation assistant who helps user create opportunity from a lead.
                                            Return "Opportunity Created Successfully".
                                       """,
                        context_providers = [business_context_provider]
                        )


decline_agent = Agent(
                client = OpenAIChatClient(),
                name = "decline_agent",
                instructions = """ You are lead decline assistant who helps user decline a lead.
                                    Return "Lead Declined Successfully".
                                      """  ,
                context_providers = [business_context_provider]
                      ) 

share_partner_agent = Agent(
                client = OpenAIChatClient(),
                name = "share_partner_agent",
                instructions = """ You are partner sharing assistant who shares the lead with partner.
                                   Return "Lead Shared with partner successfuly". 
                                """,
                context_providers = [business_context_provider]
                      ) 

general_agent = Agent(
                client = OpenAIChatClient(),
                name = "general_agent",
                instructions = " You are general assistant who helps users with account information. Provide account details if asked",
                context_providers = [business_context_provider]
                      ) 
    
routing_agent = Agent(
                client = OpenAIChatClient(),
                name = "routing_agent",
                instructions = """ You are routing assistant who classifies user query.
                                   Read user query and respond with exactly one word:
                                   OPPORTUNITY, DECLINE, PARTNERSHARE, GENERAL.
                                   Do not respond with anything else.
                               """
                      ) 

route_map = {
    "OPPORTUNITY"  : opportunity_agent,
    "DECLINE"      : decline_agent,
    "PARTNERSHARE" : share_partner_agent,
    "GENERAL"      : general_agent
            }


async def handle_user_query(query : str):
    # Get response from routing agent
    router_response = await routing_agent.run(query)
    # convert response to uppercase
    category = router_response.messages[-1].text.strip().upper()
    # Fall Back code if response is other than defined categories
    category = category if category in route_map else 'GENERAL'
    # Decide the final agent to call based on response
    specialist = route_map[category]
    print(f"Routed to : {specialist.name}")

    # Run that agent 
    specialist_response = await specialist.run(query)
    return specialist_response.messages[-1].text



async def main():
     
     queries = [
         " Tell me about Contoso Account",
         " Created opportunity for Fourth Coffee Account",
         " Decline lead for Contoso Account",
         "Share Contoso account lead with partner"
               ]
     
     for query in queries:
         response = await handle_user_query(query)
         print(f"Response : {response}")
         print("-"*30)


  

if __name__ == "__main__":
    asyncio.run(main())
