from fastapi import  APIRouter, Request
from .schemes.text import TextInput
from controllers import TextController
from models.enums import DataBaseEnum

upload_text_router = APIRouter()

@upload_text_router.post("/upload/text")
async def upload_text(data: TextInput, request:Request):

    validate_text = TextController()
    signal , message = validate_text.validate_input(data.user_id, data.content)

    if signal:
        collection = request.app.db_client[DataBaseEnum.TEXT_COLLECTION.value] 
        result = await collection.insert_one(data.dict())
        return{ "inserted_id": str(result.inserted_id)}

    return {
        "signal" : signal,
        "message" : message
        }

