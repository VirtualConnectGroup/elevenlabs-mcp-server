import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from dotenv import load_dotenv

from .elevenlabs_api import ElevenLabsAPI
from .models import AudioJob

load_dotenv()

class ElevenLabsServer:
    def __init__(self):
        self.server = Server("elevenlabs-server")
        self.api = ElevenLabsAPI()
        self.jobs: Dict[str, AudioJob] = {}
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up handlers
        self.setup_tools()
        self.setup_resources()
    
    def setup_tools(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="generate_audio",
                    description="Generate audio from a story script",
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
                ),
                types.Tool(
                    name="check_job_status",
                    description="Check the status of an audio generation job",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {"type": "string"}
                        },
                        "required": ["job_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            if name == "generate_audio":
                # Create new job
                job_id = f"job_{len(self.jobs)}"
                self.jobs[job_id] = AudioJob(
                    id=job_id,
                    status="pending",
                    script_parts=arguments["script"]
                )
                
                # Start processing in background
                asyncio.create_task(self._process_job(job_id))
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"job_id": job_id, "status": "pending"})
                )]
                
            elif name == "check_job_status":
                job_id = arguments["job_id"]
                if job_id not in self.jobs:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": "Job not found"})
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
                    
                return [types.TextContent(
                    type="text",
                    text=json.dumps(response)
                )]

    def setup_resources(self):
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            resources = []
            for job_id, job in self.jobs.items():
                if job.status == "completed" and job.output_file:
                    resources.append(
                        types.Resource(
                            uri=f"audio://{job_id}",
                            name=f"Generated Audio {job_id}",
                            mimeType="audio/mpeg"
                        )
                    )
            return resources

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> list[types.TextContent | types.ImageContent]:
            # Extract job_id from uri
            if not uri.startswith("audio://"):
                raise ValueError("Invalid resource URI")
            
            job_id = uri[7:]  # Remove 'audio://' prefix
            if job_id not in self.jobs:
                raise ValueError("Resource not found")
                
            job = self.jobs[job_id]
            if job.status != "completed" or not job.output_file:
                raise ValueError("Resource not ready")
                
            # Read the audio file
            with open(job.output_file, "rb") as f:
                content = f.read()
                
            return [types.BinaryContent(
                type="binary",
                data=content,
                mimeType="audio/mpeg"
            )]

    async def _process_job(self, job_id: str):
        """Process an audio generation job in the background"""
        job = self.jobs[job_id]
        try:
            job.status = "processing"
            
            # Generate audio using the API
            output_file = self.api.generate_full_audio(
                job.script_parts,
                self.output_dir
            )
            
            job.status = "completed"
            job.output_file = output_file
            
            # Notify client that a new resource is available
            if hasattr(self.server.request_context, "session"):
                await self.server.request_context.session.send_notification(
                    "notifications/resources/list_changed",
                    {}
                )
                
        except Exception as e:
            job.status = "failed"
            job.error = str(e)

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
                        notification_options=NotificationOptions(
                            resources={"listChanged": True}
                        ),
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
