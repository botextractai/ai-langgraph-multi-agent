import os
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from typing import TypedDict, List

os.environ['OPENAI_API_KEY'] = "REPLACE_THIS_WITH_YOUR_OPENAI_API_KEY"
os.environ['TAVILY_API_KEY'] = "REPLACE_THIS_WITH_YOUR_TAVILY_API_KEY"

# Set the conversation memory type
memory = SqliteSaver.from_conn_string(":memory:")

# Data structure of the agent state information
class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int

model = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)

PLAN_PROMPT = """You are an expert writer tasked with writing a report. \
Write a report for the user provided topic. Give an outline of the report along with any relevant notes \
or instructions for the sections."""

WRITER_PROMPT = """You are a report assistant tasked with writing excellent reports.\
Generate the best report possible for the user's request and the initial outline. \
If the user provides critique, respond with a revised version of your previous attempts. \
Use all the information below as needed: 
------ 
{content}"""

REFLECTION_PROMPT = """You are a critic reviewing a report. \
Generate critique and recommendations for the user's submission. \
Provide detailed recommendations, including requests for length, depth, style, etc."""

RESEARCH_PLAN_PROMPT = """You are a researcher charged with providing information that can \
be used when writing the following report. Generate a list of search queries that will gather \
any relevant information. Only generate 3 queries max."""

RESEARCH_CRITIQUE_PROMPT = """You are a researcher charged with providing information that can \
be used when making any requested revisions (as outlined below). \
Generate a list of search queries that will gather any relevant information. Only generate 3 queries max."""

# Queries list for the Tavily search tool
class Queries(BaseModel):
    queries: List[str]

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def plan_node(state: AgentState):
    messages = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=state['task'])
    ]
    response = model.invoke(messages)
    return {"plan": response.content}

def research_plan_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=state['task'])
    ])
    content = state['content'] or []
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

def generation_node(state: AgentState):
    content = "\n\n".join(state['content'] or [])
    user_message = HumanMessage(
        content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
    messages = [
        SystemMessage(
            content=WRITER_PROMPT.format(content=content)
        ),
        user_message
        ]
    response = model.invoke(messages)
    return {
        "draft": response.content,
        "revision_number": state.get("revision_number", 1) + 1
    }

def reflection_node(state: AgentState):
    messages = [
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state['draft'])
    ]
    response = model.invoke(messages)
    return {"critique": response.content}

def research_critique_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
        HumanMessage(content=state['critique'])
    ])
    content = state['content'] or []
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

def should_continue(state):
    if state["revision_number"] > state["max_revisions"]:
        return END
    return "reflect"

# Initialise the graph with the agent state
builder = StateGraph(AgentState)

# Add all the nodes (agents)
builder.add_node("planner", plan_node)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)
builder.add_node("research_plan", research_plan_node)
builder.add_node("research_critique", research_critique_node)

# Set the starting agent
builder.set_entry_point("planner")

# Set the conditional edge
# This decides, whether to do another refinement loop, or to end
builder.add_conditional_edges(
    "generate", 
    should_continue, 
    {END: END, "reflect": "reflect"}
)

# Agent workflow ("generate" is already covered by the conditional edge)
builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")

builder.add_edge("reflect", "research_critique")
builder.add_edge("research_critique", "generate")

# Compile with the chosen memory type
graph = builder.compile(checkpointer=memory)

# Run it!
thread = {"configurable": {"thread_id": "1"}}
for s in graph.stream({
    'task': "Write a report about the latest inflation figures in the European Union.",
    "max_revisions": 2,
    "revision_number": 1
}, thread):
    print(s)
