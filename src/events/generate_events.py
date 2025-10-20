import os
import tempfile
import requests
import socketio
import httpx
import base64
from helpers.config import get_settings
import json
from chatbots.create_message import user_preferences
from chatbots.llm import voice_headers,voice_model

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
                headers = {"Authorization": f"Bearer {data.get('access_token')}"}
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
        data = {"message": "write me a post about social media",
                "approximate_words": num,
                "hashtags": bool,
                "emojis": bool,
                "required_words": [string],
                "forbidden_words": [string]
        }
        """
        
        if not data.get("message"):
            await sio.emit("error", {"msg": "No message received"}, to=sid)
            return

        try:
            
            session = await sio.get_session(sid)
            user_id = session["user_info"]["userId"]

            await sio.emit("bot_typing", ".....", to=sid)

            config = {"configurable": {"thread_id": f"{user_id}_generate"}}

            result = await app.graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": user_preferences(data)}],
                    "user_info": session["user_info"],
                },
                config=config,
            )
            
            msg = result["messages"][-1]
            json_response = json.loads(msg.content)

            await sio.emit("bot_message", json_response, to=sid)

            session["last_post"] = json_response
            session['approximate_words'] = data['approximate_words']
            session['hashtags'] = data['hashtags']
            session['has_emojis'] = data['emojis']
            session['required_words'] = data['required_words']
            session['forbidden_words'] = data['forbidden_words']

            
            await sio.save_session(sid, session)

        except Exception as e:
            await sio.emit("error", {"msg": f"Generate failed: {str(e)}"}, to=sid)

    os.makedirs("uploads", exist_ok=True) 
    @sio.on("generate_voice")
    async def generate_voice(sid, data = {}):
        """
        data = {"audio": "base64 string",
                "approximate_words": num,
                "hashtags": bool,
                "emojis": bool,
                "required_words": [string],
                "forbidden_words": [string]
        }
        """
        try:
            if not data.get("audio"):
                await sio.emit("error", {"msg": "No audio received"}, to=sid)
                return

           
            audio_data = base64.b64decode(data["audio"])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            try:
                await sio.emit("status", {"msg": "Transcribing audio..."}, to=sid)
                with open(temp_audio_path, "rb") as f:
                    data = f.read()

                response = requests.post(voice_model, headers=voice_headers, data=data)

                os.unlink(temp_audio_path)

                await sio.emit("transcription", response.json(), to=sid)

            except Exception as e:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                await sio.emit("error", {"msg": f"Transcription failed: {str(e)}"}, to=sid)

        except Exception as e:
            await sio.emit("error", {"msg": f"Audio processing failed: {str(e)}"}, to=sid)

        try:
            
            session = await sio.get_session(sid)
            user_id = session["user_info"]["userId"]
            data['message'] = response.json().get('text','')

            await sio.emit("bot_typing", ".....", to=sid)

            config = {"configurable": {"thread_id": f"{user_id}_generate"}}

            result = await app.graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": user_preferences(data)}],
                    "user_info": session["user_info"],
                },
                config=config,
            )
            
            msg = result["messages"][-1]
            json_response = json.loads(msg.content)

            await sio.emit("bot_message", json_response, to=sid)

            session["last_post"] = json_response
            session['approximate_words'] = data['approximate_words']
            session['hashtags'] = data['hashtags']
            session['has_emojis'] = data['emojis']
            session['required_words'] = data['required_words']
            session['forbidden_words'] = data['forbidden_words']

            
            await sio.save_session(sid, session)

        except Exception as e:
            await sio.emit("error", {"msg": f"Generate failed: {str(e)}"}, to=sid)

    @sio.on("toggle_hashtags")
    async def toggle_hashtags(sid, data = {}):
        
        session = await sio.get_session(sid)
        hashtags = session.get('hashtags')

        if hashtags is None:
            await sio.emit("error", {"msg": "No post generated yet"}, to=sid)
            return
        
        if hashtags:
            session['hashtags'] = False

            user_id = session["user_info"]["userId"]
            await sio.emit("bot_typing", ".....", to=sid)
            config = {"configurable": {"thread_id": f"{user_id}_generate"}}
            result = await app.graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": "Remove hashtags from the post, keep everything else unchanged."}],
                    "user_info": session["user_info"],
                },
                config=config,
            )
            
            msg = result["messages"][-1]
            json_response = json.loads(msg.content)

            await sio.emit("bot_message", json_response, to=sid)

            session["last_post"] = json_response
            
            
        else:
            session['hashtags'] = True
            user_id = session["user_info"]["userId"]
            await sio.emit("bot_typing", ".....", to=sid)
            config = {"configurable": {"thread_id": f"{user_id}_generate"}}
            result = await app.graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": "Add hashtags to the post, keep everything else unchanged."}],
                    "user_info": session["user_info"],
                },
                config=config,
            )

            msg = result["messages"][-1]
            json_response = json.loads(msg.content)

            await sio.emit("bot_message", json_response, to=sid)
            session["last_post"] = json_response

        await sio.save_session(sid, session) 

    @sio.on("toggle_emojis")
    async def toggle_emojis(sid, data = {}):
        session = await sio.get_session(sid)
        emojis = session.get('has_emojis')

        if emojis is None:
            await sio.emit("error", {"msg": "No post generated yet"}, to=sid)
            return
        
        if emojis:
            session['has_emojis'] = False

            user_id = session["user_info"]["userId"]
            await sio.emit("bot_typing", ".....", to=sid)
            config = {"configurable": {"thread_id": f"{user_id}_generate"}}
            result = await app.graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": "Remove emojis from the post, keep everything else unchanged."}],
                    "user_info": session["user_info"],
                },
                config=config,
            )
            
            msg = result["messages"][-1]
            json_response = json.loads(msg.content)

            await sio.emit("bot_message", json_response, to=sid)

            session["last_post"] = json_response
            
            
        else:
            session['has_emojis'] = True
            user_id = session["user_info"]["userId"]
            await sio.emit("bot_typing", ".....", to=sid)
            config = {"configurable": {"thread_id": f"{user_id}_generate"}}
            result = await app.graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": "Add relevant emojis naturally to the description, keep everything else unchanged."}],
                    "user_info": session["user_info"],
                },
                config=config,
            )

            msg = result["messages"][-1]
            json_response = json.loads(msg.content)

            await sio.emit("bot_message", json_response, to=sid)
            session["last_post"] = json_response

        await sio.save_session(sid, session)

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
                "title" : session["last_post"]["title"],
                "description": session["last_post"]["description"],
                "approximate_words": session.get('approximate_words'),
                "has_emojis": session.get('has_emojis',False),
                "required_words": session.get('required_words',[]),
                "forbidden_words": session.get('forbidden_words',[])
            }
            

            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {data.get('access_token')}"}
                response = await client.post(url, json=post_data, headers=headers)
                response.raise_for_status()

            await sio.emit(
                "ack", {"msg": "Post sent to backend for publishing"}, to=sid
            )

        except Exception as e:
            await sio.emit("error", {"msg": f"Publish failed: {str(e)}"}, to=sid)

    
    @sio.on("init_ask")
    async def init_ask(sid, data = {}):
        """
        data = {"thread_id": "user123+2025-09-12T16:00:00Z"}
        """
        try:
            

            session_data = {"thread_id": data.get("thread_id")}

            await sio.save_session(sid, session_data)
            
            await sio.emit("ack", {"msg": "User info received"}, to=sid)
           
        except Exception as e:
            await sio.emit("error", {"msg": f"Init failed: {str(e)}"}, to=sid)


    @sio.on("ask_request")
    async def handle_ask(sid, data = {}):
        """
        data = {"message":"what is the best time to post on instagram?"}
        """
        
        if not data.get("message"):
            await sio.emit("error", {"msg": "No message received"}, to=sid)
            return

        try:

            session = await sio.get_session(sid)
            await sio.emit("bot_typing", ".....", to=sid)


            config = {"configurable": {"thread_id": session.get("thread_id")}}
            result = await app.ask_graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": data.get("message")}],
                },
                config=config,
            )
            
            msg = result["messages"][-1]

            await sio.emit("bot_message", msg.content, to=sid)
            await sio.save_session(sid, session)

        except Exception as e:
            await sio.emit("error", {"msg": f"Generate failed: {str(e)}"}, to=sid)



    @sio.on("ask_voice")
    async def handle_ask_voice(sid, data = {}):
        """
        data = {"audio":"base64 string"}
        """

        try:
            if not data.get("audio"):
                await sio.emit("error", {"msg": "No audio received"}, to=sid)
                return

           
            audio_data = base64.b64decode(data["audio"])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            try:
                await sio.emit("status", {"msg": "Transcribing audio..."}, to=sid)
                with open(temp_audio_path, "rb") as f:
                    data = f.read()

                response = requests.post(voice_model, headers=voice_headers, data=data)

                os.unlink(temp_audio_path)

                await sio.emit("transcription", response.json(), to=sid)

            except Exception as e:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                await sio.emit("error", {"msg": f"Transcription failed: {str(e)}"}, to=sid)

        except Exception as e:
            await sio.emit("error", {"msg": f"Audio processing failed: {str(e)}"}, to=sid)

        try:

            session = await sio.get_session(sid)
            await sio.emit("bot_typing", ".....", to=sid)
            data['message'] = response.json().get('text','')
        
            config = {"configurable": {"thread_id": session.get("thread_id")}}
            result = await app.ask_graph.ainvoke(
                {
                    "messages": [{"role": "user", "content": data.get("message")}],
                },
                config=config,
            )

            msg = result["messages"][-1]

            await sio.emit("bot_message", msg.content, to=sid)
            await sio.save_session(sid, session)

        except Exception as e:
            await sio.emit("error", {"msg": f"Generate failed: {str(e)}"}, to=sid)

            
