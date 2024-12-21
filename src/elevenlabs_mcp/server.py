import asyncio
from pathlib import Path
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from dotenv import load_dotenv

from .elevenlabs_api import ElevenLabsAPI

load_dotenv()

class ElevenLabsServer:
    def __init__(self):
        self.server = Server("elevenlabs-server")
        self.api = ElevenLabsAPI()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up handlers
        self.setup_tools()
    
    def setup_tools(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="generate_audio",
                    description="Generate audio from a story script and return the audio content directly",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "script": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "voice_id": {"type": "string"},
                                        "actor": {"type": "string"},
                                        "text": {"type": "string"}
                                    },
                                    "required": ["text"]
                                }
                            }
                        },
                        "required": ["script"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            if name == "generate_audio":
                try:
                    # Generate audio using the API - using the original API implementation
                    script_parts = arguments["script"]
                    output_file = self.api.generate_full_audio(
                        script_parts,
                        self.output_dir
                    )
                    
                    # Read the generated audio file
                    with open(output_file, "rb") as f:
                        audio_content = f.read()
                    
                    # Return both a success message and the audio content
                    return [
                        types.TextContent(
                            type="text",
                            text=f"Audio generation successful. File saved as: {output_file}"
                        )
                    ]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Error generating audio: {str(e)}"
                    )]
                    
                    
                job = self.jobs[job_id]
                response = {
                    "job_id": job_id,
                    "status": job.status
                }
                
                if job.status == "completed":
                    response["resource_uri"] = f"audio://{job_id}"
                elif job.status == "failed":
                    response["error"] = job.error
                    
            
                job = self.jobs[job_id]
                response = {
                    "job_id": job_id,
                    "status": job.status
                }
                
                if job.status == "completed":
                    response["resource_uri"] = f"audio://{job_id}"
                elif job.status == "failed":
                    response["error"] = job.error
                    
            return [types.TextContent(
                type="text",
                text="Unknown tool"
            )]

    async def run(self):
        """Run the server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="elevenlabs-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )

def main():
    """Entry point for the server"""
    server = ElevenLabsServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
