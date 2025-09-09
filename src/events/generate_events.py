import socketio
import httpx
from helpers.config import get_settings
import json

settings = get_settings()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


def init_socket(app):
    app.mount("/", socketio.ASGIApp(sio, app))

    @sio.on("init_user")
    async def init_user(sid, data = {} ):
        """
        data = {"business_id": "123",
                "access_token" : "sjshho"}
        """
        try:
            business_id = data.get("business_id")
            user_info_api = f"{settings.BACKEND_URL}/business/info/{business_id}"

            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {data.get("access_token")}"}
                response = await client.get(user_info_api, headers=headers)
                response.raise_for_status()
                user_info = response.json()
                

            session_data = {
                "business_id": business_id,
                "user_info": user_info['data']
            }

            await sio.save_session(sid, session_data)
            await sio.emit("ack", {"msg": "User info received"}, to=sid)

        except Exception as e:
            await sio.emit("error", {"msg": f"Init failed: {str(e)}"}, to=sid)

    @sio.on("generate_request")
    async def handle_generate(sid, data = {}):
        """
        data = {"message": "write me a post about social media"}
        """
        
        if not data.get("message"):
            await sio.emit("error", {"msg": "No message received"}, to=sid)
            return

        try:
            
            session = await sio.get_session(sid)
            user_id = session["user_info"]["userId"]

            await sio.emit("bot_typing", {}, to=sid)

            config = {"configurable": {"thread_id": f"{user_id}_generate"}}

            result = await app.graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": data["message"]}],
                    "user_info": session["user_info"],
                },
                config=config,
            )
            
            msg = result["messages"][-1]
            json_response = json.loads(msg.content)

            await sio.emit("bot_message", json_response, to=sid)

            session["last_post"] = json_response
            
            await sio.save_session(sid, session)

        except Exception as e:
            await sio.emit("error", {"msg": f"Generate failed: {str(e)}"}, to=sid)

    @sio.on("publish_post")
    async def publish_post(sid, data = {}):

        """
        data = {"access_token" : "sjshho"}
        """

        try:
            
            session = await sio.get_session(sid)
            last_post = session.get("last_post")
            
            if not last_post:
                await sio.emit("error", {"msg": "No post to publish"}, to=sid)
                return

            url = f"{settings.BACKEND_URL}/post"
            post_data = {
                "business_id": session["business_id"],
                "user_id": session["user_info"]["userId"],
                "content" : session["last_post"]
            }
            

            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {data.get("access_token")}"}
                response = await client.post(url, json=post_data, headers=headers)
                response.raise_for_status()

            await sio.emit(
                "ack", {"msg": "Post sent to backend for publishing"}, to=sid
            )

        except Exception as e:
            await sio.emit("error", {"msg": f"Publish failed: {str(e)}"}, to=sid)
