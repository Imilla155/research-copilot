import streamlit as st
import os
import json
import re
import numpy as np
import pandas as pd
from openai import OpenAI

# Config
st.set_page_config(page_title="Research Copilot", page_icon="📚", layout="wide")

# Get API key from Streamlit secrets
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Missing OPENAI_API_KEY in secrets.")
    st.stop()
    
OPENAI_CLIENT = OpenAI(api_key=API_KEY)

CATALOG_PATH = "data/paper_catalog.json"
NPY_PATH = "data/vector_db.npy"
META_PATH = "data/vector_meta.json"

@st.cache_data
def load_data():
    papers = []
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            papers = data.get("papers", [])
            
    vector_db = np.array([])
    vector_meta = []
    if os.path.exists(NPY_PATH) and os.path.exists(META_PATH):
        vector_db = np.load(NPY_PATH)
        with open(META_PATH, 'r', encoding='utf-8') as f:
            vector_meta = json.load(f)
            
    return papers, vector_db, vector_meta

papers, vector_db, vector_meta = load_data()

def extract_page(text: str) -> str:
    match = re.search(r"\[PAGE (\d+)\]", text)
    if match:
        return match.group(1)
    return "N/A"

st.sidebar.title("📚 Research Copilot")

# Global Year Filter
df_papers = pd.DataFrame(papers)
min_y = int(df_papers['year'].min()) if not df_papers.empty else 2000
max_y = int(df_papers['year'].max()) if not df_papers.empty else 2026
años_rango = st.sidebar.slider("Selecciona el periodo (Desde - Hasta):", min_value=min_y, max_value=max_y, value=(min_y, max_y))

# Filter papers dataframe globally
if not df_papers.empty:
    df_filtrado = df_papers[(df_papers['year'] >= años_rango[0]) & (df_papers['year'] <= años_rango[1])]
    papers = df_filtrado.to_dict('records')

app_mode = st.sidebar.radio("Navigate", ["Chat Interface", "Paper Browser", "Dashboard"])

