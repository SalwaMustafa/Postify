from fastapi import FastAPI
from helpers.config import get_settings
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from enums.DataBaseEnum import DataBaseEnum
from chatbots.generate_chat import PostGraph  
from chatbots.ask_chat import AskGraph
from routes import healthy_check, save_chat
from events.generate_events import init_socket, socket_app


settings = get_settings()
app = FastAPI()
app.mount("/socket.io", socket_app)


@app.on_event("startup")
async def startup_event():
    app.mongo_conn = MongoClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    app.memory_generate = MongoDBSaver(client = app.mongo_conn, db_name=settings.MONGODB_DATABASE,
                                       checkpoint_collection_name= DataBaseEnum.GENERATE_COLLECTION.value)
    app.memory_ask = MongoDBSaver(client = app.mongo_conn, db_name=settings.MONGODB_DATABASE,
                                  checkpoint_collection_name= DataBaseEnum.ASK_COLLECTION.value)
    
    app.chat_history = app.db_client[DataBaseEnum.CHAT_HISTORY.value]
    app.assistant_1 = PostGraph(app.memory_generate)
    app.graph = app.assistant_1.graph
    app.assistant_2 = AskGraph(app.memory_ask)
    app.ask_graph = app.assistant_2.graph
    init_socket(app)


@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_conn.close()


app.include_router(healthy_check.health_router)
app.include_router(save_chat.save_thread)
