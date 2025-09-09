from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from .prompts import post_prompt
from scheme.generate_scheme import PostOutput
from langchain_core.messages import AIMessage
from .llm import model
import json

tool_model = model.with_structured_output(PostOutput)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict 



async def chatbot(state: State):
    user_info = state["user_info"]  
    
    formatted_prompt = post_prompt.format_messages(
        main_goal = user_info["mainGoal"],   
        target_audience = user_info["targetAudience"],  
        tone_of_voice = user_info["toneOfVoice"],  
        main_topic = user_info["mainTopic"], 
        messages = state["messages"]
    )

    response: PostOutput = await tool_model.ainvoke(formatted_prompt)
    return {"messages": [AIMessage(content=json.dumps(response.dict()))]}


def get_graph(app):
    memory = app.memory_generate
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile(checkpointer=memory)




