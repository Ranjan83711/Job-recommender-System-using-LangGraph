# graph.py
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from tools import (
    get_llm, read_resume_text, make_resume_summary, extract_profile,
    search_jobs, score_jobs, compute_skill_gaps, generate_roadmap, summarize_recommendations
)

class State(TypedDict, total=False):
    resume_path: str
    resume_text: str
    summary: str
    profile: Dict[str, Any]
    target_roles: List[str]
    raw_jobs: List[Dict[str, Any]]
    ranked_jobs: List[Dict[str, Any]]
    skill_gap: Dict[str, Any]
    roadmap: str
    final_brief: str

llm = get_llm()

def node_parse_resume(state: State):
    text = read_resume_text(state["resume_path"])
    return {"resume_text": text}

def node_summary(state: State):
    return {"summary": make_resume_summary(llm, state["resume_text"])}

def node_profile(state: State):
    prof = extract_profile(llm, state["resume_text"])
    # choose target roles: from resume or sensible defaults
    targets = prof.get("target_roles") or prof.get("primary_roles") or ["Data Analyst","Business Analyst"]
    return {"profile": prof, "target_roles": targets}

def node_search(state: State):
    query = f"{', '.join(state['target_roles'])} {', '.join(state['profile'].get('skills', [])[:8])}"
    jobs = search_jobs(query=query, location="India", limit=40)
    return {"raw_jobs": jobs}

def node_rank(state: State):
    ranked = score_jobs(state["profile"], state["raw_jobs"], top_k=12)
    return {"ranked_jobs": ranked}


def node_gaps(state: State):
    # crude role requirements string: use titles+descs of top jobs
    requirements = [ (j.get("title","") + " - " + (j.get("description","") or ""))[:2000] for j in state["ranked_jobs"][:5] ]
    gap = compute_skill_gaps(llm, state["profile"].get("skills", []), requirements)
    return {"skill_gap": gap}

def node_roadmap(state: State):
    return {"roadmap": generate_roadmap(llm, state["profile"], state["target_roles"])}

def node_brief(state: State):
    return {"final_brief": summarize_recommendations(llm, state["profile"], state["ranked_jobs"])}

def build_graph():
    g = StateGraph(State)
    g.add_node("parse_resume", node_parse_resume)
    g.add_node("summary", node_summary)
    g.add_node("profile", node_profile)
    g.add_node("search_jobs", node_search)
    g.add_node("rank_jobs", node_rank)
    g.add_node("skill_gaps", node_gaps)
    g.add_node("roadmap", node_roadmap)
    g.add_node("brief", node_brief)

    g.set_entry_point("parse_resume")
    g.add_edge("parse_resume","summary")
    g.add_edge("summary","profile")
    g.add_edge("profile","search_jobs")
    g.add_edge("search_jobs","rank_jobs")
    g.add_edge("rank_jobs","skill_gaps")
    g.add_edge("skill_gaps","roadmap")
    g.add_edge("roadmap","brief")
    g.add_edge("brief", END)
    return g.compile()
