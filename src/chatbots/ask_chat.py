from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from .prompts import ask_prompt
from .llm import model, tavily_tool
import logging


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict


class AskGraph:

    def __init__(self, memory):

        self.memory = memory
        self.llm_with_tools = model.bind_tools([tavily_tool])
        self.logger = logging.getLogger(__name__)
        self.tool_node = ToolNode([tavily_tool])
        self.graph = self._ask_graph()


    async def chatbot(self, state: State):

        formatted_prompt = ask_prompt.format_messages(messages=state["messages"])
        response = await self.llm_with_tools.ainvoke(formatted_prompt)

        return {
            "messages": [response]
        }
    

    def should_continue(self, state: State):

        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "final"

    def _ask_graph(self):

        graph_builder = StateGraph(State)

        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("tools", self.tool_node)

        graph_builder.add_edge(START, "chatbot")

        graph_builder.add_conditional_edges(
            "chatbot",
            self.should_continue,
            {
                "tools": "tools",
                "final": END
            }
        )

        graph_builder.add_edge("tools", "chatbot")

        return graph_builder.compile(checkpointer=self.memory)
        