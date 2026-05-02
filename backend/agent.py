# backend/agent.py

import json
import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# OpenRouter client setup
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "deepseek/deepseek-chat-v3-0324"

# --- Step 1: Get tools from MCP server and convert to OpenAI format ---
async def get_mcp_tools(session: ClientSession):
    """Fetch tools from MCP server and format them for OpenAI tool calling"""
    tools_result = await session.list_tools()
    
    tools = []
    for tool in tools_result.tools:
        # Convert MCP tool schema to OpenAI function format
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })
    
    return tools


# --- Step 2: Call a tool on the MCP server ---
async def call_mcp_tool(session: ClientSession, tool_name: str, tool_args: dict):
    """Call a specific tool on the MCP server and return result"""
    result = await session.call_tool(tool_name, tool_args)
    
    # Extract text content from result
    if result.content:
        return result.content[0].text
    return "{}"


# --- Step 3: Main agent loop ---
async def run_agent(user_message: str, conversation_history: list, role: str = "patient"):
    """
    Main agent function:
    1. Connects to MCP server
    2. Gets available tools
    3. Sends message to LLM via OpenRouter
    4. If LLM wants to call a tool, calls it via MCP
    5. Feeds result back to LLM
    6. Returns final response
    """
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Get tools from MCP server
            tools = await get_mcp_tools(session)
            
            # Add the new user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Different system prompts based on role
            if role == "doctor":
                system_prompt = """You are a smart assistant for DOCTORS only.
You help doctors get summaries and reports about their appointments and patients.

Today's date is: """ + str(__import__('datetime').date.today()) + """

IMPORTANT: You are talking to a DOCTOR. Never ask if they are a patient or doctor.
Always use 24-hour time format (e.g. 09:00, 11:00, 14:00) when calling tools.

When a doctor asks for a summary or report:
1. Use get_appointment_stats tool to fetch their appointments
2. Summarize the results clearly in a readable format
3. A Slack notification will be sent automatically

Always be professional, clear and concise."""

            else:
                system_prompt = """You are a smart appointment assistant for PATIENTS only.
You help patients book appointments with doctors.

Today's date is: """ + str(__import__('datetime').date.today()) + """

IMPORTANT: You are talking to a PATIENT. Never ask if they are a patient or doctor.
Always use 24-hour time format (e.g. 09:00, 11:00, 14:00) when calling tools.

When showing available slots, ALWAYS format them as a simple numbered list like this:
1. 9:00 AM - 9:30 AM
2. 10:00 AM - 10:30 AM
3. 11:00 AM - 11:30 AM

Never use markdown tables for showing slots.

When a patient wants to book an appointment:
1. First check the doctor's availability using check_availability tool
2. Show available slots as a numbered list
3. When patient confirms a slot, use book_appointment tool to book it
4. If the requested slot is unavailable, use get_next_available_slot tool to find 
   the next available slot and suggest it to the patient
5. If the doctor is completely unavailable, automatically suggest the next 
   available slot using get_next_available_slot tool

AUTO-RESCHEDULING: If a patient's preferred slot or doctor is unavailable:
- Always use get_next_available_slot to find alternatives
- Present the alternative clearly
- Ask if they want to book the suggested slot

Always be helpful, clear and concise."""

            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history
            ]
            
            # Agentic loop - keep going until LLM stops calling tools
            try:
                while True:
                    import time
                    time.sleep(1)
                    
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        extra_headers={
                            "HTTP-Referer": "http://localhost:5173",
                            "X-Title": "Doctor Assistant"
                        }
                    )

                    if not response.choices or response.choices[0] is None:
                        return "I'm having trouble processing your request. Please try again."

                    response_message = response.choices[0].message

                    if response_message is None:
                        return "I received an empty response. Please try again."

                    # If no tool calls, LLM is done - return final response
                    if not response_message.tool_calls:
                        final_response = response_message.content
                        
                        # Add assistant response to history
                        conversation_history.append({
                            "role": "assistant",
                            "content": final_response
                        })
                        
                        return final_response
                    
                    # LLM wants to call tools
                    messages.append({
                        "role": "assistant",
                        "content": response_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in response_message.tool_calls
                        ]
                    })
                    
                    # Execute each tool call via MCP server
                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        print(f"[Agent] Calling tool: {tool_name} with args: {tool_args}")
                        
                        tool_result = await call_mcp_tool(session, tool_name, tool_args)
                        
                        print(f"[Agent] Tool result: {tool_result}")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })

            except Exception as e:
                print(f"[Agent] Error: {e}")
                return "Sorry, something went wrong. Please try again."
                # Loop continues - Claude will now process tool results
                # and either call more tools or give final response


def run_agent_sync(user_message: str, conversation_history: list, role: str = "patient"):
    """Synchronous wrapper around the async agent"""
    return asyncio.run(run_agent(user_message, conversation_history, role))