from fastapi import  APIRouter
from .schemes.text import TextInput
from models import storage
from controllers import TextController

upload_text_router = APIRouter()

@upload_text_router.post("/upload/text")
async def upload_text(data: TextInput):

    validate_text = TextController()
    signal , message = validate_text.validate_input(data.user_id, data.content)
    storage.text_inputs[data.user_id] = data.content
    return {
        "signal" : signal,
        "message" : message,
        "received_text": data.content
        }
