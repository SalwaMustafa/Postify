from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from .prompts import post_prompt
from langgraph.prebuilt import ToolNode
from scheme.generate_scheme import PostOutput
from langchain_core.messages import AIMessage
from .llm import model, tavily_tool
from helpers.config import get_settings
import logging
import json

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict 


class PostGraph:

    def __init__(self, memory):
        self.memory = memory
        self.settings = get_settings()
        self.structured_model = model.with_structured_output(PostOutput)
        self.llm_with_tools = model.bind_tools([tavily_tool])
        self.logger = logging.getLogger(__name__)
        self.tool_node = ToolNode([tavily_tool])
        self.graph = self._get_graph()
        


    async def chatbot(self, state: State):
        user_info = state["user_info"]  
        
        formatted_prompt = post_prompt.format_messages(
            main_goal = user_info["mainGoal"],   
            target_audience = user_info["targetAudience"],  
            tone_of_voice = user_info["toneOfVoice"],  
            main_topic = user_info["mainTopic"], 
            messages = state["messages"]
        )

        response = await self.llm_with_tools.ainvoke(formatted_prompt)
        return {"messages": [response]}


    async def final_formatter(self, state: State):
        last_ai_message = next((msg for msg in reversed(state["messages"]) if isinstance(msg, AIMessage)), None)
        content = last_ai_message.content

        if isinstance(content, list):

            text_content = "\n".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict)
                and block.get("type") == "text"
            )

        else:
            text_content = content

        response = await self.structured_model.ainvoke(text_content)

        return {
            "messages": [
                AIMessage(content=json.dumps(response.model_dump(), ensure_ascii=False))
            ]
        }

    def should_continue(self, state: State):

        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "final"


    def _get_graph(self):

        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("tools", self.tool_node)
        graph_builder.add_node("final", self.final_formatter)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges(
            "chatbot",
            self.should_continue,
            {
                "tools": "tools",
                "final": "final"
            }
        )
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge("final", END)

        return graph_builder.compile(checkpointer = self.memory)

