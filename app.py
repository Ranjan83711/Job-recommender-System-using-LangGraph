# app.py
import json
import streamlit as st
from graph import build_graph
from tools import read_resume_text

st.set_page_config(page_title="GenAI Job Recommender", layout="wide")
st.title("GenAI Job Recommender (LangChain + LangGraph + OSS LLM)")

uploaded = st.file_uploader("Upload your resume (PDF/DOCX/TXT)", type=["pdf","docx","txt"])
model = st.selectbox("Model (Ollama)", ["llama3.1:8b","qwen2.5:7b-instruct"])

run = st.button("Analyze & Recommend")

if run and uploaded:
    # persist temp file
    tmp = f"./_tmp_{uploaded.name}"
    with open(tmp, "wb") as f: f.write(uploaded.getbuffer())

    g = build_graph()
    state = {"resume_path": tmp}
    result = g.invoke(state)  # runs the whole flow

    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("📑 Resume Summary")
        st.write(result.get("summary",""))

        st.subheader("🛠️ Skill Gaps & Missing Areas")
        gap = result.get("skill_gap", {})
        st.write("- **Gaps:**", ", ".join(gap.get("gaps",[])))
        st.write("- **Easy Wins (30 days):**", ", ".join(gap.get("easiest_wins",[])))


    with col2:
        st.subheader("💼 Personalized Job Recommendations")
        jobs = result.get("ranked_jobs", [])
        for j in jobs:
            st.markdown(f"**{j.get('title','')}** · {j.get('company','')} · {j.get('location','') or ''}")
            st.write((j.get("description","") or "")[:400] + "...")
            if j.get("link"):
                st.markdown(f"[Apply / View]({j['link']})")
            st.divider()

        st.subheader("Why these jobs?")
        st.write(result.get("final_brief",""))

    st.success("Done! Demo-ready. 🎉")
elif run and not uploaded:
    st.warning("Please upload a resume first.")
