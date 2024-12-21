from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ScriptPart:
    text: str
    voice_id: Optional[str] = None
    actor: Optional[str] = None

@dataclass
class AudioJob:
    id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    script_parts: List[Dict]
    output_file: Optional[str] = None
    error: Optional[str] = None
