from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .data_scheme.threads import SaveRequest, GetHistoryRequest
from datetime import datetime
from langchain_core.messages import AIMessage, HumanMessage

save_thread = APIRouter()

@save_thread.post("/save_thread")
async def save(request: Request, data: SaveRequest):

    thread_id = data.thread_id
    title = data.title

    user_id, created_at_str = thread_id.split("+", 1)
    request.app.chat_history.update_one(
        {"user_id": user_id},
        {
            "$push": {
                "threads": {
                    "thread_id": thread_id,
                    "title": title,
                    "created_at": datetime.utcnow()
                }
            }
        },
        upsert=True  
    )
    return JSONResponse(content={"message": "Thread saved successfully"}, status_code=200)



@save_thread.post("/get_history")
async def get_history(request: Request, data: GetHistoryRequest):
    user_id = data.user_id
    user_data = request.app.chat_history.find_one({"user_id": user_id})
    if user_data and "threads" in user_data:
        threads = user_data["threads"]
        threads.sort(key=lambda x: x["created_at"], reverse=True)
        for thread in threads:
            thread["created_at"] = thread["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return JSONResponse(content={"threads": threads}, status_code=200)
    else:
        return JSONResponse(content={"threads": []}, status_code=200)




@save_thread.post("/get_chat")
async def get_chat(request: Request, data: SaveRequest):

    thread_id = data.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    state = request.app.ask_graph.get_state(config)

    messages_list = []
    for msg in state.values["messages"]:
        if isinstance(msg, HumanMessage):
            messages_list.append(("user", msg.content))
        elif isinstance(msg, AIMessage):
            messages_list.append(("AI", msg.content))

    return JSONResponse(content={"messages": messages_list}, status_code=200)

