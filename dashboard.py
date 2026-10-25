"""Epic 6: Streamlit investigator dashboard."""
import os
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="CrimeVision AI", page_icon="🕵️", layout="wide")
st.title("🕵️ CrimeVision AI")
st.caption("Intelligent Multimodal Forensic Analysis")

with st.sidebar:
    st.header("Cases")
    with st.form("new"):
        t = st.text_input("Title")
        d = st.text_area("Description")
        if st.form_submit_button("Create case") and t:
            requests.post(f"{API}/cases", json={"title": t, "description": d})
            st.rerun()
    cases = requests.get(f"{API}/cases").json()
    choice = st.radio("Select", cases, format_func=lambda c: f"#{c['id']} {c['title']}") if cases else None

if not choice:
    st.info("Create or select a case to begin.")
    st.stop()

cid = choice["id"]
case = requests.get(f"{API}/cases/{cid}").json()
tab1, tab2, tab3, tab4 = st.tabs(["Evidence", "Timeline", "AI Chat", "Report"])

with tab1:
    files = st.file_uploader("Upload images, video or audio", accept_multiple_files=True,
                             type=["jpg", "jpeg", "png", "webp", "mp4", "avi", "mov", "mkv",
                                   "mp3", "wav", "m4a", "ogg", "flac"])
    if files and st.button("Upload"):
        for f in files:
            requests.post(f"{API}/cases/{cid}/evidence", files={"file": (f.name, f.getvalue())})
        st.rerun()
    for e in case["evidence"]:
        with st.expander(f"[{e['kind']}] {e['filename']}"):
            st.json(e["analysis"] or {"status": "not analyzed yet"})
    if st.button("Run analysis", type="primary"):
        with st.spinner("Analyzing evidence and fusing results..."):
            r = requests.post(f"{API}/cases/{cid}/analyze")
        st.success("Done") if r.ok else st.error(r.text)
        st.rerun()

with tab2:
    fused = case.get("fused")
    if not fused:
        st.info("Run analysis to generate the timeline.")
    else:
        st.subheader("Summary")
        st.write(fused.get("summary"))
        st.subheader("Chronological timeline")
        st.dataframe(fused.get("timeline", []), use_container_width=True)
        for k in ["persons_of_interest", "weapons_and_objects", "inconsistencies", "recommended_follow_up"]:
            if fused.get(k):
                st.subheader(k.replace("_", " ").title())
                st.write(fused[k])

with tab3:
    for m in requests.get(f"{API}/cases/{cid}/chat").json():
        st.chat_message("user" if m["role"] == "user" else "assistant").write(m["content"])
    q = st.chat_input("Ask about the evidence...")
    if q:
        r = requests.post(f"{API}/cases/{cid}/chat", json={"question": q})
        st.chat_message("user").write(q)
        st.chat_message("assistant").write(r.json().get("answer") if r.ok else r.text)

with tab4:
    if st.button("Generate PDF report"):
        r = requests.get(f"{API}/cases/{cid}/report")
        if r.ok:
            st.download_button("Download PDF", r.content, file_name=f"case_{cid}_report.pdf",
                               mime="application/pdf")
        else:
            st.error(r.text)
