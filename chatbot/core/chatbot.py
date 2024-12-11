from typing import Annotated, Literal, Union
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph, START, END
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import plotly
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Literal
# Load Google API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print(GOOGLE_API_KEY)

# Import custom components
from chatbot.components.visualization.graph_plotter import chat2plot

class AgentState(MessagesState):
    # State for the current worker
    next: str

##### Defining all tools for agents
@tool
def plotter(
    df: Annotated[str, "The dataframe for which the graph should be plotted"],
    query: Annotated[str, "The user query for which the graph should be plotted"],
) -> Union[str, "plotly.graph_objs.Figure"]:
    """
    Plot the graph given a dataframe and user query.
    Returns a tuple of (output string, plotly figure object).
    """
    output_str = ""
    try:
        plotter_instance = chat2plot(df)
        result = plotter_instance(query, show_plot=False) 
        if result.config:
            output_str += "Chart Configuration:\n"
            output_str += str(result.config) + "\n\n"
        else:
            output_str += "No valid configuration returned.\n\n"

        if result.explanation:
            output_str += "Explanation from LLM:\n"
            output_str += result.explanation + "\n"

        # Check if a figure is generated
        if result.figure:
            return {
                "output": output_str.strip(),
                "figure": result.figure,
            }
        else:
            return {
                "output": output_str.strip() + "\nNo chart could be generated.",
                "figure": None,
            }

    except Exception as e:
        return {
            "output": f"An error occurred while plotting the graph: {str(e)}",
            "figure": None,
        }

## Classifier query tool
@tool
def classify_query(
    query: Annotated[str, "The user's query to be classified"]
) -> str:
    """
    Classify the user's query to determine the appropriate agent.
    Returns 'plotter' if visualization is needed, 'helper' for textual information.
    """
    visualization_keywords = [
        'show', 'plot', 'graph', 'chart', 'visualize', 'represent', 'diagram', 
        'trend', 'distribution', 'comparison', 'visual representation'
    ]
    
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in visualization_keywords):
        return "plotter"
    else:
        return "helper"

### Chatbot Tool
from chatbot.components.general_chatbot.chatbot import CoalMineChatbot
import json
@tool
def query_chatbot(
    user_query: Annotated[str, "The user's question about coal mining in India"]
) -> str:
    """ Use this to get information about the current shifts, datas related to the coal mines and 
    generalized information of the coal mines across india. And any data related to coal mines from the knowledge base 
    """
    try:
        chatbot = CoalMineChatbot(api_key=GOOGLE_API_KEY)
        response = chatbot.query(user_query)
        result = {
            "user_query": user_query,
            "chatbot_response": response
        }
        
        return json.dumps(result)
    
    except Exception as e:
        error_result = {
            "user_query": user_query,
            "error": f"An error occurred: {str(e)}"
        }
        return json.dumps(error_result)

    
members = ["helper", "plotter"]
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the user request, use the query"
    " classification tool to determine the appropriate worker. Each worker"
    " will perform a task and respond with their results and status."
)


class Router(BaseModel):
    """Router for selecting the next agent to process the request."""
    next: Literal["helper", "plotter", "FINISH"] = Field(
        description="The next agent to route to. Use 'FINISH' when the conversation is complete."
    )


llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=GOOGLE_API_KEY).bind_tools(classify_query, plotter, query_chatbot)
# llm = llm.bind_tools([classify_query])


def supervisor_node(state: AgentState) -> AgentState:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    
    classification_result = classify_query.invoke({"query": state["messages"][-1].content})
    next_ = classification_result
    
    if next_ == "FINISH":
        next_ = END

    return {"next": next_}


#Creating plotter agent for chatbot
plotter_agent = create_react_agent(
    llm, tools=[plotter]
)

def plotter_node(state: AgentState) -> AgentState:
    result = plotter_agent.invoke(state)
    return {
        "messages": [
            HumanMessage(content=result["messages"][-1].content, name="plotter")
        ]
    }

# Creating chatbot agent for chatbot
chatbot_agent = create_react_agent(
    llm, tools=[query_chatbot]
)


def chatbot_node(state: AgentState) -> AgentState:
    result = chatbot_agent.invoke(state)
    return {
        "messages": [
            HumanMessage(content=result["messages"][-1].content, name="helper")
        ]
    }
    
builder = StateGraph(AgentState)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("plotter", plotter_node)
builder.add_node("helper", chatbot_node)

for member in members:
    builder.add_edge(member, "supervisor")

builder.add_conditional_edges("supervisor", lambda state: state["next"])
builder.add_edge(START, "supervisor")

graph = builder.compile()


for s in graph.stream(
    {"messages": [("user", "How does the coal mining sector impact the environment?")]}, subgraphs=True
):
    print(s)
    print("----")