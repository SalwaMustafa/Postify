from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from .prompts import post_prompt
from scheme.generate_scheme import PostOutput
from .llm import model


tool_model = model.bind_tools([PostOutput])

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict 



async def chatbot(state: State):
    user_info = state["user_info"]  
    
    formatted_prompt = post_prompt.format_messages(
        level_of_complexity = user_info["level_of_complexity"],   
        target_audience = user_info["target_audience"],  
        tone_of_voice = user_info["tone_of_voice"],  
        messages = state["messages"]
    )

    response = await tool_model.ainvoke(formatted_prompt)
    return {"messages": [response]}


def get_graph(app):
    memory = app.memory_generate
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile(checkpointer=memory)




