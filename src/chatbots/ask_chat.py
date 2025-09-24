from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from .prompts import ask_prompt
from langchain_core.messages import AIMessage, HumanMessage
from .llm import model
import json


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict 


async def chatbot(state: State):  

    formatted_prompt = ask_prompt.format_messages(
        messages=state["messages"]
    )

    response = await model.ainvoke(formatted_prompt)
    return {"messages": [AIMessage(content=response.content)]}



def get_ask_graph(app):
    memory = app.memory_ask
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile(checkpointer=memory)



