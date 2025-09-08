from fastapi import APIRouter, WebSocket

api = APIRouter()


@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app = websocket.app
    graph = app.graph
    
    while True:
        data = await websocket.receive_json()

        user_msg = data["message"]       
        user_info = data["user_info"]    
        thread_id = str(user_info["user_id"]) 

        config = {"configurable": {"thread_id": thread_id}}

        result = await graph.ainvoke(
            {
                "messages": [{"role": "user", "content": user_msg}],
                "user_info": user_info
            },
            config=config
        )

        #await websocket.send_text(result["messages"][-1].content)
        msg = result["messages"][-1]
        
        
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            json_response = msg.tool_calls[0]["args"]
            await websocket.send_json(json_response)
        else:
            await websocket.send_text(msg.content)
