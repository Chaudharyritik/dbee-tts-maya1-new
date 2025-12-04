from fastapi import APIRouter, HTTPException
from app.schemas import SynthesisRequest, SynthesisResponse
from app.services.tts_service import TTSService
import base64

router = APIRouter()
tts_service = TTSService()

@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_text(request: SynthesisRequest):
    try:
        audio_bytes = tts_service.synthesize(
            request.text, 
            request.voice_description, 
            request.speed
        )
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return SynthesisResponse(audio_base64=audio_base64, sample_rate=24000)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
