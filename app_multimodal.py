import streamlit as st
import os
from PIL import Image
from rag_multimodal import ask_text, ask_image

st.set_page_config(
    page_title="TN License & Traffic Assistant",
    page_icon="🚗",
    layout="wide"
)

# Header
st.title("🚗 TN License & Traffic Assistant")
st.caption("AI-powered assistant for Tamil Nadu driving license and traffic rules")
st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs([
    "💬 License & Traffic Q&A",
    "🚦 Traffic Sign Identifier",
    "🏛️ RTO Offices"
])

# ── Tab 1 — Chat ───────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Suggested questions
    if len(st.session_state.messages) == 0:
        st.markdown("#### 💡 Try asking:")
        suggestions = [
            "How to apply for learner license?",
            "What is the fine for jumping red light?",
            "What documents are needed for driving license?",
            "How to renew my driving license?",
            "What is the speed limit in city roads?",
            "What is the fine for drunk driving?"
        ]
        cols = st.columns(3)
        for i, s in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(s, use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": s
                    })
                    with st.spinner("Finding answer..."):
                        answer, sources, images = ask_text(s)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "images": images
                    })
                    st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                # Show matched images
                if msg.get("images"):
                    valid_images = [
                        img for img in msg["images"]
                        if img.get("path") and os.path.exists(img["path"])
                    ]
                    if valid_images:
                        st.markdown("**🖼️ Related Traffic Signs:**")
                        img_cols = st.columns(len(valid_images))
                        for j, img_data in enumerate(valid_images):
                            with img_cols[j]:
                                image = Image.open(img_data["path"])
                                st.image(
                                    image,
                                    caption=img_data["filename"].replace("_", " ").replace(".jpg", ""),
                                    width=150
                                )
                # Show sources
                if msg.get("sources"):
                    with st.expander("📚 View Sources"):
                        for j, src in enumerate(msg["sources"]):
                            st.markdown(f"**Source {j+1}:** `{src['source']}` — {src['type']}")
                            st.info(src["text"][:300])

    # Chat input
    if query := st.chat_input("Ask about TN driving license or traffic rules..."):
        st.session_state.messages.append({
            "role": "user",
            "content": query
        })
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            with st.spinner("Finding answer..."):
                answer, sources, images = ask_text(query)
            st.markdown(answer)
            # Show matched images
            valid_images = [
                img for img in images
                if img.get("path") and os.path.exists(img["path"])
            ]
            if valid_images:
                st.markdown("**🖼️ Related Traffic Signs:**")
                img_cols = st.columns(len(valid_images))
                for j, img_data in enumerate(valid_images):
                    with img_cols[j]:
                        image = Image.open(img_data["path"])
                        st.image(
                            image,
                            caption=img_data["filename"].replace("_", " ").replace(".jpg", ""),
                            width=150
                        )
            with st.expander("📚 View Sources"):
                for j, src in enumerate(sources):
                    st.markdown(f"**Source {j+1}:** `{src['source']}` — {src['type']}")
                    st.info(src["text"][:300])
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "images": images
            })

# ── Tab 2 — Traffic Sign Identifier ───────────────────────
with tab2:
    st.markdown("### 🚦 Upload a Traffic Sign Image")
    st.caption("Upload any traffic sign image and get its meaning instantly")

    uploaded = st.file_uploader(
        "Upload traffic sign image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded:
        # Save temp file
        temp_path = f"temp_{uploaded.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded.getbuffer())

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded, caption="Uploaded Sign", width=200)

        with col2:
            with st.spinner("Identifying sign..."):
                answer, matched = ask_image(temp_path)

            st.markdown("### 📋 Sign Explanation")
            st.markdown(answer)

            if matched:
                st.markdown("**🔍 Similar signs in database:**")
                m_cols = st.columns(len(matched))
                for j, img_data in enumerate(matched):
                    if img_data.get("path") and os.path.exists(img_data["path"]):
                        with m_cols[j]:
                            st.image(
                                img_data["path"],
                                caption=img_data["filename"].replace("_", " ").replace(".jpg", ""),
                                width=120
                            )

        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ── Tab 3 — RTO Offices ────────────────────────────────────
with tab3:
    st.markdown("### 🏛️ Find RTO Office in Tamil Nadu")

    import pandas as pd
    try:
        df = pd.read_csv("tn_license/csv/rto_offices.csv")

        # Search filter
        search = st.text_input(
            "🔍 Search by district or RTO name",
            placeholder="e.g. Chennai, Tambaram, Madurai"
        )

        if search:
            filtered = df[
                df.apply(lambda row: search.lower() in
                         row.astype(str).str.lower().to_string(), axis=1)
            ]
        else:
            filtered = df

        st.markdown(f"**Found {len(filtered)} RTO offices**")

        for _, row in filtered.iterrows():
            with st.expander(f"🏛️ {row['RTO_Code']} — {row['RTO_Name']}"):
                st.markdown(f"**District:** {row['District']}")
                st.markdown(f"**More Info:** [Click here]({row['More_Info']})")
                st.markdown(f"**Official Portal:** [parivahan.gov.in](https://sarathi.parivahan.gov.in)")

    except Exception as e:
        st.error(f"Could not load RTO data: {e}")