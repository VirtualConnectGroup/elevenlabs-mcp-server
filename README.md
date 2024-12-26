# ElevenLabs MCP Server

A Model Context Protocol (MCP) server that integrates with ElevenLabs text-to-speech API, featuring both a server component and web-based UI for managing voice generation tasks.

## Features

- Generate audio from text using ElevenLabs API
- Support for multiple voices and script parts
- Web-based UI for:
  - Simple text-to-speech conversion
  - Multi-part script management
  - Voice history tracking and playback
  - Audio file downloads
- SQLite database for persistent history storage
- REST API endpoints for voice generation and management

## Installation

### Using uvx (recommended)

When using [`uvx`](https://docs.astral.sh/uv/guides/tools/), no specific installation is needed:

```bash
uvx elevenlabs-mcp-server
```

### Development Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   ```
3. Copy `.env.example` to `.env` and fill in your ElevenLabs credentials

## Web UI Installation

1. Navigate to the web UI directory:
   ```bash
   cd clients/web-ui
   ```
2. Install dependencies:
   ```bash
   pnpm install
   ```
3. Copy `.env.example` to `.env` and configure as needed

## MCP Settings Configuration

Add the following configuration to your MCP settings file (e.g., `cline_mcp_settings.json` for Claude Desktop):

```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "uvx",
      "args": ["elevenlabs-mcp-server"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key",
        "ELEVENLABS_VOICE_ID": "your-voice-id",
        "ELEVENLABS_MODEL_ID": "eleven_flash_v2"
      }
    }
  }
}
```

## Usage

### Starting the Server

1. Start the MCP server:
   ```bash
   uvx elevenlabs-mcp-server
   ```

2. Use with any MCP client (e.g., Claude Desktop)

### Running the Web UI

1. Start the web UI development server:
   ```bash
   cd clients/web-ui
   pnpm dev
   ```
2. Open http://localhost:5173 in your browser

### Available Tools

- `generate_audio_simple`: Generate audio from plain text using default voice settings
- `generate_audio_script`: Generate audio from a structured script with multiple voices and actors

## Development

Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
