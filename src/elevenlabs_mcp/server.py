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
        Accepts:
        1. A JSON string with a script array containing dialogue parts
        2. Plain text to be converted to speech
        
        Each dialogue part should have:
        - text (required): The text to speak
        - voice_id (optional): The voice to use
        - actor (optional): The actor/character name
        
        Args:
            script_json: Input text or JSON string
            
        Returns:
            tuple containing:
                - list of parsed script parts
                - list of debug information strings
        """
        debug_info = []
        debug_info.append(f"Raw input: {script_json}")
        
        script_array = []
        
        # Remove any leading/trailing whitespace
        script_json = script_json.strip()
        
        try:
            # Try to parse as JSON first
            if script_json.startswith('['):
                # Direct array of script parts
                script_array = json.loads(script_json)
            elif script_json.startswith('{'):
                # Object with script array
                script_data = json.loads(script_json)
                script_array = script_data.get('script', [])
            else:
                # Treat as plain text if not JSON formatted
                script_array = [{"text": script_json}]
        except json.JSONDecodeError as e:
            # If JSON parsing fails and input looks like JSON, raise error
            if script_json.startswith('{') or script_json.startswith('['):
                debug_info.append(f"JSON parsing failed: {str(e)}")
                raise Exception("Invalid JSON format")
            # Otherwise treat as plain text
            debug_info.append("Input is plain text")
            script_array = [{"text": script_json}]
        
        script_parts = []
        for part in script_array:
            if not isinstance(part, dict):
                debug_info.append(f"Skipping non-dict part: {part}")
                continue
                
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
                    description="""Generate audio from a structured script with multiple voices and actors. 
                    Accepts either:
                    1. Plain text string
                    2. JSON string with format: {
                        "script": [
                            {
                                "text": "Text to speak",
                                "voice_id": "optional-voice-id",
                                "actor": "optional-actor-name"
                            },
                            ...
                        ]
                    }""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "script": {
                                "type": "string",
                                "description": "JSON string containing script array or plain text. For JSON format, provide an object with a 'script' array containing objects with 'text' (required), 'voice_id' (optional), and 'actor' (optional) fields."
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
                    
                    output_file, api_debug_info = self.api.generate_full_audio(
                        script_parts,
                        self.output_dir
                    )
                    debug_info.extend(api_debug_info)
                    
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
                            text="\n".join([
                                "Audio generation successful. Debug info:",
                                *debug_info
                            ])
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

                    debug_info.append(f"Created script parts: {script_parts}")
                    
                    output_file, api_debug_info = self.api.generate_full_audio(
                        script_parts,
                        self.output_dir
                    )
                    debug_info.extend(api_debug_info)
                    
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
                            text="\n".join([
                                "Audio generation successful. Debug info:",
                                *debug_info
                            ])
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
