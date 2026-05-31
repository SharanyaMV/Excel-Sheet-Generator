"""
Google ADK Excel Generator Agent
Minimal working agent with Gemini integration
"""

from google.adk.agents import Agent
from typing import Dict, Any, Optional
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.adk.tools import ToolContext
from google.genai import types

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from schema import generate_schema
from tools import generate_excel

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

WEB_HOST = os.getenv("WEB_HOST", "localhost")
WEB_PORT = os.getenv("WEB_PORT", "8080")


async def excel_generator(
    user_request: str,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Generate Excel and CSV files and register them as ADK artifacts.

    Args:
        user_request: Natural language description of desired Excel sheet
        tool_context: ADK tool context injected by the runtime

    Returns:
        Dictionary with generation status, message, file_names, artifact_versions, and metadata
    """
    schema = generate_schema(user_request)
    result = generate_excel(schema)

    if result.get("status") == "success":
        file_names = result.get("file_names", [])
        artifact_versions = {}
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
            "status": "success",
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

    file_name = result.get("file_name", "Generated.xlsx")
    return {
        "status": "error",
        "message": result.get("message", "Failed to generate Excel file."),
        "file_name": file_name
    }


# Define the root agent
root_agent = Agent(
    name="excel_generator_agent",
    model="gemini-2.5-flash",
    description="AI-powered Excel file generator using Google ADK and Gemini",
    instruction="""You are an Excel generation assistant powered by Google Gemini and ADK.

Your role is to:
1. Understand user requests for Excel or CSV files
2. Generate appropriate schemas based on their descriptions
3. Create only the file format requested by the user using the excel_generator tool
4. Add visuals only inside Excel workbooks, on the second worksheet named Visuals
5. Provide helpful confirmations when files are created

When a user asks for a file:
- Always use the excel_generator tool
- If the user asks only for Excel, generate only the .xlsx artifact
- If the user asks only for CSV, generate only the .csv artifact
- If the user asks for both Excel and CSV, generate both artifacts
- Excel artifacts include a second worksheet named Visuals
- If the user requests specific visuals, generate those chart types
- If the user does not specify visual types, generate basic visuals from the workbook data
- CSV artifacts must not include visuals
- Return the generated file_names and tell the user to open the ADK Web artifacts
- Do not invent or display a /download link
- Confirm successful generation and ensure the requested file or files are registered as artifacts

You can help users create:
- Employee databases
- Customer lists
- Product inventories
- Project management sheets
- Sales tracking sheets
- Financial reports
- Any custom data structures they describe
""",
    tools=[excel_generator]
)

__all__ = ["root_agent", "excel_generator"]
