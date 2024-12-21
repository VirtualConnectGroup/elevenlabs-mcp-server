import os
import requests
from pathlib import Path
from typing import Dict, List, Optional
from pydub import AudioSegment
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsAPI:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY") or "sk_35648f52f0d7dcfe22ee543feafe21c2100a2afeb20b2957"
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID") or "dQn9HIMKSXWzKBGkbhfP"
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID") or "eleven_flash_v2"
        self.stability = os.getenv("ELEVENLABS_STABILITY") or 0.5
        self.similarity_boost = os.getenv("ELEVENLABS_SIMILARITY_BOOST") or 0.75
        self.style = os.getenv("ELEVENLABS_STYLE") or 0.1
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def generate_audio_segment(self, text: str, voice_id: str, output_file: Optional[str] = None,
                      previous_text: Optional[str] = None, next_text: Optional[str] = None,
                      previous_request_ids: Optional[List[str]] = None) -> tuple[bytes, str]:
        """Generate audio using specified voice with context conditioning"""
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
                "style": self.style
            }
        }

        # Add context conditioning
        if previous_text is not None:
            data["previous_text"] = previous_text
        if next_text is not None:
            data["next_text"] = next_text
        if previous_request_ids:
            data["previous_request_ids"] = previous_request_ids[-3:]  # Maximum of 3 previous IDs
        
        response = requests.post(
            f"{self.base_url}/text-to-speech/{voice_id}",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            if output_file:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
            return response.content, response.headers["request-id"]
        else:
            raise Exception(f"Failed to generate audio: {response.text}")

    def generate_full_audio(self, script_parts: List[Dict], output_dir: Path) -> str:
        """Generate audio for multiple parts using request stitching"""
        # Create output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        # Final output file path with unique file name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = output_dir / f"full_audio_{timestamp}.mp3"
        
        debug_info = []
        debug_info.append("ElevenLabsAPI - Starting generate_full_audio")
        debug_info.append(f"Input script_parts: {script_parts}")
        
        # Initialize segments list and request IDs tracking
        segments = []
        previous_request_ids = []
        
        debug_info.append("Processing all_texts")
        all_texts = []
        for part in script_parts:
            debug_info.append(f"Processing text from part: {part}")
            text = str(part.get('text', ''))
            debug_info.append(f"Extracted text: {text}")
            all_texts.append(text)
        debug_info.append(f"Final all_texts: {all_texts}")
        
        for i, part in enumerate(script_parts):
            debug_info.append(f"Processing part {i}: {part}")
            part_voice_id = part.get('voice_id')
            if not part_voice_id:
                part_voice_id = self.voice_id
            text = str(part.get('text', ''))
            if not text:
                continue
                
            debug_info.append(f"Using voice ID: {part_voice_id}")
            
            # Determine previous and next text for context
            is_first = i == 0
            is_last = i == len(script_parts) - 1
            
            previous_text = None if is_first else " ".join(all_texts[:i])
            next_text = None if is_last else " ".join(all_texts[i + 1:])
            
            # Generate audio with context conditioning
            audio_content, request_id = self.generate_audio_segment(
                text=text,
                voice_id=part_voice_id,
                previous_text=previous_text,
                next_text=next_text,
                previous_request_ids=previous_request_ids
            )
            
            # Add request ID to history
            previous_request_ids.append(request_id)
            
            # Convert audio content to AudioSegment and add to segments
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_content))
            segments.append(audio_segment)
        
        # Combine all segments
        if segments:
            final_audio = segments[0]
            for segment in segments[1:]:
                final_audio = final_audio + segment
            
            # Export combined audio
            final_audio.export(output_file, format="mp3")
            
            return str(output_file)
        else:
            error_msg = "\n".join([
                "No audio segments were generated. Debug info:",
                *debug_info
            ])
            raise Exception(error_msg)
