
# 🧠 **Project Title:**

## **AI-Powered Job Recommender System using LangChain, LangGraph, and Groq**

---

## 🏁 **1. Project Overview**

The **GenAI Job Recommender System** is an AI-driven platform that automatically analyzes a candidate’s resume and provides **personalized job recommendations**, **skill gap analysis**, and a **90-day learning roadmap** using **LLMs (Large Language Models)** and real-time job APIs.

The project integrates **LangChain**, **LangGraph**, **Groq API**, and **Hugging Face embeddings** to create an intelligent pipeline that mimics how a career advisor would analyze a candidate’s profile and suggest relevant opportunities.

---

## 🎯 **2. Objectives**

* To build an **end-to-end automated AI system** that reads resumes and understands user profiles.
* To generate **personalized job recommendations** from real job sources.
* To analyze **skill gaps** and suggest areas of improvement.
* To provide a **structured 90-day learning roadmap** to enhance employability.
* To display all results through an **interactive Streamlit UI**.

---

## ⚙️ **3. System Architecture**

### 🧩 Components:

| Layer                | Description                                  | Technology                 |
| -------------------- | -------------------------------------------- | -------------------------- |
| **Frontend**         | Resume upload and output visualization       | Streamlit                  |
| **Orchestration**    | Workflow coordination and state management   | LangGraph                  |
| **Reasoning Engine** | Text understanding, analysis, and generation | Groq API (LLaMA-3.1)       |
| **Embeddings**       | Similarity ranking between jobs and profile  | Hugging Face API           |
| **Data Source**      | Fetch real-time job data                     | JSearch API (via RapidAPI) |
| **Backend**          | Resume parsing, processing, ranking          | Python                     |
| **Storage**          | Temporary resume file and state memory       | Local (in runtime)         |

---

## 🔄 **4. Complete Workflow / Pipelines**

Here’s how the system flows from start to finish 👇

---

### **Step 1: Resume Upload (Input Layer)**

* **User Action:** Uploads a PDF/DOCX/TXT resume via the Streamlit interface.
* **Process:** File is temporarily saved in the backend.
* **Purpose:** Input document for analysis.

📦 **Output:** `resume_path`

---

### **Step 2: Resume Parsing & Summarization**

* **Node:** `node_parse_resume` + `node_summary`

* **Tools Used:**

  * `PdfReader` / `python-docx` for text extraction
  * **Groq API (LLaMA-3)** for summarization

* **Functions:**

  * Extracts raw text from resume.
  * Generates:

    * Short professional summary
    * List of normalized skills
    * Key achievements/projects

📦 **Output:**

```json
{
  "summary": "Data Analyst with strong Python and ML foundation.",
  "skills": ["Python", "SQL", "Pandas", "Tableau"]
}
```

---

### **Step 3: Profile Extraction**

* **Node:** `node_profile`
* **Tool:** Groq LLM
* **Purpose:** Convert unstructured resume into structured JSON data.
* **Output Fields:**

  * Name
  * Skills
  * Experience
  * Education
  * Target roles
  * Locations

📦 **Output:**

```json
{
  "name": "Ranjan Kumar Yadav",
  "skills": ["Python", "SQL", "Machine Learning", "AWS"],
  "target_roles": ["Data Analyst", "ML Engineer"]
}
```

---

### **Step 4: Job Search (Real-Time Data)**

* **Node:** `node_search`
* **Tool:** `JSearch API` (RapidAPI)
* **Query:** Uses candidate’s **skills + target roles**
* **Output:** Raw job list (title, company, location, description, link)

📦 **Output:**

```json
[
  {"title": "Data Analyst", "company": "Accenture", "location": "Bengaluru", "link": "..."},
  {"title": "ML Engineer", "company": "Google", "location": "Hyderabad", "link": "..."}
]
```

---

### **Step 5: Job Ranking (Matching Pipeline)**

* **Node:** `node_rank`

* **Tools:**

  * Hugging Face embeddings: `all-MiniLM-L6-v2`
  * NumPy for cosine similarity

* **Working:**

  1. Converts candidate profile & job descriptions to vectors.
  2. Calculates similarity between them.
  3. Sorts and returns top 10–12 relevant jobs.

📦 **Output:**
Top jobs ranked by semantic similarity.

---

### **Step 6: Skill Gap Analysis**

