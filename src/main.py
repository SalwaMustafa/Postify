from fastapi import FastAPI
from helpers.config import get_settings
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from enums.DataBaseEnum import DataBaseEnum
from chatbots.generate_chat import get_graph  
from chatbots.ask_chat import get_ask_graph
from routes import healthy_check, save_chat
from events.generate_events import init_socket


settings = get_settings()
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    app.mongo_conn = MongoClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    app.memory_generate = MongoDBSaver(app.db_client[DataBaseEnum.GENERATE_COLLECTION.value])
    app.memory_ask = MongoDBSaver(app.db_client[DataBaseEnum.ASK_COLLECTION.value])
    app.chat_history = app.db_client[DataBaseEnum.CHAT_HISTORY.value]
    app.graph = get_graph(app)
    app.ask_graph = get_ask_graph(app)
    init_socket(app)


@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_conn.close()


app.include_router(healthy_check.health_router)
app.include_router(save_chat.save_thread)
