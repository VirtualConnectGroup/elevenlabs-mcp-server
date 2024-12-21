# ElevenLabs MCP Server

A Model Context Protocol (MCP) server that integrates with ElevenLabs text-to-speech API.

## Features

- Generate audio from text using ElevenLabs API
- Support for multiple voices and script parts
- Asynchronous job processing
- Resource-based audio file access
- Job status tracking

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Copy `.env.example` to `.env` and fill in your ElevenLabs credentials

## Usage

1. Start the server:
   ```bash
   python -m elevenlabs_mcp.server
   ```

2. Use with any MCP client (e.g., Claude Desktop)

### Tools

- `generate_audio`: Start an audio generation job
- `check_job_status`: Check job status

### Resources

Generated audio files are available as resources with URIs like `audio://job_0`

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

## License

MIT