* **Node:** `node_gaps`
* **Tool:** Groq LLM
* **Process:**

  * Compares the candidate’s skills vs job requirements.
  * Identifies missing or weak skills.
  * Suggests “quick wins” (skills learnable in <30 days).

📦 **Output:**

```json
{
  "gaps": ["Power BI", "Docker"],
  "easiest_wins": ["Tableau dashboard creation"]
}
```

---

### **Step 7: 90-Day Career Roadmap**

* **Node:** `node_roadmap`
* **Tool:** Groq LLM
* **Purpose:** Generates a learning roadmap to fill skill gaps and build a portfolio.

📦 **Output Example:**

> **Weeks 1–4:** Strengthen SQL & Data Visualization
> **Weeks 5–8:** Build an ML project on Kaggle
> **Weeks 9–12:** Deploy Streamlit app on cloud

---

### **Step 8: Job Recommendation Explanation**

* **Node:** `node_brief`
* **Tool:** Groq LLM
* **Purpose:** Generates human-style explanation for job matches.
* **Input:** Profile + top-ranked jobs
* **Output:** Concise paragraph summarizing “Why these jobs?”

📦 **Example:**

> Based on Ranjan’s experience with Python, SQL, and cloud tools, Data Analyst and ML roles are an excellent fit. The jobs emphasize analytics and cloud-based dashboards — matching his strengths and learning goals.

---

### **Step 9: Streamlit Visualization (Frontend)**

* Left Panel:

  * Resume Summary
  * Skill Gaps
  * Roadmap
* Right Panel:

  * Job Cards (title, company, link)
  * “Why These Jobs” analysis

📦 **Final Output (UI):**

| Section                | Description                        |
| ---------------------- | ---------------------------------- |
| 📄 Resume Summary      | AI-generated overview of candidate |
| 🛠️ Skill Gaps         | Weak or missing skills             |
| 💼 Job Recommendations | Top matching jobs with apply links |
| 🤖 Why These Jobs      | AI explanation of match            |

---

## 🧮 **5. LangGraph Workflow**

LangGraph manages all pipeline steps as connected nodes:

```
parse_resume → summary → profile → search_jobs 
→ rank_jobs → skill_gaps → roadmap → brief → END
```

Each node:

* Takes `state` (input dictionary)
* Returns updates
* Passes merged state to next node

✅ Handles:

* Step-by-step logic
* State persistence
* Smooth chaining
* Automatic flow control

---

## 🧱 **6. Data Flow Summary**

| Stage              | Input               | Output            |
| ------------------ | ------------------- | ----------------- |
| Upload             | Resume file         | File path         |
| Parse & Summarize  | Text                | Summary text      |
| Profile Extraction | Summary text        | Structured JSON   |
| Job Search         | JSON (skills/roles) | Job list          |
| Job Ranking        | Job list + Profile  | Top jobs          |
| Skill Gap          | Profile + Job descs | Missing skills    |
| Roadmap            | Profile + Gaps      | Learning plan     |
| Summary            | Profile + Jobs      | Human explanation |

---

## ⚡ **7. Tech Stack Summary**

| Layer                | Technology                         |
| -------------------- | ---------------------------------- |
| **Frontend**         | Streamlit                          |
| **Backend Language** | Python                             |
| **Orchestration**    | LangGraph                          |
| **LLM Model**        | Groq API (LLaMA 3.1 8B)            |
| **Embeddings**       | Hugging Face API                   |
| **Job Data API**     | JSearch (RapidAPI)                 |
| **Libraries**        | LangChain, NumPy, dotenv, requests |
| **Visualization**    | Streamlit                          |
| **IDE**              | VS Code / Anaconda                 |

---

## 📈 **8. Advantages**

✅ Real-time job recommendations
✅ AI-driven insights
✅ Scalable and modular architecture
✅ Works with open-source and API models
✅ Interactive and user-friendly interface

---

## 🧩 **9. Future Enhancements**

* Add **LinkedIn/Naukri integration** for more job sources
* Introduce **resume tailoring** for specific job applications
* Add **email/LinkedIn outreach message generator**
* Support **multi-language resumes**
* Integrate **vector database (FAISS)** for caching and historical learning

---

## 🧠 **10. Conclusion**

This project demonstrates how **Generative AI + LangGraph + APIs** can automate career counseling and job recommendations.
It combines **NLP, embeddings, and cloud APIs** to deliver personalized, data-driven insights.

> “The AI acts like a personal career assistant — reading your resume, finding the best jobs, showing what to learn, and guiding your next 90 days.”

---


