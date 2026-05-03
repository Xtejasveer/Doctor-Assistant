# This file demonstrates and tests the complete MCP architecture
# Run this to verify: Tools, Resources, and Prompts are all working

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json

async def test_mcp_architecture():
    print("=" * 60)
    print("MCP ARCHITECTURE TEST")
    print("Testing: Client → Server → Tool/Resource/Prompt")
    print("=" * 60)

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("\n MCP Client connected to MCP Server successfully")

            # --- 1. Test Tool Discovery ---
            print("\n" + "=" * 60)
            print("1. DYNAMIC TOOL DISCOVERY (tools/list)")
            print("=" * 60)
            tools = await session.list_tools()
            print(f" {len(tools.tools)} tools discovered at runtime:")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")

            # --- 2. Test Resource Discovery ---
            print("\n" + "=" * 60)
            print("2. RESOURCE DISCOVERY (resources/list)")
            print("=" * 60)
            resources = await session.list_resources()
            print(f" {len(resources.resources)} resources discovered:")
            for resource in resources.resources:
                print(f"   - {resource.uri}: {resource.description}")

            # --- 3. Test Prompt Discovery ---
            print("\n" + "=" * 60)
            print("3. PROMPT DISCOVERY (prompts/list)")
            print("=" * 60)
            prompts = await session.list_prompts()
            print(f" {len(prompts.prompts)} prompts discovered:")
            for prompt in prompts.prompts:
                print(f"   - {prompt.name}: {prompt.description}")

            # --- 4. Test Tool Execution ---
            print("\n" + "=" * 60)
            print("4. TOOL EXECUTION via MCP Protocol")
            print("=" * 60)

            # Test get_all_doctors tool
            print("\n→ Calling tool: get_all_doctors")
            result = await session.call_tool("get_all_doctors", {})
            data = json.loads(result.content[0].text)
            print(f" Tool executed successfully")
            print(f"   Found {len(data['doctors'])} doctors:")
            for doc in data['doctors']:
                print(f"   - {doc['name']} ({doc['specialization']})")

            # Test check_availability tool
            from datetime import date, timedelta
            tomorrow = str(date.today() + timedelta(days=1))
            print(f"\n→ Calling tool: check_availability (Dr. Ahuja, {tomorrow})")
            result = await session.call_tool("check_availability", {
                "doctor_name": "Dr. Ahuja",
                "date": tomorrow
            })
            data = json.loads(result.content[0].text)
            print(f" Tool executed successfully")
            if "available_slots" in data:
                print(f"   Found {len(data['available_slots'])} available slots")
            else:
                print(f"   Result: {data}")

            # --- 5. Test Resource Reading ---
            print("\n" + "=" * 60)
            print("5. RESOURCE READING via MCP Protocol")
            print("=" * 60)

            print("\n→ Reading resource: doctors://all")
            result = await session.read_resource("doctors://all")
            print(f" Resource read successfully")
            print(f"   Content preview: {result.contents[0].text[:100]}...")

            print("\n→ Reading resource: appointments://today")
            result = await session.read_resource("appointments://today")
            print(f" Resource read successfully")
            print(f"   Content preview: {result.contents[0].text[:100]}...")

            # --- 6. Test Prompt Retrieval ---
            print("\n" + "=" * 60)
            print("6. PROMPT RETRIEVAL via MCP Protocol")
            print("=" * 60)

            print("\n→ Getting prompt: book_appointment_prompt")
            result = await session.get_prompt("book_appointment_prompt", {
                "doctor_name": "Dr. Ahuja",
                "date": tomorrow
            })
            print(f" Prompt retrieved successfully")
            print(f"   Prompt: {result.messages[0].content.text}")

            print("\n→ Getting prompt: doctor_report_prompt")
            result = await session.get_prompt("doctor_report_prompt", {
                "doctor_name": "Dr. Ahuja",
                "date": tomorrow
            })
            print(f" Prompt retrieved successfully")
            print(f"   Prompt: {result.messages[0].content.text}")

            # --- Summary ---
            print("\n" + "=" * 60)
            print("MCP ARCHITECTURE TEST COMPLETE")
            print("=" * 60)
            print(" MCP Client-Server connection working")
            print(" Dynamic tool discovery working")
            print(" Dynamic resource discovery working")
            print(" Dynamic prompt discovery working")
            print(" Tool execution via MCP protocol working")
            print(" Resource reading via MCP protocol working")
            print(" Prompt retrieval via MCP protocol working")
            print("\nAll MCP primitives (Tool/Resource/Prompt) are")
            print("properly implemented and accessible via MCP protocol.")
            print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp_architecture())