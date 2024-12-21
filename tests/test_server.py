import pytest
from elevenlabs_mcp.server import ElevenLabsServer


def test_parse_script_valid_input():
    server = ElevenLabsServer()
    valid_json = '''
    {
        "script": [
            {
                "text": "Hello world",
                "voice_id": "voice1",
                "actor": "narrator"
            }
        ]
    }
    '''
    
    script_parts, debug_info = server.parse_script(valid_json)
    
    assert len(script_parts) == 1
    assert script_parts[0]["text"] == "Hello world"
    assert script_parts[0]["voice_id"] == "voice1"
    assert script_parts[0]["actor"] == "narrator"

def test_parse_script_invalid_json():
    server = ElevenLabsServer()
    invalid_json = "{ invalid json }"
    
    with pytest.raises(Exception) as exc_info:
        server.parse_script(invalid_json)
    
    assert "Invalid JSON format" in str(exc_info.value)
