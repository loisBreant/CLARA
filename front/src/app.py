import streamlit as st
import requests
import json
import pandas as pd
import time
import plotly.express as px # On utilise Plotly pour des graphs plus jolis

API_URL = "http://localhost:8000"

st.set_page_config(layout="wide", page_title="Onco-Agent AI")

st.title("🩺 Onco-Agent : Assistant Diagnostic")
st.markdown("Mode : **Asynchrone** & **Data Analyst**")

# --- UTILS ---
def fetch_metrics():
    try:
        r = requests.get(f"{API_URL}/metrics", timeout=0.5)
        if r.status_code == 200:
            d = r.json()
            return pd.DataFrame(d.get("logs", [])), d.get("total_cost_usd", 0), d.get("total_tokens", 0)
    except: pass
    return pd.DataFrame(), 0.0, 0

df_logs, total_cost_usd, total_tokens_count = fetch_metrics()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📊 Métriques")
    c1, c2 = st.columns(2)
    c1.metric("Coût", f"${total_cost_usd:.4f}")
    c2.metric("Tokens", f"{total_tokens_count:,}")
    if st.button("Refresh"): df_logs, total_cost_usd, total_tokens_count = fetch_metrics()
    
    st.divider()
    st.header("Patient Setup")
    scenarios = {
        "Standard": {"id": "P1", "age": 54, "surgical_history": []},
        "Mastectomie": {"id": "P2", "age": 62, "surgical_history": ["Mastectomie Totale"]}
    }
    sel = st.selectbox("Scénario", list(scenarios.keys()))
    patient_json_str = st.text_area("JSON", value=json.dumps(scenarios[sel], indent=2))

# --- TABS ---
tab_main, tab_data = st.tabs(["🖼️ Vision & Diagnostic", "📈 Data Analyst"])

# --- TAB 1 : IMAGE (Avec Polling) ---
with tab_main:
    col_l, col_r = st.columns([1, 1.2])
    uploaded_file = col_l.file_uploader("Mammographie", type=["jpg", "png"])
    if uploaded_file: col_l.image(uploaded_file, use_column_width=True)
    
    if uploaded_file and col_l.button("Lancer Analyse", type="primary"):
        with col_r:
            st.subheader("Processus Agentique")
            status_box = st.empty()
            prog_bar = st.progress(0)
            
            # 1. Start Task
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"patient_json": patient_json_str}
            res = requests.post(f"{API_URL}/analyze_async", files=files, data=data)
            
            if res.status_code == 200:
                task_id = res.json()["task_id"]
                completed = False
                while not completed:
                    time.sleep(1)
                    t_res = requests.get(f"{API_URL}/tasks/{task_id}")
                    if t_res.status_code == 200:
                        task = t_res.json()
                        status_box.info(f"⚡ {task.get('progress', 'Wait...')}")
                        
                        if task["status"] == "completed":
                            prog_bar.progress(100)
                            completed = True
                            r = task["result"]
                            
                            status_box.success("Terminé !")
                            if r["final_status"] == "VALIDATED":
                                st.success("✅ Validé par le Garde-Fou")
                            else:
                                st.error("🛑 Rejeté par le Garde-Fou")
                            
                            st.markdown(r["preliminary_report"])
                            with st.expander("Détails"):
                                st.write(r["critique"])
                                st.write(r["vision_output"])
                        elif task["status"] == "error":
                            status_box.error(task.get("error"))
                            completed = True

# --- TAB 2 : DATA ANALYST (Graphiques) ---
with tab_data:
    st.subheader("🤖 Interrogation de la Base Clinique")
    st.markdown("L'agent génère du SQL et choisit la meilleure visualisation.")
    
    q = st.text_input("Question", placeholder="Ex: Répartition des patients par facteur de risque ?")
    
    if st.button("Analyser"):
        if q:
            with st.spinner("Analyse en cours..."):
                resp = requests.post(f"{API_URL}/chat-db", json={"question": q})
                if resp.status_code == 200:
                    data = resp.json()
                    
                    if data.get("status") == "success":
                        # 1. Réponse Textuelle
                        st.markdown(f"### 💡 {data['answer']}")
                        
                        # 2. Données
                        raw_data = data.get("data", [])
                        df = pd.DataFrame(raw_data)
                        
                        # 3. Graphique Dynamique
                        chart_config = data.get("chart")
                        
                        if chart_config and not df.empty and chart_config.get("type"):
                            viz_type = chart_config["type"]
                            x_col = chart_config.get("x_axis")
                            y_col = chart_config.get("y_axis")
                            
                            st.divider()
                            st.subheader("📊 Visualisation")
                            
                            try:
                                if viz_type == "bar":
                                    fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} par {x_col}", color=x_col)
                                    st.plotly_chart(fig, use_container_width=True)
                                elif viz_type == "pie":
                                    fig = px.pie(df, names=x_col, values=y_col, title=f"Répartition par {x_col}")
                                    st.plotly_chart(fig, use_container_width=True)
                                elif viz_type == "line":
                                    fig = px.line(df, x=x_col, y=y_col, title="Évolution")
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.bar_chart(df) # Fallback
                            except Exception as e:
                                st.warning(f"Impossible de générer le graph demandé ({viz_type}): {e}")
                                st.dataframe(df)
                        
                        # 4. Tableau de données (Expander)
                        with st.expander("Voir Données Brutes & SQL"):
                            st.code(data.get("generated_sql"), language="sql")
                            st.dataframe(df)
                            
                    else:
                        st.error(f"Erreur : {data.get('error')}")
                else:
                    st.error("Erreur API")

# --- FOOTER LOGS ---
st.divider()
with st.expander("Logs Système"):
    st.dataframe(df_logs)