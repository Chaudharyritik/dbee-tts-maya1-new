from pydantic import BaseModel
from typing import Optional

class SynthesisRequest(BaseModel):
    text: str
    voice_description: Optional[str] = "Generic female voice"
    speed: Optional[float] = 1.0

class SynthesisResponse(BaseModel):
    audio_base64: str
    sample_rate: int
