import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
import mcp.types as types
from elevenlabs_mcp.server import ElevenLabsServer

@pytest.fixture
def server():
    return ElevenLabsServer()

@pytest.mark.asyncio
async def test_list_tools(server):
    """Test that the server exposes the expected tools"""
    tools = await server.server.handle_request(
        {"method": "tools/list"}
    )
    
    tool_names = [tool.name for tool in tools.tools]
    assert "generate_audio" in tool_names
    assert "check_job_status" in tool_names

@pytest.mark.asyncio
async def test_generate_audio(server):
    """Test audio generation job creation"""
    script = [
        {
            "voice_id": "test_voice",
            "actor": "Test Actor",
            "text": "Test text"
        }
    ]
    
    result = await server.server.handle_request({
        "method": "tools/call",
        "params": {
            "name": "generate_audio",
            "args": {"script": script}
        }
    })
    
    response = json.loads(result.content[0].text)
    assert "job_id" in response
    assert response["status"] == "pending"

@pytest.mark.asyncio
async def test_check_job_status(server):
    """Test job status checking"""
    # First create a job
    script = [{"text": "Test text"}]
    result = await server.server.handle_request({
        "method": "tools/call",
        "params": {
            "name": "generate_audio",
            "args": {"script": script}
        }
    })
    job_id = json.loads(result.content[0].text)["job_id"]
    
    # Check its status
    result = await server.server.handle_request({
        "method": "tools/call",
        "params": {
            "name": "check_job_status",
            "args": {"job_id": job_id}
        }
    })
    
    status = json.loads(result.content[0].text)
    assert status["job_id"] == job_id
    assert status["status"] in ["pending", "processing", "completed", "failed"]

@pytest.mark.asyncio
async def test_list_resources(server):
    """Test resource listing"""
    resources = await server.server.handle_request(
        {"method": "resources/list"}
    )
    assert isinstance(resources.resources, list)

@pytest.mark.asyncio
async def test_read_resource(server):
    """Test reading a non-existent resource returns error"""
    with pytest.raises(ValueError, match="Invalid resource URI"):
        await server.server.handle_request({
            "method": "resources/read",
            "params": {"uri": "invalid://uri"}
        })

    with pytest.raises(ValueError, match="Resource not found"):
        await server.server.handle_request({
            "method": "resources/read",
            "params": {"uri": "audio://nonexistent"}
        })
