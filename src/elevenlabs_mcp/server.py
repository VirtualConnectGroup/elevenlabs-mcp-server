import asyncio
from pathlib import Path
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from dotenv import load_dotenv
import json

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
    
    def parse_script(self, script_json: str) -> tuple[list[dict], list[str]]:
        """
        Parse the input into a list of script parts and collect debug information.
        Accepts either JSON string containing script array or plain text.
        
        Args:
            script_json: JSON string containing script array or plain text
            
        Returns:
            tuple containing:
                - list of parsed script parts
                - list of debug information strings
                
        Raises:
            Exception: If input format is incorrect or if JSON is malformed
        """
        debug_info = []
        debug_info.append(f"Raw input: {script_json}")
        
        script_array = []
        # Check if input looks like JSON (starts with '{' after stripping whitespace)
        if script_json.strip().startswith('{'):
            try:
                # Parse as JSON since it looks like JSON
                script_data = json.loads(script_json)
                script_array = script_data.get('script', [])
                debug_info.append(f"Successfully parsed as JSON. Script array: {script_array}")
            except json.JSONDecodeError as e:
                debug_info.append(f"JSON parse error: {str(e)}")
                raise Exception(f"Invalid JSON format: {str(e)}")
        else:
            # Treat as plain text
            debug_info.append("Input is plain text")
            text = script_json.strip()
            if text:  # Only create an entry if text is not empty
                script_array = [{"text": text}]
                debug_info.append(f"Created script array from plain text: {script_array}")
        
        script_parts = []
        for part in script_array:
            debug_info.append(f"Processing part: {part}")
            debug_info.append(f"Part type: {type(part)}")
            if isinstance(part, dict):
                text = part.get("text", "").strip()
                if not text:
                    debug_info.append("Missing or empty text field")
                    raise Exception("Missing required field 'text'")
                    
                new_part = {
                    "text": text,
                    "voice_id": part.get("voice_id"),
                    "actor": part.get("actor")
                }
                debug_info.append(f"Created part: {new_part}")
                script_parts.append(new_part)
        
        debug_info.append(f"Final script_parts: {script_parts}")
        return script_parts, debug_info

    def setup_tools(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="generate_audio_simple",
                    description="Generate audio from plain text using default voice settings",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Plain text to convert to audio"
                            },
                            "voice_id": {
                                "type": "string",
                                "description": "Optional voice ID to use for generation"
                            }
                        },
                        "required": ["text"]
                    }
                ),
                types.Tool(
                    name="generate_audio_script",
                    description="Generate audio from a structured script with multiple voices and actors",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "script": {
                                "type": "string",
                                "description": "JSON string containing script array or plain text"
                            }
                        },
                        "required": ["script"]
                    }
                )
            ]

        import base64  # Add this import at the top of the file

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.EmbeddedResource]:
            try:
                debug_info = []
                
                if name == "generate_audio_simple":
                    debug_info.append(f"Processing simple audio request")
                    debug_info.append(f"Arguments: {arguments}")
                    
                    text = arguments.get("text", "").strip()
                    voice_id = arguments.get("voice_id")
                    
                    if not text:
                        raise ValueError("Text cannot be empty")
                    
                    script_parts = [{
                        "text": text,
                        "voice_id": voice_id
                    }]
                    
                    debug_info.append(f"Created script parts: {script_parts}")
                    
                    output_file = self.api.generate_full_audio(
                        script_parts,
                        self.output_dir
                    )
                    
                    # Read the generated audio file and encode it as base64
                    with open(output_file, 'rb') as f:
                        audio_bytes = f.read()
                        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                        
                    # Generate unique URI for the resource
                    filename = Path(output_file).name
                    resource_uri = f"audio://{filename}"
                        
                    # Return both a status message and the audio file content
                    return [
                        types.TextContent(
                            type="text",
                            text=f"Audio generation successful."
                        ),
                        types.EmbeddedResource(
                            type="resource",
                            resource=types.BlobResourceContents(
                                uri=resource_uri,
                                name=filename,
                                blob=audio_base64,
                                mimeType="audio/mpeg"
                            )
                        )
                    ]
                    
                elif name == "generate_audio_script":
                    script_json = arguments.get("script", "{}")
                    script_parts, parse_debug_info = self.parse_script(script_json)
                    debug_info.extend(parse_debug_info)
                    
                    output_file = self.api.generate_full_audio(
                        script_parts,
                        self.output_dir
                    )
                    
                    # Read the generated audio file and encode it as base64
                    with open(output_file, 'rb') as f:
                        audio_bytes = f.read()
                        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                        
                    # Generate unique URI for the resource
                    filename = Path(output_file).name
                    resource_uri = f"audio://{filename}"
                        
                    # Return both a status message and the audio file content
                    return [
                        types.TextContent(
                            type="text",
                            text=f"Audio generation successful."
                        ),
                        types.EmbeddedResource(
                            type="resource",
                            resource=types.BlobResourceContents(
                                uri=resource_uri,
                                name=filename,
                                blob=audio_base64,
                                mimeType="audio/mpeg"
                            )
                        )
                    ]
                    
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                error_msg = "\n".join([
                    "Error generating audio. Debug info:",
                    *debug_info,
                    f"Error: {str(e)}"
                ])
                return [types.TextContent(
                    type="text",
                    text=error_msg
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
