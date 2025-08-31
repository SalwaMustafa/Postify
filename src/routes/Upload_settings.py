from fastapi import APIRouter,Request
from models import storage
from .schemes import SettingsInput
from models.enums import DataBaseEnum
from pymongo import ReturnDocument

settings_router = APIRouter()

@settings_router.post('/upload/settings')
async def get_answers(answers : SettingsInput, request : Request):

    collection = request.app.db_client[DataBaseEnum.SETTINGS_COLLECTION.value] 
    result = await collection.find_one_and_update({"user_id": answers.user_id},{"$set": answers.dict()}, upsert=True,return_document=ReturnDocument.AFTER)
    return {"inserted_id": str(result["_id"])}


@settings_router.get("/get_users/")
async def get_users(request: Request):

    collection = request.app.db_client[DataBaseEnum.SETTINGS_COLLECTION.value] 
    users = []
    async for user in collection.find():
        user["_id"] = str(user["_id"])  
        users.append(user)
    return users