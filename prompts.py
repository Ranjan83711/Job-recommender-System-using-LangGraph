# prompts.py

# =============================
# 📄 Resume Summary Prompt
# =============================
RESUME_SUMMARY_PROMPT = """
You are a meticulous career analyst. Given the extracted resume text below, produce:
1. A crisp professional summary (3–5 sentences).
2. Key skills (bulleted, normalized).
3. Top projects or achievements (bulleted, highlight measurable impact).

Resume Text:
{resume_text}
"""

# =============================
# 🧠 Profile Extraction Prompt
# =============================
PROFILE_EXTRACTION_PROMPT = """
Extract a structured JSON with the following fields:
- name (string or null)
- years_experience (float, approximate)
- primary_roles (list[str])
- skills (list[str], normalized to standard technical terms)
- education (list[str])
- locations (list[str], cities or countries)
- target_roles (list[str])  # infer from resume; if not mentioned, suggest relevant roles

Resume Text:
{resume_text}

Return ONLY valid JSON.
"""

# =============================
# ⚙️ Skill Gap Analysis Prompt
# =============================
SKILL_GAP_PROMPT = """
You are a career coach. Compare the candidate’s current skills:
{candidate_skills}

against the skill requirements from target roles:
{target_role_requirements}

Return ONLY valid JSON with:
- "gaps": list of missing or weak skills
- "easiest_wins": list of quick upskilling areas (achievable within 30 days)

❌ Do NOT include resources, links, platform names (like Udemy, Coursera, etc.).
Keep it concise and skill-focused.
"""

# =============================
# 🚀 90-Day Roadmap Prompt
# =============================
ROADMAP_PROMPT = """
You are a career mentor. Create a pragmatic 90-day roadmap to help the candidate
become highly hireable for roles: {target_roles}.

Candidate background:
{profile_json}

Structure it by weeks (Week 1–4, 5–8, 9–12) with:
- Learning goals
- Hands-on projects
- Portfolio ideas (GitHub, Medium, etc.)
- Outcome expected by end of 90 days

Keep it concise, clear, and motivational — no external links.
"""

# =============================
# 💼 Job Recommendation Summary Prompt
# =============================
# =============================
# 💼 Job Recommendation Summary Prompt (Fixed)
# =============================
RECOMMENDER_SUMMARY_PROMPT = """
You are a professional career analyst. Analyze the candidate's profile and the top-ranked job listings below.

Your goals:
1. Write a concise 1–2 paragraph explanation describing what types of roles are the best fit for this candidate and why.
2. Explain how the candidate’s strengths align with these roles.
3. Identify any visible trend across the recommended roles (industries, skill patterns, or tools in demand).
4. Keep your tone professional, friendly, and clear.

IMPORTANT:
- Do NOT invent or create fake jobs.
- Do NOT remove or modify any job fields like title, company, location, or link.
- The job list already contains real data (with links); you are only providing the textual explanation **after** the job list is shown in the app.
- Do NOT reformat the job list, just use it as context for your reasoning.

Candidate Profile (JSON):
{profile_json}

Top Jobs (JSON data you can reference, do not rewrite or omit any fields):
{jobs_json}
"""
