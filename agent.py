from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types
from typing import Dict, Any, Optional

from schema import generate_schema
from tools import generate_excel
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Updated to accept tool_context injection from ADK
async def excel_generator(user_request: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Generate Excel and CSV files from user requirements.
    """
    try:
        # 1. Generate schema from user request
        schema = generate_schema(user_request)

        # 2. Generate Excel and CSV files and save them as ADK artifacts when available.
        result = generate_excel(schema)

        if result["status"] == "success":
            artifact_versions = {}
            file_names = result.get("file_names", [])
            file_label = "file" if len(file_names) == 1 else "files"
            if tool_context is not None:
                for generated_file in result.get("artifacts", []):
                    artifact = types.Part.from_bytes(
                        data=generated_file.get("content", b""),
                        mime_type=generated_file.get("content_type", "application/octet-stream"),
                    )
                    file_name = generated_file.get("file_name", "Generated")
                    artifact_versions[file_name] = await tool_context.save_artifact(file_name, artifact)

            return {
                "message": (
                    f"{', '.join(file_names)} generated successfully and saved as ADK {file_label}. "
                    f"Open the ADK Web artifact {'entry' if len(file_names) == 1 else 'entries'} to download."
                ),
                "file_names": file_names,
                "artifact_versions": artifact_versions,
                "columns": result.get("columns", []),
                "row_count": result.get("row_count", 0),
                "visuals": result.get("visuals", []),
            }
        else:
            return {
                "message": f"Error generating Excel file: {result['message']}",
                "status": "error"
            }
    except Exception as e:
        return {"message": f"Unexpected error: {str(e)}", "status": "error"}

# Create Agent - Use gemini-1.5-flash
root_agent = Agent(
    name="excel_generator_agent",
    model="gemini-1.5-flash", 
    description="AI-powered Excel file generator",
    instruction="""
    You are an Excel and CSV generation assistant. 
    1. Use the excel_generator tool for every request.
    2. Generate only the format requested: Excel only, CSV only, or both.
    3. Put visuals only in Excel workbooks, on the second worksheet named Visuals.
    4. If the user asks for specific visuals, generate those chart types.
    5. If the user does not specify visuals, generate basic Excel visuals from the data.
    6. CSV files must not include visuals.
    7. Tell the user the requested file or files are ready in the 'Artifacts' tab.
    """,
    tools=[excel_generator]
)

session_service = InMemorySessionService()
runner = None

def create_runner():
    global runner
    if runner is None:
        runner = Runner(
            agent=root_agent,
            app_name="excel_generator_app",
            session_service=session_service
        )
    return runner

async def main():
    print("🚀 Starting Excel Generator Agent...")
    session = await session_service.create_session(app_name="excel_generator_app", user_id="excel_user")
    runner = create_runner()
    
    while True:
        try:
            user_input = input("\n📝 Enter requirement (or 'quit'): ").strip()
            if user_input.lower() in ['quit', 'exit']: break
            if not user_input: continue

            content = types.Content(role="user", parts=[types.Part(text=user_input)])
            events = runner.run(user_id="excel_user", session_id=session.id, new_message=content)

            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(f"🤖 Agent: {part.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