if app_mode == "Chat Interface":
    st.title("💬 Chat Interface")
    
    # Filters
    st.subheader("Filters")
    
    all_topics_dict = {}
    for p in papers:
        for t in p.get("topics", []):
            all_topics_dict[t] = all_topics_dict.get(t, 0) + 1
    all_topics = sorted([t for t, c in all_topics_dict.items()])
    
    selected_topics = st.multiselect("Filter by Topic", options=all_topics)
        
    st.markdown("---")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                 with st.expander("View Context Used"):
                     for src in msg["sources"]:
                         st.markdown(f"- {src}")

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("Clear Chat", type="primary"):
            st.session_state.messages.clear()
            st.rerun()

    if prompt := st.chat_input("Ask about the papers (e.g., 'What is the impact of climate change on farmers?'):"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            contexts = []
            
            if len(vector_db) > 0:
                query_res = OPENAI_CLIENT.embeddings.create(
                    input=[prompt],
                    model="text-embedding-3-small"
                )
                q_emb = np.array(query_res.data[0].embedding, dtype=np.float32)
                
                similarities = np.dot(vector_db, q_emb)
                top_indices = np.argsort(similarities)[::-1][:20]
                
                filtered_docs = []
                for idx in top_indices:
                    meta = vector_meta[idx]
                    
                    doc_year = meta.get("year")
                    if doc_year and not (años_rango[0] <= int(doc_year) <= años_rango[1]):
                        continue
                    
                    if selected_topics and len(selected_topics) > 0:
                        doc_text = meta.get("text", "").lower()
                        if not any(t.lower() in doc_text for t in selected_topics):
                            continue
                            
                    filtered_docs.append(meta)
                    if len(filtered_docs) == 5:
                        break
                        
                for meta in filtered_docs:
                    page = extract_page(meta.get("text", ""))
                    src = meta.get("source", "Unknown Source")
                    authors = meta.get("authors", "Unknown Authors")
                    year = meta.get("year", "N/A")
                    text = meta.get("text", "")
                    contexts.append(f"Document: {src}\nAuthors: {authors}\nYear: {year}\nPage: {page}\nContent: {text}")

            system_prompt = (
                "You are 'Research Copilot', a professional Academic Paper Assistant. "
                "Use the provided context to answer the user's question accurately. "
                "If the answer is not in the context, say you don't know based on the provided papers.\n\n"
                "Critically Important Protocol:\n"
                "Every time you use information from the context, you MUST include a formal APA citation directly in your response text, "
                "and mention the exact page number (e.g., (Avelino, 2024, p. 1)). You must highlight the relevant citation source at the end.\n\n"
                "Context:\n" + "\n\n---\n\n".join(contexts)
            )

            openai_msgs = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                openai_msgs.append({"role": m["role"], "content": m["content"]})
                
            with st.spinner("Thinking..."):
                completion = OPENAI_CLIENT.chat.completions.create(
                    model="gpt-4o",
                    messages=openai_msgs,
                    temperature=0.0,
                )
            
            response = completion.choices[0].message.content
            
            formatted_sources = []
            for c in contexts:
                doc_match = re.search(r"Document:\s*(.+)", c)
                page_match = re.search(r"Page:\s*(\w+)", c)
                doc_name = doc_match.group(1).replace('.pdf', '') if doc_match else 'Unknown'
                page_num = page_match.group(1) if page_match else 'N/A'
                formatted_sources.append(f"{doc_name} (Page {page_num})")
            
            st.markdown(response)
            if contexts:
                 with st.expander("View Context Used"):
                     for src in formatted_sources:
                         st.markdown(f"- {src}")
            
            st.session_state.messages.append({"role": "assistant", "content": response, "sources": formatted_sources})

elif app_mode == "Paper Browser":
    st.title("📚 Paper Browser")
    search_query = st.text_input("Search by title or author...", "")
    
    filtered_papers = papers
    if search_query:
        sq = search_query.lower()
        filtered_papers = [
            p for p in papers 
            if sq in p.get("title", "").lower() or any(sq in a.lower() for a in p.get("authors", []))
        ]
        
    for p in filtered_papers:
        with st.container():
            st.markdown(f"### {p.get('title')}")
            authors_str = ", ".join(p.get('authors', []))
            st.markdown(f"**Authors:** {authors_str} | **Year:** {p.get('year')}")
            st.markdown(f"**Topics:** {', '.join(p.get('topics', []))}")
            st.info(p.get("abstract", ""))
            st.markdown("---")

elif app_mode == "Dashboard":
    st.title("📊 Visualization Dashboard")
    
    years_count = {}
    topics_count = {}
    for p in papers:
        y = p.get("year")
        if y:
            years_count[y] = years_count.get(y, 0) + 1
        for t in p.get("topics", []):
            topics_count[t] = topics_count.get(t, 0) + 1
            
    st.subheader("Papers by Year")
    df_years = pd.DataFrame(list(years_count.items()), columns=["Year", "Count"])
    if not df_years.empty:
      df_years = df_years.sort_values(by="Year")
      df_years["Year"] = df_years["Year"].astype(str)
      st.bar_chart(df_years.set_index("Year"))
    
    st.subheader("Top 10 Topics")
    df_topics = pd.DataFrame(list(topics_count.items()), columns=["Topic", "Count"])
    if not df_topics.empty:
      df_topics = df_topics.sort_values(by="Count", ascending=False).head(10)
      
      import altair as alt
      pie = alt.Chart(df_topics).mark_arc().encode(
          theta=alt.Theta(field="Count", type="quantitative"),
          color=alt.Color(field="Topic", type="nominal"),
          tooltip=["Topic", "Count"]
      ).properties(width=500, height=400)
      st.altair_chart(pie, use_container_width=True)
