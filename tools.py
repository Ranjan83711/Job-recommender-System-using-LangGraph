# tools.py
import os, json, re, requests
import numpy as np
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from pypdf import PdfReader
from docx import Document
from rapidfuzz import fuzz, process
import numpy as np

from prompts import (
    RESUME_SUMMARY_PROMPT, PROFILE_EXTRACTION_PROMPT,
    SKILL_GAP_PROMPT, ROADMAP_PROMPT, RECOMMENDER_SUMMARY_PROMPT
)

# --- LLM (Groq) ---
def get_llm(model="llama-3.1-8b-instant", temperature=0.2):
    return ChatGroq(model=model, temperature=temperature, api_key=os.getenv("GROQ_API_KEY"))

# --- Resume reading ---
def read_resume_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        r = PdfReader(path)
        return "\n".join([p.extract_text() or "" for p in r.pages])
    elif path.lower().endswith(".docx"):
        d = Document(path)
        return "\n".join([p.text for p in d.paragraphs])
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

# --- Hugging Face Embeddings (API-based) ---
import numpy as np
import requests
import os


def hf_embed(texts):
    """
    Returns a 2D numpy array [n_texts, dim] from Hugging Face API.
    Handles scalar, nested, dict-based, or error responses safely.
    """
    hf_key = os.getenv("HF_API_KEY")
    model = "sentence-transformers/all-MiniLM-L6-v2"
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
    headers = {"Authorization": f"Bearer {hf_key}"}

    if isinstance(texts, str):
        texts = [texts]

    try:
        resp = requests.post(
            url,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}},
            timeout=60
        )
        data = resp.json()
    except Exception as e:
        print("HF API error:", e)
        return np.zeros((len(texts), 384))

    # --- Handle different possible response formats ---
    # 1️⃣ If it's a dict (error or structured output)
    if isinstance(data, dict):
        if "error" in data:
            print("HF API error message:", data["error"])
        return np.zeros((len(texts), 384))

    # 2️⃣ If it's a list of lists of lists (token embeddings)
    if isinstance(data, list) and isinstance(data[0], list):
        # check if first element is numeric or another list
        if isinstance(data[0][0], (float, int)):
            # Sentence-level embedding
            arr = np.array(data, dtype=float)
        else:
            # Token-level embedding — average tokens
            arr = np.mean(np.array(data, dtype=float), axis=1)
        return arr

    # 3️⃣ If it's a list of dicts (some HF models return [{"embedding": [...]}])
    if isinstance(data, list) and isinstance(data[0], dict):
        try:
            emb_list = [list(d.values())[0] for d in data]
            arr = np.array(emb_list, dtype=float)
            return arr
        except Exception:
            return np.zeros((len(texts), 384))

    # 4️⃣ Fallback: single vector
    try:
        arr = np.array(data, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        elif arr.ndim == 3:
            arr = np.mean(arr, axis=1)
        return arr
    except Exception as e:
        print("Unexpected HF response:", type(data), e)
        return np.zeros((len(texts), 384))



# --- Cosine similarity ---
def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

# --- LLM helpers ---
def llm_json(llm, prompt: str, **fmt):
    tmpl = PromptTemplate.from_template(prompt)
    msg = tmpl.format(**fmt)
    resp = llm([HumanMessage(content=msg)]).content.strip()
    m = re.search(r"\{.*\}|\[.*\]", resp, re.S)
    text = m.group(0) if m else resp
    return json.loads(text)

def llm_text(llm, prompt: str, **fmt):
    tmpl = PromptTemplate.from_template(prompt)
    return llm([HumanMessage(content=tmpl.format(**fmt))]).content.strip()

# --- Job search via JSearch ---
def search_jobs(query: str, location="India", limit=30) -> List[Dict[str, Any]]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("JSEARCH_HOST", "jsearch.p.rapidapi.com")
    url = f"https://{host}/search"
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
    params = {"query": query, "page": "1", "num_pages": "1"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
        return [{
            "title": j.get("job_title"),
            "company": j.get("employer_name"),
            "location": j.get("job_city") or j.get("job_country"),
            "description": j.get("job_description"),
            "link": j.get("job_apply_link") or j.get("job_google_link"),
        } for j in data[:limit]]
    except Exception as e:
        print("JSearch failed:", e)
        return []

# --- Job ranking ---
def score_jobs(profile: Dict[str, Any], jobs: List[Dict[str, Any]], top_k=10):
    skills = ", ".join(profile.get("skills", []))
    roles = ", ".join(profile.get("target_roles", []) or profile.get("primary_roles", []))
    query_text = f"{roles}. Skills: {skills}."

    q_emb = hf_embed(query_text)
    q_emb = q_emb[0] if q_emb.ndim > 1 else q_emb  # ✅ safe extract

    scored = []
    for j in jobs:
        desc = f"{j.get('title','')} {j.get('company','')} {j.get('description','')}"
        j_emb = hf_embed(desc[:3000])
        j_emb = j_emb[0] if j_emb.ndim > 1 else j_emb  # ✅ safe extract

        sim = cosine(q_emb, j_emb)
        boost = 0
        if roles:
            score, match, _ = process.extractOne(
                j.get("title", ""), [roles], scorer=fuzz.WRatio
            ) or (0, None, None)
            boost = (score / 100.0) * 0.1
        scored.append((sim + boost, j))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [j for _, j in scored[:top_k]]


# --- Steps ---
def make_resume_summary(llm, resume_text): return llm_text(llm, RESUME_SUMMARY_PROMPT, resume_text=resume_text)
def extract_profile(llm, resume_text): return llm_json(llm, PROFILE_EXTRACTION_PROMPT, resume_text=resume_text)
def compute_skill_gaps(llm, candidate_skills, target_role_requirements):
    return llm_json(llm, SKILL_GAP_PROMPT, candidate_skills=candidate_skills, target_role_requirements=target_role_requirements)
def generate_roadmap(llm, profile_json, target_roles):
    return llm_text(llm, ROADMAP_PROMPT, profile_json=json.dumps(profile_json), target_roles=", ".join(target_roles))
def summarize_recommendations(llm, profile_json, jobs):
    return llm_text(llm, RECOMMENDER_SUMMARY_PROMPT, profile_json=json.dumps(profile_json), jobs_json=json.dumps(jobs[:8]))
