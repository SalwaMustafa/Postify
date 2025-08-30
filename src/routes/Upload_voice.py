from fastapi import APIRouter, UploadFile, File
from controllers.Validate_Voice_Controller import VoiceController


upload_voice_router = APIRouter()
voice_controller = VoiceController()

@upload_voice_router.post("/upload/voice")

async def upload_voice(file: UploadFile = File(...)):
    signal , message = await voice_controller.validate_uploaded_voice(file)
    return {
        "signal" : signal,
        "message" : message
        }

